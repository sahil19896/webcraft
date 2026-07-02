frappe.pages["webcraft-customize"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Edit site"),
		single_column: true,
	});
	frappe.webcraft_customize = new WebCraftSiteEditor(page);
	$(wrapper).bind("show", () => frappe.webcraft_customize?.on_show());
};

const WC_THEME_PRESETS = [
	{ name: __("Classic blue"), primary: "#2563eb", secondary: "#1e40af", accent: "#f59e0b", bg: "#ffffff", text: "#0f172a", surface: "#f8fafc" },
	{ name: __("Dark store"), primary: "#c4f000", secondary: "#1a1a1a", accent: "#c4f000", bg: "#0a0a0a", text: "#f5f5f5", surface: "#141414" },
	{ name: __("Warm"), primary: "#ea580c", secondary: "#9a3412", accent: "#fbbf24", bg: "#fffbeb", text: "#292524", surface: "#fef3c7" },
	{ name: __("Fresh"), primary: "#059669", secondary: "#047857", accent: "#34d399", bg: "#ffffff", text: "#064e3b", surface: "#ecfdf5" },
];

class WebCraftSiteEditor {
	constructor(page) {
		this.page = page;
		this.wrapper = $(page.body);
		this.project = null;
		this.theme = null;
		this.pages = [];
		this.currentPage = null;
		this.tab = "content";
		this.menus = { header: { items: [] }, footer: { items: [] } };
		this.publishStatus = null;
		this._saveTimer = null;
		this._previewTimer = null;
		this._focusHighlight = null;
		this._saving = false;
		this._dirty = false;
		this._dirtyTheme = false;
		this._dirtyContent = false;
		this._dirtyMenus = false;
		this._publishing = false;
		this.render_shell();
		this.bind_edit_bridge();
	}

	render_shell() {
		this.wrapper.html(`
			<div class="wc-customize">
				<header class="wc-customize__bar">
					<button class="btn btn-default btn-sm wc-btn-exit" title="${__("Back to theme store")}">←</button>
					<div class="wc-customize__bar-title">
						<strong class="wc-customize__title">${__("Edit site")}</strong>
						<span class="text-muted wc-customize__project"></span>
					</div>
					<div class="wc-customize__tabs">
						<button class="wc-customize__tab is-active" data-tab="content">${__("Pages")}</button>
						<button class="wc-customize__tab" data-tab="theme">${__("Look")}</button>
						<button class="wc-customize__tab" data-tab="navigation">${__("Navigation")}</button>
					</div>
					<div class="wc-customize__bar-spacer"></div>
					<span class="wc-customize__publish badge"></span>
					<span class="wc-customize__status text-muted">${__("All changes saved")}</span>
					<button class="btn btn-primary btn-sm wc-btn-publish">${__("Publish")}</button>
					<button class="btn btn-default btn-sm wc-btn-unpublish" style="display:none">${__("Unpublish")}</button>
					<button class="btn btn-default btn-sm wc-btn-preview-tab">${__("View live site")}</button>
				</header>
				<div class="wc-customize__body">
					<aside class="wc-customize__panel">
						<div class="wc-customize__panel-content" data-panel="content">
							<div class="wc-editor-tip" data-tip>
								<strong>${__("Tip")}</strong>
								<p>${__("Click any text or image in the preview to edit it here. Changes save automatically.")}</p>
								<button type="button" class="wc-editor-tip__dismiss">×</button>
							</div>
							<div class="wc-page-pills"></div>
							<div class="wc-content-sections"></div>
						</div>
						<div class="wc-customize__panel-theme" data-panel="theme" style="display:none">
							<section class="wc-customize__group">
								<h6>${__("Your brand")}</h6>
								<div class="wc-field">
									<label>${__("Site name")}</label>
									<input type="text" class="form-control input-sm" data-theme="brand_name" placeholder="${__("My Company")}">
								</div>
								<div class="wc-field wc-image-field wc-image-field--card" data-image-field="logo_image">
									<label>${__("Logo")}</label>
									<button type="button" class="wc-image-card wc-image-card--empty">
										<span class="wc-image-card__icon">+</span>
										<span class="wc-image-card__label">${__("Click to upload logo")}</span>
									</button>
									<input type="hidden" data-theme="logo_image">
								</div>
							</section>
							<section class="wc-customize__group">
								<h6>${__("Main color")}</h6>
								<div class="wc-field wc-color-pick">
									<input type="color" data-theme="primary_color" title="${__("Main color")}">
									<span class="wc-color-pick__label">${__("Buttons & links")}</span>
								</div>
								<div class="wc-preset-colors">
									${WC_THEME_PRESETS.map(
										(p, i) =>
											`<button type="button" class="wc-preset-color" data-preset="${i}" title="${frappe.utils.escape_html(p.name)}" style="background:${p.primary}"></button>`
									).join("")}
									<span class="text-muted wc-preset-colors__hint">${__("Quick styles")}</span>
								</div>
							</section>
							<details class="wc-customize__advanced">
								<summary>${__("More styling options")}</summary>
								<div class="wc-color-grid">
									<label>${__("Secondary")}<input type="color" data-theme="secondary_color"></label>
									<label>${__("Accent")}<input type="color" data-theme="accent_color"></label>
									<label>${__("Background")}<input type="color" data-theme="background_color"></label>
									<label>${__("Text")}<input type="color" data-theme="text_color"></label>
									<label>${__("Surface")}<input type="color" data-theme="surface_color"></label>
								</div>
								<div class="wc-field"><label>${__("Body font")}</label><input type="text" class="form-control input-sm" data-theme="font_family"></div>
								<div class="wc-field"><label>${__("Heading font")}</label><input type="text" class="form-control input-sm" data-theme="heading_font"></div>
								<div class="wc-field"><label>${__("Round corners")}</label><input type="range" data-theme="border_radius" min="0" max="24" step="1"></div>
							</details>
						</div>
						<div class="wc-customize__panel-nav" data-panel="navigation" style="display:none">
							<section class="wc-customize__group">
								<h6>${__("Header menu")}</h6>
								<div class="wc-menu-editor" data-menu="header"></div>
							</section>
							<section class="wc-customize__group">
								<h6>${__("Footer menu")}</h6>
								<p class="text-muted wc-menu-editor__hint">${__("Optional links shown in the site footer.")}</p>
								<div class="wc-menu-editor" data-menu="footer"></div>
							</section>
						</div>
					</aside>
					<div class="wc-customize__preview">
						<iframe class="wc-customize__frame" title="${__("Live preview")}"></iframe>
					</div>
				</div>
			</div>
		`);

		this.$frame = this.wrapper.find(".wc-customize__frame");
		this.$sections = this.wrapper.find(".wc-content-sections");
		this.$pagePills = this.wrapper.find(".wc-page-pills");
		this.$status = this.wrapper.find(".wc-customize__status");
		this.$publishBadge = this.wrapper.find(".wc-customize__publish");
		this.$btnPublish = this.wrapper.find(".wc-btn-publish");
		this.$btnUnpublish = this.wrapper.find(".wc-btn-unpublish");

		this.wrapper.find(".wc-btn-exit").on("click", () => frappe.set_route("webcraft"));
		this.wrapper.find(".wc-btn-preview-tab").on("click", () => {
			const url = this.get_preview_url(false);
			if (url) window.open(url, "_blank");
		});
		this.wrapper.find(".wc-btn-publish").on("click", () => this.toggle_publish(true));
		this.wrapper.find(".wc-btn-unpublish").on("click", () => this.toggle_publish(false));
		this.wrapper.find("[data-theme]").on("input change", () => {
			this._dirtyTheme = true;
			this.mark_dirty();
		});
		this.wrapper.find(".wc-customize__tab").on("click", (e) => this.switch_tab($(e.currentTarget).data("tab")));
		this.wrapper.find(".wc-preset-color").on("click", (e) => this.apply_preset($(e.currentTarget).data("preset")));
		this.wrapper.find(".wc-image-field[data-image-field='logo_image'] .wc-image-card").on("click", () => {
			this.open_image_uploader(this.wrapper.find("[data-theme='logo_image']"), true);
		});
		this.wrapper.find(".wc-editor-tip__dismiss").on("click", () => {
			this.wrapper.find("[data-tip]").slideUp(200);
			localStorage.setItem("webcraft_editor_tip_dismissed", "1");
		});

		if (localStorage.getItem("webcraft_editor_tip_dismissed")) {
			this.wrapper.find("[data-tip]").hide();
		}
	}

	bind_edit_bridge() {
		window.addEventListener("message", (event) => {
			if (event.origin !== window.location.origin) return;
			if (event.data?.type !== "webcraft-focus-field") return;
			this.focus_field(event.data);
		});
	}

	on_show() {
		const route = frappe.get_route();
		if (route[0] !== "webcraft-customize") {
			frappe.set_route("webcraft");
			return;
		}

		let tab = "content";
		const parts = route.slice(1);
		if (parts.length && ["theme", "content", "navigation"].includes(parts[parts.length - 1])) {
			tab = parts.pop();
		}
		const project = parts.join("/");

		if (!project) {
			frappe.set_route("webcraft");
			return;
		}
		this.tab = tab;
		this.load(project);
	}

	switch_tab(tab) {
		this.tab = tab;
		this.wrapper.find(".wc-customize__tab").removeClass("is-active");
		this.wrapper.find(`.wc-customize__tab[data-tab="${tab}"]`).addClass("is-active");
		this.wrapper.find('[data-panel="theme"]').toggle(tab === "theme");
		this.wrapper.find('[data-panel="content"]').toggle(tab === "content");
		this.wrapper.find('[data-panel="navigation"]').toggle(tab === "navigation");
		this.refresh_preview();
	}

	load(project) {
		frappe.call({
			method: "webcraft.website_builder.api.get_customize_context",
			args: { project },
			callback: (r) => {
				const ctx = r.message;
				if (!ctx?.theme) {
					frappe.msgprint({
						title: __("Site not found"),
						message: __("Could not load “{0}”. Open it from Theme Store → My sites.", [project]),
						indicator: "orange",
					});
					return;
				}
				this.project = ctx.project;
				this.theme = ctx.theme;
				this.pages = ctx.pages || [];
				this.menus = ctx.menus || { header: { items: [] }, footer: { items: [] } };
				this.publishStatus = ctx.publish_status || null;
				this.previewUrl = ctx.preview_url;
				this.wrapper.find(".wc-customize__project").text(ctx.project_name || ctx.project);
				this.populate_theme_fields();
				this.render_page_pills();
				this.render_menus();
				this.update_publish_ui();
				this.switch_tab(this.tab);
				this._dirty = false;
				this._dirtyTheme = false;
				this._dirtyContent = false;
				this._dirtyMenus = false;
				this.set_status("saved");
			},
		});
	}

	populate_theme_fields() {
		this.wrapper.find("[data-theme]").each((_, el) => {
			const field = el.dataset.theme;
			const value = this.theme[field];
			if (value != null && value !== "") el.value = value;
		});
		this.sync_logo_card();
	}

	sync_logo_card() {
		const url = this.wrapper.find("[data-theme='logo_image']").val();
		const $card = this.wrapper.find(".wc-image-field[data-image-field='logo_image'] .wc-image-card");
		if (url) {
			$card.removeClass("wc-image-card--empty").css("background-image", `url(${url})`);
			$card.find(".wc-image-card__label").text(__("Click to change logo"));
		} else {
			$card.addClass("wc-image-card--empty").css("background-image", "");
			$card.find(".wc-image-card__label").text(__("Click to upload logo"));
		}
	}

	apply_preset(index) {
		const preset = WC_THEME_PRESETS[index];
		if (!preset) return;
		const map = {
			primary_color: preset.primary,
			secondary_color: preset.secondary,
			accent_color: preset.accent,
			background_color: preset.bg,
			text_color: preset.text,
			surface_color: preset.surface,
		};
		Object.entries(map).forEach(([key, val]) => {
			this.wrapper.find(`[data-theme="${key}"]`).val(val);
		});
		this._dirtyTheme = true;
		this.mark_dirty();
		frappe.show_alert({ message: preset.name, indicator: "blue" });
	}

	render_page_pills() {
		this.$pagePills.empty();
		if (!this.pages.length) {
			this.$pagePills.hide();
			this.$sections.html(`<p class="text-muted">${__("No pages to edit yet.")}</p>`);
			return;
		}
		this.$pagePills.show();
		this.pages.forEach((p, i) => {
			const $btn = $(`<button type="button" class="wc-page-pill">${frappe.utils.escape_html(p.page_title || p.route)}</button>`);
			$btn.on("click", () => this.select_page(p.name));
			this.$pagePills.append($btn);
		});
		if (this.currentPage) {
			this.select_page(this.currentPage.name);
		} else {
			this.select_page(this.pages[0].name);
		}
	}

	select_page(pageName) {
		if (this._dirty && this.currentPage?.name && this.currentPage.name !== pageName) {
			this.save(false).then(() => this._apply_page(pageName));
			return;
		}
		this._apply_page(pageName);
	}

	_apply_page(pageName) {
		this.currentPage = this.pages.find((p) => p.name === pageName) || null;
		this.$pagePills.find(".wc-page-pill").removeClass("is-active");
		this.$pagePills.find(".wc-page-pill").each((i, el) => {
			if (this.pages[i]?.name === pageName) $(el).addClass("is-active");
		});
		this.render_content_sections();
		this.refresh_preview();
	}

	render_content_sections() {
		this.$sections.empty();
		if (!this.currentPage?.sections?.length) {
			this.$sections.html(`<p class="text-muted">${__("Nothing to edit on this page.")}</p>`);
			return;
		}

		this.currentPage.sections.forEach((section, idx) => {
			const $block = $(`
				<details class="wc-content-section" ${idx === 0 ? "open" : ""}>
					<summary class="wc-content-section__head">
						<span>${frappe.utils.escape_html(section.label)}</span>
						<label class="wc-section-toggle" title="${__("Show on page")}" onclick="event.stopPropagation()">
							<input type="checkbox" data-section-visible="${section.name}" ${section.visible !== false ? "checked" : ""}>
							<span>${__("Show")}</span>
						</label>
					</summary>
					<div class="wc-content-section__body" data-section="${section.name}"></div>
				</details>
			`);
			const $body = $block.find(".wc-content-section__body");
			this.render_schema_fields($body, section.schema?.fields || [], section.content, section.name);
			(section.schema?.repeaters || []).forEach((rep) => {
				this.render_repeater($body, rep, section.content, section.name);
			});
			$block.find("[data-section-visible]").on("change", () => {
				this._dirtyContent = true;
				this.mark_dirty();
			});
			this.$sections.append($block);
		});

		this.bind_content_change_handlers();
	}

	bind_content_change_handlers() {
		this.$sections.find("input, textarea, select").off("input.wcEditor change.wcEditor");
		this.$sections.find("input, textarea, select").on("input.wcEditor change.wcEditor", () => {
			this._dirtyContent = true;
			this.mark_dirty();
		});
	}

	render_schema_fields($container, fields, content, sectionName) {
		fields.forEach((field) => {
			const value = content?.[field.path];
			const id = `${sectionName}-${field.path}`.replace(/\./g, "-");

			if (field.type === "image") {
				$container.append(this.build_image_card(field, sectionName, id, value));
				return;
			}

			if (field.type === "select") {
				const opts = (field.options || [])
					.map(
						(o) =>
							`<option value="${frappe.utils.escape_html(o.value)}" ${o.value === value ? "selected" : ""}>${frappe.utils.escape_html(o.label)}</option>`
					)
					.join("");
				$container.append(this.build_field_wrap(field, id, `<select class="form-control input-sm" data-section="${sectionName}" data-path="${field.path}" id="${id}">${opts}</select>`));
				return;
			}

			let input = "";
			if (field.type === "textarea" || field.type === "html") {
				input = `<textarea class="form-control input-sm" rows="3" data-section="${sectionName}" data-path="${field.path}" id="${id}" placeholder="${frappe.utils.escape_html(field.label)}">${frappe.utils.escape_html(value || "")}</textarea>`;
			} else if (field.type === "lines") {
				const lines = Array.isArray(value) ? value.join("\n") : value || "";
				input = `<textarea class="form-control input-sm" rows="4" data-section="${sectionName}" data-path="${field.path}" data-type="lines" id="${id}" placeholder="${__("One per line")}">${frappe.utils.escape_html(lines)}</textarea>`;
			} else if (field.type === "number") {
				input = `<input type="number" class="form-control input-sm" data-section="${sectionName}" data-path="${field.path}" id="${id}" value="${frappe.utils.escape_html(String(value ?? ""))}">`;
			} else {
				input = `<input type="text" class="form-control input-sm" data-section="${sectionName}" data-path="${field.path}" id="${id}" value="${frappe.utils.escape_html(value || "")}" placeholder="${frappe.utils.escape_html(field.label)}">`;
			}
			$container.append(this.build_field_wrap(field, id, input));
		});
	}

	build_field_wrap(field, id, input) {
		return `
			<div class="wc-field">
				<label for="${id}">${frappe.utils.escape_html(field.label)}</label>
				${input}
				${field.help ? `<small class="text-muted">${frappe.utils.escape_html(field.help)}</small>` : ""}
			</div>
		`;
	}

	build_image_card(field, sectionName, id, value, repeaterField = null) {
		const dataAttrs = repeaterField
			? `data-field="${repeaterField}"`
			: `data-section="${sectionName}" data-path="${field.path}"`;
		const $wrap = $(`
			<div class="wc-field wc-image-field wc-image-field--card">
				<label>${frappe.utils.escape_html(field.label)}</label>
				<button type="button" class="wc-image-card ${value ? "" : "wc-image-card--empty"}">
					<span class="wc-image-card__icon">${value ? "↻" : "+"}</span>
					<span class="wc-image-card__label">${value ? __("Click to change") : __("Click to upload")}</span>
				</button>
				<input type="hidden" ${dataAttrs} id="${id}" value="${frappe.utils.escape_html(value || "")}">
			</div>
		`);
		if (value) $wrap.find(".wc-image-card").css("background-image", `url(${value})`);
		$wrap.find(".wc-image-card").on("click", () => {
			this.open_image_uploader($wrap.find("input"), true);
		});
		return $wrap;
	}

	render_repeater($container, repeater, content, sectionName) {
		const items = Array.isArray(content[repeater.path]) ? content[repeater.path] : [];
		const $wrap = $(`
			<div class="wc-repeater" data-section="${sectionName}" data-repeater="${repeater.path}">
				<h6 class="wc-repeater__title">${frappe.utils.escape_html(repeater.label)}</h6>
				<div class="wc-repeater__items"></div>
				<button type="button" class="btn btn-default btn-xs wc-repeater-add">+ ${__("Add")}</button>
			</div>
		`);
		const $items = $wrap.find(".wc-repeater__items");

		const renderRow = (item, index) => {
			const $row = $(`<div class="wc-repeater__row" data-index="${index}"><span class="wc-repeater__num">${index + 1}</span><div class="wc-repeater__fields"></div></div>`);
			const $fields = $row.find(".wc-repeater__fields");
			repeater.fields.forEach((field) => {
				const id = `${sectionName}-${repeater.path}-${index}-${field.path}`;
				const val = item?.[field.path] || "";
				if (field.type === "image") {
					$fields.append(this.build_image_card(field, sectionName, id, val, field.path));
					return;
				}
				const input =
					field.type === "textarea"
						? `<textarea class="form-control input-sm" rows="2" data-field="${field.path}" placeholder="${frappe.utils.escape_html(field.label)}">${frappe.utils.escape_html(val)}</textarea>`
						: `<input type="text" class="form-control input-sm" data-field="${field.path}" value="${frappe.utils.escape_html(val)}" placeholder="${frappe.utils.escape_html(field.label)}">`;
				$fields.append(`<div class="wc-field"><label>${frappe.utils.escape_html(field.label)}</label>${input}</div>`);
			});
			$row.append(`<button type="button" class="btn btn-link btn-xs text-danger wc-repeater-remove" title="${__("Remove")}">×</button>`);
			$row.find(".wc-repeater-remove").on("click", () => {
				$row.remove();
				$items.find(".wc-repeater__row").each((i, el) => {
					$(el).attr("data-index", i).find(".wc-repeater__num").text(i + 1);
				});
				this._dirtyContent = true;
				this.mark_dirty();
			});
			$items.append($row);
		};

		items.forEach((item, i) => renderRow(item, i));
		if (!items.length) renderRow({}, 0);

		$wrap.find(".wc-repeater-add").on("click", () => {
			renderRow({}, $items.find(".wc-repeater__row").length);
			this.bind_content_change_handlers();
			this._dirtyContent = true;
			this.mark_dirty();
		});
		$container.append($wrap);
	}

	open_image_uploader($input, isCard = false) {
		new frappe.ui.FileUploader({
			folder: "Home",
			restrictions: { allowed_file_types: ["image/*"] },
			on_success: (file) => {
				$input.val(file.file_url).trigger("change");
				if (isCard) {
					const $card = $input.closest(".wc-image-field").find(".wc-image-card");
					$card.removeClass("wc-image-card--empty").css("background-image", `url(${file.file_url})`);
					$card.find(".wc-image-card__label").text(__("Click to change"));
					if ($input.is("[data-theme='logo_image']")) this.sync_logo_card();
				}
				if ($input.is("[data-theme]")) this._dirtyTheme = true;
				else this._dirtyContent = true;
				this.mark_dirty();
			},
		});
	}

	render_menus() {
		["header", "footer"].forEach((location) => {
			const $editor = this.wrapper.find(`.wc-menu-editor[data-menu="${location}"]`);
			const block = this.menus?.[location] || { items: [] };
			this.render_menu_block($editor, location, block.items || []);
		});
	}

	render_menu_block($container, location, items) {
		$container.empty();
		const $list = $(`<div class="wc-menu-list" data-menu-list="${location}"></div>`);
		const renderRow = (item, index) => {
			const $row = $(`
				<div class="wc-menu-row" data-index="${index}">
					<input type="text" class="form-control input-sm" data-menu-label placeholder="${__("Label")}" value="${frappe.utils.escape_html(item.label || "")}">
					<input type="text" class="form-control input-sm" data-menu-url placeholder="${__("URL")}" value="${frappe.utils.escape_html(item.url || "")}">
					<label class="wc-menu-row__newtab">
						<input type="checkbox" data-menu-newtab ${item.open_in_new_tab ? "checked" : ""}>
						${__("New tab")}
					</label>
					<button type="button" class="btn btn-link btn-xs text-danger wc-menu-remove" title="${__("Remove")}">×</button>
				</div>
			`);
			$row.find("input").on("input change", () => {
				this._dirtyMenus = true;
				this.mark_dirty();
			});
			$row.find(".wc-menu-remove").on("click", () => {
				$row.remove();
				this._dirtyMenus = true;
				this.mark_dirty();
			});
			$list.append($row);
		};

		items.forEach((item, i) => renderRow(item, i));
		if (!items.length) renderRow({}, 0);

		$container.append($list);
		$container.append(
			`<button type="button" class="btn btn-default btn-xs wc-menu-add" data-menu-add="${location}">+ ${__("Add link")}</button>`
		);
		$container.find(".wc-menu-add").on("click", () => {
			renderRow({}, $list.find(".wc-menu-row").length);
			this._dirtyMenus = true;
			this.mark_dirty();
		});
	}

	collect_menus() {
		const payload = {
			header: { ...(this.menus.header || {}), items: [] },
			footer: { ...(this.menus.footer || {}), items: [] },
		};
		["header", "footer"].forEach((location) => {
			this.wrapper.find(`.wc-menu-list[data-menu-list="${location}"] .wc-menu-row`).each((_, row) => {
				const $row = $(row);
				const label = ($row.find("[data-menu-label]").val() || "").trim();
				const url = ($row.find("[data-menu-url]").val() || "").trim();
				if (!label) return;
				payload[location].items.push({
					label,
					url: url || "#",
					open_in_new_tab: $row.find("[data-menu-newtab]").is(":checked"),
				});
			});
		});
		return payload;
	}

	update_publish_ui() {
		const isLive = this.publishStatus?.is_live ?? this.publishStatus?.project_status === "Published";
		this.$publishBadge
			.text(isLive ? __("Live") : __("Draft"))
			.removeClass("badge-success badge-warning")
			.addClass(isLive ? "badge-success" : "badge-warning");
		this.$btnPublish.toggle(!isLive);
		this.$btnUnpublish.toggle(isLive);
	}

	toggle_publish(publish) {
		if (this._publishing || !this.project) return;
		this._publishing = true;
		const method = publish
			? "webcraft.website_builder.api.publish_project"
			: "webcraft.website_builder.api.unpublish_project";
		frappe.call({
			method,
			args: { project: this.project },
			callback: (r) => {
				this.publishStatus = {
					...(this.publishStatus || {}),
					project_status: r.message?.status || (publish ? "Published" : "Draft"),
					is_active: r.message?.is_active ?? publish,
					is_live: publish,
				};
				this.update_publish_ui();
				frappe.show_alert({
					message: publish ? __("Site published") : __("Site unpublished"),
					indicator: publish ? "green" : "blue",
				});
			},
			always: () => {
				this._publishing = false;
			},
		});
	}

	focus_field(payload) {
		if (payload.target === "theme") {
			this.switch_tab("theme");
			if (payload.fieldPath === "logo_image") {
				this.wrapper.find(".wc-image-field[data-image-field='logo_image'] .wc-image-card").focus();
			} else {
				this._highlight_field(this.wrapper.find(`[data-theme="${payload.fieldPath}"]`));
			}
			return;
		}

		this.switch_tab("content");
		const sectionId = payload.sectionId;
		const $details = this.wrapper.find(`.wc-content-section__body[data-section="${sectionId}"]`).closest(".wc-content-section");
		this.$sections.find(".wc-content-section").not($details).removeAttr("open");
		$details.prop("open", true);

		let $input;
		if (payload.index != null && payload.subField) {
			const $rep = this.wrapper.find(`.wc-repeater[data-section="${sectionId}"][data-repeater="${payload.fieldPath}"]`);
			$input = $rep.find(".wc-repeater__row").eq(payload.index).find(`[data-field="${payload.subField}"], [data-path="${payload.subField}"]`);
		} else {
			$input = this.wrapper.find(`[data-section="${sectionId}"][data-path="${payload.fieldPath}"]`);
		}
		this._highlight_field($input);
	}

	_highlight_field($input) {
		if (!$input?.length) return;
		clearTimeout(this._focusHighlight);
		const $el = $input.is(":hidden") ? $input.closest(".wc-image-field").find(".wc-image-card") : $input;
		$el[0]?.scrollIntoView({ behavior: "smooth", block: "center" });
		if ($el.is("input, textarea, select")) $el.focus();
		$el.closest(".wc-field, .wc-repeater__row, .wc-image-field").addClass("wc-field--focused");
		this._focusHighlight = setTimeout(() => {
			this.wrapper.find(".wc-field--focused").removeClass("wc-field--focused");
		}, 2500);
	}

	mark_dirty() {
		this._dirty = true;
		this.set_status("unsaved");
		clearTimeout(this._saveTimer);
		this._saveTimer = setTimeout(() => this.save(false), 1200);
		clearTimeout(this._previewTimer);
		this._previewTimer = setTimeout(() => this.refresh_preview(), 800);
	}

	set_status(state) {
		const labels = {
			saved: __("All changes saved"),
			saving: __("Saving…"),
			unsaved: __("Unsaved changes"),
			error: __("Could not save"),
		};
		this.$status.text(labels[state] || "").attr("data-state", state);
	}

	collect_theme_fields() {
		const data = {};
		this.wrapper.find("[data-theme]").each((_, el) => {
			data[el.dataset.theme] = el.value;
		});
		if (data.border_radius) data.border_radius = parseInt(data.border_radius, 10);
		return data;
	}

	collect_page_content() {
		if (!this.currentPage) return [];
		return this.currentPage.sections.map((sec) => {
			const content = { ...sec.content };
			this.wrapper
				.find(`[data-section="${sec.name}"][data-path]`)
				.filter(function () {
					return !$(this).closest(".wc-repeater").length;
				})
				.each((_, el) => {
					const path = el.dataset.path;
					if (el.dataset.type === "lines") {
						content[path] = el.value.split("\n").map((l) => l.trim()).filter(Boolean);
					} else if (el.tagName === "SELECT") {
						content[path] = el.value;
					} else if (el.type === "number") {
						content[path] = el.value ? parseInt(el.value, 10) : 0;
					} else {
						content[path] = el.value;
					}
				});
			this.wrapper.find(`.wc-repeater[data-section="${sec.name}"]`).each((_, rep) => {
				const repPath = rep.dataset.repeater;
				const rows = [];
				$(rep)
					.find(".wc-repeater__row")
					.each((_, row) => {
						const item = {};
						$(row)
							.find("[data-field], input[data-path]")
							.each((__, input) => {
								const key = input.dataset.field || input.dataset.path;
								if (key) item[key] = input.value;
							});
						if (Object.values(item).some((v) => String(v || "").trim())) rows.push(item);
					});
				content[repPath] = rows;
			});
			const $visible = this.wrapper.find(`[data-section-visible="${sec.name}"]`);
			return {
				name: sec.name,
				content,
				visible: $visible.length ? $visible.is(":checked") : sec.visible !== false,
			};
		});
	}

	get_preview_url(withEditMode = true) {
		let url = this.previewUrl;
		if (this.tab === "content" && this.currentPage?.preview_url) {
			url = this.currentPage.preview_url;
		}
		if (!url) return "";
		if (withEditMode && this.tab === "content") {
			url += `${url.includes("?") ? "&" : "?"}wc_edit=1`;
		}
		return url;
	}

	refresh_preview() {
		const url = this.get_preview_url();
		if (!url) return;
		const sep = url.includes("?") ? "&" : "?";
		this.$frame.attr("src", `${url}${sep}_=${Date.now()}`);
	}

	save(showAlert = true) {
		if (this._saving || !this.project) return Promise.resolve();
		if (!this._dirtyTheme && !this._dirtyContent && !this._dirtyMenus) {
			this.set_status("saved");
			return Promise.resolve();
		}

		this._saving = true;
		this.set_status("saving");

		const calls = [];
		if (this._dirtyTheme) {
			calls.push(
				frappe.call({
					method: "webcraft.website_builder.api.save_theme_customization",
					args: { project: this.project, theme_data: this.collect_theme_fields() },
				})
			);
		}
		if (this._dirtyContent && this.currentPage) {
			calls.push(
				frappe.call({
					method: "webcraft.website_builder.api.save_page_content",
					args: { page: this.currentPage.name, sections: this.collect_page_content() },
				})
			);
		}
		if (this._dirtyMenus) {
			calls.push(
				frappe.call({
					method: "webcraft.website_builder.api.save_project_menus",
					args: { project: this.project, menus: this.collect_menus() },
				})
			);
		}

		if (!calls.length) {
			this._saving = false;
			this.set_status("saved");
			return Promise.resolve();
		}

		return Promise.all(calls.map((p) => new Promise((resolve, reject) => p.then(resolve).catch(reject))))
			.then(() => {
				this._dirty = false;
				this._dirtyTheme = false;
				this._dirtyContent = false;
				this._dirtyMenus = false;
				this.set_status("saved");
				if (showAlert) frappe.show_alert({ message: __("Saved"), indicator: "green" });
				this.refresh_preview();
			})
			.catch(() => {
				this.set_status("error");
				frappe.show_alert({ message: __("Save failed — try again"), indicator: "red" });
			})
			.finally(() => {
				this._saving = false;
			});
	}
}
