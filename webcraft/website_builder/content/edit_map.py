# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""DOM selectors for click-to-edit in the site customizer preview."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import cint

from webcraft.website_builder.content.schema import get_section_edit_schema, is_section_editable

# Scalar fields: field_path -> CSS selector (relative to section root)
SECTION_FIELD_SELECTORS: dict[str, dict[str, str]] = {
	"header": {
		"logo_text": ".wc-logo",
		"logo_image": ".wc-logo__image",
		"cta_label": ".wc-header__actions .wc-btn--primary",
	},
	"hero": {
		"eyebrow": ".wc-eyebrow",
		"title": ".wc-hero__title",
		"subtitle": ".wc-hero__subtitle",
		"button_label": ".wc-hero__actions .wc-btn--primary",
		"secondary_button_label": ".wc-hero__actions .wc-btn--ghost",
		"image": ".wc-hero__media img",
	},
	"features": {
		"title": ".wc-section__head h2",
		"subtitle": ".wc-section__head p",
	},
	"stats": {
		"title": ".wc-stats__title",
	},
	"testimonials": {
		"title": ".wc-section__title, h2",
	},
	"pricing": {
		"title": ".wc-section__head h2",
		"subtitle": ".wc-section__head p",
	},
	"faq": {
		"title": "h2",
	},
	"cta": {
		"title": "h2",
		"subtitle": "p",
		"button_label": ".wc-btn--primary",
	},
	"contact": {
		"title": ".wc-contact__info h2",
		"subtitle": ".wc-contact__info > p",
		"email": ".wc-contact__email",
		"phone": ".wc-contact__phone",
		"address": ".wc-contact__address",
	},
	"text": {
		"title": "h2",
		"body": ".wc-text__body",
	},
	"page_banner": {
		"title": ".wc-page-banner__title",
		"subtitle": ".wc-page-banner__subtitle",
	},
	"menu_list": {
		"title": ".wc-section__head h2, .wc-porto-head h2",
		"subtitle": ".wc-section__head p, .wc-porto-head p",
	},
	"porto_blog_team": {
		"blog.title": ".wc-porto-blog-team__col--blog .wc-porto-head h2",
		"team.title": ".wc-porto-blog-team__col--team .wc-porto-head h2",
	},
	"team": {
		"title": ".wc-section__title, h2",
	},
	"footer": {
		"logo_text": ".wc-logo",
		"copyright": ".wc-muted",
	},
	"product_grid": {
		"title": ".wc-section__head h2",
		"subtitle": ".wc-section__head p",
	},
	"product_carousel": {
		"title": ".wc-section__head h2",
		"subtitle": ".wc-section__head p",
	},
	"brand_logos": {
		"title": ".wc-section__title-center, h2",
	},
	"category_tiles": {
		"title": ".wc-section__head h2",
		"subtitle": ".wc-section__head p",
	},
	"marquee": {
		"items": ".wc-marquee__track",
	},
}

# Repeater rows: container + per-field selectors inside each row
SECTION_REPEATER_SELECTORS: dict[str, dict[str, dict[str, str]]] = {
	"features": {
		"items": {
			"container": ".wc-card--feature",
			"fields": {"title": "h3", "description": "p"},
		}
	},
	"stats": {
		"items": {
			"container": ".wc-stat",
			"fields": {"value": ".wc-stat__value", "label": ".wc-stat__label"},
		}
	},
	"testimonials": {
		"items": {
			"container": ".wc-quote",
			"fields": {"quote": "p", "author": "footer strong", "role": "footer span"},
		}
	},
	"pricing": {
		"plans": {
			"container": ".wc-card--pricing",
			"fields": {
				"name": "h3",
				"price": ".wc-price",
				"period": ".wc-price span",
				"cta_label": ".wc-btn",
			},
		}
	},
	"faq": {
		"items": {
			"container": ".wc-faq__item",
			"fields": {"question": "summary", "answer": "p"},
		}
	},
	"team": {
		"members": {
			"container": ".wc-card--team",
			"fields": {
				"name": "h3",
				"role": ".wc-muted",
				"bio": "p:not(.wc-muted)",
				"photo": ".wc-team__photo",
			},
		}
	},
	"category_tiles": {
		"categories": {
			"container": ".wc-category-tile",
			"fields": {"label": ".wc-category-tile__label", "image": ".wc-category-tile__media img"},
		}
	},
}


def is_wc_edit_mode() -> bool:
	if not cint(frappe.form_dict.get("wc_edit")):
		return False
	if frappe.session.user == "Guest":
		return False
	return frappe.has_permission("Website Project", "write")


def _field_labels(section_type: str) -> dict[str, str]:
	schema = get_section_edit_schema(section_type)
	labels = {f["path"]: f.get("label") or f["path"] for f in schema.get("fields") or []}
	for rep in schema.get("repeaters") or []:
		for f in rep.get("fields") or []:
			labels[f"{rep['path']}.{f['path']}"] = f.get("label") or f["path"]
	return labels


def _enriched_fields(section_type: str) -> dict[str, dict[str, str]]:
	selectors = SECTION_FIELD_SELECTORS.get(section_type, {})
	labels = _field_labels(section_type)
	return {
		path: {"selector": selector, "label": labels.get(path, path.replace("_", " ").title())}
		for path, selector in selectors.items()
	}


def _enriched_repeaters(section_type: str) -> dict[str, dict]:
	raw = SECTION_REPEATER_SELECTORS.get(section_type, {})
	schema = get_section_edit_schema(section_type)
	rep_schemas = {r["path"]: r for r in schema.get("repeaters") or []}
	enriched = {}
	for rep_path, rep_def in raw.items():
		field_labels = {
			f["path"]: f.get("label") or f["path"]
			for f in (rep_schemas.get(rep_path) or {}).get("fields") or []
		}
		enriched[rep_path] = {**rep_def, "labels": field_labels}
	return enriched


def build_page_edit_config(page) -> dict[str, Any]:
	sections = []
	for row in sorted(page.sections or [], key=lambda r: r.section_order or 0):
		if row.is_hidden or not is_section_editable(row.section_type):
			continue
		section_type = row.section_type
		entry: dict[str, Any] = {
			"id": row.name,
			"type": section_type,
			"fields": _enriched_fields(section_type),
		}
		repeaters = _enriched_repeaters(section_type)
		if repeaters:
			entry["repeaters"] = repeaters
		sections.append(entry)

	return {
		"sections": sections,
		"theme_targets": {
			"logo_image": {"selector": ".wc-header .wc-logo__image", "label": "Logo"},
			"brand_name": {"selector": ".wc-header .wc-logo", "label": "Site name"},
		},
	}
