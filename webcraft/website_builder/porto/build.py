# Copyright (c) 2026, WebCraft Team and contributors
"""Build WebCraft templates from Porto demo bundles."""

from __future__ import annotations

import json
from pathlib import Path

import frappe

from webcraft.website_builder.installer import get_templates_root, sync_template_records
from webcraft.website_builder.porto.assets import copy_demo_assets
from webcraft.website_builder.porto.colors import extract_skin_colors
from webcraft.website_builder.porto.config import DEMO_REGISTRY, template_asset_url


def _asset(template_key: str, *parts: str) -> str:
	return template_asset_url(template_key, *parts)


def _dish(name: str, description: str, price: str, product_num: int, template_key: str) -> dict:
	return {
		"name": name,
		"description": description,
		"price": price,
		"image": _asset(template_key, f"products/product-{product_num}.jpg"),
	}


def _menu_item(name: str, description: str, price: str) -> dict:
	return {"name": name, "description": description, "price": price}


_PORTO_LOREM_BANNER = (
	"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eu pulvinar magna."
	"<br>Lorem ipsum dolor sit amet, consectetur adipiscing elit..."
)
_PORTO_LOREM_SECTION = _PORTO_LOREM_BANNER
_PORTO_LOREM_CARD = (
	"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eu pulvinar magna. "
	"Lorem ipsum dolor sit amet, consectetur adipiscing elit..."
)
_PORTO_LOREM_BLOG = (
	"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eu pulvinar magna. Lorem ipsum dolor..."
)
_PORTO_LOREM_PRESS = (
	"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eu pulvinar magna. "
	"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem donec eu pulvinar magna. "
	"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, "
	"consectetur adipiscing elit. Donec eu pulvinar magna. Lorem ipsum dolor sit amet, consectetur adipiscing elit..."
)


def _porto_footer() -> dict:
	return {
		"type": "footer",
		"content": {
			"layout": "porto",
			"address": "1234 Street Name, City Name",
			"phone": "(800) 123-4567",
			"email": "mail@example.com",
			"copyright": "© Copyright 2020. All Rights Reserved.",
			"social_links": [
				{"platform": "facebook", "url": "http://www.facebook.com/"},
				{"platform": "twitter", "url": "http://www.twitter.com/"},
				{"platform": "linkedin", "url": "http://www.linkedin.com/"},
			],
		},
	}


def _porto_special_menu(a) -> dict:
	return {
		"type": "features",
		"content": {
			"layout": "porto-special-menu",
			"title": "Special <strong>Menu</strong>",
			"subtitle": _PORTO_LOREM_SECTION,
			"show_divider": True,
			"background_image": a("background-restaurant.png"),
			"button_label": "Full Menu",
			"button_url": "/restaurant/menu",
			"items": [
				{
					"title": "Monday <em>Special</em>",
					"description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eu pulvinar magna.",
					"image": a("products/product-1.jpg"),
					"icon": "$29",
				},
				{
					"title": "Tuesday <em>Special</em>",
					"description": "Lorem ipsum dolor sit amet. Donec eu pulvinar magna.",
					"image": a("products/product-2.jpg"),
					"icon": "$39",
				},
				{
					"title": "Wednesday <em>Special</em>",
					"description": "Lorem ipsum dolor sit amet.",
					"image": a("products/product-3.jpg"),
					"icon": "$24",
				},
				{
					"title": "Thursday <em>Special</em>",
					"description": "Lorem ipsum dolor sit amet magna.",
					"image": a("products/product-4.jpg"),
					"icon": "$39",
				},
				{
					"title": "Friday <em>Special</em>",
					"description": "Lorem ipsum dolor sit amet adipiscing elit. Donec eu pulvinar magna.",
					"image": a("products/product-5.jpg"),
					"icon": "$59",
				},
			],
		},
	}


def _porto_menu_tabs() -> list[dict]:
	lunch_starters = [
		_menu_item("Consectetur Adipiscing", "Lorem, ipsum sit, amet.", "$9"),
		_menu_item("Adipiscing", "Lorem, dolor sit, amet.", "$10"),
		_menu_item("Pulvinar Magna", "Lorem, ipsum, dolor sit.", "$12"),
	]
	lunch_appetizers = [
		_menu_item("Feugiat Nibh", "Lorem, ipsum, dolor sit, amet.", "$8"),
		_menu_item("Feugiat", "Lorem, ipsum, dolor sit, amet.", "$9"),
		_menu_item("Nibh", "Lorem, ipsum, dolor sit, amet.", "$12"),
	]
	lunch_mains = [
		_menu_item("Vestibulum", "Ipsum, dolor sit, amet.", "$18"),
		_menu_item("Curabitur Pellentesque", "Lorem, ipsum sit, amet.", "$20"),
		_menu_item("Pellentesque", "Lorem, dolor sit, amet.", "$23"),
	]
	lunch_dessert = [
		_menu_item("Sit Folor", "Folor sit, amet.", "$9"),
		_menu_item("Color", "Color sit, amet.", "$10"),
		_menu_item("Light Amet", "Amet.", "$12"),
	]
	dinner_starters = [
		_menu_item("Lorem Ipsum", "Lorem, ipsum, dolor sit, amet.", "$5"),
		_menu_item("Dolor Sit", "Lorem, ipsum, dolor sit.", "$7"),
		_menu_item("Amet", "Lorem, ipsum sit, amet.", "$8"),
		_menu_item("Consectetur Adipiscing", "Lorem, ipsum sit, amet.", "$9"),
		_menu_item("Adipiscing", "Lorem, dolor sit, amet.", "$10"),
		_menu_item("Pulvinar Magna", "Lorem, ipsum, dolor sit.", "$12"),
	]
	drinks_row = [
		_menu_item("Consectetur Adipiscing", "Lorem, ipsum sit, amet.", "$9"),
		_menu_item("Adipiscing", "Lorem, dolor sit, amet.", "$10"),
		_menu_item("Pulvinar Magna", "Lorem, ipsum, dolor sit.", "$12"),
	]
	drinks_beer = [
		_menu_item("Feugiat Nibh", "Lorem, ipsum, dolor sit, amet.", "$8"),
		_menu_item("Feugiat", "Lorem, ipsum, dolor sit, amet.", "$9"),
		_menu_item("Nibh", "Lorem, ipsum, dolor sit, amet.", "$12"),
	]
	return [
		{
			"name": "Lunch",
			"categories": [
				{"name": "STARTERS", "items": lunch_starters},
				{"name": "APPETIZERS", "items": lunch_appetizers},
				{"name": "MAINS", "items": lunch_mains},
				{"name": "DESSERT", "items": lunch_dessert},
			],
		},
		{
			"name": "Dinner",
			"categories": [
				{"name": "STARTERS", "items": dinner_starters},
				{"name": "APPETIZERS", "items": lunch_appetizers},
				{"name": "ENTREES", "items": lunch_mains},
				{"name": "DESSERT", "items": lunch_dessert},
			],
		},
		{
			"name": "Drinks",
			"categories": [
				{"name": "COCKTAILS", "items": drinks_row},
				{"name": "BEER", "items": drinks_beer},
				{"name": "WINE", "items": drinks_beer},
			],
		},
	]


def _restaurant_manifest() -> dict:
	p = "restaurant"
	key = DEMO_REGISTRY[p]["key"]
	a = lambda *path: _asset(key, *path)
	d = lambda name, desc, price, num: _dish(name, desc, price, num, key)
	colors = extract_skin_colors(p)

	header = {
		"type": "header",
		"content": {
			"layout": "porto",
			"logo_text": "The Porto",
			"logo_image": a("logo-restaurant.png"),
			"top_bar_text": "The best place to eat in downtown Porto!",
			"phone": "123-456-7890",
		},
	}
	footer = _porto_footer()

	return {
		"key": "porto-restaurant",
		"title": "Porto Restaurant",
		"description": "Warm restaurant template imported from Porto — food menu, gallery, team, and reservations.",
		"category": "Restaurant",
		"version": "1.0.0",
		"route_prefix": "restaurant",
		"preview_image": a("slides/slide-restaurant-1.jpg"),
		"features": ["Hero", "Menu", "Gallery", "Team", "Testimonials", "Contact"],
		"porto": {"demo": p, "source": "themeforest-E1JFLFmv-porto-responsive-html5-template"},
		"theme": {
			"theme_name": "Porto Restaurant",
			"primary_color": colors.get("primary_color", "#e09b23"),
			"secondary_color": colors.get("secondary_color", "#344257"),
			"accent_color": colors.get("accent_color", "#D1E7E7"),
			"background_color": "#ffffff",
			"text_color": colors.get("text_color", "#212529"),
			"surface_color": "#fafafa",
			"font_family": "\"Open Sans\", Arial, sans-serif",
			"heading_font": "\"Open Sans\", Arial, sans-serif",
			"border_radius": 4,
			"animations_enabled": 1,
			"template_stylesheet": "/assets/webcraft/css/templates/porto-restaurant.css",
			"template_script": "/assets/webcraft/js/porto-restaurant.js",
			"google_fonts_url": "https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700;800&family=Shadows+Into+Light&display=swap",
			"icon_stylesheet": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css",
			"custom_css": "",
		},
		"pages": [
			{
				"title": "Home",
				"slug": "",
				"is_homepage": True,
				"seo": {
					"title": "The Porto Restaurant",
					"description": "The best place to eat in downtown Porto.",
				},
				"sections": [
					header,
					{
						"type": "hero",
						"content": {
							"layout": "slider",
							"slides": [
								{
									"eyebrow": "WELCOME TO",
									"title": "THE PORTO",
									"subtitle": "The best place to eat in downtown Porto!",
									"button_label": "Our Menu",
									"button_url": "/restaurant/menu",
									"image": a("slides/slide-restaurant-1.jpg"),
									"title_border_image": a("slide-title-border.png"),
								},
								{
									"eyebrow": "Best ingredients, fresh prepared!",
									"title": "DELICIOUS!!!",
									"subtitle": "The best place to eat in downtown Porto!",
									"image": a("slides/slide-restaurant-2.jpg"),
									"title_border_image": a("slide-title-border.png"),
								},
							],
						},
					},
					{
						"type": "features",
						"content": {
							"layout": "porto-thumb",
							"title": "Enjoy <strong>Your Meal</strong>",
							"subtitle": _PORTO_LOREM_SECTION,
							"show_divider": True,
							"items": [
								{
									"title": "Sweets",
									"description": _PORTO_LOREM_CARD,
									"icon": a("icons/restaurant-icon-1.png"),
									"image": a("blog/blog-restaurant-1.png"),
									"button_label": "View More",
									"button_url": "/restaurant/menu",
								},
								{
									"title": "Coffee & Beer",
									"description": _PORTO_LOREM_CARD,
									"icon": a("icons/restaurant-icon-2.png"),
									"image": a("blog/blog-restaurant-2.png"),
									"button_label": "View More",
									"button_url": "/restaurant/menu",
								},
								{
									"title": "Cake & Cookies",
									"description": _PORTO_LOREM_CARD,
									"icon": a("icons/restaurant-icon-3.png"),
									"image": a("blog/blog-restaurant-3.png"),
									"button_label": "View More",
									"button_url": "/restaurant/menu",
								},
							],
						},
					},
					{
						"type": "testimonials",
						"content": {
							"layout": "porto",
							"show_divider": True,
							"background_image": a("parallax-restaurant.jpg"),
							"items": [
								{
									"quote": "The best place in town! Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed eget risus porta, tincidunt turpis at, interdum tortor. Suspendisse potenti. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Fusce ante tellus, convallis non consectetur sed, pharetra nec ex.",
									"author": "John Smith",
									"role": "Porto Magazine",
								},
								{
									"quote": "Best place to eat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed eget risus porta, tincidunt turpis at, interdum tortor. Suspendisse potenti. Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
									"author": "John Smith",
									"role": "Porto Magazine",
								},
							],
						},
					},
					{
						"type": "gallery",
						"content": {
							"layout": "porto",
							"title": "Our <strong>Gallery</strong>",
							"subtitle": _PORTO_LOREM_SECTION,
							"show_divider": True,
							"images": [
								{"url": a("gallery/restaurant-gallery-1.jpg")},
								{"url": a("gallery/restaurant-gallery-2.jpg")},
								{"url": a("gallery/restaurant-gallery-4.jpg")},
								{"url": a("gallery/restaurant-gallery-3.jpg")},
								{"url": a("gallery/restaurant-gallery-5.jpg")},
							],
						},
					},
					{
						"type": "porto_blog_team",
						"content": {
							"blog": {
								"title": "Our <strong>Blog</strong>",
								"subtitle": "Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
								"show_divider": True,
								"posts": [
									{
										"title": "Lorem ipsum dolor sit",
										"excerpt": _PORTO_LOREM_BLOG,
										"image": a("blog/blog-restaurant-4.jpg"),
										"button_label": "Read More",
										"url": "/restaurant/press",
									},
									{
										"title": "Lorem ipsum dolor sit",
										"excerpt": _PORTO_LOREM_BLOG,
										"image": a("blog/blog-restaurant-5.jpg"),
										"button_label": "Read More",
										"url": "/restaurant/press",
									},
									{
										"title": "Lorem ipsum dolor sit",
										"excerpt": _PORTO_LOREM_BLOG,
										"image": a("blog/blog-restaurant-6.jpg"),
										"button_label": "Read More",
										"url": "/restaurant/press",
									},
								],
							},
							"team": {
								"title": "Our <strong>Team</strong>",
								"subtitle": "Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
								"show_divider": True,
								"members": [
									{"name": "Jessica Doe", "role": "Chef", "photo": a("team-26.jpg")},
									{"name": "John Doe", "role": "Chef", "photo": a("team-27.jpg")},
									{"name": "Angelina Doe", "role": "Chef", "photo": a("team-28.jpg")},
								],
							},
						},
					},
					_porto_special_menu(a),
					footer,
				],
			},
			{
				"title": "Menu",
				"slug": "menu",
				"seo": {"title": "Menu | The Porto", "description": "Food and drink menu."},
				"sections": [
					header,
					{
						"type": "page_banner",
						"content": {
							"layout": "simple",
							"title": "Food <strong>&amp; </strong> Drink",
							"subtitle": _PORTO_LOREM_BANNER,
							"show_divider": True,
						},
					},
					{
						"type": "menu_list",
						"content": {
							"tabs": _porto_menu_tabs(),
						},
					},
					{
						"type": "features",
						"content": {
							"layout": "porto-special-menu",
							"title": "Special <strong>Menu</strong>",
							"subtitle": _PORTO_LOREM_SECTION,
							"show_divider": True,
							"items": _porto_special_menu(a)["content"]["items"],
						},
					},
					footer,
				],
			},
			{
				"title": "About",
				"slug": "about",
				"sections": [
					header,
					{
						"type": "page_banner",
						"content": {
							"layout": "parallax",
							"title": "The <strong>Restaurant</strong>",
							"background_image": a("parallax-restaurant-2.jpg"),
						},
					},
					{
						"type": "text",
						"content": {
							"layout": "porto-about",
							"title": "The best place to eat in downtown Porto!",
							"image": a("gallery/restaurant-gallery-3.jpg"),
							"image_float": "left",
							"body": (
								'<p class="lead">Gravida nibh vel velit auctor aliquet. Aenean sollicitudin, lorem quis bibendum auctor, '
								"nisi elit consequat ipsum, nec sagittis sem nibh id elit. Duis sed odio sit amet nibh vulputate cursus a sit "
								"amet mauris. Morbi accumsan ipsum velit. Nam nec tellus a odio tincidunt auctor a ornare odio. Sed non  "
								"mauris vitae erat consequat.</p>"
								"<p>Lorem quis bibendum auctor, nisi elit consequat ipsum, nec sagittis sem nibh id elit. Duis sed odio sit "
								"amet nibh vulputate cursus a sit amet mauris. Morbi accumsan ipsum velit. Nam nec tellus a odio tincidunt "
								"auctor a ornare odio. Sed non  mauris vitae erat consequat.</p>"
								"<p>Gravida nibh vel velit auctor aliquet. Aenean sollicitudin, lorem quis bibendum auctor, nisi elit consequat "
								"ipsum, nec sagittis sem nibh id elit. Duis sed odio sit amet nibh vulputate cursus a sit amet mauris. Gravida "
								"nibh vel velit auctor aliquet. Aenean sollicitudin, lorem quis bibendum auctor, nisi elit consequat ipsum, "
								"nec sagittis sem nibh id elit. Duis sed odio sit amet nibh vulputate cursus a sit amet mauris.</p>"
								"<p>Gravida nibh vel velit auctor aliquet. Aenean sollicitudin, lorem quis bibendum auctor, nisi elit consequat "
								"ipsum, nec sagittis sem nibh id elit. Duis sed odio sit amet nibh vulputate cursus a sit amet mauris. Morbi "
								"accumsan ipsum velit. Nam nec tellus a odio tincidunt auctor.</p>"
							),
						},
					},
					{
						"type": "contact",
						"content": {
							"layout": "porto-about",
							"title": "Get in <strong>Touch</strong>",
							"subtitle": _PORTO_LOREM_SECTION,
							"show_divider": True,
							"info_blocks": [
								{"title": "Book Now", "phone": "(123) 456-789"},
								{"title": "Visit Us", "address": "123 Street Name, Porto"},
							],
						},
					},
					footer,
				],
			},
			{
				"title": "Press",
				"slug": "press",
				"sections": [
					header,
					{
						"type": "page_banner",
						"content": {
							"layout": "simple",
							"title": "Press <strong>&amp; </strong> Events",
							"subtitle": _PORTO_LOREM_BANNER,
							"show_divider": True,
						},
					},
					{
						"type": "features",
						"content": {
							"layout": "porto-press",
							"items": [
								{
									"title": "Lorem ipsum dolor sit",
									"date": "January 10, 2020",
									"author": "John Doe",
									"description": _PORTO_LOREM_PRESS,
									"image": a("blog/blog-restaurant-4.jpg"),
									"button_label": "Read More",
									"url": "/restaurant/press",
								},
								{
									"title": "Lorem ipsum dolor sit",
									"date": "January 10, 2020",
									"author": "John Doe",
									"description": _PORTO_LOREM_PRESS,
									"image": a("blog/blog-restaurant-5.jpg"),
									"button_label": "Read More",
									"url": "/restaurant/press",
								},
								{
									"title": "Lorem ipsum dolor sit",
									"date": "January 10, 2020",
									"author": "John Doe",
									"description": _PORTO_LOREM_PRESS,
									"image": a("blog/blog-restaurant-6.jpg"),
									"button_label": "Read More",
									"url": "/restaurant/press",
								},
							],
						},
					},
					footer,
				],
			},
			{
				"title": "Contact",
				"slug": "contact",
				"sections": [
					header,
					{
						"type": "page_banner",
						"content": {
							"layout": "simple",
							"title": "Get in <strong>Touch</strong>",
							"subtitle": _PORTO_LOREM_BANNER,
							"show_divider": True,
						},
					},
					{
						"type": "contact",
						"content": {
							"layout": "porto",
							"form_title": "Send a Message",
							"show_map": True,
							"map_link": "http://maps.google.com/",
							"map_embed_url": "https://maps.google.com/maps?q=Porto,+Portugal&z=14&output=embed",
							"info_blocks": [
								{"title": "Book Now", "phone": "(123) 456-789"},
								{"title": "Private Events", "phone": "(123) 456-789"},
								{"title": "Visit Us", "address": "123 Street Name, Porto"},
							],
							"hours": [
								{
									"title": "Lunch Hours",
									"lines": [
										"Monday - Friday - 9am to 5pm",
										"Saturday - 9am to 2pm",
										"Sunday - Closed",
									],
								},
								{
									"title": "Dining Hours",
									"lines": [
										"Monday - Friday - 9am to 5pm",
										"Saturday - 9am to 2pm",
										"Sunday - Closed",
									],
								},
							],
						},
					},
					footer,
				],
			},
		],
		"menus": [
			{
				"name": "Main Navigation",
				"location": "Header",
				"items": [
					{"label": "Home", "page": "Home", "url": "/restaurant"},
					{"label": "Menu", "page": "Menu", "url": "/restaurant/menu"},
					{"label": "About", "page": "About", "url": "/restaurant/about"},
					{"label": "Press", "page": "Press", "url": "/restaurant/press"},
					{"label": "Contact", "page": "Contact", "url": "/restaurant/contact"},
				],
			}
		],
		"assets": [],
	}


def build_porto_demo(demo_folder: str, write_manifest: bool = True) -> dict:
	"""Copy assets and write template.json for a Porto demo."""
	if demo_folder not in DEMO_REGISTRY:
		frappe.throw(f"Porto demo '{demo_folder}' is not registered yet.")

	meta = DEMO_REGISTRY[demo_folder]
	template_key = meta["key"]
	template_dir = get_templates_root() / template_key.replace("porto-", "porto-")
	# folder name matches key: porto-restaurant
	template_dir = get_templates_root() / meta["key"]

	if demo_folder == "restaurant":
		manifest = _restaurant_manifest()
	else:
		frappe.throw(f"Manifest builder for '{demo_folder}' is not implemented yet.")

	assets = copy_demo_assets(demo_folder)
	manifest["assets"] = assets

	if write_manifest:
		template_dir.mkdir(parents=True, exist_ok=True)
		manifest_path = template_dir / "template.json"
		with open(manifest_path, "w", encoding="utf-8") as handle:
			json.dump(manifest, handle, indent="\t", ensure_ascii=False)
			handle.write("\n")

	sync_template_records()
	frappe.db.commit()
	return {
		"template_key": manifest["key"],
		"template_dir": str(template_dir),
		"assets_copied": len(assets),
		"pages": len(manifest.get("pages", [])),
	}


@frappe.whitelist()
def build_porto_template(demo: str = "restaurant") -> dict:
	"""Desk API: build a WebCraft template from a Porto demo folder."""
	if not frappe.has_permission("Website Template", "write"):
		frappe.throw("Not permitted.")
	return build_porto_demo(demo)
