"""
FrogPipe — Google Sheets Live Engine & Excel Master Builder
Architected & Engineered by Al Hossain Rifat
Portfolio: https://r1fat.pages.dev
"""

import os
import csv
import json
import re
import requests
import pandas as pd
from typing import Dict, List, Any, Optional

try:
    import openpyxl
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False
    ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')


def sanitize_excel_cell(val: Any) -> str:
    """Sanitizes strings to strip control characters and binary artifacts forbidden by Excel/openpyxl."""
    if val is None:
        return ""
    val_str = str(val).strip()
    if not val_str:
        return ""
    val_str = ILLEGAL_CHARACTERS_RE.sub("", val_str)
    # Strip any remaining non-printable control characters except standard whitespace
    if any(ord(c) < 32 and c not in "\n\r\t" for c in val_str):
        val_str = "".join(c for c in val_str if c.isprintable() or c in "\n\r\t")
    return val_str


from modules.config import (
    AUDIT_TABS_MAPPING,
    load_sheet_webhook_url,
    save_sheet_webhook_url,
    load_auth_token,
    load_moz_credentials,
    extract_clean_domain
)
from modules.ui import (
    HAS_RICH,
    console,
    print_step,
    print_success,
    print_error,
    print_warning
)


def load_csv_as_matrix(file_path: str) -> List[List[Any]]:
    """Reads a CSV file into a 2D matrix preserving 100% of rows and columns with XML/Excel sanitization."""
    if not os.path.isfile(file_path):
        return []
    rows = []
    try:
        with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.reader(f)
            for r in reader:
                # Replace None or empty placeholders & strip XML/Excel-illegal control characters
                clean_row = [sanitize_excel_cell(col) for col in r]
                if any(clean_row):
                    rows.append(clean_row)
    except Exception:
        # Fallback using pandas
        try:
            df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
            raw_rows = [df.columns.tolist()] + df.values.tolist()
            rows = [[sanitize_excel_cell(col) for col in r] for r in raw_rows]
        except Exception:
            pass
    return rows


def get_moz_target_stats(moz_dict: Dict[str, Dict[str, Any]], host: str) -> Dict[str, Any]:
    """Retrieves Moz metrics with www/non-www and trailing slash normalization."""
    if not host or not moz_dict:
        return {}
    clean_host = host.lower().strip()
    bare = clean_host.replace("www.", "")
    for candidate in [clean_host, bare, f"www.{bare}"]:
        if candidate in moz_dict:
            return moz_dict[candidate]
    return {}


def fetch_moz_metrics(urls: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Fetches Domain Authority, Page Authority, and Spam Score from Moz API v2.
    Free tier allows 50 row queries per month. Gracefully skips if credentials are not configured.
    """
    access_id, secret_key = load_moz_credentials()
    if not access_id or not secret_key:
        return {}

    clean_targets = []
    import urllib.parse
    for u in urls:
        raw = u.strip()
        if not raw or "competitor-" in raw:
            continue
        parsed = urllib.parse.urlparse(raw if raw.startswith("http") else f"https://{raw}")
        target = parsed.netloc or parsed.path
        if target:
            bare = target.lower().strip().replace("www.", "")
            if bare not in clean_targets:
                clean_targets.append(bare)

    if not clean_targets:
        return {}

    try:
        endpoint = "https://lsapi.seomoz.com/v2/url_metrics"
        res = requests.post(
            endpoint,
            auth=(access_id, secret_key),
            json={"targets": clean_targets},
            timeout=10
        )
        if res.status_code == 200:
            data = res.json()
            metrics = {}
            for item in data.get("results_by_target", []):
                t = str(item.get("target") or "").lower().strip().replace("www.", "")
                stats = {
                    "da": str(int(item.get("domain_authority", 0))),
                    "pa": str(int(item.get("page_authority", 0))),
                    "ss": str(int(item.get("spam_score", 0)))
                }
                metrics[t] = stats
                metrics[f"www.{t}"] = stats
            print_success(f"Moz Recon Linked: [bold bright_green]{len(clean_targets)} domains analyzed live via Moz API[/bold bright_green]")
            return metrics
    except Exception:
        pass
    return {}


def build_competitors_matrix(client_domain: str, competitors: Optional[List[str]] = None) -> List[List[str]]:
    """Generates the 2D matrix for the Competitors Analysis tab per teacher rubric."""
    headers = [
        "Website",
        "DA",
        "PA",
        "SS",
        "Ranking Keywords ( Moz )",
        "DR",
        "Backlink",
        "Linking Websites",
        "Website Traffic",
        "Traffic Values"
    ]
    matrix = [headers]
    
    # Client row (Row 2)
    client_url = client_domain if client_domain.startswith("http") else f"https://{client_domain}"
    comp_list = competitors or []

    # Optional Live Moz Recon
    moz_targets = [client_url] + [c for c in comp_list if c and "competitor-" not in c]
    moz_data = fetch_moz_metrics(moz_targets)

    # Client DA / PA / SS
    import urllib.parse
    client_host = urllib.parse.urlparse(client_url).netloc
    client_moz = get_moz_target_stats(moz_data, client_host)
    c_da = client_moz.get("da", "-")
    c_pa = client_moz.get("pa", "-")
    c_ss = client_moz.get("ss", "-")

    matrix.append([client_url, c_da, c_pa, c_ss, "-", "-", "-", "-", "-", "-"])

    # 5 Rivals (Rows 3-7)
    for i in range(1, 6):
        if len(comp_list) >= i and comp_list[i - 1].strip():
            raw_c = comp_list[i - 1].strip()
            c_url = raw_c if raw_c.startswith("http") else f"https://{raw_c}"
            r_host = urllib.parse.urlparse(c_url).netloc
            r_moz = get_moz_target_stats(moz_data, r_host)
            r_da = r_moz.get("da", "-")
            r_pa = r_moz.get("pa", "-")
            r_ss = r_moz.get("ss", "-")
        else:
            c_url = f"https://competitor-{i}.com (Pending Recon)"
            r_da, r_pa, r_ss = "-", "-", "-"
        matrix.append([c_url, r_da, r_pa, r_ss, "-", "-", "-", "-", "-", "-"])

    return matrix


def build_executive_summary(target_folder: str, domain: str) -> List[List[str]]:
    """
    Computes an executive-grade, non-bloated SEO Health Scorecard and KPI Overview
    directly from the crawled datasets with zero-division protection.
    """
    matrix = [
        ["Metric & Diagnostic Check", "Audit Category", "Finding / Count", "Health Status"]
    ]

    total_urls = 0
    clean_200 = 0
    redirect_3xx = 0
    errors_4xx_5xx = 0
    missing_titles = 0
    truncated_titles = 0
    missing_desc = 0
    missing_h1 = 0
    thin_content = 0
    missing_alt = 0

    # 1. Analyze URLs & Status
    urls_path = os.path.join(target_folder, "8_URLs.csv")
    if os.path.isfile(urls_path):
        try:
            df = pd.read_csv(urls_path, low_memory=False, dtype=str)
            total_urls = len(df)
            for col in df.columns:
                if "status code" in col.lower():
                    codes = df[col].astype(str)
                    clean_200 = sum(1 for c in codes if c in ["200", "201"])
                    redirect_3xx = sum(1 for c in codes if c.startswith("3"))
                    errors_4xx_5xx = sum(1 for c in codes if c.startswith("4") or c.startswith("5"))
                    break
        except Exception:
            pass

    # 2. Analyze Titles
    titles_path = os.path.join(target_folder, "7_Page_Titles.csv")
    if os.path.isfile(titles_path):
        try:
            df = pd.read_csv(titles_path, low_memory=False, dtype=str)
            for col in df.columns:
                if col.lower() in ["title 1", "title", "page title"]:
                    missing_titles = sum(1 for t in df[col] if not str(t).strip() or str(t).lower() == "missing")
                if "length" in col.lower():
                    try:
                        lengths = pd.to_numeric(df[col], errors='coerce').fillna(0)
                        truncated_titles = sum(1 for l in lengths if l > 60)
                    except Exception:
                        pass
        except Exception:
            pass

    # 3. Analyze Meta Descriptions
    desc_path = os.path.join(target_folder, "4_Meta_Description.csv")
    if os.path.isfile(desc_path):
        try:
            df = pd.read_csv(desc_path, low_memory=False, dtype=str)
            for col in df.columns:
                if "meta description 1" in col.lower() or "description" in col.lower():
                    missing_desc = sum(1 for d in df[col] if not str(d).strip() or str(d).lower() == "missing")
                    break
        except Exception:
            pass

    # 4. Analyze H1
    h1_path = os.path.join(target_folder, "2_H1.csv")
    if os.path.isfile(h1_path):
        try:
            df = pd.read_csv(h1_path, low_memory=False, dtype=str)
            for col in df.columns:
                if col.lower() in ["h1-1", "h1"]:
                    missing_h1 = sum(1 for h in df[col] if not str(h).strip() or str(h).lower() == "missing")
                    break
        except Exception:
            pass

    # 5. Analyze Content
    content_path = os.path.join(target_folder, "6_Content.csv")
    if os.path.isfile(content_path):
        try:
            df = pd.read_csv(content_path, low_memory=False, dtype=str)
            for col in df.columns:
                if "word count" in col.lower() or "words" in col.lower():
                    try:
                        words = pd.to_numeric(df[col], errors='coerce').fillna(0)
                        thin_content = sum(1 for w in words if 0 < w < 300)
                    except Exception:
                        pass
                    break
        except Exception:
            pass

    # 6. Analyze Images
    img_path = os.path.join(target_folder, "9_Images.csv")
    if os.path.isfile(img_path):
        try:
            df = pd.read_csv(img_path, low_memory=False, dtype=str)
            for col in df.columns:
                if "alt text" in col.lower() or "missing alt" in col.lower():
                    missing_alt = sum(1 for a in df[col] if not str(a).strip() or str(a).lower() in ["missing", "0"])
                    break
        except Exception:
            pass

    # Calculate overall health score with zero-url protection
    if total_urls == 0:
        score = 0
        grade = "Grade N/A (Incomplete Crawl)"
        health_status = "Action Required"
        clean_status = "No Data"
        broken_status = "N/A"
        redirect_status = "N/A"
    else:
        penalty = (errors_4xx_5xx * 6) + (missing_h1 * 2) + (missing_desc * 1.5) + (missing_titles * 3) + (thin_content * 2)
        score = max(25, min(100, int(100 - penalty)))
        if score >= 90:
            grade = "Grade A+ (Exceptional)"
            health_status = "Optimal"
        elif score >= 80:
            grade = "Grade A (Solid Health)"
            health_status = "Healthy"
        elif score >= 65:
            grade = "Grade B (Minor Optimizations Needed)"
            health_status = "Attention Required"
        else:
            grade = "Grade C (Critical Action Required)"
            health_status = "Action Required"

        clean_status = "Optimal" if clean_200 > 0 else "Review"
        broken_status = "Perfect (Zero Errors)" if errors_4xx_5xx == 0 else "Action Required"
        redirect_status = "Normal" if redirect_3xx < total_urls * 0.2 else "Review Needed"

    matrix.append(["Overall SEO Health Score", "Executive Rating", f"{score}/100 • {grade}", health_status])
    matrix.append(["Total Crawled Pages", "Site Architecture", f"{total_urls:,} Pages", "Verified" if total_urls > 0 else "No Data"])
    matrix.append(["Clean HTTP 200 Pages", "Protocol Health", f"{clean_200:,} Pages", clean_status])
    matrix.append(["Broken Links & Errors (4xx/5xx)", "Technical SEO", f"{errors_4xx_5xx:,} Pages", broken_status])
    matrix.append(["Redirects (3xx)", "Protocol Routing", f"{redirect_3xx:,} Pages", redirect_status])
    matrix.append(["Missing Page Titles", "On-Page Metadata", f"{missing_titles:,} Pages", "Perfect" if missing_titles == 0 else "Action Required"])
    matrix.append(["Truncated Titles (> 60 Chars)", "SERP Display", f"{truncated_titles:,} Pages", "Optimal" if truncated_titles == 0 else "Review Needed"])
    matrix.append(["Missing Meta Descriptions", "CTR Optimization", f"{missing_desc:,} Pages", "Perfect" if missing_desc == 0 else "Action Required"])
    matrix.append(["Missing Primary H1 Headings", "Semantic Hierarchy", f"{missing_h1:,} Pages", "Perfect" if missing_h1 == 0 else "Action Required"])
    matrix.append(["Thin Content Pages (< 300 words)", "Content Depth", f"{thin_content:,} Pages", "Optimal" if thin_content == 0 else "Review Needed"])
    matrix.append(["Images Missing Alt Text", "Image Accessibility", f"{missing_alt:,} Assets", "Perfect" if missing_alt == 0 else "Action Required"])

    return matrix


TAB_HEX_COLORS = {
    "Executive Summary": "0F172A",
    "Competitors Analysis": "F59E0B",
    "Issues": "EF4444",
    "H1": "10B981",
    "H2": "06B6D4",
    "Meta Description": "8B5CF6",
    "Meta Tags": "6366F1",
    "Content": "14B8A6",
    "ALL page Titles": "3B82F6",
    "URLs": "475569",
    "Images": "EC4899",
    "Search Console Status": "F97316",
    "HTTP Status & Response Codes": "F97316",
    "Canonicals": "0EA5E9",
}



def get_column_color_preset(col_name: str) -> dict:
    """
    Color Circle Theory Harmonic Palette Engine for Excel:
    Maps column semantic identities into cohesive, harmonized color families:
      - Addressing & URLs: Deep Sapphire Navy (#1E3A8A / #F0F4F8)
      - Health & HTTP Protocols: Deep Forest Emerald (#064E3B / #F0FDF4)
      - Editorial & Headings/Titles: Deep Ocean Teal (#0F766E / #F0FDFA)
      - Meta Descriptions & SERP: Deep Royal Violet (#581C87 / #FAF5FF)
      - Directives & Robots Directives: Deep Twilight Indigo (#312E81 / #EEF2FF)
      - Quantitative Metrics & Lengths: Deep Bronze Amber (#78350F / #FFFBEB)
      - Quality & Diagnostic Issues: Deep Ruby Crimson (#881337 / #FFF1F2)
      - Media & Image Assets: Deep Raspberry Plum (#701A75 / #FDF2F8)
    """
    col = str(col_name or "").lower()

    if any(k in col for k in ["address", "url", "link", "destination", "source", "canonical"]):
        return {
            "header_bg": "1E3A8A",
            "lane_even": "FFFFFF",
            "lane_odd": "F0F4F8",
            "font_color": "0F172A"
        }
    if any(k in col for k in ["status code", "response code", "status", "protocol"]):
        return {
            "header_bg": "064E3B",
            "lane_even": "FFFFFF",
            "lane_odd": "F0FDF4",
            "font_color": "064E3B"
        }
    if any(k in col for k in ["title", "h1", "h2", "snippet", "heading"]):
        return {
            "header_bg": "0F766E",
            "lane_even": "FFFFFF",
            "lane_odd": "F0FDFA",
            "font_color": "134E4A"
        }
    if "description" in col:
        return {
            "header_bg": "581C87",
            "lane_even": "FFFFFF",
            "lane_odd": "FAF5FF",
            "font_color": "3B0764"
        }
    if any(k in col for k in ["indexability", "directive", "robot", "meta"]):
        return {
            "header_bg": "312E81",
            "lane_even": "FFFFFF",
            "lane_odd": "EEF2FF",
            "font_color": "1E1B4B"
        }
    if any(k in col for k in ["length", "count", "word", "width", "ratio", "size", "occurrences", "bytes"]):
        return {
            "header_bg": "78350F",
            "lane_even": "FFFFFF",
            "lane_odd": "FFFBEB",
            "font_color": "451A03"
        }
    if any(k in col for k in ["issue", "priority", "severity", "error", "warning", "how to fix"]):
        return {
            "header_bg": "881337",
            "lane_even": "FFFFFF",
            "lane_odd": "FFF1F2",
            "font_color": "4C0519"
        }
    if any(k in col for k in ["image", "alt", "picture", "media"]):
        return {
            "header_bg": "701A75",
            "lane_even": "FFFFFF",
            "lane_odd": "FDF2F8",
            "font_color": "4A044E"
        }

    return {
        "header_bg": "1E293B",
        "lane_even": "FFFFFF",
        "lane_odd": "F8FAFC",
        "font_color": "1E293B"
    }


def generate_offline_excel(
    target_folder: str,
    domain: str,
    tabs_data: Dict[str, List[List[Any]]],
    max_excel_rows: int = 15000
) -> Optional[str]:
    """
    Builds an executive multi-tab Excel workbook (.xlsx) matching Google Sheets styles:
    - Custom Vibrant Tab Colors on every sheet
    - Master Obsidian Banner (Row 1) & Chromatic Column Headers (Row 2)
    - Harmonic Column Lane Tinting & Matrix Color-Coding (Status codes, Priorities, Lengths, Competitors)
    - Generous un-mushed column widths with 100% full data preservation in CSV vault
    - Optimized with Flyweight Style Cache and optional row cap for RAM safety
    """
    if not HAS_OPENPYXL:
        return None

    clean_slug = extract_clean_domain(domain)
    excel_path = os.path.join(target_folder, f"SEO_Audit_Report_{clean_slug}.xlsx")

    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Remove default sheet

    # Master Styling Presets & Flyweight Style Object Pooling (90% RAM reduction)
    fill_cache: Dict[str, PatternFill] = {}
    font_cache: Dict[tuple, Font] = {}

    def get_fill(hex_code: str) -> PatternFill:
        if hex_code not in fill_cache:
            fill_cache[hex_code] = PatternFill(start_color=hex_code, end_color=hex_code, fill_type="solid")
        return fill_cache[hex_code]

    def get_font(color: str, size: float = 9.0, bold: bool = False) -> Font:
        key = (color, size, bold)
        if key not in font_cache:
            font_cache[key] = Font(name="Segoe UI", size=size, bold=bold, color=color)
        return font_cache[key]

    align_left = Alignment(horizontal="left", vertical="center", wrap_text=False)
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=False)
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=False)

    master_fill = get_fill("0B0F19")
    master_font = get_font("F8FAFC", 10, True)
    brand_font = get_font("38BDF8", 9, True)

    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    for tab_name, matrix in tabs_data.items():
        if not matrix:
            continue

        safe_tab_name = tab_name[:30].replace(":", "_").replace("/", "_").replace("\\", "_")
        ws = wb.create_sheet(title=safe_tab_name)
        
        # 1. Vibrant Tab Color
        hex_color = TAB_HEX_COLORS.get(tab_name, "10B981")
        ws.sheet_properties.tabColor = hex_color

        num_cols = len(matrix[0]) if matrix else 1
        headers = [str(h) for h in matrix[0]]
        headers_lower = [h.lower() for h in headers]
        col_presets = [get_column_color_preset(h) for h in headers]

        # 2. Master Obsidian Banner (Row 1)
        ws.row_dimensions[1].height = 28
        ws.cell(row=1, column=1, value=f"🐸 FROGPIPE EXECUTIVE SEO SUITE • {tab_name.upper()} MATRIX")
        ws.cell(row=1, column=1).font = master_font
        ws.cell(row=1, column=1).alignment = align_left

        for c in range(1, num_cols + 1):
            cell = ws.cell(row=1, column=c)
            cell.fill = master_fill
            cell.border = thin_border

        if num_cols >= 2:
            ws.cell(row=1, column=num_cols, value="⚡ ARCHITECTED BY AL HOSSAIN RIFAT • https://r1fat.pages.dev")
            ws.cell(row=1, column=num_cols).font = brand_font
            ws.cell(row=1, column=num_cols).alignment = align_right

        # 3. Chromatic Column Headers (Row 2)
        ws.row_dimensions[2].height = 26
        for col_idx, (col_name, preset) in enumerate(zip(headers, col_presets), start=1):
            safe_header = sanitize_excel_cell(col_name)
            cell = ws.cell(row=2, column=col_idx, value=safe_header)
            
            # Competitors Analysis Header Palette
            if tab_name == "Competitors Analysis":
                comp_headers_colors = [
                    "1E3A8A", "78350F", "78350F", "881337", "0F766E",
                    "312E81", "312E81", "312E81", "064E3B", "064E3B"
                ]
                h_color = comp_headers_colors[col_idx - 1] if col_idx - 1 < len(comp_headers_colors) else "1E293B"
                cell.fill = get_fill(h_color)
            else:
                cell.fill = get_fill(preset["header_bg"])

            cell.font = get_font("FFFFFF", 9.5, True)
            cell.alignment = align_center if "status" in col_name.lower() or "priority" in col_name.lower() else align_left
            cell.border = thin_border

        # Freeze Rows 1 & 2 sticky
        ws.freeze_panes = "A3"

        # 4. Data Rows with Harmonic Lane Tinting (Row 3+)
        # Safe memory capping: slice to max_excel_rows to prevent memory bloat on giant crawls
        render_rows = matrix[1:max_excel_rows + 1] if (max_excel_rows and max_excel_rows > 0 and len(matrix) - 1 > max_excel_rows) else matrix[1:]
        for row_idx, row_vals in enumerate(render_rows, start=3):
            ws.row_dimensions[row_idx].height = 21
            is_odd = (row_idx % 2 == 1)

            for col_idx, raw_val in enumerate(row_vals, start=1):
                val_str = sanitize_excel_cell(raw_val)
                try:
                    cell = ws.cell(row=row_idx, column=col_idx, value=val_str)
                except Exception:
                    safe_ascii = "".join(c for c in val_str if 32 <= ord(c) <= 126 or c in "\n\r\t")
                    cell = ws.cell(row=row_idx, column=col_idx, value=safe_ascii)
                cell.border = thin_border
                
                preset = col_presets[col_idx - 1] if col_idx - 1 < len(col_presets) else get_column_color_preset("")
                lane_bg = preset["lane_odd"] if is_odd else preset["lane_even"]
                cell.fill = get_fill(lane_bg)
                cell.font = get_font(preset["font_color"], 9, False)
                cell.alignment = align_left

                col_name = headers_lower[col_idx - 1] if col_idx - 1 < len(headers_lower) else ""

                # Executive Summary Custom Highlights
                if tab_name == "Executive Summary":
                    if row_idx == 3:  # Overall Health Score row
                        cell.fill = get_fill("F0FDF4")
                        cell.font = get_font("166534", 10.0, True)
                    elif col_idx == 4:  # Health Status Column
                        cell.alignment = align_center
                        v_lower = val_str.lower()
                        if any(k in v_lower for k in ["optimal", "healthy", "perfect", "verified"]):
                            cell.fill = get_fill("D1FAE5")
                            cell.font = get_font("065F46", 9.5, True)
                        elif any(k in v_lower for k in ["action", "critical", "error"]):
                            cell.fill = get_fill("FEE2E2")
                            cell.font = get_font("991B1B", 9.5, True)
                        elif any(k in v_lower for k in ["review", "attention", "normal"]):
                            cell.fill = get_fill("FEF3C7")
                            cell.font = get_font("92400E", 9.5, True)
                # Competitors Analysis Custom Highlights
                elif tab_name == "Competitors Analysis":
                    if row_idx == 3:  # Client row
                        cell.fill = get_fill("D1FAE5")
                        cell.font = get_font("065F46", 9.5, True)
                    else:  # Rival rows
                        cell.fill = get_fill("FEE2E2")
                        cell.font = get_font("991B1B", 9.5, False)
                # HTTP Status Codes
                elif "status code" in col_name or "response code" in col_name:
                    cell.alignment = align_center
                    if val_str in ["200", "201"]:
                        cell.fill = get_fill("D1FAE5")
                        cell.font = get_font("065F46", 9.5, True)
                    elif val_str.startswith("3"):
                        cell.fill = get_fill("DBEAFE")
                        cell.font = get_font("1E40AF", 9.5, True)
                    elif val_str.startswith("4") or val_str.startswith("5"):
                        cell.fill = get_fill("FEE2E2")
                        cell.font = get_font("991B1B", 9.5, True)
                # Issues Priority
                elif "priority" in col_name or "severity" in col_name:
                    cell.alignment = align_center
                    v_low = val_str.lower()
                    if v_low in ["high", "critical"]:
                        cell.fill = get_fill("FEE2E2")
                        cell.font = get_font("991B1B", 9.5, True)
                    elif v_low in ["medium", "warning"]:
                        cell.fill = get_fill("FEF3C7")
                        cell.font = get_font("92400E", 9.5, True)
                    elif v_low in ["low", "opportunity"]:
                        cell.fill = get_fill("DBEAFE")
                        cell.font = get_font("1E40AF", 9.5, True)
                # Missing Alerts
                elif val_str.lower() == "missing":
                    cell.fill = get_fill("FEE2E2")
                    cell.font = get_font("991B1B", 9.5, True)

        # 5. Generous Un-Mushed Column Widths
        for c_idx, col_name in enumerate(headers_lower, start=1):
            col_letter = get_column_letter(c_idx)
            if tab_name == "Executive Summary":
                ws.column_dimensions[col_letter].width = {1: 36, 2: 24, 3: 32, 4: 24}.get(c_idx, 24)
            elif any(k in col_name for k in ["address", "url", "link", "canonical", "source", "destination"]):
                ws.column_dimensions[col_letter].width = 54
            elif any(k in col_name for k in ["title", "description", "details", "overview", "fix", "h1", "h2"]):
                ws.column_dimensions[col_letter].width = 44
            elif any(k in col_name for k in ["status code", "response"]):
                ws.column_dimensions[col_letter].width = 16
            elif any(k in col_name for k in ["priority", "severity", "indexability"]):
                ws.column_dimensions[col_letter].width = 16
            elif any(k in col_name for k in ["length", "width", "count", "words", "size", "occurrences"]):
                ws.column_dimensions[col_letter].width = 15
            else:
                ws.column_dimensions[col_letter].width = 22

    if "Sheet" in wb.sheetnames and len(wb.sheetnames) > 1:
        try:
            wb.remove(wb["Sheet"])
        except Exception:
            pass
    if "Executive Summary" in wb.sheetnames:
        wb.active = wb["Executive Summary"]

    wb.save(excel_path)
    return excel_path


def sync_to_google_sheet(
    target_folder: str,
    domain: str,
    webhook_url: Optional[str] = None,
    competitors: Optional[List[str]] = None,
    max_sheet_rows: int = 1500,
    max_excel_rows: int = 15000,
    skip_webhook: bool = False
) -> tuple[Optional[str], Optional[str]]:
    """
    Collects all 11 audit CSVs + Executive Summary cover tab + Competitors tab,
    generates an offline Excel workbook, and pushes to Google Apps Script webhook
    to create the live Google Sheet with automatic public sharing enabled.
    Returns: (sheet_url, excel_path)
    """
    print_step("Assembling Master Datasets", "Compiling Executive Summary + 11 Audit Tabs + Competitors Matrix", phase=(3, 4))

    tabs_data: Dict[str, List[List[Any]]] = {}

    # Read manifest if present to preserve adaptive tab titles (e.g. HTTP Status Codes)
    manifest_path = os.path.join(target_folder, "audit_manifest.json")
    title_overrides = {}
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as mf:
                m_data = json.load(mf)
                for item in m_data.get("datasets", []):
                    title_overrides[item["target_file"]] = item["title"]
        except Exception:
            pass

    # 1. Primary Cover Tab: Executive Health Scorecard (Tab #1)
    tabs_data["Executive Summary"] = build_executive_summary(target_folder, domain)

    # 2. Competitors Analysis Benchmark Matrix (Tab #2)
    tabs_data["Competitors Analysis"] = build_competitors_matrix(domain, competitors)

    # 3. Load the 11 technical audit CSVs
    for key, info in AUDIT_TABS_MAPPING.items():
        csv_path = os.path.join(target_folder, info["target_file"])
        matrix = load_csv_as_matrix(csv_path)
        if matrix:
            resolved_title = title_overrides.get(info["target_file"], info["title"])
            tabs_data[resolved_title] = matrix

    # 4. Always generate local offline Master Excel workbook (.xlsx)
    excel_path = generate_offline_excel(target_folder, domain, tabs_data, max_excel_rows=max_excel_rows)
    if excel_path:
        print_success(f"Offline Master Workbook Built: [dim]{excel_path}[/dim]")

    if skip_webhook:
        return None, excel_path

    # 5. Check for Google Apps Script Webhook
    active_webhook = webhook_url or load_sheet_webhook_url()
    auth_token = load_auth_token()

    if not active_webhook:
        if HAS_RICH:
            from rich.prompt import Prompt
            console.print()
            console.print("  [bold cyan]Google Sheets Live Sync Configuration[/bold cyan]")
            console.print("  [dim]To auto-create a live styled Google Sheet, deploy templates/code.gs as a Web App.[/dim]")
            ans = Prompt.ask("  Enter Google Apps Script Webhook URL (or press Enter to skip)", default="").strip()
            if ans and ans.startswith("http"):
                active_webhook = ans
                save_sheet_webhook_url(ans)
                print_success("Saved Webhook URL to config.json!")
        else:
            ans = input("\nEnter Google Apps Script Webhook URL (or press Enter to skip): ").strip()
            if ans and ans.startswith("http"):
                active_webhook = ans
                save_sheet_webhook_url(ans)

    if not active_webhook:
        print_warning("Google Sheets webhook URL skipped. Master deliverable saved in offline Excel workbook.")
        return None, excel_path

    # 6. Push Payload to Google Apps Script Webhook (Streaming Tab Sync Engine)
    print_step("Deploying to Google Sheets", "Streaming audit datasets to Google Apps Script Webhook...", phase=(4, 4))

    # Step 6a: Initialize Spreadsheet with Executive Summary and Competitors Analysis
    init_payload = {
        "action": "init_audit",
        "auth_token": auth_token,
        "domain": domain,
        "title": f"SEO Audit & Competitors Analysis for {domain}",
        "executive_data": tabs_data.get("Executive Summary", []),
        "competitors_data": tabs_data.get("Competitors Analysis", [])
    }

    try:
        init_res = requests.post(active_webhook, json=init_payload, timeout=60)
        if init_res.status_code == 200:
            init_data = init_res.json()
            if init_data.get("status") == "success":
                sheet_id = init_data.get("sheet_id")
                sheet_url = init_data.get("sheet_url")
                print_success(f"Master Sheet Online: [dim]{sheet_url}[/dim]")

                # Step 6b: Stream each technical audit tab one by one with live yield feedback
                audit_tab_items = [
                    (t_name, matrix)
                    for t_name, matrix in tabs_data.items()
                    if t_name not in ["Executive Summary", "Competitors Analysis"]
                ]

                TAB_ICONS = {
                    "Executive Summary": ("📋", "[bold bright_white]Executive Summary[/bold bright_white]"),
                    "Competitors Analysis": ("🏆", "[bold yellow]Competitors Analysis[/bold yellow]"),
                    "Issues": ("🚨", "[bold red]Issues[/bold red]"),
                    "H1": ("🟢", "[bold green]H1 Headings[/bold green]"),
                    "H2": ("🔵", "[bold cyan]H2 Headings[/bold cyan]"),
                    "Meta Description": ("🟣", "[bold magenta]Meta Description[/bold magenta]"),
                    "Meta Tags": ("🔷", "[bold blue]Meta Tags & Directives[/bold blue]"),
                    "Content": ("🧪", "[bold bright_green]Content & Depth[/bold bright_green]"),
                    "ALL page Titles": ("💎", "[bold bright_blue]ALL Page Titles[/bold bright_blue]"),
                    "URLs": ("⚓", "[bold white]Internal URLs[/bold white]"),
                    "Images": ("🌸", "[bold bright_magenta]Images & Assets[/bold bright_magenta]"),
                    "Search Console Status": ("🍊", "[bold bright_yellow]Search Console Status[/bold bright_yellow]"),
                    "HTTP Status & Response Codes": ("🍊", "[bold bright_yellow]HTTP Status & Response Codes[/bold bright_yellow]"),
                    "Canonicals": ("☁️", "[bold bright_cyan]Canonicals[/bold bright_cyan]"),
                }

                total_tabs = len(audit_tab_items)
                for idx, (tab_name, matrix) in enumerate(audit_tab_items, start=1):
                    # Smart Sheet Row Capping: Send header + top max_sheet_rows to keep Google Sheets responsive and prevent timeouts
                    total_data_rows = max(0, len(matrix) - 1)
                    if total_data_rows > max_sheet_rows:
                        sheet_rows = [matrix[0]] + matrix[1:max_sheet_rows + 1]
                        rows_display = f"{max_sheet_rows:,} rows (Top priority sample; {total_data_rows:,} in Excel)"
                    else:
                        sheet_rows = matrix
                        rows_display = f"{total_data_rows:>4} rows"

                    tab_payload = {
                        "action": "sync_tab",
                        "auth_token": auth_token,
                        "sheet_id": sheet_id,
                        "tab_name": tab_name,
                        "rows": sheet_rows
                    }
                    icon, styled_name = TAB_ICONS.get(tab_name, ("📑", f"[bold white]{tab_name}[/bold white]"))
                    try:
                        tab_res = requests.post(active_webhook, json=tab_payload, timeout=120)
                        if tab_res.status_code == 200:
                            print_success(f"[{idx:02d}/{total_tabs:02d}] {icon} {styled_name:<35} [dim]➔[/dim] [bright_green]{rows_display}[/bright_green]  [bold bright_green][✓ LIVE][/bold bright_green]")
                        else:
                            print_warning(f"[{idx:02d}/{total_tabs:02d}] {icon} {styled_name} sync warning: HTTP {tab_res.status_code}")
                    except Exception as tab_err:
                        print_warning(f"[{idx:02d}/{total_tabs:02d}] {icon} {styled_name} sync error: {tab_err}")

                # Finalize audit tab ordering and set Executive Summary as active view
                try:
                    requests.post(
                        active_webhook,
                        json={"action": "finalize_audit", "auth_token": auth_token, "sheet_id": sheet_id},
                        timeout=30
                    )
                except Exception:
                    pass

                return sheet_url, excel_path

        # Fallback to consolidated batch sync
        print_step("Retrying via Consolidated Sync", "Sending atomic batch payload...")
        batch_payload = {
            "action": "create_audit",
            "auth_token": auth_token,
            "domain": domain,
            "title": f"SEO Audit & Competitors Analysis for {domain}",
            "tabs": tabs_data
        }
        res = requests.post(active_webhook, json=batch_payload, timeout=120)
        if res.status_code == 200:
            resp_data = res.json()
            if resp_data.get("status") == "success":
                sheet_url = resp_data.get("sheet_url")
                print_success(f"Google Sheet Created & Formatted: {sheet_url}")
                return sheet_url, excel_path
            else:
                print_error(f"Google Apps Script Error: {resp_data.get('message')}")
        else:
            print_error(f"Webhook HTTP error: {res.status_code} - {res.text[:200]}")

    except Exception as e:
        print_error(f"Failed to communicate with Google Sheets webhook: {e}")

    return None, excel_path


