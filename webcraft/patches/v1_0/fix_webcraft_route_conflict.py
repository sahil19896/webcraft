# Copyright (c) 2026, WebCraft Team and contributors

import frappe


def execute():
	"""Resolve /desk/webcraft route conflict: Workspace slug blocked the theme store Page."""
	if frappe.db.exists("Workspace", "WebCraft") and not frappe.db.exists("Workspace", "WebCraft Hub"):
		frappe.rename_doc("Workspace", "WebCraft", "WebCraft Hub", force=True)

	_sync_desk_pages()


def _sync_desk_pages():
	for page_name in ("webcraft", "webcraft-customize"):
		if not frappe.db.exists("Page", page_name):
			continue
		doc = frappe.get_doc("Page", page_name)
		doc.load_assets()
		doc.save(ignore_permissions=True)

	frappe.db.commit()
	frappe.clear_cache()
