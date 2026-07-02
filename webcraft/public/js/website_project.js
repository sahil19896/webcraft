frappe.ui.form.on("Website Project", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.homepage && frm.doc.is_active && frm.doc.status === "Published") {
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

		if (!frm.is_new()) {
			const live = frm.doc.is_active && frm.doc.status === "Published";
			frm.dashboard.set_headline(
				live
					? `<span class="indicator-pill green">${__("Live on web")}</span>`
					: `<span class="indicator-pill orange">${__("Not visible on web")}</span>`
			);
		}
	},

	is_active(frm) {
		if (frm.doc.is_active && !frm.is_new()) {
			frappe.show_alert({
				message: __("Activating this site will deactivate all other website projects."),
				indicator: "blue",
			});
		}
	},
});
