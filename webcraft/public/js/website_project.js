frappe.ui.form.on("Website Project", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.homepage) {
			frappe.db.get_value("Website Page", frm.doc.homepage, "route").then((r) => {
				const route = r?.message?.route;
				if (route) {
					frm.add_custom_button(__("View Live Site"), () => window.open(`/${route}`, "_blank"));
				}
			});
		}
		if (!frm.is_new()) {
			frm.add_custom_button(__("Edit Site"), () => frappe.set_route("webcraft-customize", frm.doc.name), __("Actions")).addClass(
				"btn-primary"
			);
			frm.add_custom_button(__("Theme Store"), () => frappe.set_route("webcraft"), __("Actions"));
		}
	},
});
