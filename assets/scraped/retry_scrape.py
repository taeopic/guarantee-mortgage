"""
Guarantee Mortgage - Retry Scrape with Browser Headers
Phase 1: Download team headshots and logo from captured URLs + live site crawl
"""

import requests
import time
import os
import re
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

BASE_URL = "https://guaranteemc.com"
PROJECT_ROOT = Path("C:/Users/Bladerah/Aeopic/prospects/guarantee-mortgage")
SCRAPED_DIR = PROJECT_ROOT / "assets/scraped"
LOGOS_DIR = SCRAPED_DIR / "logos"
TEAM_DIR = SCRAPED_DIR / "team"

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

IMAGE_HEADERS = {
    **BROWSER_HEADERS,
    "Referer": "https://guaranteemc.com/",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin",
}

# Team member URL mapping from image-urls.txt
TEAM_URLS = {
    "team-colton-rembert.webp": "https://guaranteemc.com/wp-content/uploads/2015/09/Colton-Picture-2-247x300@2x.webp",
    "team-connie-daniels.webp": "https://guaranteemc.com/wp-content/uploads/2015/09/Daniels-Connie-headshot-2-253x300@2x.webp",
    "team-jerod-rosenbarker.webp": "https://guaranteemc.com/wp-content/uploads/2015/09/Jerod.webp",
    "team-kayla-brock.webp": "https://guaranteemc.com/wp-content/uploads/2015/09/Kayla-Brock-Headshot-300x300@2x.webp",
    "team-dean-kennemer.webp": "https://guaranteemc.com/wp-content/uploads/2015/09/Kennemer-Dean-headshot-2-768x888-1.webp",
    "team-blake-hutto.webp": "https://guaranteemc.com/wp-content/uploads/2025/05/Blake-hutto-768x768-1.webp",
    "team-hong-liu.webp": "https://guaranteemc.com/wp-content/uploads/2025/05/Hong-3-768x887-1.webp",
    "team-jordan-guggenheim.png": "https://guaranteemc.com/wp-content/uploads/2025/05/Jordan-Headshot.png",
    "team-royce-horn.webp": "https://guaranteemc.com/wp-content/uploads/2025/05/royce-horn.webp",
    "team-stephen-owens.jpg": "https://guaranteemc.com/wp-content/uploads/2025/05/stephen-owens-pictur-2.jpg",
}

# These team members had null photos - need to find from crawl
MISSING_TEAM = ["Bryce Kennemer", "Parker Speer", "Troy Herring"]

# Logo candidate URLs to try
LOGO_CANDIDATES = [
    # Standard WP logo paths
    "https://guaranteemc.com/wp-content/uploads/2024/04/Purchase_Icon2.webp",  # brand icon from list
    "https://guaranteemc.com/wp-content/themes/guarantee-mortgage/images/logo.png",
    "https://guaranteemc.com/wp-content/themes/guarantee-mortgage/img/logo.png",
    "https://guaranteemc.com/wp-content/uploads/logo.png",
    "https://guaranteemc.com/wp-content/uploads/logo.svg",
    "https://guaranteemc.com/images/logo.png",
    "https://guaranteemc.com/favicon.ico",
]

def get_session():
    s = requests.Session()
    s.headers.update(BROWSER_HEADERS)
    return s

def download_image(session, url, save_path, label=""):
    """Download a single image with browser headers. Returns True on success."""
    try:
        r = session.get(url, headers=IMAGE_HEADERS, timeout=20, stream=True)
        if r.status_code == 200:
            content_type = r.headers.get("content-type", "")
            # Skip tiny files (icons/sprites < 2KB)
            content = r.content
            if len(content) < 2000:
                print(f"  SKIP (too small {len(content)}B): {url}")
                return False
            with open(save_path, "wb") as f:
                f.write(content)
            size_kb = len(content) // 1024
            print(f"  OK  [{size_kb}KB] {label} -> {os.path.basename(save_path)}")
            return True
        else:
            print(f"  {r.status_code}: {url}")
            return False
    except Exception as e:
        print(f"  ERR: {url} -- {e}")
        return False

def crawl_homepage_for_logo(session):
    """Fetch homepage HTML and parse logo img/link tags."""
    print("\n--- Crawling homepage for logo ---")
    try:
        r = session.get(BASE_URL, timeout=20)
        print(f"  Homepage status: {r.status_code}")
        if r.status_code != 200:
            return []
        html = r.text
        logo_urls = []

        # <img> with logo in src, class, id, or alt
        img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', html, re.IGNORECASE)
        for src in img_matches:
            if any(kw in src.lower() for kw in ["logo", "brand", "guarantee"]):
                full = urljoin(BASE_URL, src)
                if full not in logo_urls:
                    logo_urls.append(full)
                    print(f"  Found logo img: {full}")

        # og:image
        og_match = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if not og_match:
            og_match = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html, re.IGNORECASE)
        if og_match:
            url = og_match.group(1)
            print(f"  Found og:image: {url}")
            if url not in logo_urls:
                logo_urls.append(url)

        # favicon links
        favicon_matches = re.findall(r'<link[^>]+rel=["\'][^"\']*icon[^"\']*["\'][^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        for href in favicon_matches:
            full = urljoin(BASE_URL, href)
            print(f"  Found favicon: {full}")
            if full not in logo_urls:
                logo_urls.append(full)

        # Background-image URLs mentioning logo
        bg_matches = re.findall(r'background-image\s*:\s*url\(["\']?([^"\')\s]+)["\']?\)', html, re.IGNORECASE)
        for bg in bg_matches:
            if "logo" in bg.lower():
                full = urljoin(BASE_URL, bg)
                print(f"  Found bg logo: {full}")
                if full not in logo_urls:
                    logo_urls.append(full)

        return logo_urls
    except Exception as e:
        print(f"  ERR crawling homepage: {e}")
        return []

def crawl_team_page(session):
    """Try common team page URLs and find missing headshots."""
    print("\n--- Crawling team page for missing headshots ---")
    team_pages = [
        "https://guaranteemc.com/our-team/",
        "https://guaranteemc.com/team/",
        "https://guaranteemc.com/about-us/",
        "https://guaranteemc.com/about/",
        "https://guaranteemc.com/meet-the-team/",
        "https://guaranteemc.com/staff/",
    ]
    found = {}
    for page_url in team_pages:
        try:
            time.sleep(1.5)
            r = session.get(page_url, timeout=20)
            print(f"  {r.status_code}: {page_url}")
            if r.status_code != 200:
                continue
            html = r.text
            # Look for headshot patterns near known missing names
            for name in MISSING_TEAM:
                first = name.split()[0].lower()
                last = name.split()[-1].lower()
                # Find img tags near the name
                # Simple approach: find image URLs that contain first or last name
                img_urls = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
                for img_url in img_urls:
                    img_lower = img_url.lower()
                    if first in img_lower or last in img_lower:
                        full = urljoin(BASE_URL, img_url)
                        found[name] = full
                        print(f"  Found {name}: {full}")
        except Exception as e:
            print(f"  ERR: {page_url} -- {e}")
    return found

def try_wayback_logo(session):
    """Try Wayback Machine for logo if direct fetch failed."""
    print("\n--- Trying Wayback Machine for logo ---")
    wayback_url = "https://web.archive.org/web/2024/https://guaranteemc.com/"
    try:
        r = session.get(wayback_url, timeout=30)
        if r.status_code == 200:
            html = r.text
            # Look for logo in archived page
            img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', html, re.IGNORECASE)
            for src in img_matches:
                if "logo" in src.lower() and "guaranteemc" in src.lower():
                    print(f"  Wayback logo: {src}")
                    return src
    except Exception as e:
        print(f"  Wayback ERR: {e}")
    return None

def try_google_cache_logo(session):
    """Try Google cache for logo."""
    print("\n--- Trying Google cache ---")
    cache_url = "https://webcache.googleusercontent.com/search?q=cache:guaranteemc.com"
    try:
        r = session.get(cache_url, timeout=20)
        if r.status_code == 200:
            html = r.text
            img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
            for src in img_matches:
                if "logo" in src.lower() and "guaranteemc.com" in src.lower():
                    print(f"  Cache logo: {src}")
                    return src
    except Exception as e:
        print(f"  Cache ERR: {e}")
    return None

def main():
    session = get_session()
    results = {
        "logos": [],
        "team": {"downloaded": [], "missing": []},
        "errors": []
    }

    # --- STEP 1: Download team headshots ---
    print("\n=== STEP 1: Team Headshots ===")
    for filename, url in TEAM_URLS.items():
        save_path = TEAM_DIR / filename
        if save_path.exists():
            print(f"  SKIP (exists): {filename}")
            results["team"]["downloaded"].append(str(filename))
            continue
        time.sleep(1.5)
        ok = download_image(session, url, save_path, label=filename)
        if ok:
            results["team"]["downloaded"].append(str(filename))
        else:
            results["team"]["missing"].append(f"{filename} <- {url}")
        time.sleep(0.5)

    # --- STEP 2: Find logo from homepage ---
    print("\n=== STEP 2: Logo Hunt ===")
    time.sleep(1.5)
    logo_urls_from_html = crawl_homepage_for_logo(session)

    # Try candidates from HTML first, then hardcoded list
    all_logo_candidates = logo_urls_from_html + LOGO_CANDIDATES
    logo_saved = False

    for i, logo_url in enumerate(all_logo_candidates):
        if logo_saved and i >= len(logo_urls_from_html):
            break  # Got one, skip fallback candidates
        # Determine save name
        parsed = urlparse(logo_url)
        fname = os.path.basename(parsed.path)
        if not fname or fname in ["", "/"]:
            fname = f"logo-candidate-{i}.png"
        # Classify: favicon or logo
        if "favicon" in fname.lower() or fname == "favicon.ico":
            save_path = LOGOS_DIR / "favicon.ico"
        elif "logo" in fname.lower() or i < len(logo_urls_from_html):
            ext = os.path.splitext(fname)[1] or ".png"
            save_path = LOGOS_DIR / f"logo-primary{ext}" if not logo_saved else LOGOS_DIR / f"logo-alt-{i}{ext}"
        else:
            save_path = LOGOS_DIR / fname

        if save_path.exists():
            print(f"  SKIP (exists): {save_path.name}")
            if "favicon" not in save_path.name:
                logo_saved = True
            results["logos"].append(str(save_path.name))
            continue

        time.sleep(1.5)
        ok = download_image(session, logo_url, save_path, label="logo")
        if ok:
            results["logos"].append(str(save_path.name))
            if "favicon" not in save_path.name:
                logo_saved = True
        time.sleep(0.5)

    # Also get favicon directly
    favicon_path = LOGOS_DIR / "favicon.ico"
    if not favicon_path.exists():
        time.sleep(1.5)
        download_image(session, "https://guaranteemc.com/favicon.ico", favicon_path, label="favicon")

    # --- STEP 3: Find missing team headshots ---
    print("\n=== STEP 3: Missing Team Hunt ===")
    time.sleep(1.5)
    found_missing = crawl_team_page(session)
    for name, url in found_missing.items():
        first = name.split()[0].lower()
        last = name.split()[-1].lower()
        ext = os.path.splitext(urlparse(url).path)[1] or ".jpg"
        save_path = TEAM_DIR / f"team-{first}-{last}{ext}"
        time.sleep(1.5)
        ok = download_image(session, url, save_path, label=name)
        if ok:
            results["team"]["downloaded"].append(str(save_path.name))
            if name in MISSING_TEAM:
                MISSING_TEAM.remove(name)

    # Still missing?
    for name in MISSING_TEAM:
        results["team"]["missing"].append(f"{name} - no URL found")

    # --- STEP 4: Fallback for logo if nothing worked ---
    if not logo_saved:
        print("\n=== STEP 4: Logo Fallback ===")
        wayback_url = try_wayback_logo(session)
        if wayback_url:
            time.sleep(2)
            ext = os.path.splitext(urlparse(wayback_url).path)[1] or ".png"
            save_path = LOGOS_DIR / f"logo-primary{ext}"
            download_image(session, wayback_url, save_path, label="wayback-logo")
        else:
            google_url = try_google_cache_logo(session)
            if google_url:
                time.sleep(2)
                ext = os.path.splitext(urlparse(google_url).path)[1] or ".png"
                save_path = LOGOS_DIR / f"logo-primary{ext}"
                download_image(session, google_url, save_path, label="google-cache-logo")

    # --- SUMMARY ---
    print("\n=== SUMMARY ===")
    print(f"Logos saved:           {len(results['logos'])} files")
    for f in results["logos"]:
        print(f"  {f}")
    print(f"Team downloaded:       {len(results['team']['downloaded'])}/13")
    for f in results["team"]["downloaded"]:
        print(f"  {f}")
    if results["team"]["missing"]:
        print(f"Team MISSING ({len(results['team']['missing'])}):")
        for m in results["team"]["missing"]:
            print(f"  {m}")

    # Save summary JSON
    summary_path = SCRAPED_DIR / "scrape-retry-results.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {summary_path}")

if __name__ == "__main__":
    main()
