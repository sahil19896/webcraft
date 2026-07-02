# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Custom page renderer for dynamic store routes (product, order)."""

from __future__ import annotations

import frappe
from frappe.website.page_renderers.base_template_page import BaseTemplatePage

from webcraft.website_builder.commerce.store import build_live_dynamic_context, parse_store_path

TEMPLATE = "website_builder/doctype/website_page/templates/website_page.html"


class StoreCommerceRenderer(BaseTemplatePage):
	def can_render(self):
		parsed = parse_store_path(self.path)
		if parsed and parsed.get("mode") == "live":
			self.parsed = parsed
			return True
		return False

	def render(self):
		self.init_context()
		self.context.update(build_live_dynamic_context(self.parsed))
		self.post_process_context()
		html = frappe.get_template(TEMPLATE).render(self.context)
		return self.build_response(self.add_csrf_token(html))
