# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""WebCraft API — design catalog, preview, and install."""

from __future__ import annotations

import frappe
from frappe.utils import cint

from webcraft.website_builder.deploy import (
	get_publish_status,
	publish_project as deploy_publish_project,
	unpublish_project as deploy_unpublish_project,
)
from webcraft.website_builder.installer import install_template_for_project, sync_template_records
from webcraft.website_builder.preview import get_design_detail, list_bundled_designs


@frappe.whitelist()
def get_design_catalog() -> list[dict]:
	return list_bundled_designs()


@frappe.whitelist()
def get_my_sites() -> list[dict]:
	"""Installed website projects (Shopify 'My themes' equivalent)."""
	if not frappe.has_permission("Website Project", "read"):
		return []

	sites = []
	for row in frappe.get_all(
		"Website Project",
		fields=["name", "project_name", "status", "is_active", "website_template", "website_theme", "homepage", "modified"],
		order_by="modified desc",
	):
		route = ""
		if row.homepage:
			route = frappe.db.get_value("Website Page", row.homepage, "route") or ""
		template_title = (
			frappe.db.get_value("Website Template", row.website_template, "title")
			if row.website_template
			else None
		)
		sites.append(
			{
				**row,
				"route": route,
				"live_url": f"/{route}" if route else "",
				"template_title": template_title,
				"preview_url": f"/{route}" if route else "",
				"is_live": bool(row.is_active and row.status == "Published"),
			}
		)
	return sites


@frappe.whitelist()
def get_customize_context(project: str) -> dict:
	if not project or not frappe.db.exists("Website Project", project):
		frappe.throw("Project not found.")

	from webcraft.website_builder.content.editor import build_pages_editor_payload
	from webcraft.website_builder.content.menus import get_project_menus_detail

	doc = frappe.get_doc("Website Project", project)
	if not doc.website_theme:
		frappe.throw("This project has no theme.")

	theme = frappe.get_doc("Website Theme", doc.website_theme)
	route = ""
	if doc.homepage:
		route = frappe.db.get_value("Website Page", doc.homepage, "route") or ""

	pages = build_pages_editor_payload(project)

	return {
		"project": doc.name,
		"project_name": doc.project_name,
		"status": doc.status,
		"preview_url": f"/{route}" if route else "",
		"theme": theme.as_dict(),
		"pages": pages,
		"menus": get_project_menus_detail(project),
		"publish_status": get_publish_status(project),
	}


@frappe.whitelist()
def save_theme_customization(project: str, theme_data: dict | str) -> dict:
	import json

	if isinstance(theme_data, str):
		theme_data = json.loads(theme_data) if theme_data else {}

	if not project or not frappe.db.exists("Website Project", project):
		frappe.throw("Project not found.")

	project_doc = frappe.get_doc("Website Project", project)
	if not project_doc.website_theme:
		frappe.throw("This project has no theme.")

	allowed = {
		"primary_color",
		"secondary_color",
		"accent_color",
		"background_color",
		"text_color",
		"surface_color",
		"font_family",
		"heading_font",
		"base_font_size",
		"border_radius",
		"brand_name",
		"logo_image",
		"custom_css",
		"animations_enabled",
	}
	theme = frappe.get_doc("Website Theme", project_doc.website_theme)
	for key, value in theme_data.items():
		if key in allowed:
			theme.set(key, value)
	theme.save(ignore_permissions=True)

	if project_doc.homepage:
		page_route = frappe.db.get_value("Website Page", project_doc.homepage, "route")
		if page_route:
			from frappe.website.utils import clear_cache

			clear_cache(page_route)

	frappe.db.commit()
	return {"success": True, "theme": theme.name}


@frappe.whitelist()
def save_page_content(page: str, sections: list | str) -> dict:
	"""Save edited section content for a Website Page."""
	import json

	from webcraft.website_builder.content.editor import save_page_sections

	if isinstance(sections, str):
		sections = json.loads(sections) if sections else []
	return save_page_sections(page, sections)


@frappe.whitelist()
def get_design(template_key: str) -> dict:
	return get_design_detail(template_key) or {}


@frappe.whitelist()
def install_design(project_name: str, template_key: str, publish: int = 1) -> dict:
	if not project_name or not template_key:
		frappe.throw("Project name and design are required.")
	if frappe.db.exists("Website Project", project_name):
		frappe.throw(f"Project '{project_name}' already exists.")

	doc = frappe.get_doc(
		{
			"doctype": "Website Project",
			"project_name": project_name,
			"website_template": template_key,
			"status": "Draft",
			"site": frappe.local.site,
			"is_active": 1,
		}
	)
	doc.insert(ignore_permissions=True)

	stats = install_template_for_project(doc.name, template_key)
	result = {"project": doc.name, "template": template_key, "install": stats}

	if cint(publish):
		result["publish"] = deploy_publish_project(doc.name)

	frappe.db.commit()
	return result


@frappe.whitelist()
def get_project_status(project: str) -> dict:
	return get_publish_status(project)


@frappe.whitelist()
def save_project_menus(project: str, menus: dict | str) -> dict:
	"""Save header/footer navigation for a project."""
	import json

	from webcraft.website_builder.content.menus import save_project_menus as _save

	if isinstance(menus, str):
		menus = json.loads(menus) if menus else {}
	return _save(project, menus)


@frappe.whitelist()
def unpublish_project(project: str) -> dict:
	if not project or not frappe.db.exists("Website Project", project):
		frappe.throw("Project not found.")
	result = deploy_unpublish_project(project)
	frappe.db.commit()
	return result


@frappe.whitelist()
def update_submission_status(name: str, status: str) -> dict:
	allowed = ("Unread", "Read", "Replied", "Archived")
	if status not in allowed:
		frappe.throw("Invalid status.")
	if not name or not frappe.db.exists("Website Form Submission", name):
		frappe.throw("Submission not found.")
	if not frappe.has_permission("Website Form Submission", "write", name):
		frappe.throw("Not permitted.")

	frappe.db.set_value("Website Form Submission", name, "status", status)
	frappe.db.commit()
	return {"success": True, "status": status}


@frappe.whitelist()
def publish_project(project: str) -> dict:
	return deploy_publish_project(project)


@frappe.whitelist()
def sync_templates() -> list[str]:
	return sync_template_records()


def has_app_permission() -> bool:
	return frappe.has_permission("Website Project", "read")


@frappe.whitelist(allow_guest=True)
def submit_form(form_name: str, data: dict | str | None = None) -> dict:
	"""Submit a WebCraft website form."""
	import json

	from webcraft.website_builder.forms.validation import validate_submission

	if isinstance(data, str):
		data = json.loads(data) if data else {}
	data = data or {}

	if not form_name or not frappe.db.exists("Website Form", form_name):
		return {"success": False, "message": "Form not found."}

	form_doc = frappe.get_doc("Website Form", form_name)
	settings = form_doc.form_settings or {}
	if isinstance(settings, str):
		settings = json.loads(settings) if settings else {}

	from webcraft.website_builder.access import is_project_live

	if form_doc.website_project and not is_project_live(form_doc.website_project):
		return {"success": False, "message": "This form is not available."}

	honeypot = settings.get("honeypot_field")
	if honeypot and data.get(honeypot):
		return {"success": True, "message": form_doc.success_message or "Thank you."}

	cleaned, errors = validate_submission(form_doc, data)
	if errors:
		return {"success": False, "message": errors[0]}

	submission = frappe.get_doc(
		{
			"doctype": "Website Form Submission",
			"website_form": form_name,
			"website_project": form_doc.website_project,
			"data": json.dumps(cleaned),
		}
	)
	submission.insert(ignore_permissions=True)
	frappe.db.commit()
	return {
		"success": True,
		"message": form_doc.success_message or "Thank you for your submission.",
		"redirect_url": form_doc.redirect_url or "",
	}


@frappe.whitelist()
def reset_webcraft_data(confirm: int = 0) -> dict:
	"""Remove all Website Projects and related WebCraft content. Desk admins only."""
	if not cint(confirm):
		frappe.throw("Pass confirm=1 to reset all WebCraft site data.")

	if not frappe.has_permission("Website Project", "delete"):
		frappe.throw("Not permitted.")

	deleted = {"projects": 0, "pages": 0}
	for project in frappe.get_all("Website Project", pluck="name"):
		for page in frappe.get_all("Website Page", filters={"website_project": project}, pluck="name"):
			frappe.delete_doc("Website Page", page, force=1, ignore_permissions=True)
			deleted["pages"] += 1
		for doctype in (
			"Website Menu",
			"Website Theme",
			"Website Form",
			"Website Asset",
			"Website Form Submission",
		):
			for name in frappe.get_all(doctype, filters={"website_project": project}, pluck="name"):
				frappe.delete_doc(doctype, name, force=1, ignore_permissions=True)
		frappe.delete_doc("Website Project", project, force=1, ignore_permissions=True)
		deleted["projects"] += 1

	frappe.db.commit()
	frappe.clear_cache()
	return deleted
