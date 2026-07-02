(function () {
	"use strict";

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
			{ threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
		);

		sections.forEach((el, index) => {
			el.style.transitionDelay = `${Math.min(index * 0.06, 0.36)}s`;
			observer.observe(el);
		});
	}

	function collectFormData(form) {
		const data = {};
		const inputs = form.querySelectorAll("input, select, textarea");
		inputs.forEach((input) => {
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
						if (payload.redirect_url) {
							window.location.href = payload.redirect_url;
						}
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

	document.addEventListener("DOMContentLoaded", () => {
		revealOnScroll();
		bindForms();
	});
})();
