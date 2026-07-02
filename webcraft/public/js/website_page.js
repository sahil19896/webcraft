frappe.ui.form.on("Website Page", {
	refresh(frm) {
		if (frm.is_new()) return;

		if (frm.doc.website_project) {
			frm.add_custom_button(__("Edit Site"), () => {
				frappe.set_route("webcraft-customize", frm.doc.website_project);
			}).addClass("btn-primary");
		}

		if (frm.doc.published && frm.doc.route) {
			frm.add_custom_button(__("View Page"), () => {
				window.open(`/${frm.doc.route}`, "_blank");
			});
		}
	},
});
