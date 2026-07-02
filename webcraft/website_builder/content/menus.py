# Copyright (c) 2026, WebCraft Team and contributors
# Menu helpers for the site editor.

from __future__ import annotations

from typing import Any

import frappe


def get_project_menus_detail(project_name: str) -> dict[str, dict[str, Any]]:
	"""Return header/footer menus with doc names for editing."""
	result: dict[str, dict[str, Any]] = {
		"header": {"name": None, "location": "Header", "items": []},
		"footer": {"name": None, "location": "Footer", "items": []},
	}
	for menu in frappe.get_all(
		"Website Menu",
		filters={"website_project": project_name},
		fields=["name", "location", "menu_name"],
	):
		location = (menu.location or "Header").lower()
		if location not in result:
			location = "header"
		items = frappe.get_all(
			"Website Menu Item",
			filters={"parent": menu.name},
			fields=["name", "label", "url", "sort_order", "open_in_new_tab"],
			order_by="sort_order asc",
		)
		result[location] = {
			"name": menu.name,
			"location": menu.location or "Header",
			"menu_name": menu.menu_name,
			"items": [
				{
					"name": row.name,
					"label": row.label or "",
					"url": row.url or "#",
					"open_in_new_tab": bool(row.open_in_new_tab),
					"sort_order": row.sort_order or 0,
				}
				for row in items
			],
		}
	return result


def save_project_menus(project_name: str, menus_payload: dict) -> dict:
	if not project_name or not frappe.db.exists("Website Project", project_name):
		frappe.throw("Project not found.")

	updated = 0
	for location_key in ("header", "footer"):
		block = menus_payload.get(location_key) or {}
		menu_name = block.get("name")
		items = block.get("items") or []

		if menu_name and frappe.db.exists("Website Menu", menu_name):
			doc = frappe.get_doc("Website Menu", menu_name)
		else:
			doc = frappe.get_doc(
				{
					"doctype": "Website Menu",
					"menu_name": block.get("menu_name")
					or f"{project_name}-{location_key.title()} Menu",
					"website_project": project_name,
					"location": block.get("location") or location_key.title(),
					"items": [],
				}
			)
			doc.insert(ignore_permissions=True)
			menu_name = doc.name

		doc = frappe.get_doc("Website Menu", menu_name)
		doc.items = []
		for index, item in enumerate(items):
			label = (item.get("label") or "").strip()
			url = (item.get("url") or "#").strip() or "#"
			if not label:
				continue
			doc.append(
				{
					"label": label,
					"url": url,
					"sort_order": index,
					"open_in_new_tab": 1 if item.get("open_in_new_tab") else 0,
				}
			)
		doc.save(ignore_permissions=True)
		updated += 1

	frappe.db.commit()
	from frappe.website.utils import clear_cache

	clear_cache()
	return {"updated": updated}
