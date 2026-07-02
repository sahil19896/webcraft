# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Publishing and deployment workflow."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime


def publish_project(project: str) -> dict:
	project_doc = frappe.get_doc("Website Project", project)
	pages = frappe.get_all(
		"Website Page",
		filters={"website_project": project},
		pluck="name",
	)

	published_count = 0
	for page_name in pages:
		page = frappe.get_doc("Website Page", page_name)
		if not page.published:
			page.published = 1
			page.save(ignore_permissions=True)
			published_count += 1

	project_doc.status = "Published"
	project_doc.published_on = now_datetime()
	project_doc.save(ignore_permissions=True)

	frappe.db.commit()
	frappe.clear_cache()

	from frappe.website.page_renderers.document_page import _find_matching_document_webview

	_find_matching_document_webview.clear_cache()
	homepage_route = None
	if project_doc.homepage:
		homepage_route = frappe.db.get_value("Website Page", project_doc.homepage, "route")
	return {
		"status": "Published",
		"pages_published": published_count,
		"homepage_route": homepage_route,
	}


def unpublish_project(project: str) -> dict:
	project_doc = frappe.get_doc("Website Project", project)
	pages = frappe.get_all(
		"Website Page",
		filters={"website_project": project, "published": 1},
		pluck="name",
	)

	for page_name in pages:
		frappe.db.set_value("Website Page", page_name, "published", 0)

	project_doc.status = "Draft"
	project_doc.save(ignore_permissions=True)
	frappe.clear_cache()
	return {"status": "Draft", "pages_unpublished": len(pages)}


def get_publish_status(project: str) -> dict:
	project_doc = frappe.get_doc("Website Project", project)
	total = frappe.db.count("Website Page", {"website_project": project})
	published = frappe.db.count("Website Page", {"website_project": project, "published": 1})
	return {
		"project_status": project_doc.status,
		"total_pages": total,
		"published_pages": published,
		"homepage": project_doc.homepage,
		"homepage_route": frappe.db.get_value("Website Page", project_doc.homepage, "route")
		if project_doc.homepage
		else None,
	}
