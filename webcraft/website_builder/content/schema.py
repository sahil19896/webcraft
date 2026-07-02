# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Editable field schemas for the WebCraft content editor (Shopify-style)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from webcraft.website_builder.components.registry import COMPONENTS

# Sections that are system/commerce flows — not user-editable in the content panel.
NON_EDITABLE_SECTIONS = frozenset(
	{
		"cart",
		"checkout",
		"order_confirmation",
		"product_detail",
		"form",
	}
)

# Field types: text, textarea, html, url, image, number, select
SECTION_EDIT_SCHEMA: dict[str, dict[str, Any]] = {
	"header": {
		"fields": [
			{"path": "logo_text", "label": "Site name", "type": "text"},
			{"path": "cta_label", "label": "Button text", "type": "text"},
			{"path": "cta_url", "label": "Button link", "type": "url"},
		]
	},
	"hero": {
		"fields": [
			{"path": "eyebrow", "label": "Small label above headline", "type": "text"},
			{"path": "title", "label": "Main headline", "type": "text", "required": True},
			{"path": "subtitle", "label": "Description", "type": "textarea"},
			{"path": "button_label", "label": "Main button text", "type": "text"},
			{"path": "button_url", "label": "Main button link", "type": "url"},
			{"path": "secondary_button_label", "label": "Second button text", "type": "text"},
			{"path": "secondary_button_url", "label": "Second button link", "type": "url"},
			{"path": "image", "label": "Hero photo", "type": "image"},
		]
	},
	"marquee": {
		"fields": [
			{
				"path": "items",
				"label": "Scrolling messages",
				"type": "lines",
				"help": "One message per line.",
			},
		]
	},
	"features": {
		"fields": [
			{"path": "title", "label": "Heading", "type": "text"},
			{"path": "subtitle", "label": "Description", "type": "textarea"},
		],
		"repeaters": [
			{
				"path": "items",
				"label": "Features",
				"fields": [
					{"path": "title", "label": "Title", "type": "text"},
					{"path": "description", "label": "Description", "type": "textarea"},
				],
			}
		],
	},
	"stats": {
		"fields": [{"path": "title", "label": "Heading", "type": "text"}],
		"repeaters": [
			{
				"path": "items",
				"label": "Stats",
				"fields": [
					{"path": "value", "label": "Value", "type": "text"},
					{"path": "label", "label": "Label", "type": "text"},
				],
			}
		],
	},
	"testimonials": {
		"fields": [{"path": "title", "label": "Heading", "type": "text"}],
		"repeaters": [
			{
				"path": "items",
				"label": "Testimonials",
				"fields": [
					{"path": "quote", "label": "Quote", "type": "textarea"},
					{"path": "author", "label": "Author", "type": "text"},
					{"path": "role", "label": "Role", "type": "text"},
				],
			}
		],
	},
	"pricing": {
		"fields": [
			{"path": "title", "label": "Heading", "type": "text"},
			{"path": "subtitle", "label": "Description", "type": "textarea"},
		],
		"repeaters": [
			{
				"path": "plans",
				"label": "Pricing plans",
				"fields": [
					{"path": "name", "label": "Plan name", "type": "text"},
					{"path": "price", "label": "Price", "type": "text"},
					{"path": "period", "label": "Period", "type": "text"},
					{"path": "cta_label", "label": "Button label", "type": "text"},
				],
			}
		],
	},
	"faq": {
		"fields": [{"path": "title", "label": "Heading", "type": "text"}],
		"repeaters": [
			{
				"path": "items",
				"label": "Questions",
				"fields": [
					{"path": "question", "label": "Question", "type": "text"},
					{"path": "answer", "label": "Answer", "type": "textarea"},
				],
			}
		],
	},
	"cta": {
		"fields": [
			{"path": "title", "label": "Headline", "type": "text"},
			{"path": "subtitle", "label": "Description", "type": "textarea"},
			{"path": "button_label", "label": "Button text", "type": "text"},
			{"path": "button_url", "label": "Button link", "type": "url"},
		]
	},
	"contact": {
		"fields": [
			{"path": "title", "label": "Heading", "type": "text"},
			{"path": "subtitle", "label": "Description", "type": "textarea"},
			{"path": "email", "label": "Email", "type": "text"},
			{"path": "phone", "label": "Phone", "type": "text"},
			{"path": "address", "label": "Address", "type": "textarea"},
		]
	},
	"text": {
		"fields": [
			{"path": "title", "label": "Heading", "type": "text"},
			{"path": "body", "label": "Text", "type": "html"},
		]
	},
	"team": {
		"fields": [{"path": "title", "label": "Heading", "type": "text"}],
		"repeaters": [
			{
				"path": "members",
				"label": "Team members",
				"fields": [
					{"path": "name", "label": "Name", "type": "text"},
					{"path": "role", "label": "Role", "type": "text"},
					{"path": "bio", "label": "Bio", "type": "textarea"},
					{"path": "photo", "label": "Photo", "type": "image"},
				],
			}
		],
	},
	"footer": {
		"fields": [
			{"path": "logo_text", "label": "Site name", "type": "text"},
			{"path": "copyright", "label": "Copyright line", "type": "text"},
		]
	},
	"product_grid": {
		"fields": [
			{"path": "title", "label": "Heading", "type": "text"},
			{"path": "subtitle", "label": "Description", "type": "textarea"},
			{
				"path": "source",
				"label": "Product source",
				"type": "select",
				"options": [{"value": "webshop", "label": "Live Webshop catalog"}, {"value": "static", "label": "Static list"}],
			},
			{"path": "limit", "label": "Product count", "type": "number"},
		]
	},
	"product_carousel": {
		"fields": [
			{"path": "title", "label": "Heading", "type": "text"},
			{"path": "subtitle", "label": "Description", "type": "textarea"},
			{"path": "limit", "label": "Product count", "type": "number"},
		]
	},
	"brand_logos": {
		"fields": [{"path": "title", "label": "Heading", "type": "text"}],
		"repeaters": [
			{
				"path": "brands",
				"label": "Brands",
				"fields": [
					{"path": "name", "label": "Brand name", "type": "text"},
					{"path": "url", "label": "Link URL", "type": "url"},
				],
			}
		],
	},
	"category_tiles": {
		"fields": [
			{"path": "title", "label": "Heading", "type": "text"},
			{"path": "subtitle", "label": "Description", "type": "textarea"},
		],
		"repeaters": [
			{
				"path": "categories",
				"label": "Categories",
				"fields": [
					{"path": "label", "label": "Label", "type": "text"},
					{"path": "url", "label": "Link URL", "type": "url"},
					{"path": "image", "label": "Photo", "type": "image"},
				],
			}
		],
	},
}


def is_section_editable(section_type: str) -> bool:
	return section_type not in NON_EDITABLE_SECTIONS and section_type in SECTION_EDIT_SCHEMA


def get_section_edit_schema(section_type: str) -> dict[str, Any]:
	return deepcopy(SECTION_EDIT_SCHEMA.get(section_type, {}))


def get_section_label(section_type: str) -> str:
	meta = COMPONENTS.get(section_type) or {}
	return meta.get("label") or section_type.replace("_", " ").title()
