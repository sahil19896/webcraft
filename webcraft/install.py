# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

import json
import os

from webcraft.website_builder.installer import sync_template_records


def after_install():
	sync_template_records()
	sync_desk_pages()


def sync_desk_pages():
	"""Load Page JS/CSS from module files and sync title from JSON."""
	import frappe
	from frappe.modules import get_module_path, scrub

	for page_name in ("webcraft", "webcraft-customize"):
		if not frappe.db.exists("Page", page_name):
			continue
		doc = frappe.get_doc("Page", page_name)
		doc.load_assets()

		page_folder = scrub(page_name)
		json_path = os.path.join(get_module_path(doc.module), "page", page_folder, f"{page_folder}.json")
		if os.path.exists(json_path):
			with open(json_path) as f:
				meta = json.load(f)
			if meta.get("title"):
				doc.title = meta["title"]

		doc.save(ignore_permissions=True)
	frappe.db.commit()
