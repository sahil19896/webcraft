# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Optional Webshop integration for live product sections and storefront commerce."""

from __future__ import annotations

from typing import Any

import frappe


def webshop_available() -> bool:
	return bool(frappe.db.exists("DocType", "Website Item"))


def is_ecommerce_template(template_key: str | None) -> bool:
	if not template_key:
		return False
	if template_key == "ecommerce":
		return True
	try:
		from webcraft.website_builder.installer import load_template_manifest

		if frappe.db.exists("Website Template", template_key):
			folder = frappe.db.get_value("Website Template", template_key, "folder_path")
		else:
			folder = template_key
		manifest = load_template_manifest(folder)
		return (manifest.get("category") or "").lower() == "e-commerce"
	except Exception:
		return False


def product_store_url(
	item_code: str,
	route_prefix: str = "store",
	preview_template: str | None = None,
) -> str:
	if preview_template:
		return f"/webcraft-preview/{preview_template}/product/{item_code}"
	return f"/{route_prefix.strip('/')}/product/{item_code}"


def map_website_item(
	item: dict,
	route_prefix: str = "store",
	preview_template: str | None = None,
) -> dict:
	item_code = item.get("item_code") or item.get("name")
	url = product_store_url(item_code, route_prefix, preview_template) if item_code else "#"
	price = item.get("formatted_price") or item.get("price_list_rate") or ""
	badge = ""
	if item.get("discount"):
		badge = "Sale"
	elif item.get("on_backorder"):
		badge = "Pre-order"

	return {
		"item_code": item_code,
		"name": item.get("web_item_name") or item.get("item_name") or item_code,
		"brand": item.get("brand") or item.get("item_group") or "",
		"price": price if isinstance(price, str) else frappe.format_value(price, {"fieldtype": "Currency"}),
		"image": item.get("website_image") or item.get("thumbnail") or "",
		"url": url,
		"badge": badge,
	}


def fetch_webshop_products(
	settings: dict | None = None,
	content: dict | None = None,
	route_prefix: str = "store",
	preview_template: str | None = None,
) -> list[dict]:
	if not webshop_available():
		return []

	settings = settings or {}
	content = content or {}
	item_group = settings.get("item_group") or content.get("item_group")
	limit = int(settings.get("limit") or content.get("limit") or 8)
	search = settings.get("search") or content.get("search")

	try:
		from webshop.webshop.product_data_engine.query import ProductQuery

		query = ProductQuery()
		result = query.query(search_term=search, item_group=item_group, start=0)
		items = (result or {}).get("items") or []
		return [map_website_item(row, route_prefix, preview_template) for row in items[:limit]]
	except Exception:
		frappe.log_error(title="WebCraft Webshop Product Fetch Failed")
		return []


def enrich_product_section(
	content: dict,
	settings: dict | None = None,
	route_prefix: str = "store",
	preview_template: str | None = None,
) -> dict[str, Any]:
	content = dict(content or {})
	settings = settings or {}
	source = (settings.get("source") or content.get("source") or "").lower()

	if source == "webshop":
		live = fetch_webshop_products(settings, content, route_prefix, preview_template)
		if live:
			content["products"] = live

	return content
