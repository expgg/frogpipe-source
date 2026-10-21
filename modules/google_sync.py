"""
FrogPipe — Google Sheets Live Engine & Excel Master Builder
Architected & Engineered by Al Hossain Rifat
Portfolio: https://r1fat.pages.dev
"""

import os
import csv
import json
import requests
import pandas as pd
from typing import Dict, List, Any, Optional

try:
    import openpyxl
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

from modules.config import (
    AUDIT_TABS_MAPPING,
    load_sheet_webhook_url,
    save_sheet_webhook_url,
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
    """Reads a CSV file into a 2D matrix preserving 100% of rows and columns."""
    if not os.path.isfile(file_path):
        return []
    rows = []
    try:
        with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.reader(f)
            for r in reader:
                # Replace None or empty placeholders
                clean_row = ["" if col is None else str(col).strip() for col in r]
                if any(clean_row):
                    rows.append(clean_row)
    except Exception:
        # Fallback using pandas
        try:
            df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
            rows = [df.columns.tolist()] + df.values.tolist()
        except Exception:
            pass
    return rows


def build_competitors_matrix(client_domain: str, competitors: List[str] = None) -> List[List[str]]:
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
    matrix.append([client_url, "-", "-", "-", "-", "-", "-", "-", "-", "-"])

    # 5 Rivals (Rows 3-7)
    comp_list = competitors or []
    for i in range(1, 6):
        c_url = comp_list[i - 1] if len(comp_list) >= i else f"https://competitor-{i}.com (Pending Recon)"
        matrix.append([c_url, "-", "-", "-", "-", "-", "-", "-", "-", "-"])

    return matrix


TAB_HEX_COLORS = {
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
    "Canonicals": "0EA5E9",
}


def generate_offline_excel(
    target_folder: str,
    domain: str,
    tabs_data: Dict[str, List[List[Any]]]
) -> Optional[str]:
    """
    Builds an executive multi-tab Excel workbook (.xlsx) matching Google Sheets styles:
    - Custom Vibrant Tab Colors on every sheet
    - Master Obsidian Banner (Row 1) & Frozen Column Headers (Row 2)
    - Full Cell Matrix Color-Coding (Status codes, Priorities, Lengths, Competitors)
    - Generous un-mushed column widths with 100% full data preservation
    """
    if not HAS_OPENPYXL:
        return None

    clean_slug = extract_clean_domain(domain)
    excel_path = os.path.join(target_folder, f"SEO_Audit_Report_{clean_slug}.xlsx")

    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Remove default sheet

    # Master Styling Presets
    master_fill = PatternFill(start_color="0B0F19", end_color="0B0F19", fill_type="solid")
    master_font = Font(name="Segoe UI", size=10, bold=True, color="F8FAFC")
    brand_font = Font(name="Segoe UI", size=9, bold=True, color="38BDF8")

    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Segoe UI", size=9.5, bold=True, color="F8FAFC")

    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    plain_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

    green_fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
    green_font = Font(name="Segoe UI", size=9.5, bold=True, color="065F46")

    blue_fill = PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid")
    blue_font = Font(name="Segoe UI", size=9.5, bold=True, color="1E40AF")

    amber_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    amber_font = Font(name="Segoe UI", size=9.5, bold=True, color="92400E")

    red_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    red_font = Font(name="Segoe UI", size=9.5, bold=True, color="991B1B")

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

        # 2. Master Obsidian Banner (Row 1)
        ws.row_dimensions[1].height = 28
        ws.cell(row=1, column=1, value=f"🐸 FROGPIPE EXECUTIVE SEO SUITE • {tab_name.upper()} MATRIX")
        ws.cell(row=1, column=1).font = master_font
        ws.cell(row=1, column=1).alignment = Alignment(horizontal="left", vertical="center")

        for c in range(1, num_cols + 1):
            cell = ws.cell(row=1, column=c)
            cell.fill = master_fill
            cell.border = thin_border

        if num_cols >= 2:
            ws.cell(row=1, column=num_cols, value="⚡ ARCHITECTED BY AL HOSSAIN RIFAT • https://r1fat.pages.dev")
            ws.cell(row=1, column=num_cols).font = brand_font
            ws.cell(row=1, column=num_cols).alignment = Alignment(horizontal="right", vertical="center")

        # 3. Column Headers (Row 2)
        ws.row_dimensions[2].height = 24
        for col_idx, col_name in enumerate(headers, start=1):
            cell = ws.cell(row=2, column=col_idx, value=col_name)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)
            cell.border = thin_border

        # Freeze Rows 1 & 2 sticky
        ws.freeze_panes = "A3"

        # 4. Data Rows (Row 3+)
        for row_idx, row_vals in enumerate(matrix[1:], start=3):
            ws.row_dimensions[row_idx].height = 21
            is_odd = (row_idx % 2 == 1)
            default_fill = zebra_fill if is_odd else plain_fill

            for col_idx, raw_val in enumerate(row_vals, start=1):
                val_str = str(raw_val or "").strip()
                cell = ws.cell(row=row_idx, column=col_idx, value=val_str)
                cell.border = thin_border
                cell.fill = default_fill
                cell.font = Font(name="Segoe UI", size=9, color="1E293B")
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)

                col_name = headers_lower[col_idx - 1] if col_idx - 1 < len(headers_lower) else ""

                # Competitors Analysis Custom Highlights
                if tab_name == "Competitors Analysis":
                    if row_idx == 3:  # Client row
                        cell.fill = green_fill
                        cell.font = green_font
                    else:  # Rival rows
                        cell.fill = red_fill
                        cell.font = red_font
                # HTTP Status Codes
                elif "status code" in col_name or "response code" in col_name:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    if val_str in ["200", "201"]:
                        cell.fill = green_fill
                        cell.font = green_font
                    elif val_str.startswith("3"):
                        cell.fill = blue_fill
                        cell.font = blue_font
                    elif val_str.startswith("4") or val_str.startswith("5"):
                        cell.fill = red_fill
                        cell.font = red_font
                # Issues Priority
                elif "priority" in col_name or "severity" in col_name:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    v_low = val_str.lower()
                    if v_low in ["high", "critical"]:
                        cell.fill = red_fill
                        cell.font = red_font
                    elif v_low in ["medium", "warning"]:
                        cell.fill = amber_fill
                        cell.font = amber_font
                    elif v_low in ["low", "opportunity"]:
                        cell.fill = blue_fill
                        cell.font = blue_font
                # Missing Alerts
                elif val_str.lower() == "missing":
                    cell.fill = red_fill
                    cell.font = red_font

        # 5. Generous Un-Mushed Column Widths
        for c_idx, col_name in enumerate(headers_lower, start=1):
            col_letter = get_column_letter(c_idx)
            if any(k in col_name for k in ["address", "url", "link", "canonical", "source", "destination"]):
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

    wb.save(excel_path)
    return excel_path


def sync_to_google_sheet(
    target_folder: str,
    domain: str,
    webhook_url: Optional[str] = None,
    skip_webhook: bool = False
) -> tuple[Optional[str], Optional[str]]:
    """
    Collects all 10 audit CSVs + Competitors tab, generates an offline Excel workbook,
    and pushes to Google Apps Script webhook to create the live Google Sheet.
    Returns: (sheet_url, excel_path)
    """
    print_step("Assembling Master Datasets", "Compiling 11 Audit Tabs + Competitors Matrix (100% Data Fidelity)")

    tabs_data: Dict[str, List[List[Any]]] = {}

    # 1. Load the 10 technical audit CSVs
    for key, info in AUDIT_TABS_MAPPING.items():
        csv_path = os.path.join(target_folder, info["target_file"])
        matrix = load_csv_as_matrix(csv_path)
        if matrix:
            tabs_data[info["title"]] = matrix

    # 2. Append Competitors Analysis tab
    tabs_data["Competitors Analysis"] = build_competitors_matrix(domain)

    # 3. Always generate local offline Master Excel workbook (.xlsx)
    excel_path = generate_offline_excel(target_folder, domain, tabs_data)
    if excel_path:
        print_success(f"Offline Master Workbook Built: [dim]{excel_path}[/dim]")

    if skip_webhook:
        return None, excel_path

    # 4. Check for Google Apps Script Webhook
    active_webhook = webhook_url or load_sheet_webhook_url()


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

    # 5. Push Payload to Google Apps Script Webhook (Streaming Tab Sync Engine)
    print_step("Deploying to Google Sheets", "Streaming audit datasets to Google Apps Script Webhook...")

    # Step 5a: Initialize Spreadsheet
    init_payload = {
        "action": "init_audit",
        "domain": domain,
        "title": f"SEO Audit & Competitors Analysis for {domain}",
        "competitors_data": tabs_data.get("Competitors Analysis", [])
    }

    try:
        init_res = requests.post(active_webhook, json=init_payload, timeout=40)
        if init_res.status_code == 200:
            init_data = init_res.json()
            if init_data.get("status") == "success":
                sheet_id = init_data.get("sheet_id")
                sheet_url = init_data.get("sheet_url")
                print_success(f"Master Sheet Online: [dim]{sheet_url}[/dim]")

                # Step 5b: Stream each tab one by one with live yield feedback
                audit_tab_items = [
                    (info["title"], tabs_data.get(info["title"], []))
                    for key, info in AUDIT_TABS_MAPPING.items()
                    if info["title"] in tabs_data
                ]

                total_tabs = len(audit_tab_items)
                for idx, (tab_name, matrix) in enumerate(audit_tab_items, start=1):
                    tab_payload = {
                        "action": "sync_tab",
                        "sheet_id": sheet_id,
                        "tab_name": tab_name,
                        "rows": matrix
                    }
                    try:
                        tab_res = requests.post(active_webhook, json=tab_payload, timeout=30)
                        if tab_res.status_code == 200:
                            print_success(f"[{idx}/{total_tabs}] {tab_name} Synced ({max(0, len(matrix)-1)} rows)")
                        else:
                            print_warning(f"[{idx}/{total_tabs}] {tab_name} sync warning: HTTP {tab_res.status_code}")
                    except Exception as tab_err:
                        print_warning(f"[{idx}/{total_tabs}] {tab_name} sync error: {tab_err}")

                return sheet_url, excel_path

        # Fallback to consolidated batch sync
        print_step("Retrying via Consolidated Sync", "Sending atomic batch payload...")
        batch_payload = {
            "action": "create_audit",
            "domain": domain,
            "title": f"SEO Audit & Competitors Analysis for {domain}",
            "tabs": tabs_data
        }
        res = requests.post(active_webhook, json=batch_payload, timeout=90)
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

