# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Render Website Form definitions as HTML."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import cstr

from webcraft.website_builder.forms.registry import FIELD_TYPES


def get_form_doc(form_name: str):
	if not form_name or not frappe.db.exists("Website Form", form_name):
		return None
	return frappe.get_doc("Website Form", form_name)


def get_form_fields_payload(form_doc) -> list[dict[str, Any]]:
	fields = []
	for row in sorted(form_doc.fields or [], key=lambda f: f.sort_order or 0):
		fields.append(
			{
				"field_type": row.field_type,
				"label": row.label,
				"fieldname": row.fieldname or frappe.scrub(row.label or row.field_type),
				"required": bool(row.required),
				"placeholder": row.placeholder or "",
				"default_value": row.default_value or "",
				"help_text": row.help_text or "",
				"width": row.width or "Full",
				"options": _parse_options(row.options),
			}
		)
	return fields


def _parse_options(options: str | None) -> list[str]:
	if not options:
		return []
	return [line.strip() for line in cstr(options).splitlines() if line.strip()]


def _width_class(width: str | None) -> str:
	width = (width or "Full").lower()
	if width == "half":
		return "wc-form__field--half"
	if width == "third":
		return "wc-form__field--third"
	return "wc-form__field--full"


def render_form_html(form_name: str) -> str:
	"""Jinja-callable: render a published form by name."""
	form_doc = get_form_doc(form_name)
	if not form_doc or not form_doc.published:
		return ""

	from webcraft.website_builder.access import is_project_live

	if form_doc.website_project and not is_project_live(form_doc.website_project):
		return ""

	settings = form_doc.form_settings or {}
	if isinstance(settings, str):
		import json

		try:
			settings = json.loads(settings)
		except json.JSONDecodeError:
			settings = {}

	return frappe.render_template(
		"templates/includes/webcraft_form.html",
		{
			"form": form_doc,
			"fields": get_form_fields_payload(form_doc),
			"form_name": form_doc.name,
			"submit_label": settings.get("submit_label") or "Submit",
		},
	)


def get_form_preview_html(form_name: str) -> str:
	form_doc = get_form_doc(form_name)
	if not form_doc:
		return ""
	return frappe.render_template(
		"templates/includes/webcraft_form.html",
		{
			"form": form_doc,
			"fields": get_form_fields_payload(form_doc),
			"form_name": form_doc.name,
			"submit_label": (form_doc.form_settings or {}).get("submit_label") if isinstance(form_doc.form_settings, dict) else "Submit",
			"preview": True,
		},
	)
