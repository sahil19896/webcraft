# Copyright (c) 2026, WebCraft Team and contributors
# Preview bundled WebCraft designs on the public website.

from __future__ import annotations

import frappe

from webcraft.website_builder.preview import get_preview_context

no_cache = 1


def get_context(context):
	template_key = frappe.form_dict.get("template")
	page_slug = frappe.form_dict.get("page") or None

	if not template_key:
		path = (frappe.local.path or "").strip("/")
		parts = path.split("/")
		if len(parts) >= 2 and parts[0] == "webcraft-preview":
			template_key = parts[1]
			page_slug = parts[2] if len(parts) > 2 else None

	if not template_key:
		frappe.throw("Design not specified.")

	preview = get_preview_context(template_key, page_slug)
	context.update(preview)
	context.no_cache = 1
	context.show_sidebar = 0
