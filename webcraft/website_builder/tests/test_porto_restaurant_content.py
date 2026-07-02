"""Porto Restaurant content parity tests against the ThemeForest demo."""

from __future__ import annotations

import frappe
import requests

from webcraft.website_builder.installer import load_template_manifest

TEMPLATE_KEY = "porto-restaurant"
MARKERS = {
	"home": [
		"WELCOME TO",
		"THE PORTO",
		"Enjoy <strong>Your Meal</strong>",
		"Our <strong>Gallery</strong>",
		"Our <strong>Blog</strong>",
		"Our <strong>Team</strong>",
		"Special <strong>Menu</strong>",
		"Monday <em>Special</em>",
		"© Copyright 2020. All Rights Reserved.",
	],
	"menu": [
		"Food <strong>&amp; </strong> Drink",
		"STARTERS",
		"APPETIZERS",
		"DESSERT",
		"Sit Folor",
		"Light Amet",
		"Dinner",
		"Drinks",
		"COCKTAILS",
		"WINE",
	],
	"about": [
		"The <strong>Restaurant</strong>",
		"Gravida nibh vel velit auctor aliquet",
		"Get in <strong>Touch</strong>",
		"Book Now",
		"123 Street Name, Porto",
	],
	"press": [
		"Press <strong>&amp; </strong> Events",
		"January 10, 2020",
		"John Doe",
		"Read More",
	],
	"contact": [
		"Get in <strong>Touch</strong>",
		"Private Events",
		"Lunch Hours",
		"Dining Hours",
		"Send a Message",
		"Sunday - Closed",
		"fa-phone",
		"fa-map-marker-alt",
		"fa-clock",
		"(Get Directions)",
	],
}


def _header(title: str) -> None:
	print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def _ok(label: str, passed: bool, detail: str = "") -> bool:
	status = "PASS" if passed else "FAIL"
	line = f"[{status}] {label}"
	if detail:
		line += f" — {detail}"
	print(line)
	return passed


def _base_url() -> str:
	port = frappe.conf.http_port or 8000
	return f"http://127.0.0.1:{port}"


def _fetch(path: str) -> tuple[int, str]:
	url = f"{_base_url()}{path}"
	headers = {"Host": frappe.local.site}
	try:
		resp = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
		return resp.status_code, resp.text
	except requests.RequestException as exc:
		return 0, str(exc)


def run():
	results: list[bool] = []
	manifest = load_template_manifest(TEMPLATE_KEY)
	pages = {}
	for page in manifest.get("pages") or []:
		key = "home" if page.get("is_homepage") or page.get("slug") in (None, "") else page.get("slug")
		pages[key] = page

	_header("A — Manifest structure")
	home = pages.get("home") or pages.get("")
	home_sections = [s.get("type") for s in (home or {}).get("sections") or []]
	results.append(_ok("Home includes porto_blog_team section", "porto_blog_team" in home_sections))
	results.append(_ok("Home excludes generic CTA section", "cta" not in home_sections))
	results.append(_ok("Menu page defines Lunch/Dinner/Drinks tabs", bool((pages.get("menu") or {}).get("sections"))))

	menu_section = next(
		(s for s in (pages.get("menu") or {}).get("sections") or [] if s.get("type") == "menu_list"),
		{},
	)
	tab_names = [t.get("name") for t in (menu_section.get("content") or {}).get("tabs") or []]
	results.append(_ok("Menu tabs match Porto demo", tab_names == ["Lunch", "Dinner", "Drinks"], str(tab_names)))

	footer = next((s for s in (home or {}).get("sections") or [] if s.get("type") == "footer"), {})
	results.append(
		_ok(
			"Footer uses Porto 2020 copyright",
			(footer.get("content") or {}).get("copyright") == "© Copyright 2020. All Rights Reserved.",
		)
	)

	_header("B — HTTP preview content markers")
	for slug, markers in MARKERS.items():
		path = f"/webcraft-preview/{TEMPLATE_KEY}" if slug == "home" else f"/webcraft-preview/{TEMPLATE_KEY}/{slug}"
		code, body = _fetch(path)
		results.append(_ok(f"{slug.title()} preview returns 200", code == 200, f"HTTP {code}"))
		if code != 200:
			continue
		for marker in markers:
			results.append(_ok(f"{slug.title()} contains `{marker[:40]}`", marker in body, marker[:60]))

	_header("SUMMARY")
	passed = sum(results)
	total = len(results)
	print(f"\n{passed}/{total} Porto content checks passed")
	if passed != total:
		raise Exception(f"Porto Restaurant content tests failed: {total - passed} failing checks")


if __name__ == "__main__":
	run()
