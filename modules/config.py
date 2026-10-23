"""
FrogPipe — Configuration & System Utilities
Architected by Al Hossain Rifat
"""

import os
import sys
import io
import re
import json
import urllib.parse
from typing import Optional, Dict, Any

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
# Config Persistence (config.json)
# ---------------------------------------------------------------------------

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
DEFAULT_EXAMPLE_URL = "https://r1fat.pages.dev"


def load_config() -> dict:
    """Loads configuration dictionary from config.json."""
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config_value(key: str, value: Any) -> None:
    """Saves a key-value pair to config.json."""
    cfg = load_config()
    cfg[key] = value
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
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


import platform
import shutil


def get_screaming_frog_cli() -> Optional[str]:
    """Finds path to Screaming Frog SEO Spider CLI executable across Windows, macOS, and Linux."""
    # 1. Check saved config.json
    cfg = load_config()
    saved_path = cfg.get("screaming_frog_cli", "").strip().strip('"\'')
    if saved_path and os.path.isfile(saved_path):
        return saved_path

    # 2. Check system-specific standard candidate paths
    system = platform.system()
    candidates = []
    if system == "Windows":
        candidates = [
            r"X:\APPS\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe",
            r"C:\Program Files\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe",
            r"C:\Program Files (x86)\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe",
            r"D:\APPS\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe",
        ]
    elif system == "Darwin":  # macOS
        candidates = [
            "/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/ScreamingFrogSEOSpiderCli",
            "/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/ScreamingFrogSEOSpiderLauncher"
        ]
    else:  # Linux / Unix
        which_path = shutil.which("screamingfrogseospider") or shutil.which("screamingfrogseospidercli")
        if which_path:
            candidates.append(which_path)
        candidates.extend([
            "/usr/bin/screamingfrogseospider",
            "/usr/local/bin/screamingfrogseospider"
        ])

    for c in candidates:
        if os.path.isfile(c):
            # Auto-persist to config for fast future lookups
            save_config_value("screaming_frog_cli", c)
            return c
    return None


def load_auth_token() -> Optional[str]:
    """Loads optional Google Apps Script secret authentication token from config.json."""
    cfg = load_config()
    token = cfg.get("auth_token", "").strip()
    return token if token else None


def load_spider_config_path() -> Optional[str]:
    """Loads optional custom .seospiderconfig profile path from config.json."""
    cfg = load_config()
    path = cfg.get("spider_config_file", "").strip().strip('"\'')
    return path if path and os.path.isfile(path) else None



def prompt_and_save_frog_cli() -> Optional[str]:
    """Interactively prompts user for the Screaming Frog CLI path and persists it."""
    print("\n[!] Screaming Frog CLI was not detected in standard directories.")
    print("Please provide the full path to ScreamingFrogSEOSpiderCli.exe (or its install directory).")
    
    while True:
        raw_path = input("Enter Screaming Frog CLI path (or 'q' to cancel): ").strip().strip('"\'')
        if not raw_path or raw_path.lower() == 'q':
            return None
        
        # If user entered a directory, append the executable name
        candidate = raw_path
        if os.path.isdir(candidate):
            candidate = os.path.join(candidate, "ScreamingFrogSEOSpiderCli.exe")
            
        if os.path.isfile(candidate):
            save_config_value("screaming_frog_cli", candidate)
            print(f"  [✓] Linked and saved to config.json: {candidate}\n")
            return candidate
        else:
            print(f"  [✗] File not found at: {candidate}. Please try again.")



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


def get_project_root() -> str:
    """Returns absolute path to the FrogPipe project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_audits_vault_dir() -> str:
    """Returns absolute path to the audited_sites directory at project root."""
    d = os.path.join(get_project_root(), "audited_sites")
    os.makedirs(d, exist_ok=True)
    return d


def get_target_seo_folder(domain_or_url: str) -> str:
    """
    Resolves the dedicated audit directory inside audited_sites/:
    audited_sites/SEO_<clean_domain>
    """
    clean_slug = extract_clean_domain(domain_or_url)
    folder_name = f"SEO_{clean_slug}"
    target_path = os.path.join(get_audits_vault_dir(), folder_name)
    os.makedirs(target_path, exist_ok=True)
    return target_path



def load_sheet_webhook_url() -> Optional[str]:
    """Loads saved Google Apps Script webhook URL from config.json."""
    cfg = load_config()
    url = cfg.get("sheet_webhook_url", "").strip()
    return url if url and "YOUR_DEPLOYMENT_ID" not in url else None


def save_sheet_webhook_url(url: str) -> None:
    """Saves Google Apps Script webhook URL to config.json."""
    save_config_value("sheet_webhook_url", url.strip())


# ---------------------------------------------------------------------------
# The 11 Audit Datasets Definition (Zero Data Pruned, Separate H1 & H2, Separate Meta Description & Meta Tags)
# ---------------------------------------------------------------------------

AUDIT_TABS_MAPPING = {
    "issues": {
        "title": "Issues",
        "target_file": "1_Issues.csv",
        "raw_source": "issues_overview_report.csv",
        "description": "Executive Overview of all SEO issues, warnings, and opportunities.",
    },
    "h1": {
        "title": "H1",
        "target_file": "2_H1.csv",
        "raw_source": "h1_all.csv",
        "description": "Primary H1 heading tags and character analysis.",
    },
    "h2": {
        "title": "H2",
        "target_file": "3_H2.csv",
        "raw_source": "h2_all.csv",
        "description": "Secondary H2 heading tags and structure analysis.",
    },
    "meta_desc": {
        "title": "Meta Description",
        "target_file": "4_Meta_Description.csv",
        "raw_source": "meta_description_all.csv",
        "description": "Page meta descriptions, character lengths, and search snippet analysis.",
    },
    "meta_tags": {
        "title": "Meta Tags",
        "target_file": "5_Meta_Tags.csv",
        "raw_source": "directives_all.csv",
        "description": "Meta robots directives, canonical tags, noindex/nofollow flags, and keywords.",
    },
    "content": {
        "title": "Content",
        "target_file": "6_Content.csv",
        "raw_source": "content_all.csv",
        "description": "Word counts, text ratios, and content depth analysis.",
    },
    "page_titles": {
        "title": "ALL page Titles",
        "target_file": "7_Page_Titles.csv",
        "raw_source": "page_titles_all.csv",
        "description": "Page title tags, character lengths, and pixel widths.",
    },
    "urls": {
        "title": "URLs",
        "target_file": "8_URLs.csv",
        "raw_source": "internal_all.csv",
        "description": "Complete list of internal crawlable URLs and status codes.",
    },
    "images": {
        "title": "Images",
        "target_file": "9_Images.csv",
        "raw_source": "images_all.csv",
        "description": "Image assets, missing alt text, dimensions, and file sizes.",
    },
    "search_console": {
        "title": "Search Console Status",
        "target_file": "10_Search_Console_Status.csv",
        "raw_source": "search_console_all.csv",
        "description": "Search console status / HTTP response codes verification.",
    },
    "canonicals": {
        "title": "Canonicals",
        "target_file": "11_Canonicals.csv",
        "raw_source": "canonicals_all.csv",
        "description": "Canonical tag implementation and indexability signals.",
    },
}

