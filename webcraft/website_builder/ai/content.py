# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""AI-assisted section content generation."""

from __future__ import annotations

import json
import re

import frappe

from webcraft.website_builder.components.registry import get_component_defaults


def generate_section_content(section_type: str, prompt: str = "", context: dict | None = None) -> dict:
	context = context or {}
	prompt = (prompt or "").strip()

	ai_result = _try_openai(section_type, prompt, context)
	if ai_result:
		return ai_result

	return _template_generate(section_type, prompt, context)


def _try_openai(section_type: str, prompt: str, context: dict) -> dict | None:
	api_key = frappe.conf.get("openai_api_key")
	if not api_key:
		return None

	try:
		from openai import OpenAI

		client = OpenAI(api_key=api_key)
		defaults = get_component_defaults(section_type)
		system = (
			f"You generate JSON content for a website section of type '{section_type}'. "
			f"Return ONLY valid JSON matching this schema shape: {json.dumps(defaults)}"
		)
		user = prompt or f"Generate compelling {section_type} content for a modern website."
		if context.get("project_name"):
			user += f" Business/project: {context['project_name']}."
		if context.get("page_title"):
			user += f" Page: {context['page_title']}."

		response = client.chat.completions.create(
			model=frappe.conf.get("webcraft_ai_model") or "gpt-4o-mini",
			messages=[
				{"role": "system", "content": system},
				{"role": "user", "content": user},
			],
			temperature=0.7,
		)
		text = (response.choices[0].message.content or "").strip()
		match = re.search(r"\{[\s\S]*\}", text)
		if match:
			return json.loads(match.group())
	except Exception:
		frappe.log_error(title="WebCraft AI Content Generation Failed")
	return None


def _template_generate(section_type: str, prompt: str, context: dict) -> dict:
	defaults = dict(get_component_defaults(section_type))
	topic = prompt or context.get("project_name") or context.get("page_title") or "your brand"

	if section_type == "hero":
		defaults.update(
			{
				"title": f"Discover {topic}",
				"subtitle": "Premium quality, delivered fast. Shop the latest collection today.",
				"button_label": "Shop Now",
				"button_url": "#",
			}
		)
	elif section_type == "features":
		defaults["title"] = f"Why choose {topic}"
		defaults["items"] = [
			{"title": "Quality First", "description": "Curated products you can trust.", "icon": "shield"},
			{"title": "Fast Delivery", "description": "Ships quickly to your door.", "icon": "zap"},
			{"title": "Easy Returns", "description": "Hassle-free returns within 30 days.", "icon": "refresh"},
		]
	elif section_type == "cta":
		defaults.update(
			{
				"title": f"Ready to explore {topic}?",
				"subtitle": "Join thousands of happy customers.",
				"button_label": "Get Started",
			}
		)
	elif section_type == "text":
		defaults.update(
			{
				"title": f"About {topic}",
				"body": f"<p>{topic} is built for people who expect more — better design, better service, and a better experience from start to finish.</p>",
			}
		)
	elif section_type in ("product_grid", "product_carousel"):
		defaults["title"] = "Featured Products"
		defaults["subtitle"] = f"Top picks from {topic}"

	return defaults
