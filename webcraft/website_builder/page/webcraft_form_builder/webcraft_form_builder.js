frappe.pages["webcraft-form-builder"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Form Builder"),
		single_column: true,
	});
	frappe.webcraft_form_builder = new WebCraftFormBuilder(page);
	$(wrapper).bind("show", () => frappe.webcraft_form_builder?.on_show());
};

class WebCraftFormBuilder {
	constructor(page) {
		this.page = page;
		this.wrapper = $(page.body);
		this.project = null;
		this.forms = [];
		this.render_shell();
	}

	render_shell() {
		this.wrapper.html(`
			<div class="wc-form-builder">
				<header class="wc-form-builder__bar">
					<button class="btn btn-default btn-sm wc-btn-back">← ${__("Back")}</button>
					<div class="wc-form-builder__title">
						<strong>${__("Forms")}</strong>
						<span class="text-muted wc-form-builder__project"></span>
					</div>
					<div class="wc-form-builder__bar-spacer"></div>
					<button class="btn btn-primary btn-sm wc-btn-new-form">${__("New form")}</button>
				</header>
				<div class="wc-form-builder__list"></div>
			</div>
		`);

		this.$list = this.wrapper.find(".wc-form-builder__list");
		this.wrapper.find(".wc-btn-back").on("click", () => {
			if (this.project) frappe.set_route("webcraft-customize", this.project);
			else frappe.set_route("webcraft");
		});
		this.wrapper.find(".wc-btn-new-form").on("click", () => this.create_form());
	}

	on_show() {
		const route = frappe.get_route();
		if (route[0] !== "webcraft-form-builder") return;
		this.project = route[1] || null;
		const selectedForm = route[2] || null;

		if (!this.project) {
			frappe.set_route("webcraft");
			return;
		}

		this.wrapper.find(".wc-form-builder__project").text(this.project);
		this.load_forms(selectedForm);
	}

	load_forms(openForm = null) {
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Website Form",
				filters: { website_project: this.project },
				fields: ["name", "form_title", "route", "modified"],
				order_by: "modified desc",
			},
			callback: (r) => {
				this.forms = r.message || [];
				this.render_list();
				if (openForm && this.forms.some((f) => f.name === openForm)) {
					this.open_form(openForm);
				}
			},
		});
	}

	render_list() {
		if (!this.forms.length) {
			this.$list.html(`
				<div class="wc-form-builder__empty">
					<p class="text-muted">${__("No forms yet for this site.")}</p>
					<button class="btn btn-primary btn-sm wc-btn-new-form-inline">${__("Create your first form")}</button>
				</div>
			`);
			this.$list.find(".wc-btn-new-form-inline").on("click", () => this.create_form());
			return;
		}

		const rows = this.forms
			.map(
				(f) => `
			<div class="wc-form-builder__row" data-form="${frappe.utils.escape_html(f.name)}">
				<div>
					<strong>${frappe.utils.escape_html(f.form_title || f.name)}</strong>
					<div class="text-muted">${frappe.utils.escape_html(f.route ? `/${f.route}` : f.name)}</div>
				</div>
				<div class="wc-form-builder__row-actions">
					<button class="btn btn-default btn-xs wc-btn-edit">${__("Edit")}</button>
					<button class="btn btn-default btn-xs wc-btn-submissions">${__("Submissions")}</button>
				</div>
			</div>`
			)
			.join("");

		this.$list.html(rows);
		this.$list.find(".wc-form-builder__row").each((_, el) => {
			const $row = $(el);
			const formName = $row.data("form");
			$row.find(".wc-btn-edit").on("click", () => this.open_form(formName));
			$row.find(".wc-btn-submissions").on("click", () => this.open_submissions(formName));
		});
	}

	create_form() {
		frappe.new_doc("Website Form", {
			website_project: this.project,
		});
	}

	open_form(formName) {
		frappe.set_route("Form", "Website Form", formName);
	}

	open_submissions(formName) {
		frappe.set_route("List", "Website Form Submission", {
			website_form: formName,
		});
	}
}
