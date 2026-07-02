app_name = "webcraft"
app_title = "WebCraft"
app_publisher = "WebCraft Team"
app_description = "Pre-built website designs for Frappe — browse, preview, and publish."
app_email = "contact@webcraft.local"
app_license = "mit"

add_to_apps_screen = [
	{
		"name": "webcraft",
		"logo": "/assets/webcraft/images/webcraft-logo.svg",
		"title": "WebCraft",
		"route": "/app/webcraft",
		"has_permission": "webcraft.website_builder.api.has_app_permission",
	}
]

web_include_css = "/assets/webcraft/css/webcraft.css"
web_include_js = "/assets/webcraft/js/webcraft.js"

website_generators = ["Website Page"]

website_route_rules = [
	{"from_route": "/webcraft-preview/<template>", "to_route": "webcraft-preview"},
	{"from_route": "/webcraft-preview/<template>/<path:page>", "to_route": "webcraft-preview"},
]

page_renderer = "webcraft.website_builder.commerce.renderer.StoreCommerceRenderer"

after_install = "webcraft.install.after_install"

doctype_js = {
	"Website Project": "public/js/website_project.js",
	"Website Page": "public/js/website_page.js",
}

jinja = {
	"methods": [
		"webcraft.website_builder.forms.renderer.render_form_html",
	],
}
