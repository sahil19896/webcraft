# Copyright (c) 2026, WebCraft Team and contributors
# Public visibility rules for Website Projects.

from __future__ import annotations

import frappe


def is_project_live(project_name: str | None) -> bool:
	"""True when a project is the active, published site."""
	if not project_name or not frappe.db.exists("Website Project", project_name):
		return False
	row = frappe.db.get_value(
		"Website Project",
		project_name,
		["is_active", "status"],
		as_dict=True,
	)
	return bool(row and row.is_active and row.status == "Published")


def sync_project_pages_published(project_name: str) -> None:
	"""Keep page published flags aligned with project live status for Frappe routing."""
	published = 1 if is_project_live(project_name) else 0
	for page_name in frappe.get_all(
		"Website Page",
		filters={"website_project": project_name},
		pluck="name",
	):
		frappe.db.set_value("Website Page", page_name, "published", published, update_modified=False)
	clear_project_route_cache(project_name)


def deactivate_other_projects(project_name: str) -> list[str]:
	"""Ensure only one Website Project is active at a time."""
	deactivated = []
	for name in frappe.get_all(
		"Website Project",
		filters={"name": ["!=", project_name], "is_active": 1},
		pluck="name",
	):
		frappe.db.set_value("Website Project", name, "is_active", 0, update_modified=True)
		sync_project_pages_published(name)
		deactivated.append(name)
	return deactivated


def clear_project_route_cache(project_name: str) -> None:
	from frappe.website.page_renderers.document_page import _find_matching_document_webview
	from frappe.website.utils import WEBSITE_PAGE_CACHE_PREFIX

	_find_matching_document_webview.clear_cache()
	for route in frappe.get_all(
		"Website Page",
		filters={"website_project": project_name},
		pluck="route",
	):
		if route:
			frappe.cache.delete_value(f"{WEBSITE_PAGE_CACHE_PREFIX}{route}")
			from frappe.website.utils import clear_cache

			clear_cache(route)
	frappe.clear_cache()
