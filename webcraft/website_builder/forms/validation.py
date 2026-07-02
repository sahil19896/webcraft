# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Server-side form submission validation."""

from __future__ import annotations

import re
from typing import Any

import frappe

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_submission(form_doc, data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
	"""Return cleaned data and list of error messages."""
	cleaned: dict[str, Any] = {}
	errors: list[str] = []

	# Honeypot handled in submit_form before validation

	for field in sorted(form_doc.fields or [], key=lambda f: f.sort_order or 0):
		if field.field_type in ("Heading", "Divider"):
			continue

		key = field.fieldname or frappe.scrub(field.label or field.field_type)
		value = data.get(key)

		if field.required and (value is None or str(value).strip() == ""):
			errors.append(f"{field.label or key} is required.")
			continue

		if value in (None, ""):
			continue

		value = str(value).strip()
		ftype = field.field_type

		if ftype == "Email" and not EMAIL_RE.match(value):
			errors.append(f"{field.label or key} must be a valid email.")
			continue

		if ftype == "URL" and not value.startswith(("http://", "https://")):
			errors.append(f"{field.label or key} must be a valid URL.")
			continue

		if ftype == "Number" or ftype == "Currency":
			try:
				value = float(value)
			except ValueError:
				errors.append(f"{field.label or key} must be a number.")
				continue

		if ftype == "Phone" and len(re.sub(r"\D", "", value)) < 7:
			errors.append(f"{field.label or key} must be a valid phone number.")
			continue

		cleaned[key] = value

	return cleaned, errors
