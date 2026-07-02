# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Render bundled template designs without installing a Website Project."""

from __future__ import annotations

import copy
import re
from typing import Any

import frappe

from webcraft.website_builder.builder import build_theme_css, get_theme_variables
from webcraft.website_builder.commerce.webshop import enrich_product_section
from webcraft.website_builder.commerce.store import commerce_context_flags
from webcraft.website_builder.components.registry import get_component_defaults
from webcraft.website_builder.installer import get_templates_root, load_template_manifest


def list_bundled_designs() -> list[dict]:
	designs = []
	root = get_templates_root()
	if not root.exists():
		return designs

	for entry in sorted(root.iterdir()):
		if not entry.is_dir():
			continue
		manifest_path = entry / "template.json"
		if not manifest_path.exists():
			continue
		manifest = load_template_manifest(entry.name)
		key = manifest.get("key") or entry.name
		pages = _pages_summary(manifest, key)
		designs.append(
			{
				"key": key,
				"folder": entry.name,
				"title": manifest.get("title") or key.title(),
				"description": manifest.get("description") or "",
				"category": manifest.get("category") or "General",
				"version": manifest.get("version") or "1.0.0",
				"route_prefix": manifest.get("route_prefix") or "wc",
				"page_count": len(pages),
				"pages": pages,
				"preview_home": f"/webcraft-preview/{key}",
				"preview_image": manifest.get("preview_image") or "",
				"features": manifest.get("features") or [],
				"theme": manifest.get("theme") or {},
			}
		)
	return designs


def get_design_detail(template_key: str) -> dict:
	for design in list_bundled_designs():
		if design["key"] == template_key:
			manifest = _load_manifest_by_key(template_key)
			design["menus"] = _menus_summary(manifest, template_key)
			return design
	return {}


def _load_manifest_by_key(template_key: str) -> dict:
	if frappe.db.exists("Website Template", template_key):
		folder = frappe.db.get_value("Website Template", template_key, "folder_path")
	else:
		folder = template_key
	return load_template_manifest(folder)


def _pages_summary(manifest: dict, template_key: str) -> list[dict]:
	pages = []
	for page_def in manifest.get("pages") or []:
		slug = page_def.get("slug")
		if page_def.get("is_homepage"):
			preview_path = f"/webcraft-preview/{template_key}"
		elif slug:
			preview_path = f"/webcraft-preview/{template_key}/{slug}"
		else:
			slug = frappe.scrub(page_def.get("title") or "page").replace("_", "-")
			preview_path = f"/webcraft-preview/{template_key}/{slug}"
		pages.append(
			{
				"title": page_def.get("title") or "Page",
				"slug": slug or "",
				"is_homepage": bool(page_def.get("is_homepage")),
				"preview_url": preview_path,
			}
		)
	return pages


def _menus_summary(manifest: dict, template_key: str) -> list[dict]:
	menus = []
	for menu_def in manifest.get("menus") or []:
		items = []
		for item in menu_def.get("items") or []:
			url = item.get("url") or "#"
			items.append(
				{
					"label": item.get("label"),
					"url": _to_preview_url(url, template_key, manifest.get("route_prefix") or "wc"),
					"open_in_new_tab": item.get("open_in_new_tab") or 0,
				}
			)
		menus.append(
			{
				"name": menu_def.get("name"),
				"location": (menu_def.get("location") or "Header").lower(),
				"items": items,
			}
		)
	return menus


def get_preview_context(template_key: str, page_slug: str | None = None) -> dict[str, Any]:
	if page_slug and page_slug.startswith("product/"):
		from webcraft.website_builder.commerce.store import build_preview_product_context

		return build_preview_product_context(template_key, page_slug.split("/", 1)[1])
	if page_slug and page_slug.startswith("order/"):
		from webcraft.website_builder.commerce.store import build_preview_order_context

		return build_preview_order_context(template_key, page_slug.split("/", 1)[1])

	manifest = _load_manifest_by_key(template_key)
	route_prefix = manifest.get("route_prefix") or "wc"
	page_def = _find_page_def(manifest, page_slug)
	if not page_def:
		frappe.throw("Design page not found.", frappe.DoesNotExistError)

	theme_def = manifest.get("theme") or {}
	theme = get_theme_variables(None)
	for key, value in theme_def.items():
		if value not in (None, ""):
			theme[key] = value

	sections = _sections_from_page_def(page_def, route_prefix, template_key)
	sections = _rewrite_section_links(sections, template_key, route_prefix)

	menus = {"header": [], "footer": []}
	for menu in _menus_summary(manifest, template_key):
		menus[menu["location"]] = menu["items"]

	seo = page_def.get("seo") or {}
	fake_page = frappe._dict(
		{
			"name": f"preview-{template_key}-{page_slug or 'home'}",
			"page_title": page_def.get("title") or "Preview",
			"route": page_slug or route_prefix,
			"meta_title": seo.get("title") or page_def.get("title"),
			"meta_description": seo.get("description") or "",
			"meta_keywords": seo.get("keywords") or "",
			"og_image": "",
			"canonical_url": "",
		}
	)

	return {
		"page": fake_page,
		"project": frappe._dict({"name": template_key, "project_name": manifest.get("title"), "website_template": template_key}),
		"theme": theme,
		"theme_css": build_theme_css(theme),
		"sections": sections,
		"header_menu": menus.get("header", []),
		"footer_menu": menus.get("footer", []),
		"meta_title": fake_page.meta_title,
		"meta_description": fake_page.meta_description,
		"meta_keywords": fake_page.meta_keywords,
		"og_image": "",
		"canonical_url": "",
		"is_preview": True,
		"preview_template": template_key,
		"preview_pages": _pages_summary(manifest, template_key),
		**commerce_context_flags(
			frappe._dict(website_template=template_key),
			fake_page,
			is_preview=True,
			preview_template=template_key,
		),
		"site_brand": {
			"brand_name": (manifest.get("theme") or {}).get("theme_name") or manifest.get("title"),
			"logo_image": "",
		},
		"no_header": 1,
		"show_sidebar": 0,
		"full_width": 1,
		"animations_enabled": theme.get("animations_enabled", True),
		**_preview_nav_extras(template_key, page_slug, manifest),
	}


def _preview_nav_extras(template_key: str, page_slug: str | None, manifest: dict) -> dict:
	from webcraft.website_builder.template_render import get_template_render_extras

	base = f"/webcraft-preview/{template_key}"
	active = f"{base}/{page_slug}" if page_slug else base
	return {**get_template_render_extras(template_key), "active_nav_url": active}


def _find_page_def(manifest: dict, page_slug: str | None) -> dict | None:
	pages = manifest.get("pages") or []
	if not page_slug:
		for page in pages:
			if page.get("is_homepage"):
				return page
		return pages[0] if pages else None

	slug = page_slug.strip("/")
	for page in pages:
		if page.get("slug") == slug:
			return page
		if frappe.scrub(page.get("title") or "").replace("_", "-") == slug:
			return page
	return None


def _sections_from_page_def(page_def: dict, route_prefix: str = "wc", preview_template: str | None = None) -> list[dict]:
	sections = []
	for order, section in enumerate(page_def.get("sections") or []):
		if section.get("hidden"):
			continue
		section_type = section.get("type")
		content = copy.deepcopy(section.get("content") or get_component_defaults(section_type))
		settings = section.get("settings") or {}
		if section_type in ("product_grid", "product_carousel"):
			content = enrich_product_section(content, settings, route_prefix, preview_template)
		sections.append(
			{
				"type": section_type,
				"content": content,
				"style": section.get("style") or {},
				"settings": settings,
				"order": order,
			}
		)
	return sections


def _to_preview_url(url: str, template_key: str, route_prefix: str) -> str:
	if not url or url == "#":
		return "#"
	if url.startswith("/webcraft-preview/"):
		return url
	base = f"/webcraft-preview/{template_key}"
	if url in (f"/{route_prefix}", f"/{route_prefix}/"):
		return base
	if url.startswith(f"/{route_prefix}/"):
		slug = url[len(f"/{route_prefix}/") :]
		return f"{base}/{slug}"
	return url


def _rewrite_section_links(sections: list[dict], template_key: str, route_prefix: str) -> list[dict]:
	pattern = re.compile(rf"^/{re.escape(route_prefix)}(/|$)")

	def walk(value):
		if isinstance(value, str):
			if pattern.match(value):
				slug = value[len(f"/{route_prefix}") :].lstrip("/")
				return f"/webcraft-preview/{template_key}" + (f"/{slug}" if slug else "")
			return value
		if isinstance(value, list):
			return [walk(item) for item in value]
		if isinstance(value, dict):
			return {k: walk(v) for k, v in value.items()}
		return value

	return walk(sections)
