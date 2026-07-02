frappe.ui.form.on("Website Form Submission", {
	refresh(frm) {
		if (frm.is_new()) return;

		["Read", "Replied", "Archived"].forEach((status) => {
			if (frm.doc.status === status) return;
			frm.add_custom_button(__(status), () => {
				frappe.call({
					method: "webcraft.website_builder.api.update_submission_status",
					args: { name: frm.doc.name, status },
					callback() {
						frm.reload_doc();
					},
				});
			});
		});
	},
});
