#!/usr/bin/env python3
"""Build Luci static site from theme assets for Cloudflare Pages."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS_SRC = ROOT / "assets"
OUT = ROOT / "site"
SITE_URL = os.environ.get("LUCI_SITE_URL", "https://luci.ltd").rstrip("/")
PLID = "601024"
WEB3FORMS_KEY = os.environ.get("WEB3FORMS_ACCESS_KEY", "b1ddb137-eb70-44f0-816f-e0387b045a22")

STORE = "https://my.luci.ltd"
CART = f"https://cart.secureserver.net/?pl_id={PLID}&prog_id={PLID}"
SSO = f"https://sso.secureserver.net/?app=account&path=%2F&plid={PLID}&prog_id={PLID}&realm=idp&referrer=sso"
HELP = f"{STORE}/help?plid={PLID}&prog_id={PLID}"
WHOIS = f"{STORE}/whois?plid={PLID}&prog_id={PLID}"
UTOS = f"{STORE}/legal-agreement?id=utos&plid={PLID}&prog_id={PLID}"
LEGAL = f"{STORE}/legal-agreements?plid={PLID}&prog_id={PLID}"
PRIVACY = f"{STORE}/legal-agreement?id=privacy&plid={PLID}&prog_id={PLID}"
DOMAIN_SEARCH = f"https://www.secureserver.net/products/domain-registration/find?plid={PLID}&prog_id={PLID}"
DCC_TRANSFER = f"https://dcc.secureserver.net/control/transfers?plid={PLID}&prog_id={PLID}&realm=idp&referrer=sso"
LOGO = "/assets/logo-desktop.svg"
LOGO_ERROR = "/assets/images/luci-logo-error.png"
GD_HEADER_CSS = "https://img6.wsimg.com/wrhs-next/cc77f1c32e31a8e336253a30687e61e8/reseller-sales-header.css"

ICON_CLASSES = {
    "phone": "fa-solid fa-phone",
    "help": "fa-solid fa-circle-question",
    "user-circle": "fa-solid fa-user",
    "chevron-down": "fa-solid fa-chevron-down",
    "cart": "fa-solid fa-cart-shopping",
    "close": "fa-solid fa-xmark",
    "account": "fa-solid fa-id-card",
    "domain-register": "fa-solid fa-magnifying-glass",
    "domains": "fa-solid fa-globe",
    "transfer": "fa-solid fa-right-left",
    "email": "fa-solid fa-envelope",
    "websites": "fa-solid fa-window-maximize",
    "ssl": "fa-solid fa-lock",
    "hosting": "fa-solid fa-server",
    "wordpress": "fa-brands fa-wordpress",
    "design": "fa-solid fa-palette",
    "website-builder": "fa-solid fa-pen-ruler",
}


def product(slug: str) -> str:
    return f"{STORE}/products/{slug}"


# Scroll-to-text fragment highlights the Online Store plan on the Website Builder page.
ONLINE_STORE_BUILDER = f"{product('website-builder')}#:~:text=Online%20Store"


NAV_CATALOG = {
    "domains": {
        "title": "Domains",
        "href": product("domain-registration"),
        "children": [
            ("domain_registration", "Domain Registration", product("domain-registration")),
            ("bulk_registration", "Bulk Registration", f"{STORE}/domains/bulk-domain-search?plid={PLID}&prog_id={PLID}"),
            ("domain_transfer", "Domain Transfer", product("domain-transfer")),
            ("bulk_transfer", "Bulk Transfer", f"{STORE}/domains/bulk-domain-transfer.aspx?plid={PLID}&prog_id={PLID}"),
        ],
    },
    "websites": {
        "title": "Websites",
        "href": product("website-builder"),
        "children": [
            ("bespoke", "Let us Design It", "/bespoke/"),
            ("website_builder", "Make Your Own", product("website-builder")),
            ("online_store", "Start an Online Store", "/online-store/"),
            ("wordpress", "WordPress", product("wordpress")),
        ],
    },
    "hosting": {
        "title": "Hosting",
        "href": product("cpanel"),
        "children": [
            ("cpanel", "cPanel", product("cpanel")),
            ("wordpress", "WordPress", product("wordpress")),
            ("business", "Web Hosting Plus", product("business")),
            ("vps", "VPS", product("vps")),
        ],
    },
    "security": {
        "title": "Security",
        "href": product("website-security"),
        "children": [
            ("website_security", "Website Security", product("website-security")),
            ("ssl", "SSL", product("ssl")),
            ("ssl_managed", "Managed SSL Service", product("ssl-managed")),
            ("website_backup", "Website Backup", product("website-backup")),
        ],
    },
    "marketing": {
        "title": "Marketing",
        "href": product("email-marketing"),
        "children": [
            ("email_marketing", "Email Marketing", product("email-marketing")),
            ("seo", "SEO", product("seo")),
        ],
    },
    "email": {
        "title": "Email",
        "href": product("microsoft-365"),
        "children": [
            ("microsoft365", "Microsoft 365", product("microsoft-365")),
        ],
    },
}

PORTAL_TILES = [
    ("myLuci Account", SSO, "account", True),
    ("Domain Registration", product("domain-registration"), "domain-register", False),
    ("Bulk Domain Transfer", f"{STORE}/domains/bulk-domain-transfer.aspx?plid={PLID}&prog_id={PLID}", "transfer", False),
    ("Microsoft 365", product("microsoft-365"), "email", False),
    ("Let us Design It", "/bespoke/", "design", False),
    ("Make Your Own", product("website-builder"), "websites", False),
    ("Start an Online Store", "/online-store/", "cart", False),
    ("SSL Certificates", product("ssl"), "ssl", False),
    ("Web Hosting (cPanel)", product("cpanel"), "hosting", False),
    ("Managed Hosting for WordPress", product("wordpress"), "wordpress", False),
]

HUB_CONTENT = {
    "domains": ("Search, register, transfer, or move domains in bulk on our secure storefront.", "domains"),
    "hosting": ("cPanel, WordPress, Web Hosting Plus, and VPS — available from Luci.", "hosting"),
    "websites": ("Launch a site without touching code — builders and WordPress on my.luci.ltd.", "websites"),
    "email": ("Professional email on your domain — Microsoft 365 for teams of every size.", "email"),
    "security": ("Protect visitors and recover quickly — SSL, website security, and backups.", "security"),
    "marketing": ("Get found and stay in touch — SEO and email marketing tools.", "marketing"),
}

CSS_BUNDLE_ORDER = [
    "css/godaddy-fonts.css",
    "css/godaddy-reseller-layout.css",
    "css/storefront-parity.css",
    "css/fontawesome-subset.css",
    "css/luci-icons.css",
    "css/luci-storefront.css",
    "css/standalone-layout.css",
    "css/luci-header-layout.css",
    "css/mobile-nav.css",
    "css/storefront-nav.css",
    "css/hydra-replacements.css",
    "css/mobile-layout.css",
    "css/home-shell.css",
    "css/white-shell.css",
]

CSS_HOME_EXTRA = [
    "css/home-page.css",
    "css/portal-hub.css",
    "css/meet-luci.css",
]

CSS_LANDING_EXTRA = [
    "css/meet-luci.css",
    "css/fabform-landing.css",
]

CSS_ERROR = [
    "css/godaddy-fonts.css",
    "css/error-pages.css",
    "css/white-shell.css",
]


def icon(name: str, size: str = "md", extra: str = "") -> str:
    cls = ICON_CLASSES.get(name, ICON_CLASSES["domains"])
    classes = f"{cls} luci-icon luci-icon--{size}"
    if extra:
        classes += f" {extra}"
    return f'<i class="{classes}" aria-hidden="true"></i>'


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def is_external(href: str) -> bool:
    return href.startswith("http")


def head(
    title: str,
    *,
    bundle: str = "site.css",
    extra_css: list[str] | None = None,
    preload_reach: bool = False,
    description: str | None = None,
) -> str:
    links = [
        f'<link rel="preconnect" href="https://img1.wsimg.com" crossorigin>',
        f'<link rel="preconnect" href="https://img6.wsimg.com" crossorigin>',
        f'<link rel="preload" href="{LOGO}" as="image" type="image/svg+xml" fetchpriority="high">',
    ]
    if preload_reach:
        links.append('<link rel="preload" href="/assets/Reach.svg" as="image" type="image/svg+xml">')
    links.append(f'<link rel="stylesheet" href="/{bundle}">')
    if extra_css:
        for href in extra_css:
            links.append(f'<link rel="stylesheet" href="/{href}">')
    links.append(f'<link rel="stylesheet" href="{GD_HEADER_CSS}" media="print" onload="this.media=\'all\'">')
    links.append(f'<noscript><link rel="stylesheet" href="{GD_HEADER_CSS}"></noscript>')
    boot = """<script>
(function () {
  var mobile = window.matchMedia('(max-width: 991px)');
  var coarse = window.matchMedia('(max-width: 991px), (hover: none), (pointer: coarse)');
  function apply() {
    document.documentElement.classList.toggle('luci-nav-mobile', mobile.matches);
    document.documentElement.classList.toggle('luci-coarse-pointer', coarse.matches);
  }
  apply();
  if (mobile.addEventListener) {
    mobile.addEventListener('change', apply);
    coarse.addEventListener('change', apply);
  }
})();
</script>"""
    meta_description = description or (
        "Domains, websites, hosting, and email — sorted without the jargon. "
        "Built in the UK for people who have better things to do."
    )
    return f"""<!DOCTYPE html>
<html lang="en-GB" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Luci</title>
<meta name="description" content="{esc(meta_description)}">
{chr(10).join(links)}
{boot}
</head>"""


def primary_nav() -> str:
    items = ['<li id="home" class="topnav-item menu-item-home"><div class="tray-menu"><div class="tray-toggle-wrapper"><a class="tray-toggle topnav-nontray-btn" href="/"><span>Home</span></a></div></div></li>']
    for section_id, section in NAV_CATALOG.items():
        title = section["title"]
        href = section["href"]
        children = section["children"]
        panel_id = f"luci-nav-panel-{section_id}"
        items.append(f'<li id="{section_id}" class="topnav-item menu-item-{section_id} has-dropdown">')
        items.append('<div class="tray-menu luci-nav-dropdown"><div class="tray-toggle-wrapper">')
        items.append(
            f'<button type="button" class="tray-toggle luci-nav-dropdown__trigger" aria-expanded="false" aria-haspopup="true" aria-controls="{panel_id}">'
            f'<span class="luci-nav-dropdown__label">{esc(title)}</span>'
            f'<span class="luci-nav-dropdown__caret chevron-down" aria-hidden="true">{icon("chevron-down", "sm")}</span></button>'
        )
        items.append(f'<ul class="luci-nav-dropdown__panel" id="{panel_id}" role="menu" hidden>')
        items.append(f'<li role="none"><a role="menuitem" class="luci-nav-dropdown__overview" href="{href}">All {esc(title)}</a></li>')
        for slug, child_title, child_href in children:
            items.append(f'<li role="none"><a role="menuitem" href="{child_href}">{esc(child_title)}</a></li>')
        items.append("</ul></div></div></li>")
    return '<ul class="topnav-items" id="luci-topnav-items">' + "".join(items) + "</ul>"


def secondary_nav(section_slug: str | None) -> str:
    if not section_slug or section_slug not in NAV_CATALOG:
        return ""
    section = NAV_CATALOG[section_slug]
    label = section["title"]
    links = section["children"]
    items = [f'<li class="secondarynav-item">{esc(label)}</li>']
    for slug, title, href in links:
        items.append(
            f'<li class="secondarynav-item" id="{slug}"><a href="{href}">{esc(title)}</a></li>'
        )
    return f"""<nav class="secondarynav luci-secondarynav" aria-label="Product categories">
<div class="product-nav-container"><div class="product-nav-flex">
<ul class="secondarynav-items">{"".join(items)}</ul>
</div></div></nav>"""


def header_html(section_slug: str | None = None, extra_body_classes: str = "") -> str:
    body_classes = "luci-site ux-app luci-standalone luci-secureserver-shell luci-home-shell"
    if extra_body_classes:
        body_classes += f" {extra_body_classes}"
    return f"""<body class="{body_classes}">
<div id="luci-hcs-header" class="luci-store-header luci-header-shell skip-nav-spacing">
<div class="utility-bar single-use-header pl reseller reseller-sales-header luci-header__utility">
<div class="utility-bar-flex">
<div class="utility-left-nav">
<div class="topnav-logo-wrap">
<a class="topnav-logo pl-large-logo white-logo-bg" href="/" rel="home">
<figure class="logo-img" style="margin:0">
<img id="registrar" class="luci-brand__logo" src="{LOGO}" alt="Luci" width="280" height="70" decoding="async" loading="eager" fetchpriority="high">
</figure></a></div></div>
<div class="utility-right-nav">
<div class="basic-phone-container">
<a class="basic-phone-btn" href="tel:+447432233596">
<span class="phone-header" title="Contact Us">{icon("phone")}</span>
<span class="basic-phone-text title-text">07432 233596</span></a></div>
<a class="help-link" href="{HELP}" title="Help">
<span class="help-icon">{icon("help")}</span>
<span class="help-link-text"><span>Help</span></span></a>
<a class="luci-account-link help-link" href="{SSO}" title="myLuci Account">
<span class="user-icon">{icon("user-circle")}</span>
<span class="help-link-text title-text"><span>myLuci Account</span></span></a>
<div id="cart-icon-wrapper">
<a class="cart-link luci-cart-link" href="{CART}" aria-label="Cart" title="Cart">
<span class="cart-icon" style="display:flex">{icon("cart")}</span></a></div>
</div></div></div>
<div class="top luci-header__nav"><section>
<nav class="topnav" aria-label="Products">
<div class="product-nav-container"><div class="product-nav-row">
<button type="button" class="luci-topnav-toggle hamburger-icon" aria-expanded="false" aria-controls="luci-topnav-items" aria-label="Open products menu">
<span class="luci-hamburger" aria-hidden="true"><span class="luci-hamburger__bar"></span><span class="luci-hamburger__bar"></span><span class="luci-hamburger__bar"></span></span>
<span class="luci-topnav-toggle__label">Menu</span></button>
{primary_nav()}
<ul class="topnav-right"></ul>
</div></div></nav></section></div></div>
{secondary_nav(section_slug)}
<main id="main" class="luci-site-main body" role="main">"""


def footer_html(*, scripts: list[str] | None = None) -> str:
    footer_links = [
        ("Home", "/"),
        ("Cart", CART),
        ("myLuci Account", SSO),
        ("Help Center", HELP),
        ("Contact Us", "/contact/"),
        ("WHOIS", WHOIS),
    ]
    link_items = "".join(f'<li><a href="{href}">{esc(title)}</a></li>' for title, href in footer_links)
    script_tags = ""
    default_scripts = ["/assets/js/nav-dropdowns.js", "/assets/js/hydra-trays.js"]
    for src in scripts or default_scripts:
        script_tags += f'<script src="{src}" defer></script>\n'
    return f"""</main>
<div class="luci-tax-disclaimer"><div class="container">
<p>Pricing excludes applicable taxes and ICANN fees.</p></div></div>
<footer id="luci-hcs-footer" class="reseller-footer" role="contentinfo">
<div class="reseller-container">
<ul class="reseller-footer-links">{link_items}</ul>
<p class="reseller-footer-utos"><span>Use of this Site is subject to express terms of use. By using this site, you signify that you agree to be bound by these <a href="{UTOS}">Universal Terms of Service</a>.</span></p>
<ul class="reseller-footer-legal">
<li><a href="{LEGAL}">Legal</a></li>
<li><a href="{PRIVACY}">Privacy Policy</a></li>
</ul></div></footer>
{script_tags}</body></html>"""


def hub_page_html(slug: str, page_title: str) -> str:
    lead, section = HUB_CONTENT[slug]
    section_data = NAV_CATALOG[section]
    links_html = "".join(
        f'<li><a class="luci-btn luci-btn-secondary" href="{href}">{esc(title)}</a></li>'
        for _, title, href in section_data["children"]
    )
    content = f"""<div id="primary" class="luci-home-below-hero luci-page-area luci-site-content">
<div class="luci-home-below-hero__inner">
<div class="luci-page-main luci-content-shell luci-page-card">
<article class="page">
<header class="entry-header"><h1 class="entry-title luci-heading">{esc(page_title)}</h1></header>
<div class="entry-content">
<p class="luci-lead">{esc(lead)}</p>
<ul class="luci-outbound-links">{links_html}</ul>
<p class="luci-disclaimer">You will continue on Luci's storefront (my.luci.ltd). Pricing excludes applicable taxes and ICANN fees.</p>
</div></article></div></div></div>"""
    return (
        head(page_title)
        + header_html(section)
        + content
        + footer_html()
    )


def meet_hero() -> str:
    return """<section class="luci-meet-hero" aria-labelledby="luci-meet-hero-title">
<div class="luci-meet-hero__inner">
<div class="luci-meet-hero__visual" aria-hidden="true">
<img class="luci-meet-hero__reach" src="/assets/Reach.svg" alt="" width="725" height="246" decoding="async" loading="eager" fetchpriority="high">
</div>
<div class="luci-meet-hero__copy">
<h1 id="luci-meet-hero-title" class="luci-meet-hero__title">Meet Luci</h1>
<p class="luci-meet-hero__tagline">A guiding paw to your digital presence.</p>
<p class="luci-meet-hero__lede">Domains, websites, hosting, and email — sorted without the jargon. Built in the UK for people who have better things to do.</p>
<a class="luci-meet-hero__cta" href="#luci-portal-hub-title">What can we do for you?</a>
</div></div></section>"""


def meet_journey() -> str:
    steps = [
        ("Searching.svg", "left", "Sniff out the perfect domain", True, 400, 280),
        ("Kneading.svg", "right", "Build it your way", False, 400, 280),
        ("Jumpscare.svg", "left", "Hosting &amp; email that behave", False, 400, 280),
        ("Luci.svg", "right", "Stick with Luci", False, 400, 283),
    ]
    texts = [
        f'Search, register, or <a href="{DCC_TRANSFER}" class="luci-meet-step__inline-link">transfer</a> — we keep domains straightforward so your name fits just right.',
        "DIY with our builder, go WordPress, or let us design something bespoke. Your site, your rules.",
        "cPanel, Microsoft 365, SSL — the grown-up stuff, explained in human terms with UK support behind it.",
        "One friendly place for your digital footprint. No corporate maze — just a guiding paw when you need it.",
    ]
    titles = [s[2] for s in steps]
    html = '<div class="luci-meet-journey">'
    for i, (asset, align, title, has_search, w, h) in enumerate(steps):
        html += f'<section class="luci-meet-step luci-meet-step--{align}"><div class="luci-meet-step__inner">'
        html += f'<figure class="luci-meet-step__figure"><img class="luci-meet-step__img" src="/assets/{asset}" alt="" width="{w}" height="{h}" loading="lazy" decoding="async"></figure>'
        html += '<div class="luci-meet-step__copy">'
        html += f'<h2 class="luci-meet-step__title">{title}</h2>'
        html += f'<p class="luci-meet-step__text">{texts[i]}</p>'
        if has_search:
            html += f"""<form class="luci-meet-domain-search" action="{DOMAIN_SEARCH}" method="get" role="search" aria-label="Domain search">
<div class="luci-meet-domain-search__pill">
<label class="screen-reader-text" for="luci-meet-domain-input">Domain name</label>
<input type="search" id="luci-meet-domain-input" class="luci-meet-domain-search__input" name="domainToCheck" placeholder="e.g. yourbusiness.co.uk" autocomplete="off" inputmode="url" spellcheck="false">
<button type="submit" class="luci-meet-domain-search__submit">Search</button></div></form>
<p class="luci-meet-domain-search__transfer"><a class="luci-meet-domain-search__transfer-link" href="{DCC_TRANSFER}">Create an Account / Sign In to transfer your existing domain</a></p>"""
        html += "</div></div></section>"
    html += "</div>"
    return html


def portal_hub() -> str:
    tiles = ""
    for title, href, ic, external in PORTAL_TILES:
        target = ' target="_blank" rel="noopener noreferrer"' if external else ""
        tiles += f"""<li><a class="luci-portal-tile" href="{href}"{target}>
<span class="luci-portal-tile__icon luci-portal-tile__icon--{ic}">{icon(ic, "xl", "luci-portal-tile__glyph")}</span>
<span class="luci-portal-tile__label">{esc(title)}</span></a></li>"""
    return f"""<section class="luci-portal-hub" aria-labelledby="luci-portal-hub-title">
<h2 id="luci-portal-hub-title" class="luci-portal-hub__title">What can we do for you?</h2>
<p class="luci-portal-hub__intro">Pick a path — we will walk you through domains, sites, hosting, and the rest.</p>
<ul class="luci-portal-hub__grid">{tiles}</ul></section>"""


def home_page() -> str:
    extra = """<p class="luci-lead">Luci helps you register domains, launch websites, and grow online — with straightforward pricing and support that actually answers.</p>
<h2 class="luci-heading">Why choose Luci?</h2>
<ul class="luci-benefits">
<li><strong>One place for everything</strong> — domains, hosting, email, security, and marketing.</li>
<li><strong>Transparent pricing</strong> — taxes and ICANN fees shown where they apply.</li>
<li><strong>Built for the UK</strong> — shop in GBP with products for British businesses.</li>
</ul>
<p class="luci-disclaimer">Pricing excludes applicable taxes and ICANN fees.</p>"""
    # Match WordPress front-page.php: hero → journey → then portal hub in luci-home-below-hero.
    body = f"""{meet_hero()}
{meet_journey()}
<div class="luci-home-below-hero"><div class="luci-home-below-hero__inner">
{portal_hub()}
<div class="entry-content luci-hero-extra">{extra}</div>
</div></div>"""
    scripts = ["/assets/js/nav-dropdowns.js", "/assets/js/hydra-trays.js", "/assets/js/home-hero-search.js"]
    return (
        head("Home", bundle="site-home.css", preload_reach=True)
        + header_html(None, "luci-front-page")
        + body
        + footer_html(scripts=scripts)
        + f'<script>window.luciHomeHero={{"searchBase":"{DOMAIN_SEARCH}"}};</script>'
    )


def contact_form() -> str:
    redirect = f"{SITE_URL}/contact/thank-you/"
    return f"""<section class="luci-meet-step luci-fabform-form-section" aria-labelledby="luci-contact-form-title">
<div class="luci-fabform-form-section__inner">
<h2 id="luci-contact-form-title" class="luci-meet-step__title luci-fabform-form-section__title">Send a message</h2>
<p class="luci-meet-step__text luci-fabform-form-lead">Tell us what you need — the more detail you give, the faster we can help.</p>
<form class="luci-fabform-form" method="post" action="https://api.web3forms.com/submit" accept-charset="UTF-8">
<input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
<input type="hidden" name="redirect" value="{redirect}">
<input type="checkbox" name="botcheck" class="luci-fabform-form__hp" style="display: none;" tabindex="-1" autocomplete="off" aria-hidden="true">
<div class="luci-fabform-form__grid">
<p class="luci-fabform-form__field"><label for="luci-contact-name">Your name</label><input type="text" id="luci-contact-name" name="name" required autocomplete="name"></p>
<p class="luci-fabform-form__field"><label for="luci-contact-email">Email</label><input type="email" id="luci-contact-email" name="email" required autocomplete="email" inputmode="email"></p>
<p class="luci-fabform-form__field luci-fabform-form__field--full"><label for="luci-contact-subject">Subject</label><input type="text" id="luci-contact-subject" name="subject" required placeholder="e.g. Domain transfer question"></p>
<p class="luci-fabform-form__field"><label for="luci-contact-phone">Phone <span class="luci-fabform-optional">(optional)</span></label><input type="tel" id="luci-contact-phone" name="phone" autocomplete="tel" inputmode="tel"></p>
<p class="luci-fabform-form__field luci-fabform-form__field--full"><label for="luci-contact-message">Message</label><textarea id="luci-contact-message" name="message" rows="6" required placeholder="How can we help?"></textarea></p>
</div>
<p class="luci-fabform-form__actions"><button type="submit" class="luci-meet-hero__cta luci-fabform-submit">Send message</button></p>
</form>
<p class="luci-fabform-form-note">By submitting you agree we may contact you about this enquiry. Pricing excludes applicable taxes and ICANN fees where relevant.</p>
</div></section>"""


def contact_page() -> str:
    intro = f"""<section class="luci-meet-hero luci-fabform-hero" aria-labelledby="luci-contact-title">
<div class="luci-meet-hero__inner">
<div class="luci-meet-hero__visual" aria-hidden="true"><img class="luci-meet-hero__reach luci-fabform-hero__img" src="/assets/Jumpscare.svg" alt="" width="400" height="280" decoding="async"></div>
<div class="luci-meet-hero__copy">
<p class="luci-fabform-eyebrow">Support</p>
<h1 id="luci-contact-title" class="luci-meet-hero__title">Contact Us</h1>
<p class="luci-meet-hero__tagline">Questions about domains, hosting, email, or your account?</p>
<p class="luci-meet-hero__lede">Send us a message and a real person on the Luci team will get back to you. For quick answers, try the <a class="luci-meet-step__inline-link" href="{HELP}">Help Center</a>.</p>
</div></div></section>"""
    details = f"""<section class="luci-meet-step luci-fabform-details" aria-label="How we can help">
<div class="luci-fabform-details__inner">
<div class="luci-fabform-details__col"><h2 class="luci-meet-step__title">We can help with</h2>
<ul class="luci-fabform-list"><li>Domains, transfers, and DNS</li><li>Hosting, WordPress, and website builder</li><li>Email, Microsoft 365, and security products</li><li>Billing, renewals, and your myLuci account</li></ul></div>
<div class="luci-fabform-details__col"><h2 class="luci-meet-step__title">What happens next</h2>
<ul class="luci-fabform-list"><li>Your message goes straight to our support inbox.</li><li>We aim to reply within one working day — often much sooner.</li>
<li>Prefer to talk? <a class="luci-meet-step__inline-link" href="tel:+447432233596">07432 233596</a></li></ul></div>
</div></section>"""
    shell = '<div id="primary" class="luci-landing-page luci-page-area luci-site-content luci-contact-shell luci-fabform-page-shell"><div class="luci-landing-page__inner">'
    return (
        head("Contact Us", bundle="site-landing.css")
        + header_html(None, "luci-contact-page luci-landing-layout")
        + shell + intro + details + contact_form() + "</div></div>"
        + footer_html()
    )


def bespoke_form() -> str:
    redirect = f"{SITE_URL}/bespoke/thank-you/"
    return f"""<section class="luci-meet-step luci-bespoke-form-section" aria-labelledby="luci-bespoke-form-title">
<div class="luci-bespoke-form-section__inner">
<h2 id="luci-bespoke-form-title" class="luci-meet-step__title luci-bespoke-form-section__title">Request a quote</h2>
<p class="luci-meet-step__text luci-bespoke-form-lead">Fill in the form and we will email you back. No obligation — just a straight conversation about your project.</p>
<form class="luci-bespoke-form" method="post" action="https://api.web3forms.com/submit" accept-charset="UTF-8">
<input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
<input type="hidden" name="redirect" value="{redirect}">
<input type="hidden" name="subject" value="Luci bespoke enquiry">
<input type="checkbox" name="botcheck" class="luci-bespoke-form__hp" style="display: none;" tabindex="-1" autocomplete="off" aria-hidden="true">
<div class="luci-bespoke-form__grid">
<p class="luci-bespoke-form__field"><label for="luci-bespoke-name">Your name</label><input type="text" id="luci-bespoke-name" name="name" required autocomplete="name"></p>
<p class="luci-bespoke-form__field"><label for="luci-bespoke-email">Email</label><input type="email" id="luci-bespoke-email" name="email" required autocomplete="email" inputmode="email"></p>
<p class="luci-bespoke-form__field"><label for="luci-bespoke-company">Company or organisation <span class="luci-bespoke-optional">(optional)</span></label><input type="text" id="luci-bespoke-company" name="company" autocomplete="organization"></p>
<p class="luci-bespoke-form__field"><label for="luci-bespoke-phone">Phone <span class="luci-bespoke-optional">(optional)</span></label><input type="tel" id="luci-bespoke-phone" name="phone" autocomplete="tel" inputmode="tel"></p>
<p class="luci-bespoke-form__field luci-bespoke-form__field--full"><label for="luci-bespoke-message">Tell us about your project</label><textarea id="luci-bespoke-message" name="message" rows="6" required placeholder="Goals, pages you need, examples you like, launch date…"></textarea></p>
</div>
<p class="luci-bespoke-form__actions"><button type="submit" class="luci-meet-hero__cta luci-bespoke-submit">Send enquiry</button></p>
</form>
<p class="luci-meet-domain-search__transfer luci-bespoke-form__transfer"><a class="luci-meet-domain-search__transfer-link" href="{DCC_TRANSFER}">Create an Account / Sign In to transfer your existing domain</a></p>
<p class="luci-bespoke-form-note">Pricing excludes applicable taxes. By submitting you agree we may contact you about this enquiry.</p>
</div></section>"""


def online_store_page() -> str:
    purchase = ONLINE_STORE_BUILDER
    meta = (
        "Build your own online store from £22/month with Luci Website Builder — a DIY plan you set up yourself. "
        "Hosting, SSL, cart, and payments included. Prefer a done-for-you site? See our bespoke design service."
    )
    intro = f"""<section class="luci-meet-hero luci-online-store-hero" aria-labelledby="luci-online-store-title">
<div class="luci-meet-hero__inner">
<div class="luci-meet-hero__visual" aria-hidden="true"><img class="luci-meet-hero__reach luci-online-store-hero__img" src="/assets/Treats.svg" alt="" width="400" height="280" decoding="async"></div>
<div class="luci-meet-hero__copy">
<p class="luci-online-store-eyebrow">DIY · Luci Website Builder · Online Store</p>
<h1 id="luci-online-store-title" class="luci-meet-hero__title">Build your own online store</h1>
<p class="luci-meet-hero__tagline">Luci <strong>Online Store</strong> plan — <strong>£22/month</strong> to design, populate, and publish your shop yourself.</p>
<p class="luci-meet-hero__lede">This is a <strong>do-it-yourself</strong> website builder: you pick the template, add your products, write the pages, and connect payments. Luci provides the tools, hosting, and SSL — we do not design or build your store for you. Ideal if you are happy rolling up your sleeves and want full control without agency fees.</p>
<p class="luci-online-store-hero__actions">
<a class="luci-meet-hero__cta" href="{purchase}" target="_blank" rel="noopener noreferrer">Start building for £22/month</a>
</p>
</div></div></section>"""
    diy_callout = """<section class="luci-online-store-diy" aria-labelledby="luci-online-store-diy-title">
<div class="luci-online-store-diy__inner">
<h2 id="luci-online-store-diy-title" class="luci-meet-step__title luci-online-store-diy__title">A DIY plan — not a done-for-you service</h2>
<p class="luci-meet-step__text luci-online-store-diy__lead">The Online Store plan is for people who want to <strong>build and manage their own shop</strong>. You will use Luci Website Builder to lay out pages, upload product photos, set prices, and publish when you are ready. Support is available if you get stuck, but the creative and setup work is yours.</p>
<p class="luci-meet-step__text luci-online-store-diy__bespoke">Would you rather someone else handled it? <a class="luci-meet-step__inline-link" href="/bespoke/">Request a bespoke website enquiry</a> — we can design and build a site around your brand while you stay hands-off.</p>
</div></section>"""
    features = """<section class="luci-meet-step luci-online-store-features" aria-labelledby="luci-online-store-features-title">
<div class="luci-online-store-features__inner">
<h2 id="luci-online-store-features-title" class="luci-meet-step__title luci-online-store-features__title">The toolbox for your DIY shop</h2>
<p class="luci-meet-step__text luci-online-store-features__lead">Everything below is included in the Online Store plan — you bring the products and content; the builder handles the technical heavy lifting.</p>
<div class="luci-online-store-features__grid">
<div class="luci-online-store-features__col">
<h3 class="luci-online-store-features__heading">Look great on every device</h3>
<ul class="luci-online-store-features__list">
<li>Responsive mobile design</li>
<li>Website hosting included</li>
<li>Rapid page-load performance</li>
<li>Security (SSL certificate)</li>
<li>Create a blog</li>
</ul>
</div>
<div class="luci-online-store-features__col">
<h3 class="luci-online-store-features__heading">Get found and stay connected</h3>
<ul class="luci-online-store-features__list">
<li>Search engine optimisation (SEO)</li>
<li>Social media integration</li>
<li>Share content to Facebook</li>
<li>Online appointments</li>
<li>PayPal Buy Now or Donate button</li>
</ul>
</div>
<div class="luci-online-store-features__col">
<h3 class="luci-online-store-features__heading">Sell with confidence</h3>
<ul class="luci-online-store-features__list">
<li>Built-in shopping cart</li>
<li>Sell physical and digital products</li>
<li>Accept credit and debit cards, PayPal and more</li>
<li>Flexible shipping options</li>
<li>Discounts and promotions</li>
<li>Manage inventory</li>
</ul>
</div>
</div>
</div></section>"""
    steps = """<section class="luci-meet-step luci-online-store-steps" aria-labelledby="luci-online-store-steps-title">
<div class="luci-online-store-steps__inner">
<div class="luci-online-store-steps__col">
<h2 id="luci-online-store-steps-title" class="luci-meet-step__title">How it works</h2>
<ol class="luci-online-store-steps__list">
<li>Sign up for the <strong>Online Store</strong> plan on our secure storefront.</li>
<li><strong>You</strong> choose a template, add products, write your pages, and connect payments.</li>
<li>When <strong>you</strong> are happy with it, publish your shop and start taking orders.</li>
</ol>
</div>
<div class="luci-online-store-steps__col">
<h2 class="luci-meet-step__title">Why Luci?</h2>
<ul class="luci-online-store-steps__list luci-online-store-steps__list--bullets">
<li>Transparent UK pricing in GBP — no surprise checkout fees from us.</li>
<li>Luci Website Builder — powerful and straightforward, explained in plain English.</li>
<li>Domains, hosting, email, and SSL available in the same place when you grow.</li>
</ul>
</div>
</div></section>"""
    cta = f"""<section class="luci-online-store-cta" aria-labelledby="luci-online-store-cta-title">
<div class="luci-online-store-cta__inner">
<h2 id="luci-online-store-cta-title" class="luci-meet-step__title">Ready to build your shop?</h2>
<p class="luci-meet-step__text">The Online Store plan is <strong>£22/month</strong> — a self-build ecommerce website with hosting and SSL. You create the site; we provide the platform.</p>
<p class="luci-online-store-cta__actions">
<a class="luci-meet-hero__cta" href="{purchase}" target="_blank" rel="noopener noreferrer">Start building your store</a>
<a class="luci-meet-hero__cta luci-online-store-cta__secondary" href="/bespoke/">Prefer bespoke? Get a quote</a>
</p>
<p class="luci-online-store-cta__note">Pricing excludes applicable taxes. See the full feature list and sign up at <a class="luci-meet-step__inline-link" href="{purchase}">my.luci.ltd</a>.</p>
</div></section>"""
    shell = '<div id="primary" class="luci-landing-page luci-page-area luci-site-content luci-online-store-shell luci-fabform-page-shell"><div class="luci-landing-page__inner">'
    return (
        head("Start an Online Store — Website Builder from £22/month", bundle="site-landing.css", description=meta)
        + header_html("websites", "luci-online-store-page luci-landing-layout")
        + shell + intro + diy_callout + features + steps + cta + "</div></div>"
        + footer_html()
    )


def bespoke_page() -> str:
    intro = """<section class="luci-meet-hero luci-bespoke-hero" aria-labelledby="luci-bespoke-title">
<div class="luci-meet-hero__inner">
<div class="luci-meet-hero__visual" aria-hidden="true"><img class="luci-meet-hero__reach luci-bespoke-hero__img" src="/assets/Kneading.svg" alt="" width="400" height="280" decoding="async"></div>
<div class="luci-meet-hero__copy">
<p class="luci-bespoke-eyebrow">Websites</p>
<h1 id="luci-bespoke-title" class="luci-meet-hero__title">Bespoke Website Design</h1>
<p class="luci-meet-hero__tagline">Built around your brand — not a template with your logo dropped in.</p>
<p class="luci-meet-hero__lede">Tell us what you need and we will come back with a clear quote and a sensible plan.</p>
</div></div></section>"""
    details = """<section class="luci-meet-step luci-bespoke-details" aria-label="What you get and how it works">
<div class="luci-bespoke-details__inner">
<div class="luci-bespoke-details__col"><h2 class="luci-meet-step__title">What you get</h2>
<ul class="luci-bespoke-list"><li>Discovery call and written scope so everyone agrees what “done” looks like</li><li>Custom layout, typography, and colour — aligned with Luci brand standards or your own guidelines</li><li>Mobile-first build, basic SEO setup, and handover documentation</li><li>Optional hosting, domains, and email through Luci once you are live</li></ul></div>
<div class="luci-bespoke-details__col"><h2 class="luci-meet-step__title">How it works</h2>
<ol class="luci-bespoke-steps"><li>Share your goals, examples you like, and any deadlines in the form below.</li><li>We review and reply with questions or a fixed-price quote — usually within two working days.</li><li>Design, build, review rounds, then launch with UK-based support behind you.</li></ol></div>
</div></section>"""
    shell = '<div id="primary" class="luci-landing-page luci-page-area luci-site-content luci-bespoke-shell luci-fabform-page-shell"><div class="luci-landing-page__inner">'
    return (
        head("Bespoke Website Design", bundle="site-landing.css")
        + header_html("websites", "luci-bespoke-page luci-landing-layout")
        + shell + intro + details + bespoke_form() + "</div></div>"
        + footer_html()
    )


def thank_you(title: str, eyebrow: str, secondary: str, body_class: str, back_href: str, back_label: str) -> str:
    hero = f"""<section class="luci-meet-hero luci-fabform-thank-you" aria-labelledby="thank-you-title">
<div class="luci-meet-hero__inner">
<div class="luci-meet-hero__visual" aria-hidden="true"><img class="luci-meet-hero__reach luci-fabform-hero__img" src="/assets/Luci.svg" alt="" width="320" height="320" decoding="async"></div>
<div class="luci-meet-hero__copy">
<p class="luci-fabform-eyebrow">{esc(eyebrow)}</p>
<h1 id="thank-you-title" class="luci-meet-hero__title">Thanks — we have got it.</h1>
<p class="luci-meet-hero__tagline">Your message is in our inbox.</p>
<p class="luci-meet-hero__lede">{esc(secondary)}</p>
<p class="luci-fabform-thank-you-actions">
<a class="luci-meet-hero__cta" href="/">Back to home</a>
<a class="luci-meet-hero__cta luci-fabform-thank-you__cta--secondary" href="{back_href}">{esc(back_label)}</a>
</p></div></div></section>"""
    return (
        head(title, bundle="site-landing.css")
        + header_html(None, f"{body_class} luci-landing-layout")
        + f'<div id="primary" class="luci-landing-page luci-page-area luci-site-content"><div class="luci-landing-page__inner">{hero}</div></div>'
        + footer_html()
    )


def cart_page() -> str:
    content = f"""<div id="primary" class="luci-home-below-hero luci-page-area luci-site-content">
<div class="luci-home-below-hero__inner"><div class="luci-page-main luci-content-shell luci-page-card">
<article><header class="entry-header"><h1 class="entry-title luci-heading">Cart</h1></header>
<div class="entry-content">
<p class="luci-lead">Your cart lives on Luci's secure checkout.</p>
<p><a class="luci-btn luci-btn-primary" href="{CART}" target="_blank" rel="noopener noreferrer">Open cart</a></p>
</div></article></div></div></div>"""
    return head("Cart") + header_html(None) + content + footer_html()


def error_fullscreen(title: str, headline: str, line1: str, line2: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en-GB"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, follow">
<title>{esc(title)} — Luci</title>
<link rel="stylesheet" href="/site-error.css">
</head>
<body class="luci-error-fullscreen-page">
<main id="main" class="luci-error-fullscreen" role="main">
<div class="luci-error-fullscreen__inner">
<figure class="luci-error-fullscreen__figure">
<img class="luci-error-fullscreen__cat" src="/assets/Searching.svg" alt="" width="800" height="480" loading="eager" decoding="async">
</figure>
<div class="luci-error-fullscreen__copy">
<h1 class="luci-error-fullscreen__title">{esc(headline)}</h1>
<p class="luci-error-fullscreen__text">{esc(line1)}</p>
<p class="luci-error-fullscreen__text">{esc(line2)}</p>
</div></div>
<a class="luci-error-fullscreen__logo" href="/">
<img src="{LOGO}" alt="Luci — back to home" width="96" height="68">
</a></main></body></html>"""


def error_card_page(title: str, headline: str, line1: str, line2: str, image: str, show_home: bool, body_extra: str = "") -> str:
    home_btn = '<div class="luci-error-actions"><a class="luci-btn luci-btn-primary" href="/">Back to Luci</a></div>' if show_home else ""
    content = f"""<div class="luci-error-standalone">{body_extra}
<div class="luci-error-wrap"><article class="luci-error-card">
<div class="luci-error-visual"><img src="{image}" alt="" loading="lazy"></div>
<div class="luci-error-copy">
<h1 class="luci-error-headline luci-heading">{esc(headline)}</h1>
<p>{esc(line1)}</p><p>{esc(line2)}</p>{home_btn}
<img class="luci-error-logo" src="{LOGO_ERROR}" alt="Luci" width="96" height="68">
</div></article></div></div>"""
    return head(title, bundle="site.css") + header_html(None) + content + footer_html()


def bundle_css(files: list[str], out_name: str) -> None:
    parts = []
    for rel in files:
        path = ASSETS_SRC / rel
        if not path.exists():
            raise FileNotFoundError(path)
        css = path.read_text(encoding="utf-8")
        css = re.sub(r"url\((['\"]?)\.\./", r"url(\1/assets/", css)
        css = re.sub(r"url\((['\"]?)\./", r"url(\1/assets/", css)
        css = re.sub(r"url\((['\"]?)\.\./fonts/", r"url(\1/assets/fonts/", css)
        parts.append(f"/* {rel} */\n{css}")
    (OUT / out_name).write_text("\n".join(parts), encoding="utf-8")


def copy_assets() -> None:
    dst = OUT / "assets"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        ASSETS_SRC,
        dst,
        ignore=shutil.ignore_patterns("*.af", "*.af~lock~", "Table Cat.af", "css"),
    )


def write_page(rel_path: str, html: str) -> None:
    path = OUT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    print(f"  wrote {rel_path}")


def main() -> None:
    if not ASSETS_SRC.is_dir():
        raise SystemExit(f"Assets not found: {ASSETS_SRC}")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    print("Copying assets…")
    copy_assets()

    print("Bundling CSS…")
    bundle_css(CSS_BUNDLE_ORDER, "site.css")
    bundle_css(CSS_BUNDLE_ORDER + CSS_HOME_EXTRA, "site-home.css")
    bundle_css(CSS_BUNDLE_ORDER + CSS_LANDING_EXTRA, "site-landing.css")
    bundle_css(CSS_ERROR, "site-error.css")

    print("Generating pages…")
    write_page("index.html", home_page())

    for slug, (lead, _) in HUB_CONTENT.items():
        title = slug.capitalize() if slug != "email" else "Email"
        write_page(f"{slug}/index.html", hub_page_html(slug, title))

    write_page("cart/index.html", cart_page())
    write_page("contact/index.html", contact_page())
    write_page(
        "contact/thank-you/index.html",
        thank_you(
            "Thank you",
            "Message received",
            "Someone from Luci will reply as soon as we can — usually within one working day. If it is urgent, call the number in the header.",
            "luci-contact-thank-you-page",
            "/contact/",
            "Send another message",
        ),
    )
    write_page("online-store/index.html", online_store_page())
    write_page("bespoke/index.html", bespoke_page())
    write_page(
        "bespoke/thank-you/index.html",
        thank_you(
            "Thank you",
            "Enquiry received",
            "A member of the Luci team will review your project and reply within two working days — often sooner. Explore domains, hosting, and builders from the menu above, or reply to our confirmation email if you forgot something.",
            "luci-bespoke-thank-you-page",
            "/bespoke/",
            "Send another enquiry",
        ),
    )
    write_page(
        "404.html",
        error_fullscreen("Page not found", "WHERE'S IT GONE?", "We can't find that page.", "Luci hasn't eaten it. We promise."),
    )
    write_page(
        "maintenance/index.html",
        error_card_page(
            "Maintenance",
            "it's time for trEatS.",
            "This Luci site has been put on paws.",
            "Please contact us to get back on line.",
            "/assets/images/luci-cat-maintenance.png",
            False,
            "",
        ),
    )
    write_page(
        "forbidden/index.html",
        error_card_page(
            "Forbidden",
            "scccrrratch",
            "You do not have permission to view this page.",
            "If you think this is a mistake, contact us.",
            "/assets/Jumpscare.svg",
            True,
        ),
    )

    # Cloudflare Pages redirects
    (OUT / "_redirects").write_text(
        "/contact/thank-you /contact/thank-you/ 301\n"
        "/bespoke/thank-you /bespoke/thank-you/ 301\n"
        "/* /404.html 404\n",
        encoding="utf-8",
    )

    (OUT / "_headers").write_text(
        "/*\n"
        "  X-Frame-Options: SAMEORIGIN\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "\n"
        "/assets/*\n"
        "  Cache-Control: public, max-age=31536000, immutable\n"
        "\n"
        "/site*.css\n"
        "  Cache-Control: public, max-age=604800\n"
        "\n"
        "/assets/js/*\n"
        "  Cache-Control: public, max-age=604800\n",
        encoding="utf-8",
    )

    print(f"\nDone — static site in {OUT}")
    print(f"Site URL for forms: {SITE_URL}")
    print("Preview: python3 -m http.server 8765 --directory site")
    print("Deploy: npx wrangler pages deploy site --project-name=luci")


if __name__ == "__main__":
    main()
