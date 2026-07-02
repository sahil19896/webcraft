(function () {
	"use strict";

	const root = document.querySelector(".wc-page");
	if (!root || root.dataset.commerceEnabled !== "1") return;

	const storePrefix = root.dataset.storePrefix || "store";
	const cartUrl = root.dataset.cartUrl || `/${storePrefix}/cart`;
	const checkoutUrl = root.dataset.checkoutUrl || `/${storePrefix}/checkout`;
	const isPreview = root.dataset.previewTemplate || "";
	const orderBase = isPreview
		? `/webcraft-preview/${isPreview}/order`
		: `/${storePrefix}/order`;

	function csrfToken() {
		return window.frappe?.csrf_token || "";
	}

	function isLoggedIn() {
		if (window.frappe?.session?.user) return frappe.session.user !== "Guest";
		const status = document.body.getAttribute("frappe-session-status");
		return status === "logged-in";
	}

	function loginUrl(redirectTo) {
		return `/login?redirect-to=${encodeURIComponent(redirectTo || window.location.pathname)}`;
	}

	async function call(method, args) {
		const response = await fetch(`/api/method/${method}`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-Frappe-CSRF-Token": csrfToken(),
			},
			body: JSON.stringify(args || {}),
			credentials: "same-origin",
		});
		const result = await response.json();
		if (result.exc) {
			let message = "Request failed.";
			try {
				const msgs = JSON.parse(result._server_messages || "[]");
				if (msgs.length) message = JSON.parse(msgs[0]).message || message;
			} catch (e) {
				/* ignore */
			}
			throw new Error(message);
		}
		return result.message;
	}

	function formatMoney(value, currency) {
		if (value == null || value === "") return "";
		const num = Number(value);
		if (Number.isNaN(num)) return String(value);
		try {
			return new Intl.NumberFormat(undefined, {
				style: "currency",
				currency: currency || "USD",
			}).format(num);
		} catch (e) {
			return num.toFixed(2);
		}
	}

	function productUrl(itemCode) {
		if (!itemCode) return "#";
		if (isPreview) return `/webcraft-preview/${isPreview}/product/${encodeURIComponent(itemCode)}`;
		return `/${storePrefix}/product/${encodeURIComponent(itemCode)}`;
	}

	function setCartCount(count) {
		document.querySelectorAll("[data-wc-cart-count]").forEach((el) => {
			const qty = parseInt(count, 10) || 0;
			el.textContent = String(qty);
			el.hidden = qty <= 0;
		});
	}

	function readCartCookie() {
		const match = document.cookie.match(/(?:^|;\s*)cart_count=([^;]*)/);
		return match ? decodeURIComponent(match[1]) : "0";
	}

	function showMessage(el, text, isError) {
		if (!el) return;
		el.hidden = !text;
		el.textContent = text || "";
		el.classList.toggle("is-error", !!isError);
		el.classList.toggle("is-success", !!text && !isError);
	}

	async function updateCart(itemCode, qty) {
		if (!isLoggedIn()) {
			window.location.href = loginUrl(window.location.pathname);
			return;
		}
		await call("webshop.webshop.shopping_cart.cart.update_cart", {
			item_code: itemCode,
			qty: qty,
		});
		setCartCount(readCartCookie());
	}

	function bindAddToCart() {
		document.querySelectorAll(".wc-add-to-cart").forEach((btn) => {
			if (btn.dataset.bound) return;
			btn.dataset.bound = "1";
			btn.addEventListener("click", async () => {
				const itemCode = btn.dataset.itemCode;
				if (!itemCode) return;
				const qtyInput = document.getElementById("wc-product-qty");
				const qty = qtyInput ? Math.max(1, parseInt(qtyInput.value, 10) || 1) : 1;
				btn.disabled = true;
				const status = document.querySelector("[data-wc-product-status]");
				try {
					await updateCart(itemCode, qty);
					showMessage(status, "Added to cart.", false);
					if (!document.querySelector('[data-wc-section="product_detail"]')) {
						setTimeout(() => {
							window.location.href = cartUrl;
						}, 400);
					}
				} catch (error) {
					showMessage(status, error.message, true);
				} finally {
					btn.disabled = false;
				}
			});
		});
	}

	function renderCartItem(item, currency) {
		const image = item.website_image || item.thumbnail || "";
		const name = item.web_item_name || item.item_name || item.item_code;
		return `
			<div class="wc-cart-item" data-item-code="${item.item_code}">
				<a href="${productUrl(item.item_code)}" class="wc-cart-item__media">
					${image ? `<img src="${image}" alt="">` : '<div class="wc-product-card__placeholder"></div>'}
				</a>
				<div class="wc-cart-item__body">
					<a href="${productUrl(item.item_code)}"><strong>${name}</strong></a>
					<p class="wc-muted">${formatMoney(item.rate, currency)} each</p>
					<div class="wc-cart-item__qty">
						<button type="button" class="wc-btn wc-btn--ghost wc-btn--sm" data-wc-qty-minus>-</button>
						<input type="number" class="wc-input wc-qty-input" value="${item.qty}" min="0" max="99">
						<button type="button" class="wc-btn wc-btn--ghost wc-btn--sm" data-wc-qty-plus>+</button>
					</div>
				</div>
				<div class="wc-cart-item__total">${formatMoney(item.amount, currency)}</div>
			</div>
		`;
	}

	function renderTotals(doc) {
		const currency = doc.currency || "USD";
		const rows = (doc.taxes || [])
			.map((tax) => `<div class="wc-summary-row"><span>${tax.description}</span><span>${formatMoney(tax.tax_amount, currency)}</span></div>`)
			.join("");
		return `
			<div class="wc-summary-row"><span>Subtotal</span><span>${formatMoney(doc.net_total, currency)}</span></div>
			${rows}
			<div class="wc-summary-row wc-summary-row--total"><span>Total</span><span>${formatMoney(doc.grand_total, currency)}</span></div>
		`;
	}

	async function loadCart() {
		const section = document.querySelector('[data-wc-section="cart"]');
		if (!section) return;

		const loading = section.querySelector("[data-wc-cart-loading]");
		const empty = section.querySelector("[data-wc-cart-empty]");
		const body = section.querySelector("[data-wc-cart-body]");
		const itemsEl = section.querySelector("[data-wc-cart-items]");
		const totalsEl = section.querySelector("[data-wc-cart-totals]");
		const message = section.querySelector("[data-wc-commerce-message]");

		if (!isLoggedIn()) {
			if (loading) loading.hidden = true;
			showMessage(message, "Please log in to view your cart.", true);
			const link = document.createElement("a");
			link.className = "wc-btn wc-btn--primary";
			link.href = loginUrl(cartUrl);
			link.textContent = "Log In";
			message?.after(link);
			return;
		}

		try {
			const data = await call("webshop.webshop.shopping_cart.cart.get_cart_quotation");
			const doc = data.doc || {};
			const items = doc.items || [];
			if (loading) loading.hidden = true;

			if (!items.length) {
				if (empty) empty.hidden = false;
				setCartCount(0);
				return;
			}

			if (body) body.hidden = false;
			if (itemsEl) {
				itemsEl.innerHTML = items.map((item) => renderCartItem(item, doc.currency)).join("");
				bindCartQtyHandlers(itemsEl, doc.currency);
			}
			if (totalsEl) totalsEl.innerHTML = renderTotals(doc);
			setCartCount(doc.total_qty || readCartCookie());
		} catch (error) {
			if (loading) loading.hidden = true;
			showMessage(message, error.message, true);
		}
	}

	function bindCartQtyHandlers(container, currency) {
		container.querySelectorAll(".wc-cart-item").forEach((row) => {
			const itemCode = row.dataset.itemCode;
			const input = row.querySelector("input");
			const apply = async (qty) => {
				try {
					await updateCart(itemCode, qty);
					await loadCart();
				} catch (error) {
					alert(error.message);
				}
			};
			row.querySelector("[data-wc-qty-minus]")?.addEventListener("click", () => {
				const next = Math.max(0, (parseInt(input.value, 10) || 0) - 1);
				apply(next);
			});
			row.querySelector("[data-wc-qty-plus]")?.addEventListener("click", () => {
				const next = (parseInt(input.value, 10) || 0) + 1;
				apply(next);
			});
			input?.addEventListener("change", () => {
				const next = Math.max(0, parseInt(input.value, 10) || 0);
				apply(next);
			});
		});
	}

	function fillAddressSelect(select, addresses, selected) {
		if (!select) return;
		select.innerHTML = (addresses || [])
			.map((addr) => `<option value="${addr.name}" ${addr.name === selected ? "selected" : ""}>${addr.title || addr.display || addr.name}</option>`)
			.join("");
	}

	async function loadCheckout() {
		const section = document.querySelector('[data-wc-section="checkout"]');
		if (!section) return;

		const loading = section.querySelector("[data-wc-checkout-loading]");
		const guest = section.querySelector("[data-wc-checkout-guest]");
		const body = section.querySelector("[data-wc-checkout-body]");
		const message = section.querySelector("[data-wc-commerce-message]");

		if (!isLoggedIn()) {
			if (loading) loading.hidden = true;
			if (guest) guest.hidden = false;
			return;
		}

		try {
			const data = await call("webshop.webshop.shopping_cart.cart.get_cart_quotation");
			const doc = data.doc || {};
			if (!(doc.items || []).length) {
				if (loading) loading.hidden = true;
				showMessage(message, "Your cart is empty.", true);
				return;
			}

			if (loading) loading.hidden = true;
			if (body) body.hidden = false;

			const shipSelect = section.querySelector("[data-wc-shipping-address]");
			const billSelect = section.querySelector("[data-wc-billing-address]");
			fillAddressSelect(shipSelect, data.shipping_addresses, doc.shipping_address_name);
			fillAddressSelect(billSelect, data.billing_addresses, doc.customer_address);

			const itemsEl = section.querySelector("[data-wc-checkout-items]");
			const totalsEl = section.querySelector("[data-wc-checkout-totals]");
			if (itemsEl) {
				itemsEl.innerHTML = (doc.items || [])
					.map((item) => `<div class="wc-summary-row"><span>${item.qty}× ${item.web_item_name || item.item_name}</span><span>${formatMoney(item.amount, doc.currency)}</span></div>`)
					.join("");
			}
			if (totalsEl) totalsEl.innerHTML = renderTotals(doc);

			shipSelect?.addEventListener("change", async () => {
				await call("webshop.webshop.shopping_cart.cart.update_cart_address", {
					address_type: "shipping",
					address_name: shipSelect.value,
				});
				await loadCheckout();
			});
			billSelect?.addEventListener("change", async () => {
				await call("webshop.webshop.shopping_cart.cart.update_cart_address", {
					address_type: "billing",
					address_name: billSelect.value,
				});
				await loadCheckout();
			});

			const addressForm = section.querySelector("[data-wc-address-form]");
			addressForm?.addEventListener("submit", async (event) => {
				event.preventDefault();
				const formData = new FormData(addressForm);
				const docPayload = Object.fromEntries(formData.entries());
				docPayload.doctype = "Address";
				await call("webshop.webshop.shopping_cart.cart.add_new_address", { doc: docPayload });
				addressForm.reset();
				await loadCheckout();
			});

			const placeBtn = section.querySelector("[data-wc-place-order]");
			placeBtn?.addEventListener("click", async () => {
				placeBtn.disabled = true;
				try {
					const result = await call("webcraft.website_builder.commerce.api.place_store_order");
					const orderName = result.sales_order;
					window.location.href = `${orderBase}/${encodeURIComponent(orderName)}`;
				} catch (error) {
					showMessage(message, error.message, true);
					placeBtn.disabled = false;
				}
			});
		} catch (error) {
			if (loading) loading.hidden = true;
			showMessage(message, error.message, true);
		}
	}

	async function loadOrder() {
		const section = document.querySelector('[data-wc-section="order_confirmation"]');
		if (!section) return;

		const orderName = section.querySelector("[data-wc-order-root]")?.dataset.orderName;
		const loading = section.querySelector("[data-wc-order-loading]");
		const body = section.querySelector("[data-wc-order-body]");
		const message = section.querySelector("[data-wc-commerce-message]");

		if (!orderName) {
			if (loading) loading.hidden = true;
			showMessage(message, "Order not found.", true);
			return;
		}

		if (!isLoggedIn()) {
			if (loading) loading.hidden = true;
			showMessage(message, "Please log in to view your order.", true);
			return;
		}

		try {
			const order = await call("webcraft.website_builder.commerce.api.get_order_summary", {
				order_name: orderName,
			});
			if (!order.name) {
				throw new Error("Order not found or access denied.");
			}
			if (loading) loading.hidden = true;
			if (body) body.hidden = false;
			section.querySelector("[data-wc-order-id]").textContent = order.name;
			section.querySelector("[data-wc-order-total]").textContent = formatMoney(order.grand_total, order.currency);
			const itemsEl = section.querySelector("[data-wc-order-items]");
			if (itemsEl) {
				itemsEl.innerHTML = (order.items || [])
					.map((item) => `<div class="wc-summary-row"><span>${item.qty}× ${item.item_name}</span><span>${formatMoney(item.amount, order.currency)}</span></div>`)
					.join("");
			}
		} catch (error) {
			if (loading) loading.hidden = true;
			showMessage(message, error.message, true);
		}
	}

	document.addEventListener("DOMContentLoaded", () => {
		setCartCount(readCartCookie());
		bindAddToCart();
		loadCart();
		loadCheckout();
		loadOrder();
	});
})();
