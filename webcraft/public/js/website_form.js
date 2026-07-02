frappe.ui.form.on("Website Form", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Open Form Builder"), () => {
				frappe.set_route("webcraft-form-builder", frm.doc.website_project, frm.doc.name);
			}).addClass("btn-primary");
		}
	},
});
