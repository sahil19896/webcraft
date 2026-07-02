(function () {
	"use strict";

	if (window.__wcPortoBootstrapped) return;
	window.__wcPortoBootstrapped = true;

	const REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
	const PORTO_ANIMATION_MS = 750;

	function onReady(fn) {
		if (document.readyState === "loading") {
			document.addEventListener("DOMContentLoaded", fn, { once: true });
		} else {
			fn();
		}
	}

	function isPortoRestaurant() {
		return document.body.classList.contains("wc-template-porto-restaurant");
	}

	function animationsEnabled() {
		const page = document.querySelector(".wc-page");
		return page && page.dataset.animationsEnabled !== "0";
	}

	function resetAppear(el) {
		el.classList.remove("wc-porto-animated");
		el.style.animationName = "";
		el.style.animationDelay = "";
	}

	function runAppear(el) {
		const name = el.dataset.wcAppear;
		if (!name) return;
		resetAppear(el);
		void el.offsetWidth;
		const delay = Number(el.dataset.wcAppearDelay || 0);
		el.style.animationDelay = `${delay}ms`;
		el.classList.add("wc-porto-animated");
		el.style.animationName = name;
	}

	function animateElements(elements) {
		elements.forEach((el) => runAppear(el));
	}

	function animateHeroSlide(slide) {
		if (!slide || REDUCED_MOTION || !animationsEnabled()) {
			slide?.querySelectorAll("[data-wc-appear]").forEach((el) => {
				el.classList.add("wc-porto-animated");
				el.style.opacity = "1";
				el.style.animationName = "none";
			});
			return;
		}
		const items = Array.from(slide.querySelectorAll("[data-wc-appear]"));
		items.forEach((el) => resetAppear(el));
		items.forEach((el) => runAppear(el));
	}

	function initHeroSliders() {
		document.querySelectorAll("[data-wc-hero-slider]").forEach((slider) => {
			if (slider.dataset.bound) return;
			slider.dataset.bound = "1";

			const slides = Array.from(slider.querySelectorAll("[data-wc-slide]"));
			const dots = Array.from(slider.querySelectorAll("[data-wc-slide-dot]"));
			const prev = slider.querySelector(".wc-hero-slider__nav--prev");
			const next = slider.querySelector(".wc-hero-slider__nav--next");
			if (!slides.length) return;

			let index = slides.findIndex((slide) => slide.classList.contains("is-active"));
			if (index < 0) index = 0;

			let timer = null;

			const show = (nextIndex, animate = true) => {
				index = (nextIndex + slides.length) % slides.length;
				slides.forEach((slide, i) => {
					const active = i === index;
					slide.classList.toggle("is-active", active);
					if (!active) {
						slide.querySelectorAll("[data-wc-appear]").forEach((el) => resetAppear(el));
					}
				});
				dots.forEach((dot, i) => dot.classList.toggle("is-active", i === index));
				if (animate) {
					window.setTimeout(() => animateHeroSlide(slides[index]), 80);
				}
			};

			prev?.addEventListener("click", () => {
				show(index - 1);
				restartAutoplay();
			});
			next?.addEventListener("click", () => {
				show(index + 1);
				restartAutoplay();
			});
			dots.forEach((dot) => {
				dot.addEventListener("click", () => {
					show(Number(dot.dataset.wcSlideDot || 0));
					restartAutoplay();
				});
			});

			function restartAutoplay() {
				if (timer) window.clearInterval(timer);
				if (REDUCED_MOTION || !animationsEnabled() || slides.length < 2) return;
				timer = window.setInterval(() => show(index + 1), 7000);
			}

			show(index, false);
			animateHeroSlide(slides[index]);
			restartAutoplay();
		});
	}

	function initScrollAppear() {
		const targets = Array.from(document.querySelectorAll("[data-wc-appear]:not(.wc-hero-slide [data-wc-appear])"));
		if (!targets.length) return;

		if (REDUCED_MOTION || !animationsEnabled()) {
			targets.forEach((el) => {
				el.classList.add("wc-porto-animated");
				el.style.opacity = "1";
				el.style.animationName = "none";
			});
			return;
		}

		const observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (!entry.isIntersecting) return;
					runAppear(entry.target);
					observer.unobserve(entry.target);
				});
			},
			{ threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
		);

		targets.forEach((el) => observer.observe(el));
	}

	function initPortoCarousels() {
		document.querySelectorAll("[data-wc-porto-carousel]").forEach((root) => {
			if (root.dataset.bound) return;
			root.dataset.bound = "1";

			const track = root.querySelector(".wc-porto-carousel__track");
			if (!track) return;

			const items = Array.from(track.children);
			const perPage = root.dataset.wcPortoCarousel === "team" ? 2 : 2;
			if (items.length <= perPage) return;

			let page = 0;
			const pageCount = Math.ceil(items.length / perPage);

			const render = () => {
				items.forEach((item, index) => {
					const itemPage = Math.floor(index / perPage);
					item.hidden = itemPage !== page;
				});
			};

			root.querySelector(".wc-porto-carousel__btn--prev")?.addEventListener("click", () => {
				page = (page - 1 + pageCount) % pageCount;
				render();
			});
			root.querySelector(".wc-porto-carousel__btn--next")?.addEventListener("click", () => {
				page = (page + 1) % pageCount;
				render();
			});

			render();
		});
	}

	function initMenuTabs() {
		document.querySelectorAll("[data-wc-menu-tabs]").forEach((root) => {
			if (root.dataset.bound) return;
			root.dataset.bound = "1";
			const buttons = Array.from(root.querySelectorAll("[data-wc-menu-tab]"));
			const panels = Array.from(root.querySelectorAll("[data-wc-menu-panel]"));
			buttons.forEach((button) => {
				button.addEventListener("click", () => {
					const index = button.dataset.wcMenuTab;
					buttons.forEach((btn) => {
						const active = btn === button;
						btn.classList.toggle("is-active", active);
						btn.setAttribute("aria-selected", active ? "true" : "false");
					});
					panels.forEach((panel) => {
						panel.classList.toggle("is-active", panel.dataset.wcMenuPanel === index);
					});
				});
			});
		});
	}

	onReady(() => {
		if (!isPortoRestaurant()) return;
		initHeroSliders();
		initScrollAppear();
		initMenuTabs();
		initPortoCarousels();
	});
})();
