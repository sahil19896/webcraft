# Copyright (c) 2026, WebCraft Team and contributors
"""Copy Porto demo assets into WebCraft public files."""

from __future__ import annotations

import shutil
from pathlib import Path

from webcraft.website_builder.porto.config import (
	DEMO_REGISTRY,
	WEBCRAFT_PUBLIC_ROOT,
	get_bundle_root,
	get_demo_asset_source,
	get_demo_public_dir,
	get_template_key,
)


def copy_demo_assets(demo_folder: str) -> list[str]:
	"""Copy img/demos/{demo} into public/files/{template_key}. Returns asset URLs."""
	source = get_demo_asset_source(demo_folder)
	if not source.exists():
		raise FileNotFoundError(f"Porto demo assets not found: {source}")

	target = get_demo_public_dir(demo_folder)
	if target.exists():
		shutil.rmtree(target)
	shutil.copytree(source, target)

	meta = DEMO_REGISTRY.get(demo_folder) or {}
	for rel_src, rel_dest in meta.get("extra_assets") or []:
		src = get_bundle_root() / rel_src
		if not src.is_file():
			continue
		dest = target / rel_dest
		dest.parent.mkdir(parents=True, exist_ok=True)
		shutil.copy2(src, dest)

	template_key = get_template_key(demo_folder)
	copied = []
	for path in sorted(target.rglob("*")):
		if path.is_file():
			rel = path.relative_to(WEBCRAFT_PUBLIC_ROOT)
			copied.append(f"/assets/webcraft/{rel.as_posix()}")

	return copied
