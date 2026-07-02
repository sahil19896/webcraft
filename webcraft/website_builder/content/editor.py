# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Load and save page section content for the site editor."""

from __future__ import annotations

import json
from typing import Any

import frappe

from webcraft.website_builder.content.schema import (
	get_section_edit_schema,
	get_section_label,
	is_section_editable,
)


def _parse_json(value) -> dict:
	if isinstance(value, dict):
		return value
	if isinstance(value, str) and value.strip():
		try:
			return json.loads(value)
		except json.JSONDecodeError:
			return {}
	return {}


def build_pages_editor_payload(project_name: str) -> list[dict]:
	pages = []
	for row in frappe.get_all(
		"Website Page",
		filters={"website_project": project_name},
		fields=["name", "page_title", "route", "is_homepage"],
		order_by="is_homepage desc, page_title asc",
	):
		doc = frappe.get_doc("Website Page", row.name)
		sections = []
		for sec in sorted(doc.sections or [], key=lambda r: r.section_order or 0):
			if not is_section_editable(sec.section_type):
				continue
			content = _parse_json(sec.content)
			sections.append(
				{
					"name": sec.name,
					"section_type": sec.section_type,
					"section_order": sec.section_order or 0,
					"label": get_section_label(sec.section_type),
					"visible": not bool(sec.is_hidden),
					"content": content,
					"schema": get_section_edit_schema(sec.section_type),
				}
			)
		pages.append(
			{
				"name": doc.name,
				"page_title": doc.page_title,
				"route": doc.route,
				"preview_url": f"/{doc.route}" if doc.route else "",
				"is_homepage": bool(doc.is_homepage),
				"sections": sections,
			}
		)
	return pages


def save_page_sections(page_name: str, sections_payload: list[dict]) -> dict:
	if not page_name or not frappe.db.exists("Website Page", page_name):
		frappe.throw("Page not found.")

	doc = frappe.get_doc("Website Page", page_name)
	allowed_rows = {row.name: row for row in doc.sections or []}
	updated = 0

	for item in sections_payload or []:
		row_name = item.get("name")
		if not row_name or row_name not in allowed_rows:
			continue
		row = allowed_rows[row_name]
		if not is_section_editable(row.section_type):
			continue
		if "visible" in item:
			row.is_hidden = 0 if item.get("visible") else 1
		content = item.get("content") or {}
		if not isinstance(content, dict):
			frappe.throw(f"Invalid content for section {row_name}.")
		row.content = content
		updated += 1

	if not updated:
		return {"updated": 0, "page": page_name}

	doc.save(ignore_permissions=True)

	if doc.route:
		from frappe.website.utils import clear_cache

		clear_cache(doc.route)

	frappe.db.commit()
	return {"updated": updated, "page": page_name, "route": doc.route}
