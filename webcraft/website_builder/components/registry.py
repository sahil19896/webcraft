# Copyright (c) 2026, WebCraft Team and contributors
# For license information, please see license.txt

"""Component registry: schemas, defaults, and metadata for section types."""

from __future__ import annotations

COMPONENTS: dict[str, dict] = {
	"header": {
		"label": "Header",
		"category": "Layout",
		"icon": "layout",
		"defaults": {
			"logo_text": "WebCraft",
			"logo_image": "",
			"cta_label": "Get Started",
			"cta_url": "#contact",
			"sticky": True,
		},
	},
	"hero": {
		"label": "Hero",
		"category": "Content",
		"icon": "star",
		"defaults": {
			"title": "Build something remarkable",
			"subtitle": "Create beautiful websites without writing code.",
			"button_label": "Get Started",
			"button_url": "#",
			"secondary_button_label": "Learn More",
			"secondary_button_url": "#",
			"image": "",
			"alignment": "center",
			"overlay": True,
		},
	},
	"features": {
		"label": "Features",
		"category": "Content",
		"icon": "grid",
		"defaults": {
			"title": "Why choose us",
			"subtitle": "Everything you need to launch fast",
			"items": [
				{"title": "Fast Setup", "description": "Launch in minutes", "icon": "zap"},
				{"title": "Fully Customizable", "description": "Edit every section visually", "icon": "edit"},
				{"title": "Built on Frappe", "description": "Enterprise-ready backend", "icon": "shield"},
			],
		},
	},
	"stats": {
		"label": "Statistics",
		"category": "Content",
		"icon": "bar-chart",
		"defaults": {
			"title": "By the numbers",
			"items": [
				{"value": "250+", "label": "Projects launched"},
				{"value": "98%", "label": "Client satisfaction"},
				{"value": "24/7", "label": "Support available"},
			],
		},
	},
	"testimonials": {
		"label": "Testimonials",
		"category": "Social Proof",
		"icon": "message-circle",
		"defaults": {
			"title": "What our clients say",
			"items": [
				{
					"quote": "WebCraft transformed how we launch marketing sites.",
					"author": "Alex Morgan",
					"role": "CEO, Acme Inc",
					"avatar": "",
				}
			],
		},
	},
	"pricing": {
		"label": "Pricing",
		"category": "Commerce",
		"icon": "credit-card",
		"defaults": {
			"title": "Simple pricing",
			"subtitle": "Choose the plan that fits your needs",
			"plans": [
				{
					"name": "Starter",
					"price": "$29",
					"period": "/mo",
					"features": ["1 Website", "5 Pages", "Basic Forms"],
					"cta_label": "Start Free",
					"highlighted": False,
				},
				{
					"name": "Pro",
					"price": "$79",
					"period": "/mo",
					"features": ["Unlimited Pages", "Advanced Forms", "Custom Theme"],
					"cta_label": "Go Pro",
					"highlighted": True,
				},
			],
		},
	},
	"faq": {
		"label": "FAQ",
		"category": "Content",
		"icon": "help-circle",
		"defaults": {
			"title": "Frequently asked questions",
			"items": [
				{"question": "How fast can I launch?", "answer": "Most sites go live in under an hour."},
				{"question": "Can I customize everything?", "answer": "Yes, every section is fully editable."},
			],
		},
	},
	"cta": {
		"label": "Call to Action",
		"category": "Content",
		"icon": "megaphone",
		"defaults": {
			"title": "Ready to get started?",
			"subtitle": "Launch your website today.",
			"button_label": "Start Building",
			"button_url": "#",
		},
	},
	"form": {
		"label": "Form",
		"category": "Forms",
		"icon": "inbox",
		"defaults": {
			"title": "Get in touch",
			"subtitle": "",
			"form": "",
		},
	},
	"contact": {
		"label": "Contact",
		"category": "Forms",
		"icon": "mail",
		"defaults": {
			"title": "Get in touch",
			"subtitle": "We would love to hear from you",
			"form": "contact",
			"email": "hello@example.com",
			"phone": "+1 555 0100",
			"address": "123 Business Ave, Suite 100",
		},
	},
	"team": {
		"label": "Team",
		"category": "Content",
		"icon": "users",
		"defaults": {
			"title": "Meet the team",
			"members": [
				{"name": "Jane Doe", "role": "Founder", "bio": "Vision and strategy", "photo": ""},
				{"name": "John Smith", "role": "Lead Developer", "bio": "Product and engineering", "photo": ""},
			],
		},
	},
	"gallery": {
		"label": "Gallery",
		"category": "Media",
		"icon": "image",
		"defaults": {
			"title": "Our work",
			"images": [],
		},
	},
	"page_banner": {
		"label": "Page Banner",
		"category": "Layout",
		"icon": "layout",
		"defaults": {
			"title": "Page title",
			"subtitle": "",
			"background_image": "",
		},
	},
	"menu_list": {
		"label": "Menu List",
		"category": "Content",
		"icon": "list",
		"defaults": {
			"title": "Our Menu",
			"subtitle": "",
			"categories": [
				{
					"name": "Starters",
					"items": [
						{"name": "House Salad", "description": "Fresh greens with vinaigrette", "price": "$9"},
						{"name": "Soup of the Day", "description": "Chef's daily selection", "price": "$8"},
					],
				}
			],
		},
	},
	"porto_blog_team": {
		"label": "Blog & Team",
		"category": "Content",
		"icon": "users",
		"defaults": {
			"blog": {"title": "Our Blog", "subtitle": "", "posts": []},
			"team": {"title": "Our Team", "subtitle": "", "members": []},
		},
	},
	"text": {
		"label": "Text Block",
		"category": "Content",
		"icon": "type",
		"defaults": {
			"title": "Section title",
			"body": "<p>Add your content here.</p>",
		},
	},
	"footer": {
		"label": "Footer",
		"category": "Layout",
		"icon": "layout",
		"defaults": {
			"logo_text": "WebCraft",
			"copyright": "© 2026 WebCraft. All rights reserved.",
			"social_links": [
				{"platform": "twitter", "url": "#"},
				{"platform": "linkedin", "url": "#"},
			],
		},
	},
	"product_grid": {
		"label": "Product Grid",
		"category": "Commerce",
		"icon": "shopping-bag",
		"defaults": {
			"title": "Featured Products",
			"subtitle": "Shop our latest drops",
			"columns": 4,
			"source": "static",
			"item_group": "",
			"limit": 8,
			"products": [
				{
					"name": "ProGrid Omni 9",
					"brand": "Saucony",
					"price": "$149",
					"image": "",
					"url": "#",
					"badge": "Hot",
				},
				{
					"name": "Gel Kayano 14",
					"brand": "ASICS",
					"price": "$159",
					"image": "",
					"url": "#",
					"badge": "New",
				},
			],
		},
	},
	"product_carousel": {
		"label": "Product Carousel",
		"category": "Commerce",
		"icon": "shopping-cart",
		"defaults": {
			"title": "New In",
			"subtitle": "Fresh arrivals this week",
			"source": "static",
			"item_group": "",
			"limit": 12,
			"products": [
				{
					"name": "Air Max Pulse",
					"brand": "Nike",
					"price": "$179",
					"image": "",
					"url": "#",
					"badge": "New",
				},
				{
					"name": "Samba OG",
					"brand": "adidas",
					"price": "$120",
					"image": "",
					"url": "#",
					"badge": "",
				},
			],
		},
	},
	"brand_logos": {
		"label": "Brand Logos",
		"category": "Commerce",
		"icon": "award",
		"defaults": {
			"title": "Shop by Brand",
			"brands": [
				{"name": "Nike", "url": "#", "logo": ""},
				{"name": "adidas", "url": "#", "logo": ""},
				{"name": "Jordan", "url": "#", "logo": ""},
				{"name": "New Balance", "url": "#", "logo": ""},
			],
		},
	},
	"category_tiles": {
		"label": "Category Tiles",
		"category": "Commerce",
		"icon": "grid",
		"defaults": {
			"title": "Shop Categories",
			"subtitle": "Find your next pair",
			"categories": [
				{"label": "Sneakers", "url": "#", "image": ""},
				{"label": "Running", "url": "#", "image": ""},
				{"label": "Lifestyle", "url": "#", "image": ""},
				{"label": "Sale", "url": "#", "image": ""},
			],
		},
	},
	"marquee": {
		"label": "Marquee Banner",
		"category": "Content",
		"icon": "move-horizontal",
		"defaults": {
			"items": [
				"Free Shipping over $150",
				"Guaranteed Authenticity",
				"Next Day Shipping On Select Sizes",
			],
			"speed": "slow",
		},
	},
	"product_detail": {
		"label": "Product Detail",
		"category": "Commerce",
		"icon": "shopping-bag",
		"defaults": {"item_code": "", "product": {}},
	},
	"cart": {
		"label": "Shopping Cart",
		"category": "Commerce",
		"icon": "shopping-cart",
		"defaults": {
			"title": "Your Cart",
			"subtitle": "Review items before checkout.",
		},
	},
	"checkout": {
		"label": "Checkout",
		"category": "Commerce",
		"icon": "credit-card",
		"defaults": {
			"title": "Checkout",
			"subtitle": "Complete your purchase.",
		},
	},
	"order_confirmation": {
		"label": "Order Confirmation",
		"category": "Commerce",
		"icon": "check-circle",
		"defaults": {"order_name": ""},
	},
}


def get_component_types() -> list[str]:
	return list(COMPONENTS.keys())


def get_component_defaults(section_type: str) -> dict:
	return dict(COMPONENTS.get(section_type, {}).get("defaults", {}))


def get_component_schema() -> dict:
	return COMPONENTS
