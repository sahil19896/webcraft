# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.website.website_generator import WebsiteGenerator

from webcraft.website_builder.builder import get_page_context, get_project_for_page


class WebsitePage(WebsiteGenerator):
	def validate(self):
		self.set_route()
		self._normalize_sections()

	def set_route(self):
		if not self.route and self.page_title:
			slug = frappe.scrub(self.page_title).replace("_", "-")
			if self.is_homepage:
				self.route = "wc"
			else:
				self.route = f"wc/{slug}"

	def _normalize_sections(self):
		for row in self.sections or []:
			for field in ("content", "style", "settings"):
				value = row.get(field)
				if isinstance(value, str) and value.strip():
					try:
						row.set(field, json.loads(value))
					except json.JSONDecodeError:
						pass

	def get_context(self, context):
		project = get_project_for_page(self.name)
		page_ctx = get_page_context(self, project)
		context.update(page_ctx)
		context.no_cache = 1

	def on_update(self):
		super().on_update()
		self._clear_route_cache()

	def on_trash(self):
		self._clear_route_cache()
		super().on_trash()

	def _clear_route_cache(self):
		from frappe.website.page_renderers.document_page import _find_matching_document_webview

		_find_matching_document_webview.clear_cache()
		if self.route:
			from frappe.website.utils import clear_cache

			clear_cache(self.route)

	def is_website_published(self):
		return bool(self.published)
