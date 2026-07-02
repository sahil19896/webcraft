# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Form field type registry."""

from __future__ import annotations

FIELD_TYPES: dict[str, dict] = {
	"Text": {"label": "Text", "category": "Basic", "html_type": "text", "defaults": {"label": "Text Field", "placeholder": "", "required": 0, "width": "Full"}},
	"Email": {"label": "Email", "category": "Basic", "html_type": "email", "defaults": {"label": "Email", "placeholder": "you@example.com", "required": 1, "width": "Full"}},
	"Phone": {"label": "Phone", "category": "Basic", "html_type": "tel", "defaults": {"label": "Phone", "placeholder": "", "required": 0, "width": "Half"}},
	"URL": {"label": "URL", "category": "Basic", "html_type": "url", "defaults": {"label": "Website", "placeholder": "https://", "required": 0, "width": "Full"}},
	"Number": {"label": "Number", "category": "Basic", "html_type": "number", "defaults": {"label": "Number", "placeholder": "", "required": 0, "width": "Half"}},
	"Password": {"label": "Password", "category": "Basic", "html_type": "password", "defaults": {"label": "Password", "required": 0, "width": "Full"}},
	"Textarea": {"label": "Textarea", "category": "Basic", "html_type": "textarea", "defaults": {"label": "Message", "placeholder": "", "required": 0, "width": "Full"}},
	"Date": {"label": "Date", "category": "Basic", "html_type": "date", "defaults": {"label": "Date", "required": 0, "width": "Half"}},
	"Time": {"label": "Time", "category": "Basic", "html_type": "time", "defaults": {"label": "Time", "required": 0, "width": "Half"}},
	"Checkbox": {"label": "Checkbox", "category": "Choice", "html_type": "checkbox", "defaults": {"label": "I agree", "required": 0, "width": "Full"}},
	"Switch": {"label": "Switch", "category": "Choice", "html_type": "checkbox", "defaults": {"label": "Enable option", "required": 0, "width": "Full"}},
	"Select": {"label": "Select", "category": "Choice", "html_type": "select", "defaults": {"label": "Select option", "options": "Option 1\nOption 2", "required": 0, "width": "Full"}},
	"Radio": {"label": "Radio", "category": "Choice", "html_type": "radio", "defaults": {"label": "Choose one", "options": "Option A\nOption B", "required": 0, "width": "Full"}},
	"Heading": {"label": "Heading", "category": "Layout", "html_type": "heading", "defaults": {"label": "Section heading", "width": "Full"}},
	"Divider": {"label": "Divider", "category": "Layout", "html_type": "divider", "defaults": {"width": "Full"}},
	"File Upload": {"label": "File Upload", "category": "Advanced", "html_type": "file", "defaults": {"label": "Upload file", "required": 0, "width": "Full"}},
	"Image Upload": {"label": "Image Upload", "category": "Advanced", "html_type": "file", "defaults": {"label": "Upload image", "required": 0, "width": "Full"}},
	"Address": {"label": "Address", "category": "Advanced", "html_type": "textarea", "defaults": {"label": "Address", "required": 0, "width": "Full"}},
	"Currency": {"label": "Currency", "category": "Advanced", "html_type": "number", "defaults": {"label": "Amount", "required": 0, "width": "Half"}},
	"Rating": {"label": "Rating", "category": "Advanced", "html_type": "rating", "defaults": {"label": "Rating", "required": 0, "width": "Full"}},
	"Color": {"label": "Color", "category": "Advanced", "html_type": "color", "defaults": {"label": "Pick a color", "required": 0, "width": "Half"}},
	"Slider": {"label": "Slider", "category": "Advanced", "html_type": "range", "defaults": {"label": "Value", "default_value": "50", "required": 0, "width": "Full"}},
}


def get_field_types() -> dict:
	return FIELD_TYPES


def get_field_defaults(field_type: str) -> dict:
	meta = FIELD_TYPES.get(field_type, {})
	defaults = dict(meta.get("defaults", {}))
	defaults["field_type"] = field_type
	return defaults
