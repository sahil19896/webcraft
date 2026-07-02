"""Porto Restaurant theme fidelity tests (fonts, animations, assets)."""

from __future__ import annotations

from pathlib import Path

import frappe
import requests

from webcraft.website_builder.installer import load_template_manifest
from webcraft.website_builder.preview import get_preview_context
from webcraft.website_builder.template_render import get_template_render_extras

TEMPLATE_KEY = "porto-restaurant"
WEBCRAFT_ROOT = Path(__file__).resolve().parents[2]


def _header(title: str) -> None:
	print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def _ok(label: str, passed: bool, detail: str = "") -> bool:
	status = "PASS" if passed else "FAIL"
	line = f"[{status}] {label}"
	if detail:
		line += f" — {detail}"
	print(line)
	return passed


def _manifest() -> dict:
	return load_template_manifest(TEMPLATE_KEY)


def _css_text() -> str:
	path = WEBCRAFT_ROOT / "public" / "css" / "templates" / "porto-restaurant.css"
	return path.read_text(encoding="utf-8")


def _js_text() -> str:
	path = WEBCRAFT_ROOT / "public" / "js" / "porto-restaurant.js"
	return path.read_text(encoding="utf-8")


def _render_home_hero() -> str:
	from webcraft.website_builder.preview import _sections_from_page_def

	manifest = _manifest()
	page = next(p for p in manifest["pages"] if p.get("is_homepage"))
	route_prefix = manifest.get("route_prefix") or "restaurant"
	sections = _sections_from_page_def(page, route_prefix, TEMPLATE_KEY)
	hero = next(s for s in sections if s.get("type") == "hero")
	return frappe.render_template(
		"templates/sections/hero.html",
		{"content": hero.get("content") or {}, "section_id": hero.get("id")},
	)


def _base_url() -> str:
	port = frappe.conf.http_port or 8000
	return f"http://127.0.0.1:{port}"


def _fetch_preview() -> tuple[int, str]:
	url = f"{_base_url()}/webcraft-preview/{TEMPLATE_KEY}"
	headers = {"Host": frappe.local.site}
	try:
		resp = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
		return resp.status_code, resp.text
	except requests.RequestException as exc:
		return 0, str(exc)


def run():
	results: list[bool] = []
	manifest = _manifest()
	theme = manifest.get("theme") or {}
	css = _css_text()
	js = _js_text()
	extras = get_template_render_extras(TEMPLATE_KEY)
	preview = get_preview_context(TEMPLATE_KEY)

	_header("A — Manifest fonts and template assets")
	fonts_url = theme.get("google_fonts_url") or ""
	results.append(_ok("Google Fonts URL includes Open Sans", "Open+Sans" in fonts_url, fonts_url))
	results.append(_ok("Google Fonts URL includes Shadows Into Light", "Shadows+Into+Light" in fonts_url, fonts_url))
	results.append(
		_ok(
			"Theme font_family quotes Open Sans",
			'"Open Sans"' in (theme.get("font_family") or ""),
			theme.get("font_family"),
		)
	)
	results.append(
		_ok(
			"template_script points to porto-restaurant.js",
			theme.get("template_script", "").endswith("porto-restaurant.js"),
			theme.get("template_script"),
		)
	)

	_header("B — Render context wiring")
	results.append(_ok("template_skin_class is Porto scoped", extras.get("template_skin_class") == f"wc-template-{TEMPLATE_KEY}"))
	results.append(_ok("Preview context exposes template_script", bool(preview.get("template_script"))))
	results.append(_ok("Preview context exposes google_fonts_url", "Shadows+Into+Light" in (preview.get("google_fonts_url") or "")))
	results.append(_ok("Preview context exposes icon_stylesheet", bool(preview.get("icon_stylesheet"))))

	_header("C — CSS animation keyframes and font overrides")
	for keyframe in (
		"fadeInDownShorterPlus",
		"fadeInLeftShorter",
		"fadeInUpShorter",
		"blurIn",
		"fadeIn",
	):
		results.append(_ok(f"CSS defines @keyframes {keyframe}", f"@keyframes {keyframe}" in css))
	results.append(_ok("CSS forces Open Sans on body", '"Open Sans"' in css and "!important" in css))
	results.append(_ok("CSS defines .alternative-font display face", ".alternative-font" in css and "--porto-display" in css))
	results.append(_ok("CSS defines Porto quaternary/tertiary section colors", "--porto-quaternary" in css and "--porto-tertiary" in css))
	results.append(_ok("CSS defines team caption card styling", ".wc-porto-team-card__caption" in css))
	results.append(_ok("CSS defines gallery masonry layout", ".wc-gallery--porto .wc-gallery__item:nth-child(2)" in css))

	_header("D — Section markup uses Porto appear attributes")
	hero_html = _render_home_hero()
	results.append(_ok("Hero slider renders data-wc-hero-slider", "data-wc-hero-slider" in hero_html))
	results.append(_ok("Hero eyebrow uses alternative-font", "alternative-font" in hero_html))
	results.append(_ok("Hero title uses blurIn appear", 'data-wc-appear="blurIn"' in hero_html))
	results.append(_ok("Hero subtitle uses fadeInUpShorter appear", 'data-wc-appear="fadeInUpShorter"' in hero_html))

	features_html = frappe.render_template(
		"templates/sections/features.html",
		{
			"content": {
				"layout": "porto-thumb",
				"title": "Test",
				"items": [{"title": "A", "description": "B"}],
			},
			"section_id": "test-features",
		},
	)
	results.append(_ok("Features porto-thumb uses data-wc-appear", "data-wc-appear" in features_html))
	results.append(_ok("Features porto-thumb avoids wc-animate class", "wc-animate" not in features_html))

	_header("E — Porto JS bootstrap")
	results.append(_ok("porto-restaurant.js defines appear runner", "runAppear" in js and "data-wc-appear" in js))
	results.append(_ok("porto-restaurant.js replays hero slide animations", "animateHeroSlide" in js))
	results.append(_ok("webcraft.js skips generic animations on Porto", "wc-template-porto-restaurant" in (WEBCRAFT_ROOT / "public" / "js" / "webcraft.js").read_text(encoding="utf-8")))

	_header("F — HTTP preview includes theme assets")
	code, body = _fetch_preview()
	results.append(_ok("Preview returns HTTP 200", code == 200, f"HTTP {code}"))
	if code == 200:
		results.append(_ok("Preview body has Porto skin class", "wc-template-porto-restaurant" in body))
		results.append(_ok("Preview loads Porto stylesheet", "porto-restaurant.css" in body))
		results.append(_ok("Preview loads Porto script", "porto-restaurant.js" in body))
		results.append(_ok("Preview loads Shadows Into Light font", "Shadows+Into+Light" in body or "Shadows Into Light" in body))
		results.append(_ok("Preview hero has data-wc-appear", "data-wc-appear" in body))

	_header("SUMMARY")
	passed = sum(results)
	total = len(results)
	print(f"\n{passed}/{total} Porto theme checks passed")
	if passed != total:
		raise Exception(f"Porto Restaurant theme tests failed: {total - passed} failing checks")


if __name__ == "__main__":
	run()
