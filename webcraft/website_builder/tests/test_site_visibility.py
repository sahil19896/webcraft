"""Manual integration tests for WebCraft site visibility rules."""

from __future__ import annotations

import frappe

from webcraft.website_builder.access import deactivate_other_projects, is_project_live, sync_project_pages_published
from webcraft.website_builder.deploy import publish_project, unpublish_project


def _header(title: str) -> None:
	print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def _ok(label: str, passed: bool, detail: str = "") -> bool:
	status = "PASS" if passed else "FAIL"
	line = f"[{status}] {label}"
	if detail:
		line += f" — {detail}"
	print(line)
	return passed


def _page_is_public(page_name: str) -> bool:
	page = frappe.get_doc("Website Page", page_name)
	return page.is_website_published()


def _find_project() -> str | None:
	return frappe.db.get_value("Website Project", {}, "name")


def _homepage_route(project: str) -> str | None:
	homepage = frappe.db.get_value("Website Project", project, "homepage")
	if not homepage:
		return None
	return frappe.db.get_value("Website Page", homepage, "route")


def run():
	results: list[bool] = []
	project = _find_project()
	if not project:
		print("No Website Project found — install a template first.")
		return

	homepage = frappe.db.get_value("Website Project", project, "homepage")
	route = _homepage_route(project)

	_header("1. Inactive project blocks public pages")
	frappe.db.set_value("Website Project", project, {"is_active": 0, "status": "Draft"}, update_modified=False)
	frappe.db.commit()
	sync_project_pages_published(project)
	results.append(_ok("is_project_live is False when inactive", not is_project_live(project)))
	if homepage:
		results.append(
			_ok(
				"Published page hidden when project inactive",
				not _page_is_public(homepage),
				f"page={homepage}",
			)
		)

	_header("2. Active but Draft still blocks public pages")
	frappe.db.set_value("Website Project", project, {"is_active": 1, "status": "Draft"}, update_modified=False)
	frappe.db.commit()
	sync_project_pages_published(project)
	results.append(_ok("is_project_live is False when Draft", not is_project_live(project)))
	if homepage:
		results.append(_ok("Page hidden when project is Draft", not _page_is_public(homepage)))

	_header("3. Publish makes site live")
	publish_project(project)
	frappe.db.commit()
	results.append(_ok("is_project_live is True after publish", is_project_live(project)))
	if homepage:
		results.append(_ok("Homepage is public after publish", _page_is_public(homepage), f"route=/{route}"))

	_header("4. Deactivate hides site from web")
	frappe.db.set_value("Website Project", project, "is_active", 0, update_modified=False)
	frappe.db.commit()
	sync_project_pages_published(project)
	results.append(_ok("is_project_live is False after deactivating", not is_project_live(project)))
	if homepage:
		results.append(_ok("Homepage hidden after deactivating", not _page_is_public(homepage)))

	_header("5. Only one active project at a time")
	# Re-activate original for multi-project test
	frappe.db.set_value("Website Project", project, "is_active", 1, update_modified=False)
	frappe.db.commit()

	second_name = f"{project}-test-copy"
	if frappe.db.exists("Website Project", second_name):
		frappe.delete_doc("Website Project", second_name, force=1, ignore_permissions=True)

	second = frappe.get_doc(
		{
			"doctype": "Website Project",
			"project_name": second_name,
			"status": "Published",
			"is_active": 1,
			"site": frappe.local.site,
		}
	)
	second.insert(ignore_permissions=True)
	frappe.db.commit()

	first_active = frappe.db.get_value("Website Project", project, "is_active")
	second_active = frappe.db.get_value("Website Project", second_name, "is_active")
	results.append(_ok("First project deactivated when second activated", not first_active and bool(second_active)))

	deactivate_other_projects(project)
	frappe.db.set_value("Website Project", project, "is_active", 1, update_modified=False)
	frappe.db.commit()
	second_active_after = frappe.db.get_value("Website Project", second_name, "is_active")
	results.append(_ok("Second project deactivated when first re-activated", not second_active_after))

	frappe.delete_doc("Website Project", second_name, force=1, ignore_permissions=True)
	frappe.db.commit()

	_header("6. Unpublish deactivates project")
	publish_project(project)
	frappe.db.commit()
	unpublish_project(project)
	frappe.db.commit()
	is_active = frappe.db.get_value("Website Project", project, "is_active")
	status = frappe.db.get_value("Website Project", project, "status")
	results.append(
		_ok(
			"Unpublish sets Draft + inactive",
			status == "Draft" and not is_active,
			f"status={status}, is_active={is_active}",
		)
	)
	if homepage:
		results.append(_ok("Homepage not public after unpublish", not _page_is_public(homepage)))

	_header("7. Commerce route resolution respects live status")
	from webcraft.website_builder.commerce.store import find_published_project_by_prefix

	prefix = (route or "store").split("/")[0]
	frappe.db.set_value("Website Project", project, {"is_active": 0, "status": "Published"}, update_modified=False)
	frappe.db.commit()
	results.append(
		_ok(
			"find_published_project_by_prefix returns None when inactive",
			find_published_project_by_prefix(prefix) is None,
			f"prefix={prefix}",
		)
	)

	publish_project(project)
	frappe.db.commit()
	found = find_published_project_by_prefix(prefix)
	results.append(
		_ok(
			"find_published_project_by_prefix finds project when live",
			found is not None and found.get("name") == project,
		)
	)

	# Restore to inactive/draft state (original DB state)
	frappe.db.set_value("Website Project", project, {"is_active": 0, "status": "Draft"}, update_modified=False)
	frappe.db.commit()
	sync_project_pages_published(project)

	_header("SUMMARY")
	passed = sum(results)
	total = len(results)
	print(f"\n{passed}/{total} checks passed")
	if passed != total:
		raise Exception(f"WebCraft visibility tests failed: {total - passed} failing checks")


if __name__ == "__main__":
	run()
