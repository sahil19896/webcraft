# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Store routing, project resolution, and dynamic page context."""

from __future__ import annotations

from typing import Any

import frappe

from webcraft.website_builder.builder import build_theme_css, get_menus, get_theme_variables
from webcraft.website_builder.commerce.products import get_product_detail
from webcraft.website_builder.commerce.webshop import is_ecommerce_template, webshop_available
from webcraft.website_builder.installer import load_template_manifest


def _template_folder(template_key: str) -> str:
	if frappe.db.exists("Website Template", template_key):
		return frappe.db.get_value("Website Template", template_key, "folder_path")
	return template_key


def route_prefix_from_page(page, project: dict | None = None) -> str:
	route = (page.route if page else "") or ""
	if route:
		return route.split("/")[0]
	if project and project.get("website_template"):
		return _manifest_route_prefix(project["website_template"])
	return "wc"


def _manifest_route_prefix(template_key: str) -> str:
	try:
		if frappe.db.exists("Website Template", template_key):
			folder = frappe.db.get_value("Website Template", template_key, "folder_path")
		else:
			folder = template_key
		manifest = load_template_manifest(folder)
		return manifest.get("route_prefix") or "wc"
	except Exception:
		return "wc"


def find_published_project_by_prefix(prefix: str) -> dict | None:
	if not prefix:
		return None
	project_name = frappe.db.sql(
		"""
		SELECT DISTINCT website_project
		FROM `tabWebsite Page`
		WHERE published = 1 AND (route = %s OR route LIKE %s)
		LIMIT 1
		""",
		(prefix, f"{prefix}/%"),
	)
	if not project_name:
		return None
	project = project_name[0][0]
	if not frappe.db.exists("Website Project", project):
		return None
	return frappe.get_doc("Website Project", project).as_dict()


def parse_store_path(path: str) -> dict[str, Any] | None:
	parts = (path or "").strip("/").split("/")
	if len(parts) < 3:
		return None

	if parts[1] == "product":
		item_code = parts[2]
		project = find_published_project_by_prefix(parts[0])
		if not project or not is_ecommerce_template(project.get("website_template")):
			return None
		return {
			"mode": "live",
			"page_type": "product",
			"route_prefix": parts[0],
			"project_name": project["name"],
			"item_code": item_code,
		}

	if parts[1] == "order":
		order_name = parts[2]
		project = find_published_project_by_prefix(parts[0])
		if not project or not is_ecommerce_template(project.get("website_template")):
			return None
		return {
			"mode": "live",
			"page_type": "order",
			"route_prefix": parts[0],
			"project_name": project["name"],
			"order_name": order_name,
		}

	return None


def commerce_context_flags(project: dict | None, page, is_preview: bool = False, preview_template: str | None = None) -> dict[str, Any]:
	template_key = preview_template or (project or {}).get("website_template")
	enabled = webshop_available() and is_ecommerce_template(template_key)
	prefix = route_prefix_from_page(page, project)

	if is_preview and preview_template:
		base = f"/webcraft-preview/{preview_template}"
	else:
		base = f"/{prefix}"

	return {
		"commerce_enabled": enabled,
		"store_route_prefix": prefix,
		"store_home_url": base,
		"cart_url": f"{base}/cart",
		"checkout_url": f"{base}/checkout",
		"is_preview": is_preview,
		"preview_template": preview_template,
	}


def _base_store_sections(project_name: str, route_prefix: str, is_preview: bool, preview_template: str | None) -> tuple[list[dict], list[dict], list[dict]]:
	project = frappe.get_doc("Website Project", project_name)
	homepage = project.homepage
	if homepage:
		home_page = frappe.get_doc("Website Page", homepage)
		header_section = None
		footer_section = None
		for row in home_page.sections or []:
			if row.section_type == "header" and not header_section:
				from webcraft.website_builder.builder import parse_section_row

				header_section = parse_section_row(row)
			if row.section_type == "footer":
				from webcraft.website_builder.builder import parse_section_row

				footer_section = parse_section_row(row)
	else:
		header_section = {"type": "header", "content": {"logo_text": project.project_name}, "style": {}, "settings": {}}
		footer_section = {"type": "footer", "content": {"logo_text": project.project_name}, "style": {}, "settings": {}}

	menus = get_menus(project_name)
	flags = commerce_context_flags(project.as_dict(), frappe._dict(route=route_prefix), is_preview, preview_template)
	return [header_section] if header_section else [], [footer_section] if footer_section else [], [flags, menus]


def build_live_dynamic_context(parsed: dict[str, Any]) -> dict[str, Any]:
	project = frappe.get_doc("Website Project", parsed["project_name"])
	theme = get_theme_variables(project.website_theme)
	menus = get_menus(project.name)
	flags = commerce_context_flags(project.as_dict(), frappe._dict(route=parsed["route_prefix"]))

	header_sections, footer_sections, _ = _base_store_sections(
		project.name, parsed["route_prefix"], False, None
	)
	sections = (header_sections or []) + _dynamic_middle_sections(parsed) + (footer_sections or [])

	fake_page = frappe._dict(
		{
			"name": f"dynamic-{parsed['page_type']}",
			"page_title": _dynamic_title(parsed),
			"route": frappe.local.path,
			"meta_title": _dynamic_title(parsed),
			"meta_description": "",
			"meta_keywords": "",
			"og_image": "",
			"canonical_url": "",
		}
	)

	ctx = {
		"page": fake_page,
		"project": project.as_dict(),
		"theme": theme,
		"theme_css": build_theme_css(theme),
		"sections": sections,
		"header_menu": menus.get("header", []),
		"footer_menu": menus.get("footer", []),
		"meta_title": fake_page.meta_title,
		"meta_description": "",
		"meta_keywords": "",
		"og_image": "",
		"canonical_url": "",
		"no_cache": 1,
		"no_header": 1,
		"show_sidebar": 0,
		"full_width": 1,
		"body_class": "wc-body",
	}
	ctx.update(flags)
	return ctx


def build_preview_product_context(template_key: str, item_code: str) -> dict[str, Any]:
	from webcraft.website_builder.preview import get_preview_context

	manifest = load_template_manifest(_template_folder(template_key))
	home_def = next((p for p in manifest.get("pages", []) if p.get("is_homepage")), manifest.get("pages", [{}])[0])
	ctx = get_preview_context(template_key, home_def.get("slug") or None)
	product = get_product_detail(item_code)
	if not product:
		frappe.throw("Product not found.", frappe.DoesNotExistError)

	middle = [{"type": "product_detail", "content": {"product": product, "item_code": item_code}, "style": {}, "settings": {}}]
	ctx["sections"] = [s for s in ctx["sections"] if s["type"] not in ("hero", "marquee", "category_tiles", "product_grid", "product_carousel", "cta")]
	# Keep header/footer only from trimmed sections
	header = next((s for s in ctx["sections"] if s["type"] == "header"), None)
	footer = next((s for s in ctx["sections"] if s["type"] == "footer"), None)
	ctx["sections"] = ([header] if header else []) + middle + ([footer] if footer else [])
	ctx["meta_title"] = f"{product.get('name')} | {manifest.get('title', 'Store')}"
	ctx.update(commerce_context_flags(None, frappe._dict(route=manifest.get("route_prefix")), True, template_key))
	return ctx


def build_preview_order_context(template_key: str, order_name: str) -> dict[str, Any]:
	manifest = load_template_manifest(_template_folder(template_key))
	slug = "cart"
	from webcraft.website_builder.preview import get_preview_context

	ctx = get_preview_context(template_key, slug)
	middle = [{"type": "order_confirmation", "content": {"order_name": order_name}, "style": {}, "settings": {}}]
	header = next((s for s in ctx["sections"] if s["type"] == "header"), None)
	footer = next((s for s in ctx["sections"] if s["type"] == "footer"), None)
	ctx["sections"] = ([header] if header else []) + middle + ([footer] if footer else [])
	ctx["meta_title"] = f"Order {order_name}"
	ctx.update(commerce_context_flags(None, frappe._dict(route=manifest.get("route_prefix")), True, template_key))
	return ctx


def _dynamic_title(parsed: dict[str, Any]) -> str:
	if parsed["page_type"] == "product":
		product = get_product_detail(parsed["item_code"])
		return product.get("name") if product else parsed["item_code"]
	if parsed["page_type"] == "order":
		return f"Order {parsed['order_name']}"
	return "Store"


def _dynamic_middle_sections(parsed: dict[str, Any]) -> list[dict]:
	if parsed["page_type"] == "product":
		product = get_product_detail(parsed["item_code"])
		if not product:
			frappe.throw("Product not found.", frappe.DoesNotExistError)
		return [{"type": "product_detail", "content": {"product": product, "item_code": parsed["item_code"]}, "style": {}, "settings": {}}]
	if parsed["page_type"] == "order":
		return [{"type": "order_confirmation", "content": {"order_name": parsed["order_name"]}, "style": {}, "settings": {}}]
	return []
