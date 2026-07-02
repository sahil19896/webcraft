# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class WebsiteProject(Document):
	def validate(self):
		if not self.site:
			self.site = frappe.local.site

	def on_update(self):
		if self.status == "Published" and not self.published_on:
			self.db_set("published_on", now_datetime(), update_modified=False)
