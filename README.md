# WebCraft

**Pre-built website designs for Frappe** — like Wix or Shopify themes, running inside your site.

## What WebCraft is

1. **Browse** pre-built designs (Corporate, E-Commerce, …)
2. **Preview** the entire website — every page — before you commit
3. **Use this design** — installs pages, theme, menus, and publishes your site

WebCraft is **not** a from-scratch page builder. For custom pixel-perfect pages, use [Frappe Builder](https://frappe.io/builder) (`/builder`).

## Quick start

1. Open **WebCraft** from the apps screen or `/app/webcraft`
2. Browse the **Theme store** — filter by Corporate or E-Commerce
3. Click a theme → preview every page (desktop / tablet / mobile)
4. Click **Add theme to site** → customize colors & logo → publish

### Shopify-like workflow

| Shopify | WebCraft |
|---------|----------|
| Online Store → Themes | `/app/webcraft` → Theme store |
| Preview theme | Full-screen preview + device toggles |
| Add theme | **Add theme to site** |
| Customize theme | `/app/webcraft-customize/<project>` |
| My themes | **My sites** tab |

## Pre-built designs

| Design | Key | Preview |
|--------|-----|---------|
| Corporate Blue | `corporate` | `/webcraft-preview/corporate` |
| Kick Store (E-Commerce) | `ecommerce` | `/webcraft-preview/ecommerce` |

### E-Commerce (ERPNext / Webshop)

The **Kick Store** design is a full storefront wired to **Webshop**:

| Step | URL | ERPNext document |
|------|-----|------------------|
| Browse products | `/store/shop` | Website Item |
| Product page | `/store/product/<item_code>` | Website Item |
| Cart | `/store/cart` | Quotation (`order_type = Shopping Cart`) |
| Checkout | `/store/checkout` | Quotation + Address |
| Order placed | `/store/order/<sales_order>` | Sales Order (converted from Quotation) |

**Requirements:** Install `webshop` and `erpnext`, enable **Webshop Settings**, publish **Website Items**, and log in as a website user to add to cart (Webshop stores the cart as a draft Quotation per customer).

Add more designs by adding a folder under `website_builder/templates/<name>/template.json`.

## Architecture

```
website_builder/
├── templates/     # Bundled designs (JSON manifests + assets)
├── preview.py     # Render full-site preview without installing
├── installer.py   # Copy design → Website Project
├── builder.py     # Live site rendering
└── page/webcraft/ # Design gallery desk UI
```

## Development

```bash
bench build --app webcraft
bench --site site1.local migrate
bench --site site1.local clear-website-cache
```

Reset all installed WebCraft sites (destructive):

```bash
bench --site site1.local execute webcraft.website_builder.api.reset_webcraft_data --kwargs "{'confirm': 1}"
```
