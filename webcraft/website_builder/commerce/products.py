# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Product detail helpers for WebCraft storefront pages."""

from __future__ import annotations

from typing import Any

import frappe

from webcraft.website_builder.commerce.webshop import product_store_url, webshop_available


def get_product_detail(item_code: str, route_prefix: str = "store", preview_template: str | None = None) -> dict[str, Any] | None:
	if not item_code or not webshop_available():
		return None

	fields = [
		"name",
		"item_code",
		"web_item_name",
		"item_name",
		"brand",
		"website_image",
		"description",
		"short_description",
		"website_warehouse",
		"route",
		"published",
	]
	wi = frappe.db.get_value("Website Item", {"item_code": item_code, "published": 1}, fields, as_dict=True)
	if not wi:
		return None

	price_label = ""
	in_stock = True
	stock_qty = 0
	on_backorder = False
	cart_qty = 0

	try:
		from webshop.webshop.shopping_cart.product_info import get_product_info_for_website

		info = get_product_info_for_website(item_code, skip_quotation_creation=True)
		product_info = info.get("product_info") or {}
		price = product_info.get("price") or {}
		if price.get("formatted_price"):
			price_label = price["formatted_price"]
		elif price.get("price_list_rate") is not None:
			price_label = frappe.format_value(price["price_list_rate"], {"fieldtype": "Currency"})
		in_stock = product_info.get("in_stock", True)
		stock_qty = product_info.get("stock_qty") or 0
		on_backorder = product_info.get("on_backorder", False)
		cart_qty = product_info.get("qty") or 0
	except Exception:
		frappe.log_error(title="WebCraft Product Info Failed")

	description = wi.short_description or wi.description or ""
	if description and "<" not in description:
		description = f"<p>{frappe.utils.escape_html(description)}</p>"

	return {
		"item_code": wi.item_code,
		"name": wi.web_item_name or wi.item_name or wi.item_code,
		"brand": wi.brand or "",
		"image": wi.website_image or "",
		"description": description,
		"price": price_label,
		"in_stock": in_stock,
		"stock_qty": stock_qty,
		"on_backorder": on_backorder,
		"cart_qty": cart_qty,
		"url": product_store_url(wi.item_code, route_prefix, preview_template),
	}
