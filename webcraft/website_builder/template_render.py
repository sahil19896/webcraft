# Copyright (c) 2026, WebCraft Team and contributors
"""Template-level render context (stylesheets, fonts, body class)."""

from __future__ import annotations

from typing import Any

import frappe

from webcraft.website_builder.installer import load_template_manifest


def _manifest_for_template(template_key: str | None) -> dict[str, Any]:
	if not template_key:
		return {}
	try:
		if frappe.db.exists("Website Template", template_key):
			folder = frappe.db.get_value("Website Template", template_key, "folder_path")
		else:
			folder = template_key
		return load_template_manifest(folder)
	except Exception:
		return {}


def get_template_render_extras(template_key: str | None) -> dict[str, str]:
	manifest = _manifest_for_template(template_key)
	theme_def = manifest.get("theme") or {}
	key = manifest.get("key") or template_key or "default"
	return {
		"template_skin_class": f"wc-template-{key}",
		"template_stylesheet": theme_def.get("template_stylesheet") or "",
		"template_script": theme_def.get("template_script") or "",
		"google_fonts_url": theme_def.get("google_fonts_url") or "",
		"icon_stylesheet": theme_def.get("icon_stylesheet") or "",
	}
