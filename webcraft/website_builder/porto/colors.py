# Copyright (c) 2026, WebCraft Team and contributors
"""Extract theme tokens from Porto skin CSS files."""

from __future__ import annotations

import re
from pathlib import Path

from webcraft.website_builder.porto.config import get_bundle_root


def extract_skin_colors(demo_folder: str) -> dict[str, str]:
	"""Parse primary/secondary/accent from skin-{demo}.css."""
	skin_path = get_bundle_root() / "css" / "skins" / f"skin-{demo_folder}.css"
	if not skin_path.exists():
		return {
			"primary_color": "#2563eb",
			"secondary_color": "#1e40af",
			"accent_color": "#f59e0b",
		}

	text = skin_path.read_text(encoding="utf-8", errors="ignore")
	colors: dict[str, str] = {}

	primary = re.search(r"html \.text-color-primary[^\{]*\{[^}]*color:\s*(#[0-9a-fA-F]{3,8})", text)
	secondary = re.search(r"html \.text-color-secondary[^\{]*\{[^}]*color:\s*(#[0-9a-fA-F]{3,8})", text)
	tertiary = re.search(r"html \.text-color-tertiary[^\{]*\{[^}]*color:\s*(#[0-9a-fA-F]{3,8})", text)
	dark = re.search(r"html \.text-color-dark[^\{]*\{[^}]*color:\s*(#[0-9a-fA-F]{3,8})", text)

	if primary:
		colors["primary_color"] = primary.group(1)
	if secondary:
		colors["secondary_color"] = secondary.group(1)
	if tertiary:
		colors["accent_color"] = tertiary.group(1)
	if dark:
		colors["text_color"] = dark.group(1)

	return colors
