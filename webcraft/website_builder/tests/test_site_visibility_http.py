"""HTTP-level tests for WebCraft public route access."""

from __future__ import annotations

import time

import frappe
import requests

from webcraft.website_builder.access import sync_project_pages_published
from webcraft.website_builder.deploy import publish_project


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
		resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
		body = resp.text[:500].lower()
		return resp.status_code, body
	except requests.RequestException as exc:
		return 0, str(exc).lower()


def _looks_like_webcraft_page(body: str) -> bool:
	markers = ("wc-page", "wc-header", "wc-body", "webcraft", "kick store", "store")
	return any(marker in body for marker in markers)


def _deactivate_via_form(project: str) -> None:
	doc = frappe.get_doc("Website Project", project)
	doc.is_active = 0
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	time.sleep(0.3)


def run():
	results: list[bool] = []
	project = frappe.db.get_value("Website Project", {}, "name")
	if not project:
		print("No Website Project found.")
		return

	homepage = frappe.db.get_value("Website Project", project, "homepage")
	route = frappe.db.get_value("Website Page", homepage, "route") if homepage else None
	if not route:
		print("No homepage route found.")
		return

	path = f"/{route}"
	base = _base_url()
	print(f"Testing public HTTP at {base}{path} (project: {project})")

	_header("HTTP A — inactive project returns not found")
	frappe.db.set_value("Website Project", project, {"is_active": 0, "status": "Draft"}, update_modified=False)
	frappe.db.commit()
	sync_project_pages_published(project)
	time.sleep(0.3)

	code, body = _fetch(path)
	results.append(
		_ok(
			"Inactive site not served as live WebCraft page",
			code in (404, 403) or (code == 200 and not _looks_like_webcraft_page(body)),
			f"HTTP {code}",
		)
	)

	_header("HTTP B — published + active site is reachable")
	publish_project(project)
	frappe.db.commit()
	time.sleep(0.3)

	code, body = _fetch(path)
	results.append(
		_ok(
			"Live site returns 200 with WebCraft content",
			code == 200 and _looks_like_webcraft_page(body),
			f"HTTP {code}",
		)
	)

	_header("HTTP C — deactivating via form save hides site")
	_deactivate_via_form(project)
	sync_project_pages_published(project)

	code, body = _fetch(path)
	results.append(
		_ok(
			"Deactivated site not served as live WebCraft page",
			code in (404, 403) or (code == 200 and not _looks_like_webcraft_page(body)),
			f"HTTP {code}",
		)
	)

	_header("HTTP D — commerce product route blocked when inactive")
	product_path = f"/{route.split('/')[0]}/product/test-item"
	code, body = _fetch(product_path)
	results.append(
		_ok(
			"Inactive commerce route not served",
			code in (404, 403) or not _looks_like_webcraft_page(body),
			f"HTTP {code} for {product_path}",
		)
	)

	frappe.db.set_value("Website Project", project, {"is_active": 0, "status": "Draft"}, update_modified=False)
	frappe.db.commit()
	sync_project_pages_published(project)

	_header("SUMMARY")
	passed = sum(results)
	total = len(results)
	print(f"\n{passed}/{total} HTTP checks passed")
	if passed != total:
		raise Exception(f"WebCraft HTTP tests failed: {total - passed} failing checks")


if __name__ == "__main__":
	run()
