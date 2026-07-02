# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Page rendering and context building."""

from __future__ import annotations

import json
from typing import Any

import frappe


def get_project_for_page(page_name: str) -> dict | None:
	project = frappe.db.get_value(
		"Website Page",
		page_name,
		"website_project",
	)
	if not project:
		return None
	return frappe.get_doc("Website Project", project).as_dict()


def get_theme_variables(theme_name: str | None) -> dict[str, Any]:
	defaults = {
		"primary_color": "#2563eb",
		"secondary_color": "#1e40af",
		"accent_color": "#f59e0b",
		"background_color": "#ffffff",
		"text_color": "#0f172a",
		"surface_color": "#f8fafc",
		"font_family": "Inter, system-ui, sans-serif",
		"heading_font": "Inter, system-ui, sans-serif",
		"base_font_size": 16,
		"border_radius": 8,
		"spacing_scale": 1.0,
		"animations_enabled": True,
		"custom_css": "",
	}
	if not theme_name or not frappe.db.exists("Website Theme", theme_name):
		return defaults

	theme = frappe.get_doc("Website Theme", theme_name)
	for key in defaults:
		value = theme.get(key)
		if value not in (None, ""):
			defaults[key] = value
	# custom_css may be intentionally empty string — always read from doc
	if theme.get("custom_css") is not None:
		defaults["custom_css"] = theme.custom_css or ""
	return defaults


def _site_brand(theme_name: str | None) -> dict[str, str]:
	if not theme_name or not frappe.db.exists("Website Theme", theme_name):
		return {}
	return (
		frappe.db.get_value(
			"Website Theme",
			theme_name,
			["brand_name", "logo_image"],
			as_dict=True,
		)
		or {}
	)


def get_menus(project_name: str) -> dict[str, list[dict]]:
	menus: dict[str, list[dict]] = {"header": [], "footer": []}
	for menu in frappe.get_all(
		"Website Menu",
		filters={"website_project": project_name},
		fields=["name", "location"],
	):
		items = frappe.get_all(
			"Website Menu Item",
			filters={"parent": menu.name},
			fields=["label", "url", "parent_item", "sort_order", "open_in_new_tab"],
			order_by="sort_order asc",
		)
		location = (menu.location or "header").lower()
		menus[location] = items
	return menus


def parse_section_row(row: frappe._dict) -> dict[str, Any]:
	def _load(value):
		if isinstance(value, str) and value.strip():
			try:
				return json.loads(value)
			except (json.JSONDecodeError, TypeError):
				return {}
		return value or {}

	content = _load(row.content)
	style = _load(row.style)
	settings = _load(row.settings)

	return {
		"type": row.section_type,
		"id": row.name,
		"content": content,
		"style": style,
		"settings": settings,
		"hidden": bool(row.is_hidden),
		"order": row.section_order or 0,
	}


def get_visible_sections(page, route_prefix: str = "wc", preview_template: str | None = None) -> list[dict]:
	from webcraft.website_builder.commerce.webshop import enrich_product_section

	sections = sorted(page.sections or [], key=lambda r: r.section_order or 0)
	visible = []
	for row in sections:
		if row.is_hidden:
			continue
		section = parse_section_row(row)
		if section["type"] in ("product_grid", "product_carousel"):
			section["content"] = enrich_product_section(
				section.get("content"), section.get("settings"), route_prefix, preview_template
			)
		visible.append(section)
	return visible


def get_page_context(page, project: dict | None = None) -> dict[str, Any]:
	from webcraft.website_builder.commerce.store import commerce_context_flags, route_prefix_from_page

	project = project or get_project_for_page(page.name)
	theme_name = project.get("website_theme") if project else None
	theme = get_theme_variables(theme_name)
	menus = get_menus(project["name"]) if project else {"header": [], "footer": []}
	prefix = route_prefix_from_page(page, project)

	ctx = {
		"page": page,
		"project": project,
		"theme": theme,
		"theme_css": build_theme_css(theme),
		"sections": get_visible_sections(page, prefix),
		"header_menu": menus.get("header", []),
		"footer_menu": menus.get("footer", []),
		"meta_title": page.meta_title or page.page_title,
		"meta_description": page.meta_description or "",
		"meta_keywords": page.meta_keywords or "",
		"og_image": page.og_image or "",
		"canonical_url": page.canonical_url or "",
		"site_brand": _site_brand(theme_name),
		"animations_enabled": theme.get("animations_enabled", True),
	}
	ctx.update(commerce_context_flags(project, page))
	template_key = (project or {}).get("website_template")
	from webcraft.website_builder.template_render import get_template_render_extras

	ctx.update(get_template_render_extras(template_key))
	ctx["active_nav_url"] = _active_nav_url(prefix, page, project)
	ctx["no_header"] = 1
	ctx["show_sidebar"] = 0
	ctx["full_width"] = 1

	from webcraft.website_builder.content.edit_map import build_page_edit_config, is_wc_edit_mode

	ctx["wc_edit_mode"] = is_wc_edit_mode()
	if ctx["wc_edit_mode"]:
		ctx["wc_edit_config"] = build_page_edit_config(page)

	return ctx


def _active_nav_url(route_prefix: str, page, project: dict | None) -> str:
	route = (getattr(page, "route", None) or "").strip("/")
	base = f"/{route_prefix}"
	if not route or route == route_prefix:
		return base
	if route.startswith(f"{route_prefix}/"):
		return f"/{route}"
	return f"{base}/{route.split('/')[-1]}"


def build_theme_css(theme: dict[str, Any]) -> str:
	primary = theme.get("primary_color", "#2563eb")
	btn_text = _contrast_text(primary)
	return f"""
:root {{
	--wc-primary: {primary};
	--wc-secondary: {theme.get("secondary_color", "#1e40af")};
	--wc-accent: {theme.get("accent_color", "#f59e0b")};
	--wc-bg: {theme.get("background_color", "#ffffff")};
	--wc-text: {theme.get("text_color", "#0f172a")};
	--wc-surface: {theme.get("surface_color", "#f8fafc")};
	--wc-font: {theme.get("font_family", "Inter, system-ui, sans-serif")};
	--wc-heading-font: {theme.get("heading_font", "Inter, system-ui, sans-serif")};
	--wc-radius: {theme.get("border_radius", 8)}px;
	--wc-spacing: {theme.get("spacing_scale", 1)};
	--wc-btn-primary-text: {btn_text};
}}
{theme.get("custom_css") or ""}
"""


def _contrast_text(hex_color: str) -> str:
	"""Pick readable text on primary button background."""
	if not hex_color or not str(hex_color).startswith("#"):
		return "#ffffff"
	try:
		h = hex_color.lstrip("#")
		if len(h) == 3:
			h = "".join(c * 2 for c in h)
		r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
		luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
		return "#0a0a0a" if luminance > 0.65 else "#ffffff"
	except (ValueError, TypeError):
		return "#ffffff"
