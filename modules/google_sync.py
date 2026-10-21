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


def generate_offline_excel(
    target_folder: str,
    domain: str,
    tabs_data: Dict[str, List[List[Any]]]
) -> Optional[str]:
    """
    Builds an executive multi-tab Excel workbook (.xlsx) matching Google Sheets styles:
    - 10 Technical Screaming Frog tabs with 100% full data preservation
    - Competitors Analysis tab with light green client row and soft red rivals
    - Dark slate sticky headers (#0F172A)
    """
    if not HAS_OPENPYXL:
        return None

    clean_slug = extract_clean_domain(domain)
    excel_path = os.path.join(target_folder, f"SEO_Audit_Report_{clean_slug}.xlsx")

    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    header_font = Font(name="Segoe UI", size=10, bold=True, color="F8FAFC")
    data_font = Font(name="Segoe UI", size=9)
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    green_fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
    green_font = Font(name="Segoe UI", size=10, bold=True, color="065F46")

    red_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    red_font = Font(name="Segoe UI", size=9, color="991B1B")

    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    for tab_name, matrix in tabs_data.items():
        if not matrix:
            continue

        # Clean tab name for Excel (max 31 chars, valid chars)
        safe_tab_name = tab_name[:30].replace(":", "_").replace("/", "_").replace("\\", "_")
        ws = wb.create_sheet(title=safe_tab_name)
        ws.freeze_panes = "A2"

        for row_idx, row_vals in enumerate(matrix, start=1):
            for col_idx, val in enumerate(row_vals, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.border = thin_border

                if row_idx == 1:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)
                else:
                    cell.font = data_font
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)

                    # Custom coloring for Competitors Analysis
                    if tab_name == "Competitors Analysis":
                        if row_idx == 2:
                            cell.fill = green_fill
                            cell.font = green_font
                        elif 3 <= row_idx <= 7:
                            cell.fill = red_fill
                            cell.font = red_font
                    elif row_idx % 2 == 1:
                        cell.fill = zebra_fill

            ws.row_dimensions[row_idx].height = 24 if row_idx == 1 else 20

        # Adjust column widths
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col[:20]: # Sample first 20 rows
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            adjusted_width = min(max(max_len + 3, 12), 45)
            ws.column_dimensions[col_letter].width = adjusted_width

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
    print_step("Assembling Master Datasets", "Compiling 10 Audit Tabs + Competitors Matrix (100% Data Fidelity)")

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

    # 5. Push Payload to Google Apps Script Webhook
    print_step("Deploying to Google Sheets", "Transmitting audit datasets to Google Apps Script Webhook...")

    payload = {
        "action": "create_audit",
        "domain": domain,
        "title": f"SEO Audit & Competitors Analysis for {domain}",
        "tabs": tabs_data
    }

    try:
        if HAS_RICH:
            with console.status("[bold green]Creating Google Spreadsheet & Applying Styles...[/bold green]", spinner="dots"):
                res = requests.post(active_webhook, json=payload, timeout=60)
        else:
            res = requests.post(active_webhook, json=payload, timeout=60)

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
