# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Page version snapshots for rollback."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime


def _page_snapshot(page) -> dict:
	sections = []
	for row in page.sections or []:
		sections.append(
			{
				"type": row.section_type,
				"order": row.section_order,
				"content": row.content or {},
				"style": row.style or {},
				"settings": row.settings or {},
				"hidden": row.is_hidden or 0,
			}
		)

	return {
		"page_title": page.page_title,
		"route": page.route,
		"meta_title": page.meta_title,
		"meta_description": page.meta_description,
		"meta_keywords": page.meta_keywords,
		"og_image": page.og_image,
		"canonical_url": page.canonical_url,
		"sections": sections,
	}


def snapshot_page(page_name: str, label: str | None = None) -> str:
	page = frappe.get_doc("Website Page", page_name)
	label = label or frappe.format_value(now_datetime(), {"fieldtype": "Datetime"})

	doc = frappe.get_doc(
		{
			"doctype": "Website Page Version",
			"website_page": page.name,
			"website_project": page.website_project,
			"version_label": label,
			"snapshot": _page_snapshot(page),
			"created_by": frappe.session.user,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def snapshot_project(project: str, label: str | None = None) -> list[str]:
	pages = frappe.get_all("Website Page", filters={"website_project": project}, pluck="name")
	return [snapshot_page(page_name, label) for page_name in pages]


def restore_page_version(version_name: str) -> dict:
	version = frappe.get_doc("Website Page Version", version_name)
	snapshot = version.snapshot or {}
	if isinstance(snapshot, str):
		import json

		snapshot = json.loads(snapshot)

	page = frappe.get_doc("Website Page", version.website_page)
	page.sections = []
	for index, section in enumerate(snapshot.get("sections") or []):
		page.append(
			"sections",
			{
				"section_type": section.get("type"),
				"section_order": section.get("order", index),
				"content": section.get("content") or {},
				"style": section.get("style") or {},
				"settings": section.get("settings") or {},
				"is_hidden": section.get("hidden") or 0,
			},
		)

	for field in ("meta_title", "meta_description", "meta_keywords", "og_image", "canonical_url", "page_title"):
		if field in snapshot:
			page.set(field, snapshot.get(field))

	page.save(ignore_permissions=True)
	frappe.db.commit()
	return {"page": page.name, "version": version_name}
