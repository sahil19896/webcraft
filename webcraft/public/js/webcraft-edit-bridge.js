/**
 * WebCraft click-to-edit bridge — runs inside the preview iframe when ?wc_edit=1.
 */
(function () {
	const configEl = document.getElementById("wc-edit-config");
	if (!configEl) return;

	let config;
	try {
		config = JSON.parse(configEl.textContent || "{}");
	} catch (e) {
		return;
	}

	document.body.classList.add("wc-edit-mode");

	const tip = document.createElement("div");
	tip.className = "wc-edit-tooltip";
	tip.hidden = true;
	document.body.appendChild(tip);

	function postFocus(payload) {
		window.parent.postMessage({ type: "webcraft-focus-field", ...payload }, window.location.origin);
	}

	function showTip(target, label) {
		if (!label) return;
		tip.textContent = label;
		tip.hidden = false;
		const rect = target.getBoundingClientRect();
		tip.style.top = `${Math.max(8, rect.top - 36 + window.scrollY)}px`;
		tip.style.left = `${Math.min(window.innerWidth - 160, rect.left + window.scrollX)}px`;
	}

	function hideTip() {
		tip.hidden = true;
	}

	function bindTarget(target, label, onClick) {
		if (!target) return;
		target.classList.add("wc-editable");
		target.addEventListener("mouseenter", () => showTip(target, label || "Click to edit"));
		target.addEventListener("mouseleave", hideTip);
		target.addEventListener("click", (e) => {
			e.preventDefault();
			e.stopPropagation();
			hideTip();
			onClick();
		});
	}

	function bindScalar(sectionRoot, sectionId, fieldPath, selector, label) {
		bindTarget(sectionRoot.querySelector(selector), label, () => {
			postFocus({ sectionId, fieldPath });
		});
	}

	function bindRepeater(sectionRoot, sectionId, repeaterPath, repeaterDef) {
		const rows = sectionRoot.querySelectorAll(repeaterDef.container);
		rows.forEach((row, index) => {
			Object.entries(repeaterDef.fields || {}).forEach(([subField, selector]) => {
				const label = repeaterDef.labels?.[subField] || subField;
				bindTarget(row.querySelector(selector), label, () => {
					postFocus({ sectionId, fieldPath: repeaterPath, index, subField });
				});
			});
		});
	}

	(config.sections || []).forEach((section) => {
		const root = document.querySelector(`[data-wc-section-id="${section.id}"]`);
		if (!root) return;

		Object.entries(section.fields || {}).forEach(([fieldPath, meta]) => {
			const selector = typeof meta === "string" ? meta : meta.selector;
			const label = typeof meta === "string" ? fieldPath : meta.label;
			bindScalar(root, section.id, fieldPath, selector, label);
		});

		Object.entries(section.repeaters || {}).forEach(([repeaterPath, repeaterDef]) => {
			bindRepeater(root, section.id, repeaterPath, repeaterDef);
		});
	});

	Object.entries(config.theme_targets || {}).forEach(([field, meta]) => {
		const selector = typeof meta === "string" ? meta : meta.selector;
		const label = typeof meta === "string" ? field : meta.label;
		document.querySelectorAll(selector).forEach((target) => {
			bindTarget(target, label || "Edit site look", () => {
				postFocus({ target: "theme", fieldPath: field });
			});
		});
	});
})();
