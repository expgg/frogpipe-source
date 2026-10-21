"""
FrogPipe — Configuration & System Utilities
Architected by Al Hossain Rifat
"""

import os
import sys
import io
import re
import urllib.parse
from typing import Optional, Dict

# Force UTF-8 on Windows terminal to prevent cp1252 encoding crashes
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Path & Environment Resolution
# ---------------------------------------------------------------------------

def get_desktop_dir() -> str:
    """Returns the absolute path to the user's Desktop directory."""
    desktop = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Desktop")
    if not os.path.isdir(desktop):
        # Fallback to local desktop folder
        desktop = os.path.abspath("./output_desktop")
        os.makedirs(desktop, exist_ok=True)
    return desktop


def get_temp_crawl_dir() -> str:
    """Returns the absolute path for temporary raw crawl outputs."""
    p = os.path.abspath("./temp_crawl")
    os.makedirs(p, exist_ok=True)
    return p


def get_screaming_frog_cli() -> Optional[str]:
    """Finds path to Screaming Frog SEO Spider CLI executable."""
    candidates = [
        r"X:\APPS\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe",
        r"C:\Program Files\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe",
        r"C:\Program Files (x86)\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe",
        r"D:\APPS\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


# ---------------------------------------------------------------------------
# Domain & URL Sanitizers
# ---------------------------------------------------------------------------

def normalize_url(raw_url: str) -> str:
    """Ensures URL has a proper scheme (defaulting to https://)."""
    raw_url = raw_url.strip()
    if not raw_url.startswith("http://") and not raw_url.startswith("https://"):
        raw_url = "https://" + raw_url
    return raw_url


def extract_clean_domain(url: str) -> str:
    """
    Extracts a sanitized domain slug for folder naming.
    e.g. 'https://www.drstangale.com/about/' -> 'drstangale_com'
    """
    parsed = urllib.parse.urlparse(normalize_url(url))
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    # Replace non-alphanumeric chars with underscore
    clean_name = re.sub(r"[^a-zA-Z0-9]+", "_", netloc).strip("_")
    return clean_name or "target_site"


def get_target_seo_folder(domain_or_url: str) -> str:
    """
    Resolves the teacher-specified folder path on Desktop:
    Desktop/SEO_<Website_Name>
    """
    clean_slug = extract_clean_domain(domain_or_url)
    folder_name = f"SEO_{clean_slug}"
    return os.path.join(get_desktop_dir(), folder_name)


# ---------------------------------------------------------------------------
# The 9 Audit Datasets Definition
# ---------------------------------------------------------------------------

# Exact tab names requested by the teacher's rubric
AUDIT_TABS_MAPPING = {
    "issues": {
        "title": "Issues",
        "target_file": "1_Issues.csv",
        "description": "Executive Overview of all SEO issues, warnings, and opportunities.",
    },
    "h1_h2": {
        "title": "H1 + H2",
        "target_file": "2_H1_H2.csv",
        "description": "Primary and secondary heading tags analysis.",
    },
    "meta": {
        "title": "Meta Tags + Meta description",
        "target_file": "3_Meta_Tags_Description.csv",
        "description": "Page meta descriptions, character lengths, and snippets.",
    },
    "content": {
        "title": "Content",
        "target_file": "4_Content.csv",
        "description": "Word counts, text ratios, and content depth analysis.",
    },
    "page_titles": {
        "title": "ALL page Titles",
        "target_file": "5_Page_Titles.csv",
        "description": "Page title tags, character lengths, and pixel widths.",
    },
    "urls": {
        "title": "URLs",
        "target_file": "6_URLs.csv",
        "description": "Complete list of internal crawlable URLs and status.",
    },
    "images": {
        "title": "Images",
        "target_file": "7_Images.csv",
        "description": "Image assets, missing alt text, and file sizes.",
    },
    "search_console": {
        "title": "Search Console Status",
        "target_file": "8_Search_Console_Status.csv",
        "description": "Search console status / HTTP response codes verification.",
    },
    "canonicals": {
        "title": "Canonicals",
        "target_file": "9_Canonicals.csv",
        "description": "Canonical tag implementation and indexability signals.",
    },
}
