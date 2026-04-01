#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║        🔍  Arab Phone Prices Scraper  (v1.0)                ║
║  Scrapes phone prices from Jumia · Noon · OpenSooq          ║
║  across 17+ Arab countries → outputs prices_arab.json       ║
╚══════════════════════════════════════════════════════════════╝
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import logging
import random
import os
from datetime import date
from urllib.parse import quote_plus

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("scraper")

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices_arab.json")
REQUEST_TIMEOUT = 20
MIN_DELAY = 2
MAX_DELAY = 5

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

# ── Keywords that mark accessories (not actual phones) ──────
ACCESSORY_KW = {
    "case", "cover", "protector", "screen", "glass", "film", "charger",
    "cable", "adapter", "holder", "stand", "mount", "earbuds", "earphone",
    "headphone", "headset", "band", "wallet", "pouch", "sleeve", "skin",
    "sticker", "decal", "lens", "tempered", "silicone", "tpu", "ring",
    "grip", "strap", "armor", "bumper", "shield", "mug", "chopper",
    "bodysuit", "puzzle", "keyboard", "armband",
    "كفر", "جراب", "شاحن", "سماعة", "حماية", "اسكرينة", "جلاس",
}

# ── Minimum price (local currency) to accept as a real phone ─
MIN_PHONE_PRICE = {
    "EGP": 2000, "SAR": 200, "AED": 200, "MAD": 500, "DZD": 5000,
    "SYP": 500000, "JOD": 30, "IQD": 50000, "KWD": 15, "BHD": 15,
    "OMR": 15, "LYD": 100, "TND": 100, "SDG": 10000, "LBP": 2000000,
    "ILS": 150, "YER": 10000,
}

# ─────────────────────────────────────────────────────────────
# Phones to Track  (add / remove freely)
# ─────────────────────────────────────────────────────────────
PHONES_TO_TRACK = [
    "Samsung Galaxy S24 Ultra",
    "Samsung Galaxy S24",
    "Samsung Galaxy S23 FE",
    "Samsung Galaxy A55",
    "Samsung Galaxy A54",
    "Samsung Galaxy A35",
    "Samsung Galaxy A25",
    "Samsung Galaxy A15",
    "iPhone 15 Pro Max",
    "iPhone 15 Pro",
    "iPhone 15",
    "iPhone 14",
    "iPhone 13",
    "Honor Magic 6 Pro",
    "Honor Magic 6 Lite",
    "Honor X9b",
    "Honor X8b",
    "Xiaomi 14 Ultra",
    "Xiaomi Redmi Note 13 Pro",
    "Xiaomi Redmi Note 13",
    "Xiaomi Redmi 13C",
    "OPPO Reno 11 Pro",
    "OPPO Reno 11",
    "OPPO A78",
    "OPPO A58",
    "Realme 12 Pro Plus",
    "Realme 12 Pro",
    "Realme C67",
    "Huawei Nova 12",
    "Huawei Pura 70 Pro",
    "Tecno Spark 20 Pro",
    "Tecno Camon 30",
    "Infinix Note 40 Pro",
    "Infinix Hot 40 Pro",
    "OnePlus 12",
    "Google Pixel 8 Pro",
    "Google Pixel 8",
    "Motorola Edge 50 Pro",
    "Nothing Phone 2",
    "Vivo V30 Pro",
    "Vivo Y27",
]

# ─────────────────────────────────────────────────────────────
# Countries & Sources
# ─────────────────────────────────────────────────────────────
COUNTRIES = {
    "eg": {
        "name": "مصر", "currency": "EGP",
        "sources": {
            "jumia":    {"domain": "www.jumia.com.eg"},
            "noon":     {"locale": "egypt-en"},
            "opensooq": {"sub": "eg"},
        },
    },
    "sa": {
        "name": "السعودية", "currency": "SAR",
        "sources": {
            "noon":     {"locale": "saudi-en"},
            "opensooq": {"sub": "sa"},
        },
    },
    "ae": {
        "name": "الإمارات", "currency": "AED",
        "sources": {
            "noon":     {"locale": "uae-en"},
            "opensooq": {"sub": "uae"},
        },
    },
    "ma": {
        "name": "المغرب", "currency": "MAD",
        "sources": {
            "jumia":    {"domain": "www.jumia.ma"},
            "opensooq": {"sub": "ma"},
        },
    },
    "dz": {
        "name": "الجزائر", "currency": "DZD",
        "sources": {
            "jumia":    {"domain": "www.jumia.dz"},
            "opensooq": {"sub": "dz"},
        },
    },
    "sy": {"name": "سوريا",   "currency": "SYP", "sources": {"opensooq": {"sub": "sy"}}},
    "jo": {"name": "الأردن",  "currency": "JOD", "sources": {"opensooq": {"sub": "jo"}}},
    "iq": {"name": "العراق",  "currency": "IQD", "sources": {"opensooq": {"sub": "iq"}}},
    "kw": {"name": "الكويت",  "currency": "KWD", "sources": {"opensooq": {"sub": "kw"}}},
    "bh": {"name": "البحرين", "currency": "BHD", "sources": {"opensooq": {"sub": "bh"}}},
    "om": {"name": "عمان",    "currency": "OMR", "sources": {"opensooq": {"sub": "om"}}},
    "ly": {"name": "ليبيا",   "currency": "LYD", "sources": {"opensooq": {"sub": "ly"}}},
    "tn": {"name": "تونس",    "currency": "TND", "sources": {"opensooq": {"sub": "tn"}}},
    "sd": {"name": "السودان",  "currency": "SDG", "sources": {"opensooq": {"sub": "sd"}}},
    "lb": {"name": "لبنان",   "currency": "LBP", "sources": {"opensooq": {"sub": "lb"}}},
    "ps": {"name": "فلسطين",  "currency": "ILS", "sources": {"opensooq": {"sub": "ps"}}},
    "ye": {"name": "اليمن",   "currency": "YER", "sources": {"opensooq": {"sub": "ye"}}},
}

# ═════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════

def _ua():
    return random.choice(USER_AGENTS)


def _delay():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


def _num(text: str):
    """Return integer-string price from messy text, or None."""
    if not text:
        return None
    cleaned = re.sub(r"[^\d.,]", " ", str(text))
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)", cleaned)
    if m:
        try:
            return str(int(float(m.group(1).replace(",", ""))))
        except ValueError:
            pass
    return None


def _is_accessory(title: str) -> bool:
    words = set(re.findall(r"\w+", title.lower()))
    return bool(words & ACCESSORY_KW)


def _relevant(phone_name: str, title: str, threshold=0.45) -> bool:
    """True when enough words from the phone name appear in the title."""
    pwords = phone_name.lower().split()
    tlow = title.lower()
    hits = sum(1 for w in pwords if w in tlow)
    return hits >= len(pwords) * threshold


def _above_min(price_str, currency):
    """Reject prices that are too low to be a real phone."""
    try:
        return int(price_str) >= MIN_PHONE_PRICE.get(currency, 0)
    except (ValueError, TypeError):
        return False


def _session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": _ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
    })
    return s


# ═════════════════════════════════════════════════════════════
# Jumia Scraper
# ═════════════════════════════════════════════════════════════

def scrape_jumia(session, phone, cfg, currency):
    domain = cfg["domain"]
    url = f"https://{domain}/catalog/?q={quote_plus(phone)}"
    log.info("  🟠 Jumia (%s) …", domain)

    try:
        r = session.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": _ua()})
        r.raise_for_status()
    except Exception as e:
        log.warning("    ✖ request failed: %s", e)
        return None

    soup = BeautifulSoup(r.text, "lxml")

    # --- strategy 1: product cards ---
    cards = soup.select("article.prd") or soup.select("div[data-sku]") or soup.select("section.card")
    for card in cards:
        name_el = card.select_one(".name") or card.select_one("h3") or card.select_one(".info a")
        if not name_el:
            continue
        title = name_el.get_text(" ", strip=True)
        if _is_accessory(title) or not _relevant(phone, title):
            continue
        # price
        p_el = card.select_one("[data-price]")
        if p_el:
            price = _num(p_el.get("data-price"))
            if price and _above_min(price, currency):
                log.info("    ✔ %s → %s", title[:45], price)
                return price
        p_el = card.select_one(".prc") or card.select_one(".price")
        if p_el:
            price = _num(p_el.get_text())
            if price and _above_min(price, currency):
                log.info("    ✔ %s → %s", title[:45], price)
                return price

    # --- strategy 2: JSON-LD ---
    for tag in soup.select('script[type="application/ld+json"]'):
        try:
            ld = json.loads(tag.string or "{}")
            items = ld if isinstance(ld, list) else [ld]
            for item in items:
                if "offers" in item:
                    p = item["offers"].get("price") or item["offers"].get("lowPrice")
                    if p:
                        ps = str(int(float(p)))
                        if _above_min(ps, currency):
                            log.info("    ✔ JSON-LD → %s", ps)
                            return ps
        except Exception:
            pass

    # --- strategy 3: regex on full text ---
    currency_symbols = {"EGP": "EGP", "MAD": "MAD", "DZD": "DZD"}
    sym = currency_symbols.get(currency, "")
    if sym:
        pat = re.compile(rf"{sym}\s*([\d,]+(?:\.\d+)?)")
        for m in pat.finditer(r.text):
            price = _num(m.group(1))
            if price and _above_min(price, currency):
                log.info("    ✔ regex → %s", price)
                return price

    log.info("    – no match")
    return None


# ═════════════════════════════════════════════════════════════
# Noon Scraper
# ═════════════════════════════════════════════════════════════

def scrape_noon(session, phone, cfg, currency):
    locale = cfg["locale"]
    q = quote_plus(phone)
    log.info("  🟡 Noon (%s) …", locale)

    # --- attempt 1: internal catalog API ---
    api_urls = [
        f"https://www.noon.com/_svc/catalog/api/v3/u/{locale}/search?q={q}&limit=20",
        f"https://www.noon.com/_svc/catalog/api/v3/search?q={q}&locale={locale}&limit=20",
    ]
    for api_url in api_urls:
        try:
            headers = {
                "User-Agent": _ua(),
                "Accept": "application/json",
                "Referer": f"https://www.noon.com/{locale}/search/?q={q}",
                "X-Locale": locale.replace("-", "_"),
            }
            r = session.get(api_url, headers=headers, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                continue
            data = r.json()
            hits = data.get("hits") or data.get("results") or []
            for hit in hits:
                title = hit.get("name") or hit.get("name_en") or hit.get("title") or ""
                if _is_accessory(title) or not _relevant(phone, title):
                    continue
                price = hit.get("sale_price") or hit.get("price") or hit.get("offer", {}).get("sale_price")
                if price:
                    ps = str(int(float(price)))
                    if _above_min(ps, currency):
                        log.info("    ✔ API %s → %s", title[:40], ps)
                        return ps
        except Exception:
            continue

    # --- attempt 2: page scrape + __NEXT_DATA__ ---
    try:
        page_url = f"https://www.noon.com/{locale}/search/?q={q}"
        r = session.get(page_url, headers={"User-Agent": _ua()}, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            # Next.js data
            nd = soup.select_one("script#__NEXT_DATA__")
            if nd and nd.string:
                try:
                    jd = json.loads(nd.string)
                    props = jd.get("props", {}).get("pageProps", {})
                    catalog = props.get("catalog") or props.get("searchResult") or {}
                    hits = catalog.get("hits") or catalog.get("products") or []
                    for hit in hits:
                        title = hit.get("name") or hit.get("title") or ""
                        if _is_accessory(title) or not _relevant(phone, title):
                            continue
                        price = hit.get("sale_price") or hit.get("price")
                        if price:
                            ps = str(int(float(price)))
                            if _above_min(ps, currency):
                                log.info("    ✔ NEXT %s → %s", title[:40], ps)
                                return ps
                except Exception:
                    pass

            # JSON-LD fallback
            for tag in soup.select('script[type="application/ld+json"]'):
                try:
                    ld = json.loads(tag.string or "{}")
                    items = ld if isinstance(ld, list) else [ld]
                    for item in items:
                        offers = item.get("offers", {})
                        p = offers.get("price") or offers.get("lowPrice")
                        if p:
                            ps = str(int(float(p)))
                            if _above_min(ps, currency):
                                log.info("    ✔ LD → %s", ps)
                                return ps
                except Exception:
                    pass
    except Exception as e:
        log.warning("    ✖ page scrape: %s", e)

    log.info("    – no match")
    return None


# ═════════════════════════════════════════════════════════════
# OpenSooq Scraper
# ═════════════════════════════════════════════════════════════

def scrape_opensooq(session, phone, cfg, currency):
    sub = cfg["sub"]
    q = quote_plus(phone)
    base = f"https://{sub}.opensooq.com"
    # Try category-filtered URL first, then generic search
    urls = [
        f"{base}/en/mobiles-tablets/mobiles?term={q}",
        f"{base}/en/find?term={q}",
    ]
    log.info("  🟢 OpenSooq (%s) …", sub)

    for url in urls:
        try:
            headers = {
                "User-Agent": _ua(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
                "Referer": f"{base}/",
                "Cache-Control": "no-cache",
            }
            r = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                log.debug("    status %d for %s", r.status_code, url)
                continue

            soup = BeautifulSoup(r.text, "lxml")

            # JSON-LD
            for tag in soup.select('script[type="application/ld+json"]'):
                try:
                    ld = json.loads(tag.string or "{}")
                    items = ld if isinstance(ld, list) else [ld]
                    for item in items:
                        if item.get("@type") in ("Product", "Offer") or "offers" in item:
                            offers = item.get("offers", item)
                            if isinstance(offers, list):
                                offers = offers[0] if offers else {}
                            p = offers.get("price") or offers.get("lowPrice")
                            if p:
                                ps = str(int(float(p)))
                                if _above_min(ps, currency):
                                    log.info("    ✔ LD → %s", ps)
                                    return ps
                except Exception:
                    pass

            # CSS selectors
            for sel in (".postPrice", ".price", "[data-price]", ".priceTag", ".post-price"):
                for el in soup.select(sel):
                    price = _num(el.get_text())
                    if price and _above_min(price, currency):
                        log.info("    ✔ CSS → %s", price)
                        return price

            # Regex
            m = re.search(r'"price"\s*:\s*"?(\d[\d,.]*)"?', r.text)
            if m:
                price = _num(m.group(1))
                if price and _above_min(price, currency):
                    log.info("    ✔ regex → %s", price)
                    return price

        except Exception as e:
            log.warning("    ✖ %s: %s", url, e)

    log.info("    – no match")
    return None


# ═════════════════════════════════════════════════════════════
# Orchestrator
# ═════════════════════════════════════════════════════════════

SCRAPERS = {
    "jumia":    scrape_jumia,
    "noon":     scrape_noon,
    "opensooq": scrape_opensooq,
}


def scrape_phone(session, phone_name):
    """Scrape one phone across every country → dict."""
    row = {"phone_name": phone_name}

    for code, country in COUNTRIES.items():
        currency = country["currency"]
        found = []

        for src_name, src_cfg in country["sources"].items():
            fn = SCRAPERS.get(src_name)
            if not fn:
                continue
            try:
                price = fn(session, phone_name, src_cfg, currency)
                if price:
                    found.append(int(price))
            except Exception as e:
                log.error("    💥 %s/%s: %s", src_name, code, e)
            _delay()

        row[f"price_{code}"] = str(min(found)) if found else ""

    row["last_updated"] = str(date.today())
    return row


def load_existing():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def merge(old_list, new_list):
    """Keep old prices where the new run found nothing."""
    old_map = {item["phone_name"]: item for item in old_list}
    for new in new_list:
        old = old_map.get(new["phone_name"], {})
        for k, v in new.items():
            if k.startswith("price_") and not v and old.get(k):
                new[k] = old[k]
    return new_list


# ─────────────────────────────────────────────────────────────
def main():
    log.info("═" * 55)
    log.info("🚀  Arab Phone Prices Scraper")
    log.info("📱  Phones : %d", len(PHONES_TO_TRACK))
    log.info("🌍  Countries : %d", len(COUNTRIES))
    log.info("═" * 55)

    session = _session()
    old = load_existing()
    results = []

    for i, phone in enumerate(PHONES_TO_TRACK, 1):
        log.info("\n─── [%d/%d] %s ───", i, len(PHONES_TO_TRACK), phone)
        row = scrape_phone(session, phone)
        results.append(row)
        # rotate UA every 5 phones
        if i % 5 == 0:
            session.headers["User-Agent"] = _ua()

    final = merge(old, results)
    final.sort(key=lambda x: x["phone_name"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    total = sum(1 for r in final for k, v in r.items() if k.startswith("price_") and v)
    log.info("\n═" * 55)
    log.info("✅  Saved %d phones → %s", len(final), OUTPUT_FILE)
    log.info("📊  Total prices found: %d", total)
    log.info("═" * 55)


if __name__ == "__main__":
    main()
