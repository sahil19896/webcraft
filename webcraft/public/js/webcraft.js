(function () {
	"use strict";

	if (window.__wcBootstrapped) return;
	window.__wcBootstrapped = true;

	const REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

	function onReady(fn) {
		if (document.readyState === "loading") {
			document.addEventListener("DOMContentLoaded", fn, { once: true });
		} else {
			fn();
		}
	}

	function animationsEnabled() {
		const page = document.querySelector(".wc-page");
		return page && page.dataset.animationsEnabled !== "0";
	}

	function revealOnScroll() {
		const sections = document.querySelectorAll(".wc-animate");
		if (!sections.length) return;

		const observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting) {
						entry.target.classList.add("is-visible");
						observer.unobserve(entry.target);
					}
				});
			},
			{ threshold: 0.1, rootMargin: "0px 0px -32px 0px" }
		);

		sections.forEach((el, index) => {
			el.style.transitionDelay = `${Math.min(index * 0.05, 0.3)}s`;
			observer.observe(el);
		});
	}

	function showAllImmediately() {
		document.querySelectorAll(".wc-animate").forEach((el) => el.classList.add("is-visible"));
	}

	function initAnimations() {
		if (document.body.classList.contains("wc-template-porto-restaurant")) {
			return;
		}
		if (!animationsEnabled() || REDUCED_MOTION) {
			showAllImmediately();
			return;
		}
		revealOnScroll();
	}

	function collectFormData(form) {
		const data = {};
		form.querySelectorAll("input, select, textarea").forEach((input) => {
			if (!input.name || input.type === "file") return;
			if (input.type === "checkbox") {
				data[input.name] = input.checked ? input.value || "1" : "";
			} else if (input.type === "radio") {
				if (input.checked) data[input.name] = input.value;
			} else if (input.classList.contains("wc-form__honeypot")) {
				data[input.name] = input.value;
			} else {
				data[input.name] = input.value;
			}
		});
		return data;
	}

	function bindForms() {
		document.querySelectorAll("[data-wc-form]").forEach((form) => {
			if (form.dataset.bound) return;
			form.dataset.bound = "1";

			form.addEventListener("submit", async (event) => {
				event.preventDefault();
				if (form.dataset.wcPreview) return;

				const status = form.querySelector(".wc-form__status");
				const formName = form.dataset.wcForm;

				if (!form.checkValidity()) {
					form.reportValidity();
					return;
				}

				const data = collectFormData(form);

				try {
					const response = await fetch("/api/method/webcraft.website_builder.api.submit_form", {
						method: "POST",
						headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": frappe?.csrf_token || "" },
						body: JSON.stringify({ form_name: formName, data }),
					});
					const result = await response.json();
					const payload = result.message || result;

					if (status) {
						status.hidden = false;
						status.textContent = payload.message || (payload.success ? "Submitted." : "Error.");
						status.classList.toggle("is-success", !!payload.success);
						status.classList.toggle("is-error", !payload.success);
					}

					if (payload.success) {
						form.reset();
						if (payload.redirect_url) window.location.href = payload.redirect_url;
					}
				} catch (error) {
					if (status) {
						status.hidden = false;
						status.textContent = "Something went wrong. Please try again.";
						status.classList.add("is-error");
					}
				}
			});
		});
	}

	onReady(() => {
		initAnimations();
		bindForms();
		initMobileNav();
		initHeroSliders();
	});

	function initHeroSliders() {
		if (document.body.classList.contains("wc-template-porto-restaurant")) {
			return;
		}
		document.querySelectorAll("[data-wc-hero-slider]").forEach((slider) => {
			if (slider.dataset.bound) return;
			slider.dataset.bound = "1";

			const slides = Array.from(slider.querySelectorAll("[data-wc-slide]"));
			const dots = Array.from(slider.querySelectorAll("[data-wc-slide-dot]"));
			const prev = slider.querySelector(".wc-hero-slider__nav--prev");
			const next = slider.querySelector(".wc-hero-slider__nav--next");
			if (slides.length < 2) return;

			let index = slides.findIndex((slide) => slide.classList.contains("is-active"));
			if (index < 0) index = 0;

			const show = (nextIndex) => {
				index = (nextIndex + slides.length) % slides.length;
				slides.forEach((slide, i) => slide.classList.toggle("is-active", i === index));
				dots.forEach((dot, i) => dot.classList.toggle("is-active", i === index));
			};

			prev?.addEventListener("click", () => show(index - 1));
			next?.addEventListener("click", () => show(index + 1));
			dots.forEach((dot) => {
				dot.addEventListener("click", () => show(Number(dot.dataset.wcSlideDot || 0)));
			});

			if (!REDUCED_MOTION && animationsEnabled()) {
				window.setInterval(() => show(index + 1), 7000);
			}
		});
	}

	function initMobileNav() {
		document.querySelectorAll(".wc-header").forEach((header) => {
			const toggle = header.querySelector(".wc-nav-toggle");
			const nav = header.querySelector(".wc-nav");
			if (!toggle || !nav || toggle.dataset.bound) return;
			toggle.dataset.bound = "1";

			toggle.addEventListener("click", () => {
				const open = header.classList.toggle("is-nav-open");
				toggle.setAttribute("aria-expanded", open ? "true" : "false");
			});

			nav.querySelectorAll("a").forEach((link) => {
				link.addEventListener("click", () => {
					header.classList.remove("is-nav-open");
					toggle.setAttribute("aria-expanded", "false");
				});
			});
		});
	}
})();
