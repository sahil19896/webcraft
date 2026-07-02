# Copyright (c) 2026, WebCraft Team and contributors
"""Paths and demo registry for the Porto HTML bundle."""

from __future__ import annotations

import os
from pathlib import Path

# Bench root: .../frappe-bench
BENCH_ROOT = Path(__file__).resolve().parents[5]
PORTO_BUNDLE_ROOT = BENCH_ROOT / "themeforest-E1JFLFmv-porto-responsive-html5-template" / "HTML"
WEBCRAFT_PUBLIC_ROOT = Path(__file__).resolve().parents[2] / "public"
TEMPLATE_FILES_ROOT = WEBCRAFT_PUBLIC_ROOT / "files"

# WebCraft category per Porto demo folder name (under img/demos/)
DEMO_REGISTRY: dict[str, dict] = {
	"restaurant": {
		"key": "porto-restaurant",
		"title": "Porto Restaurant",
		"category": "Restaurant",
		"route_prefix": "restaurant",
		"description": "Warm restaurant template from Porto — hero, menu, gallery, team, and reservations.",
		"features": ["Hero slider", "Food menu", "Gallery", "Team", "Contact form"],
		"pages": ["Home", "Menu", "About", "Press", "Contact"],
		"home_html": "demo-restaurant.html",
		"fonts": "Open Sans, sans-serif",
		"extra_assets": [
			("img/team/team-26.jpg", "team-26.jpg"),
			("img/team/team-27.jpg", "team-27.jpg"),
			("img/team/team-28.jpg", "team-28.jpg"),
			("img/custom-divider-1.png", "custom-divider-1.png"),
			("img/slides/slide-title-border.png", "slide-title-border.png"),
		],
	},
	# Additional demos will be added here as we batch-import the bundle.
}


def get_bundle_root() -> Path:
	"""Return Porto HTML bundle root, overridable via env."""
	override = os.environ.get("WEBCRAFT_PORTO_BUNDLE")
	if override:
		return Path(override)
	return PORTO_BUNDLE_ROOT


def get_demo_asset_source(demo_folder: str) -> Path:
	return get_bundle_root() / "img" / "demos" / demo_folder


def get_template_key(demo_folder: str) -> str:
	meta = DEMO_REGISTRY.get(demo_folder) or {}
	return meta.get("key") or demo_folder


def get_template_files_dir(template_key: str) -> Path:
	"""Public files directory for a bundled template, e.g. public/files/porto-restaurant."""
	return TEMPLATE_FILES_ROOT / template_key


def template_asset_url(template_key: str, *parts: str) -> str:
	"""Public URL for a file under public/files/{template_key}/."""
	return f"/assets/webcraft/files/{template_key}/{'/'.join(parts)}"


def get_demo_public_dir(demo_folder: str) -> Path:
	"""Target directory when importing a Porto demo into WebCraft public files."""
	return get_template_files_dir(get_template_key(demo_folder))
