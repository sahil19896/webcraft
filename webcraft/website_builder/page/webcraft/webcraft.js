frappe.pages["webcraft"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("WebCraft"),
		single_column: true,
	});
	frappe.webcraft_gallery = new WebCraftGallery(page);
	$(wrapper).bind("show", () => frappe.webcraft_gallery?.on_show());
};

class WebCraftGallery {
	constructor(page) {
		this.page = page;
		this.wrapper = $(page.body);
		this.designs = [];
		this.mySites = [];
		this.current = null;
		this.view = "store";
		this.tab = "themes";
		this.category = "All";
		this.device = "desktop";
		this.render_shell();
	}

	render_shell() {
		this.wrapper.html(`
			<div class="wc-store">
				<div class="wc-store__view wc-store__view--store">
					<header class="wc-store__hero">
						<div class="wc-store__hero-copy">
							<p class="wc-store__eyebrow">${__("Theme store")}</p>
							<h1>${__("Pick a design. Preview everything. Go live.")}</h1>
							<p class="wc-store__hero-desc">${__("Shopify-style pre-built website templates for Frappe — browse, preview every page, customize, and publish.")}</p>
						</div>
					</header>
					<nav class="wc-store__tabs">
						<button class="wc-store__tab is-active" data-tab="themes">${__("Theme store")}</button>
						<button class="wc-store__tab" data-tab="my-sites">${__("My sites")}</button>
						<div class="wc-store__tabs-spacer"></div>
						<div class="wc-store__filters" data-panel="themes">
							<button class="wc-store__filter is-active" data-category="All">${__("All")}</button>
							<button class="wc-store__filter" data-category="Corporate">${__("Corporate")}</button>
							<button class="wc-store__filter" data-category="Agency">${__("Agency")}</button>
							<button class="wc-store__filter" data-category="E-Commerce">${__("E-Commerce")}</button>
						</div>
					</nav>
					<div class="wc-store__panel" data-panel="themes">
						<div class="wc-store__grid"></div>
					</div>
					<div class="wc-store__panel" data-panel="my-sites" style="display:none">
						<div class="wc-store__sites"></div>
					</div>
				</div>

				<div class="wc-store__view wc-store__view--preview" style="display:none">
					<header class="wc-preview-bar">
						<button class="btn btn-default btn-sm wc-btn-back">${__("← Theme store")}</button>
						<div class="wc-preview-bar__title">
							<strong class="wc-preview-bar__name"></strong>
							<span class="wc-preview-bar__category text-muted"></span>
						</div>
						<div class="wc-preview-bar__devices">
							<button class="wc-device-btn is-active" data-device="desktop" title="${__("Desktop")}">🖥</button>
							<button class="wc-device-btn" data-device="tablet" title="${__("Tablet")}">📱</button>
							<button class="wc-device-btn" data-device="mobile" title="${__("Mobile")}">📲</button>
						</div>
						<div class="wc-preview-bar__spacer"></div>
						<button class="btn btn-default btn-sm wc-btn-open-tab">${__("Open preview")}</button>
						<button class="btn btn-primary btn-sm wc-btn-add-theme">${__("Add theme to site")}</button>
					</header>
					<div class="wc-preview-layout">
						<aside class="wc-preview-sidebar">
							<div class="wc-preview-sidebar__section">
								<h6>${__("Pages")}</h6>
								<div class="wc-preview-pages"></div>
							</div>
							<div class="wc-preview-sidebar__section">
								<h6>${__("Includes")}</h6>
								<ul class="wc-preview-features"></ul>
							</div>
						</aside>
						<div class="wc-preview-stage">
							<div class="wc-preview-frame-shell" data-device="desktop">
								<iframe class="wc-preview-frame" title="${__("Theme preview")}"></iframe>
							</div>
						</div>
					</div>
				</div>
			</div>
		`);

		this.$storeView = this.wrapper.find(".wc-store__view--store");
		this.$previewView = this.wrapper.find(".wc-store__view--preview");
		this.$grid = this.wrapper.find(".wc-store__grid");
		this.$sites = this.wrapper.find(".wc-store__sites");
		this.$frame = this.wrapper.find(".wc-preview-frame");
		this.$frameShell = this.wrapper.find(".wc-preview-frame-shell");
		this.$pages = this.wrapper.find(".wc-preview-pages");
		this.$features = this.wrapper.find(".wc-preview-features");

		this.wrapper.find(".wc-store__tab").on("click", (e) => this.switch_tab($(e.currentTarget).data("tab")));
		this.wrapper.find(".wc-store__filter").on("click", (e) => this.filter_category($(e.currentTarget).data("category")));
		this.wrapper.find(".wc-btn-back").on("click", () => this.show_store());
		this.wrapper.find(".wc-btn-add-theme").on("click", () => this.install_design());
		this.wrapper.find(".wc-btn-open-tab").on("click", () => {
			if (this.current?.preview_url) window.open(this.current.preview_url, "_blank");
		});
		this.wrapper.find(".wc-device-btn").on("click", (e) => this.set_device($(e.currentTarget).data("device")));
	}

	on_show() {
		const route = frappe.get_route();
		const template = route.length > 1 && route[1] !== "customize" ? route[1] : null;
		if (this._loading) return this._loading;
		this._loading = Promise.all([this.load_catalog(), this.load_my_sites()]).then(() => {
			if (template) this.open_design(template);
		}).finally(() => {
			this._loading = null;
		});
		return this._loading;
	}

	load_catalog() {
		return frappe.call({
			method: "webcraft.website_builder.api.get_design_catalog",
			callback: (r) => {
				this.designs = r.message || [];
				if (this.view === "store" && this.tab === "themes") this.render_themes();
			},
		});
	}

	load_my_sites() {
		return frappe.call({
			method: "webcraft.website_builder.api.get_my_sites",
			callback: (r) => {
				this.mySites = r.message || [];
				if (this.view === "store" && this.tab === "my-sites") this.render_my_sites();
			},
		});
	}

	switch_tab(tab) {
		this.tab = tab;
		this.wrapper.find(".wc-store__tab").removeClass("is-active");
		this.wrapper.find(`.wc-store__tab[data-tab="${tab}"]`).addClass("is-active");
		this.wrapper.find('.wc-store__filters').toggle(tab === "themes");
		this.wrapper.find('[data-panel="themes"]').toggle(tab === "themes");
		this.wrapper.find('[data-panel="my-sites"]').toggle(tab === "my-sites");
		if (tab === "themes") this.render_themes();
		else this.render_my_sites();
	}

	filter_category(category) {
		this.category = category;
		this.wrapper.find(".wc-store__filter").removeClass("is-active");
		this.wrapper.find(`.wc-store__filter[data-category="${category}"]`).addClass("is-active");
		this.render_themes();
	}

	render_themes() {
		const filtered = this.designs.filter(
			(d) => this.category === "All" || (d.category || "") === this.category
		);
		this.$grid.empty();
		if (!filtered.length) {
			this.$grid.append(`<p class="wc-store__empty">${__("No themes in this category.")}</p>`);
			return;
		}

		filtered.forEach((d) => {
			const thumb = d.preview_image
				? `<img src="${frappe.utils.escape_html(d.preview_image)}" alt="" loading="lazy">`
				: `<div class="wc-theme-card__gradient" style="background:linear-gradient(135deg, ${d.theme?.primary_color || '#2563eb'}, ${d.theme?.background_color || '#0f172a'})"></div>`;
			const features = (d.features || []).slice(0, 3).map((f) => `<li>${frappe.utils.escape_html(f)}</li>`).join("");
			this.$grid.append(`
				<article class="wc-theme-card" data-key="${frappe.utils.escape_html(d.key)}">
					<div class="wc-theme-card__thumb">${thumb}
						<span class="wc-theme-card__badge">${frappe.utils.escape_html(d.category || "General")}</span>
						<div class="wc-theme-card__overlay">
							<button class="btn btn-primary btn-sm">${__("Preview")}</button>
						</div>
					</div>
					<div class="wc-theme-card__body">
						<div class="wc-theme-card__head">
							<h3>${frappe.utils.escape_html(d.title || d.key)}</h3>
							<span class="wc-theme-card__price">${__("Free")}</span>
						</div>
						<p>${frappe.utils.escape_html((d.description || "").slice(0, 120))}</p>
						${features ? `<ul class="wc-theme-card__features">${features}</ul>` : ""}
						<div class="wc-theme-card__meta">${d.page_count || 0} ${__("pages")}</div>
					</div>
				</article>
			`);
		});

		this.$grid.find(".wc-theme-card").on("click", (e) => {
			const key = $(e.currentTarget).data("key");
			this.open_design(key);
		});
	}

	render_my_sites() {
		this.$sites.empty();
		if (!this.mySites.length) {
			this.$sites.html(`
				<div class="wc-store__empty-state">
					<h3>${__("No sites yet")}</h3>
					<p>${__("Pick a theme from the store and add it to your site.")}</p>
					<button class="btn btn-primary btn-sm wc-go-themes">${__("Browse themes")}</button>
				</div>
			`);
			this.$sites.find(".wc-go-themes").on("click", () => this.switch_tab("themes"));
			return;
		}

		this.$sites.append(`<div class="wc-sites-grid"></div>`);
		const $grid = this.$sites.find(".wc-sites-grid");
		this.mySites.forEach((site) => {
			const statusClass = (site.status || "Draft").toLowerCase();
			$grid.append(`
				<article class="wc-site-card">
					<div class="wc-site-card__head">
						<h3>${frappe.utils.escape_html(site.project_name)}</h3>
						<span class="wc-site-card__status wc-site-card__status--${statusClass}">${frappe.utils.escape_html(site.status || "Draft")}</span>
					</div>
					<p class="text-muted">${frappe.utils.escape_html(site.template_title || site.website_template || "")}</p>
					<div class="wc-site-card__actions">
						${site.live_url ? `<button class="btn btn-default btn-sm" data-action="view" data-url="${frappe.utils.escape_html(site.live_url)}">${__("View site")}</button>` : ""}
						<button class="btn btn-primary btn-sm" data-action="customize" data-project="${frappe.utils.escape_html(site.name)}">${__("Edit site")}</button>
						<button class="btn btn-default btn-sm" data-action="form" data-project="${frappe.utils.escape_html(site.name)}">${__("Settings")}</button>
					</div>
				</article>
			`);
		});

		$grid.find("button").on("click", (e) => {
			e.stopPropagation();
			const btn = $(e.currentTarget);
			const action = btn.data("action");
			if (action === "view") window.open(btn.data("url"), "_blank");
			if (action === "customize") frappe.set_route("webcraft-customize", btn.data("project"));
			if (action === "form") frappe.set_route("Form", "Website Project", btn.data("project"));
		});
	}

	open_design(templateKey) {
		frappe.call({
			method: "webcraft.website_builder.api.get_design",
			args: { template_key: templateKey },
			callback: (r) => {
				const design = r.message;
				if (!design?.key) return;
				this.current = design;
				this.view = "preview";
				frappe.set_route("webcraft", templateKey);
				this.show_preview();
			},
		});
	}

	show_preview() {
		this.$storeView.hide();
		this.$previewView.show();
		this.wrapper.find(".wc-preview-bar__name").text(this.current.title);
		this.wrapper.find(".wc-preview-bar__category").text(this.current.category || "");

		this.$pages.empty();
		(this.current.pages || []).forEach((p, i) => {
			this.$pages.append(`
				<button class="wc-preview-page-btn ${i === 0 ? "is-active" : ""}" data-url="${frappe.utils.escape_html(p.preview_url)}">
					${frappe.utils.escape_html(p.title)}
				</button>
			`);
		});

		this.$features.empty();
		(this.current.features || []).forEach((f) => {
			this.$features.append(`<li>${frappe.utils.escape_html(f)}</li>`);
		});

		const first = (this.current.pages || [])[0];
		if (first) {
			this.$frame.attr("src", first.preview_url);
			this.current.preview_url = first.preview_url;
		}

		this.$pages.find(".wc-preview-page-btn").on("click", (e) => {
			const url = $(e.currentTarget).data("url");
			this.$pages.find(".wc-preview-page-btn").removeClass("is-active");
			$(e.currentTarget).addClass("is-active");
			this.$frame.attr("src", url);
			this.current.preview_url = url;
		});
	}

	set_device(device) {
		this.device = device;
		this.wrapper.find(".wc-device-btn").removeClass("is-active");
		this.wrapper.find(`.wc-device-btn[data-device="${device}"]`).addClass("is-active");
		this.$frameShell.attr("data-device", device);
	}

	show_store() {
		this.view = "store";
		this.current = null;
		frappe.set_route("webcraft");
		this.$previewView.hide();
		this.$storeView.show();
		this.switch_tab(this.tab);
	}

	install_design() {
		if (!this.current) return;
		const d = new frappe.ui.Dialog({
			title: __("Add theme to site"),
			fields: [
				{
					fieldname: "project_name",
					label: __("Site name"),
					fieldtype: "Data",
					reqd: 1,
					default: this.current.title,
					description: __("This becomes your Website Project name and live site label."),
				},
				{
					fieldname: "publish",
					label: __("Publish immediately"),
					fieldtype: "Check",
					default: 1,
				},
				{
					fieldname: "customize",
					label: __("Open editor after install"),
					fieldtype: "Check",
					default: 1,
				},
			],
			primary_action_label: __("Add theme"),
			primary_action: (values) => {
				d.hide();
				frappe.call({
					method: "webcraft.website_builder.api.install_design",
					args: {
						project_name: values.project_name,
						template_key: this.current.key,
						publish: values.publish ? 1 : 0,
					},
					freeze: true,
					callback: (r) => {
						const project = r.message?.project;
						const route = r.message?.publish?.homepage_route;
						frappe.show_alert({ message: __("Theme installed successfully"), indicator: "green" });
						this.load_my_sites();
						if (values.customize && project) {
							frappe.set_route("webcraft-customize", project);
						} else if (route) {
							window.open(`/${route}`, "_blank");
							frappe.set_route("Form", "Website Project", project);
						}
					},
				});
			},
		});
		d.show();
	}
}
