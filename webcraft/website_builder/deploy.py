# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Publishing and deployment workflow."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from webcraft.website_builder.access import clear_project_route_cache, deactivate_other_projects, sync_project_pages_published


def publish_project(project: str) -> dict:
	project_doc = frappe.get_doc("Website Project", project)
	deactivate_other_projects(project)
	project_doc.is_active = 1
	project_doc.status = "Published"
	project_doc.published_on = now_datetime()
	project_doc.save(ignore_permissions=True)

	sync_project_pages_published(project)
	frappe.db.commit()

	homepage_route = None
	if project_doc.homepage:
		homepage_route = frappe.db.get_value("Website Page", project_doc.homepage, "route")
	published_count = frappe.db.count("Website Page", {"website_project": project, "published": 1})
	return {
		"status": "Published",
		"pages_published": published_count,
		"homepage_route": homepage_route,
		"is_active": 1,
	}


def unpublish_project(project: str) -> dict:
	project_doc = frappe.get_doc("Website Project", project)
	project_doc.status = "Draft"
	project_doc.is_active = 0
	project_doc.save(ignore_permissions=True)

	sync_project_pages_published(project)
	frappe.db.commit()

	pages = frappe.db.count("Website Page", {"website_project": project, "published": 0})
	return {"status": "Draft", "pages_unpublished": pages, "is_active": 0}


def get_publish_status(project: str) -> dict:
	project_doc = frappe.get_doc("Website Project", project)
	total = frappe.db.count("Website Page", {"website_project": project})
	published = frappe.db.count("Website Page", {"website_project": project, "published": 1})
	return {
		"project_status": project_doc.status,
		"is_active": bool(project_doc.is_active),
		"is_live": bool(project_doc.is_active and project_doc.status == "Published"),
		"total_pages": total,
		"published_pages": published,
		"homepage": project_doc.homepage,
		"homepage_route": frappe.db.get_value("Website Page", project_doc.homepage, "route")
		if project_doc.homepage
		else None,
	}
