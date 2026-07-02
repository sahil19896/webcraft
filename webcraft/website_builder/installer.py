# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Template installation: copy bundled JSON into Website Project records."""

from __future__ import annotations

import json
import os
from pathlib import Path

import frappe
from frappe.utils import get_files_path, now_datetime

from webcraft.website_builder.components.registry import get_component_defaults


def get_templates_root() -> Path:
	return Path(frappe.get_app_path("webcraft", "website_builder", "templates"))


def load_template_manifest(folder_path: str) -> dict:
	manifest_path = get_templates_root() / folder_path / "template.json"
	if not manifest_path.exists():
		frappe.throw(f"Template manifest not found: {manifest_path}")
	with open(manifest_path, encoding="utf-8") as handle:
		return json.load(handle)


def install_template_for_project(project: str, template_key: str | None = None) -> dict:
	project_doc = frappe.get_doc("Website Project", project)
	template_key = template_key or project_doc.website_template
	if not template_key:
		frappe.throw("No template selected for this project.")

	if frappe.db.exists("Website Template", template_key):
		template_doc = frappe.get_doc("Website Template", template_key)
		folder_path = template_doc.folder_path
	else:
		folder_path = template_key

	manifest = load_template_manifest(folder_path)
	return _apply_manifest(project_doc, manifest, folder_path)


def _apply_manifest(project_doc, manifest: dict, folder_path: str) -> dict:
	stats = {"pages": 0, "menus": 0, "assets": 0, "theme": None, "forms": 0}
	route_prefix = manifest.get("route_prefix") or "wc"

	theme_name = _create_theme(project_doc.name, manifest.get("theme", {}))
	project_doc.website_theme = theme_name
	stats["theme"] = theme_name

	contact_form = _create_contact_form(project_doc.name)
	stats["forms"] = 1 if contact_form else 0

	_copy_template_assets(project_doc.name, folder_path)
	stats["assets"] = len(manifest.get("assets", []))

	page_map = {}
	for index, page_def in enumerate(manifest.get("pages", [])):
		page_name = _create_page(project_doc.name, page_def, index, contact_form, route_prefix)
		page_map[page_def.get("title")] = page_name
		if page_def.get("slug"):
			page_map[page_def["slug"]] = page_name
		stats["pages"] += 1
		if page_def.get("is_homepage"):
			project_doc.homepage = page_name

	for menu_def in manifest.get("menus", []):
		_create_menu(project_doc.name, menu_def, page_map)
		stats["menus"] += 1

	project_doc.save(ignore_permissions=True)
	frappe.db.commit()
	return stats


def _create_theme(project_name: str, theme_def: dict) -> str:
	display_name = theme_def.get("theme_name") or f"{project_name} Theme"
	theme_doc_name = frappe.scrub(f"{project_name}-theme")
	if frappe.db.exists("Website Theme", theme_doc_name):
		frappe.delete_doc("Website Theme", theme_doc_name, force=1)

	fieldnames = {f.fieldname for f in frappe.get_meta("Website Theme").fields}
	doc = frappe.get_doc(
		{
			"doctype": "Website Theme",
			"theme_name": theme_doc_name,
			"website_project": project_name,
			"is_default": 1,
			"brand_name": theme_def.get("theme_name") or display_name,
			**{k: v for k, v in theme_def.items() if k in fieldnames and k != "theme_name"},
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def _create_contact_form(project_name: str) -> str | None:
	from webcraft.website_builder.forms.registry import get_field_defaults

	form_key = f"{frappe.scrub(project_name)}-contact"
	if frappe.db.exists("Website Form", form_key):
		return form_key

	doc = frappe.get_doc(
		{
			"doctype": "Website Form",
			"form_name": form_key,
			"website_project": project_name,
			"title": "Contact Us",
			"description": "Send us a message and we will get back to you shortly.",
			"published": 1,
			"enable_notification": 0,
			"success_message": "Thank you for reaching out. We will be in touch soon.",
			"form_settings": {"submit_label": "Send Message", "honeypot_field": "_wc_honeypot"},
			"fields": [
				{
					**get_field_defaults("Text"),
					"label": "Name",
					"fieldname": "name",
					"required": 1,
					"placeholder": "Your name",
					"sort_order": 0,
					"width": "Half",
				},
				{
					**get_field_defaults("Email"),
					"label": "Email",
					"fieldname": "email",
					"required": 1,
					"placeholder": "you@company.com",
					"sort_order": 1,
					"width": "Half",
				},
				{
					**get_field_defaults("Phone"),
					"label": "Phone",
					"fieldname": "phone",
					"required": 0,
					"sort_order": 2,
					"width": "Half",
				},
				{
					**get_field_defaults("Textarea"),
					"label": "Message",
					"fieldname": "message",
					"required": 1,
					"placeholder": "How can we help?",
					"sort_order": 3,
					"width": "Full",
				},
			],
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def _create_page(
	project_name: str, page_def: dict, index: int, contact_form: str | None = None, route_prefix: str = "wc"
) -> str:
	title = page_def.get("title") or f"Page {index + 1}"
	slug = page_def.get("slug")
	is_homepage = page_def.get("is_homepage", False)
	prefix = (route_prefix or "wc").strip("/")

	if is_homepage:
		route = prefix
	elif slug:
		route = f"{prefix}/{slug}"
	else:
		route = f"{prefix}/{frappe.scrub(title).replace('_', '-')}"

	sections = []
	for order, section in enumerate(page_def.get("sections", [])):
		section_type = section.get("type")
		content = section.get("content") or get_component_defaults(section_type)
		if section_type == "contact" and contact_form:
			content = dict(content)
			content["form"] = contact_form
		sections.append(
			{
				"section_type": section_type,
				"section_order": order,
				"content": content,
				"style": section.get("style") or {},
				"settings": section.get("settings") or {},
				"is_hidden": section.get("hidden", 0),
			}
		)

	doc = frappe.get_doc(
		{
			"doctype": "Website Page",
			"page_title": title,
			"website_project": project_name,
			"route": route,
			"is_homepage": is_homepage,
			"published": 0,
			"sections": sections,
			"meta_title": page_def.get("seo", {}).get("title") or title,
			"meta_description": page_def.get("seo", {}).get("description") or "",
			"meta_keywords": page_def.get("seo", {},).get("keywords") or "",
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def _create_menu(project_name: str, menu_def: dict, page_map: dict) -> str:
	items = []
	for order, item in enumerate(menu_def.get("items", [])):
		url = item.get("url")
		if item.get("page") and item["page"] in page_map:
			page_route = frappe.db.get_value("Website Page", page_map[item["page"]], "route")
			url = f"/{page_route}" if page_route else url
		items.append(
			{
				"label": item.get("label"),
				"url": url or "#",
				"sort_order": order,
				"open_in_new_tab": item.get("open_in_new_tab", 0),
			}
		)

	doc = frappe.get_doc(
		{
			"doctype": "Website Menu",
			"menu_name": menu_def.get("name") or f"{project_name}-{menu_def.get('location', 'header')}",
			"website_project": project_name,
			"location": menu_def.get("location", "Header"),
			"items": items,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def _copy_template_assets(project_name: str, folder_path: str) -> None:
	assets_dir = get_templates_root() / folder_path / "assets"
	if not assets_dir.exists():
		return

	files_path = get_files_path("webcraft", is_private=0)
	target_dir = os.path.join(files_path, project_name)
	os.makedirs(target_dir, exist_ok=True)

	for asset_file in assets_dir.iterdir():
		if not asset_file.is_file():
			continue
		dest = os.path.join(target_dir, asset_file.name)
		if not os.path.exists(dest):
			with open(asset_file, "rb") as src, open(dest, "wb") as out:
				out.write(src.read())

		file_url = f"/files/webcraft/{project_name}/{asset_file.name}"
		if not frappe.db.exists("Website Asset", {"website_project": project_name, "asset_name": asset_file.name}):
			frappe.get_doc(
				{
					"doctype": "Website Asset",
					"asset_name": asset_file.name,
					"website_project": project_name,
					"asset_type": _guess_asset_type(asset_file.suffix),
					"file_url": file_url,
				}
			).insert(ignore_permissions=True)


def _guess_asset_type(suffix: str) -> str:
	suffix = suffix.lower()
	if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
		return "Image"
	if suffix in {".mp4", ".webm"}:
		return "Video"
	if suffix == ".pdf":
		return "PDF"
	if suffix == ".svg":
		return "SVG"
	return "Other"


def sync_template_records() -> list[str]:
	"""Register or update bundled templates as Website Template records."""
	synced = []
	root = get_templates_root()
	if not root.exists():
		return synced

	for entry in root.iterdir():
		if not entry.is_dir() or entry.name == "sections":
			continue
		manifest_path = entry / "template.json"
		if not manifest_path.exists():
			continue
		with open(manifest_path, encoding="utf-8") as handle:
			manifest = json.load(handle)

		key = manifest.get("key") or entry.name
		fields = {
			"title": manifest.get("title") or key.title(),
			"description": manifest.get("description") or "",
			"category": manifest.get("category") or "Corporate",
			"folder_path": entry.name,
			"version": manifest.get("version") or "1.0.0",
			"is_active": 1,
		}

		if frappe.db.exists("Website Template", key):
			current = frappe.db.get_value("Website Template", key, list(fields.keys()), as_dict=True) or {}
			if any(current.get(field) != value for field, value in fields.items()):
				frappe.db.set_value("Website Template", key, fields, update_modified=True)
		else:
			frappe.get_doc({"doctype": "Website Template", "template_key": key, **fields}).insert(
				ignore_permissions=True
			)
		synced.append(key)

	if synced:
		frappe.db.commit()
	return synced
