# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Storefront APIs — thin wrappers over Webshop cart (Quotation → Sales Order)."""

from __future__ import annotations

import frappe

from webcraft.website_builder.commerce.products import get_product_detail
from webcraft.website_builder.commerce.webshop import webshop_available


@frappe.whitelist(allow_guest=True)
def get_store_product(item_code: str, route_prefix: str = "store") -> dict:
	if not webshop_available():
		return {}
	product = get_product_detail(item_code, route_prefix=route_prefix)
	return product or {}


@frappe.whitelist(allow_guest=True)
def get_store_status() -> dict:
	enabled = webshop_available()
	settings = {}
	if enabled:
		try:
			settings = frappe.get_cached_doc("Webshop Settings").as_dict()
		except Exception:
			pass
	return {
		"webshop_available": enabled,
		"cart_enabled": bool(settings.get("enabled")),
		"show_price": bool(settings.get("show_price")),
		"enable_checkout": bool(settings.get("enable_checkout")),
		"is_logged_in": frappe.session.user != "Guest",
		"user": frappe.session.user,
	}


@frappe.whitelist()
def place_store_order() -> dict:
	"""Submit cart quotation and create Sales Order via Webshop."""
	if not webshop_available():
		frappe.throw("Webshop is not available on this site.")
	from webshop.webshop.shopping_cart.cart import place_order

	order_name = place_order()
	return {"sales_order": order_name, "success": True}


@frappe.whitelist()
def get_order_summary(order_name: str) -> dict:
	if not order_name or not frappe.db.exists("Sales Order", order_name):
		return {}
	if frappe.session.user == "Guest":
		return {}

	doc = frappe.get_doc("Sales Order", order_name)
	if not frappe.has_website_permission(doc):
		return {}

	items = []
	for row in doc.items:
		items.append(
			{
				"item_code": row.item_code,
				"item_name": row.item_name,
				"qty": row.qty,
				"rate": row.rate,
				"amount": row.amount,
			}
		)

	return {
		"name": doc.name,
		"status": doc.status,
		"transaction_date": str(doc.transaction_date),
		"grand_total": doc.grand_total,
		"currency": doc.currency,
		"items": items,
		"customer": doc.customer_name,
	}
