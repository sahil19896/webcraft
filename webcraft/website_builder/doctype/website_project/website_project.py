# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from webcraft.website_builder.access import clear_project_route_cache, deactivate_other_projects, sync_project_pages_published


class WebsiteProject(Document):
	def validate(self):
		if not self.site:
			self.site = frappe.local.site

	def before_save(self):
		if self.is_active:
			deactivate_other_projects(self.name)

	def on_update(self):
		if self.status == "Published" and not self.published_on:
			self.db_set("published_on", now_datetime(), update_modified=False)
		sync_project_pages_published(self.name)
