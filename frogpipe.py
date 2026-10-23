#!/usr/bin/env python3
"""
FrogPipe — Autonomous Screaming Frog SEO Pipeline
Mark 1: Headless SEO Spider & 9-Data File Organizer
Architected by Al Hossain Rifat
"""

import os
import sys
import shutil
import argparse
import time
from typing import Optional


from modules.config import (
    normalize_url,
    get_screaming_frog_cli,
    prompt_and_save_frog_cli,
    get_temp_crawl_dir,
    extract_clean_domain,
    DEFAULT_EXAMPLE_URL
)
from modules.ui import (
    HAS_RICH,
    console,
    print_banner,
    print_step,
    print_success,
    print_error,
    print_warning,
    print_files_summary
)
from modules.crawler import run_headless_crawl
from modules.organizer import organize_audit_datasets
from modules.google_sync import sync_to_google_sheet


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="FrogPipe — Autonomous Screaming Frog SEO Audit Engine (Mark 2)"
    )
    parser.add_argument(
        "-u", "--url",
        type=str,
        help="Target website URL to audit (e.g. r1fat.pages.dev or drstangale.com)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Custom output folder path (defaults to audited_sites/SEO_<domain>)"
    )
    parser.add_argument(
        "-w", "--webhook",
        type=str,
        default=None,
        help="Google Apps Script Webhook URL for live Google Sheets publishing"
    )
    parser.add_argument(
        "--no-sheet",
        action="store_true",
        help="Skip Google Sheets sync (only package CSVs and offline Excel workbook)"
    )
    parser.add_argument(
        "-c", "--competitors",
        type=str,
        default=None,
        help="Comma-separated competitor URLs/domains for the Competitor Matrix (e.g. comp1.com,comp2.com)"
    )
    parser.add_argument(
        "--config-file",
        type=str,
        default=None,
        help="Path to custom .seospiderconfig profile for advanced spider settings/limits"
    )
    parser.add_argument(
        "--max-sheet-rows",
        type=int,
        default=1500,
        help="Maximum rows to stream per tab in Google Sheets (default: 1500, preserves full dataset in Excel)"
    )
    parser.add_argument(
        "--max-excel-rows",
        type=int,
        default=15000,
        help="Maximum rows to format per tab in Master Excel workbook (default: 15000, 0 for unlimited)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Display verbose logging from Screaming Frog CLI"
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Retain raw crawl dump directory instead of cleaning up"
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        default=None,
        help="Batch Lead Gen Mode: Path to text file containing target website URLs (one URL per line)"
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=None,
        help="Maximum URLs to crawl (requires custom spider config profile in CLI mode)"
    )
    return parser.parse_args()


def get_interactive_url() -> str:
    """Prompts the user interactively for a website URL."""
    if HAS_RICH:
        from rich.prompt import Prompt
        url = Prompt.ask(
            f"[bold bright_green]Enter Target Website URL[/bold bright_green] [dim](e.g. [bold cyan]{DEFAULT_EXAMPLE_URL}[/bold cyan])[/dim]",
            default=DEFAULT_EXAMPLE_URL
        )
        console.print()
        return url.strip()
    else:
        url = input(f"\nEnter Target Website URL [{DEFAULT_EXAMPLE_URL}]: ").strip()
        return url or DEFAULT_EXAMPLE_URL


def get_interactive_competitors() -> list[str]:
    """Prompts user interactively for optional competitor URLs."""
    if HAS_RICH:
        from rich.prompt import Prompt
        ans = Prompt.ask(
            "[bold cyan]Enter Competitor URLs[/bold cyan] [dim](comma-separated, or press Enter to skip)[/dim]",
            default=""
        )
        console.print()
        if ans:
            return [c.strip() for c in ans.split(",") if c.strip()]
        return []
    else:
        ans = input("Enter Competitor URLs (comma-separated, or Enter to skip): ").strip()
        return [c.strip() for c in ans.split(",") if c.strip()] if ans else []


def sweep_old_temp_crawls():
    """Removes abandoned crawl folders in temp_crawl older than 2 hours."""
    temp_root = get_temp_crawl_dir()
    if not os.path.exists(temp_root):
        return
    now = time.time()
    for item in os.listdir(temp_root):
        item_path = os.path.join(temp_root, item)
        if os.path.isdir(item_path) and item.startswith("crawl_"):
            try:
                # If older than 2 hours (7200 seconds)
                if now - os.path.getmtime(item_path) > 7200:
                    shutil.rmtree(item_path, ignore_errors=True)
            except Exception:
                pass


def audit_single_target(
    raw_url: str,
    cli_path: str,
    args: argparse.Namespace,
    competitor_list: list[str],
    override_output_dir: Optional[str] = None
) -> dict:
    """
    Executes the end-to-end 4-phase audit pipeline for a single target URL.
    Returns audit result metadata dictionary.
    """
    target_url = normalize_url(raw_url)
    clean_domain = extract_clean_domain(target_url)

    temp_dir = os.path.join(get_temp_crawl_dir(), f"crawl_{clean_domain}_{int(time.time())}")

    def cleanup_workspace():
        if not args.keep_temp and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    try:
        # 1. Execute Headless Crawl
        crawl_ok = run_headless_crawl(
            target_url=target_url,
            output_dir=temp_dir,
            crawl_limit=args.limit,
            config_file=args.config_file,
            verbose=args.verbose
        )

        if not crawl_ok:
            print_error(f"Crawl terminated unexpectedly for {clean_domain}.")
            return {
                "url": target_url,
                "domain": clean_domain,
                "status": "Failed",
                "folder": None,
                "sheet_url": None,
                "excel_path": None
            }

        # 2. Package and Normalize Audit Datasets (Zero Data Loss)
        target_folder, datasets = organize_audit_datasets(
            raw_crawl_dir=temp_dir,
            target_url=target_url,
            custom_output_dir=override_output_dir or args.output,
            crawl_limit=args.limit
        )

        # 3. Google Sheets Live Engine & Master Excel Builder
        sheet_url, excel_path = sync_to_google_sheet(
            target_folder=target_folder,
            domain=clean_domain,
            webhook_url=args.webhook,
            competitors=competitor_list,
            max_sheet_rows=args.max_sheet_rows,
            max_excel_rows=args.max_excel_rows,
            skip_webhook=args.no_sheet
        )

        # 4. Display Executive Summary
        print_files_summary(
            folder_path=target_folder,
            datasets=datasets,
            sheet_url=sheet_url,
            excel_path=excel_path
        )

        return {
            "url": target_url,
            "domain": clean_domain,
            "status": "Success",
            "folder": target_folder,
            "sheet_url": sheet_url,
            "excel_path": excel_path
        }

    finally:
        cleanup_workspace()


def print_batch_summary(results: list[dict]):
    """Renders a consolidated master report table for batch lead generation audits."""
    if HAS_RICH:
        from rich.table import Table
        table = Table(
            title="🐸 FROGPIPE BATCH / LEAD GEN CONSOLIDATED AUDIT REPORT",
            title_style="bold bright_green",
            border_style="bright_blue",
            header_style="bold bright_white on blue"
        )
        table.add_column("Domain / Target", style="bold bright_white", width=25)
        table.add_column("Status", justify="center", width=12)
        table.add_column("Live Google Sheet (Public View)", style="bright_cyan", width=55)
        table.add_column("Offline Master Excel", style="dim", width=35)

        for res in results:
            stat = "[bold bright_green]COMPLETED[/bold bright_green]" if res.get("status") == "Success" else "[bold red]FAILED[/bold red]"
            sheet_disp = res.get("sheet_url") or "[dim]N/A (Offline mode)[/dim]"
            excel_disp = os.path.basename(res.get("excel_path", "")) if res.get("excel_path") else "[dim]-[/dim]"
            table.add_row(res.get("domain", "Unknown"), stat, sheet_disp, excel_disp)

        console.print()
        console.print(table)
        console.print()
    else:
        print("\n" + "=" * 80)
        print("FROGPIPE BATCH AUDIT CONSOLIDATED REPORT")
        print("=" * 80)
        for res in results:
            print(f"Domain:    {res.get('domain')}")
            print(f"Status:    {res.get('status')}")
            print(f"Sheet URL: {res.get('sheet_url') or 'N/A'}")
            print(f"Excel:     {res.get('excel_path') or 'N/A'}")
            print("-" * 80)


def main():
    print_banner()

    # Pre-sweep abandoned temporary crawls from previous runs
    sweep_old_temp_crawls()

    args = parse_arguments()

    # Verify or prompt for Screaming Frog CLI path
    cli_path = get_screaming_frog_cli()
    if not cli_path:
        cli_path = prompt_and_save_frog_cli()
        if not cli_path:
            print_error("Screaming Frog CLI path was not provided. Exiting.")
            sys.exit(1)

    print_success(f"Engine Linked: [dim]{cli_path}[/dim]")

    # Resolve Competitor Domains (global or default)
    competitor_list = [c.strip() for c in args.competitors.split(",") if c.strip()] if args.competitors else []

    # -------------------------------------------------------------------------
    # Mode A: Batch / Lead Gen Mode (--file leads.txt)
    # -------------------------------------------------------------------------
    if args.file:
        leads_path = os.path.abspath(args.file)
        if not os.path.isfile(leads_path):
            print_error(f"Batch file not found: {leads_path}")
            sys.exit(1)

        with open(leads_path, "r", encoding="utf-8") as f:
            targets = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

        if not targets:
            print_error(f"Batch file {leads_path} contains no valid target URLs.")
            sys.exit(1)

        print_step("Batch Engine Activated", f"Loaded {len(targets)} target websites from {os.path.basename(leads_path)}", phase=(1, 4))
        
        batch_results = []
        for idx, target_raw in enumerate(targets, start=1):
            if HAS_RICH:
                console.print(f"\n[bold bright_yellow]⚡ BATCH AUDIT [{idx}/{len(targets)}]: {target_raw}[/bold bright_yellow]")
            else:
                print(f"\n--- BATCH AUDIT [{idx}/{len(targets)}]: {target_raw} ---")

            target_norm = normalize_url(target_raw)
            site_domain = extract_clean_domain(target_norm)
            site_output = os.path.join(args.output, f"SEO_{site_domain}") if args.output else None

            try:
                res = audit_single_target(
                    raw_url=target_raw,
                    cli_path=cli_path,
                    args=args,
                    competitor_list=competitor_list,
                    override_output_dir=site_output
                )
                batch_results.append(res)
            except KeyboardInterrupt:
                print_warning("\nBatch run interrupted by user (Ctrl+C). Generating summary for completed audits...")
                break
            except Exception as batch_err:
                print_error(f"Error auditing {target_raw}: {batch_err}")
                batch_results.append({
                    "url": target_raw,
                    "domain": extract_clean_domain(target_raw),
                    "status": "Failed",
                    "folder": None,
                    "sheet_url": None,
                    "excel_path": None
                })

        print_batch_summary(batch_results)
        return

    # -------------------------------------------------------------------------
    # Mode B: Single Site Interactive / CLI Audit Mode
    # -------------------------------------------------------------------------
    raw_url = args.url if args.url else get_interactive_url()
    if not raw_url:
        print_error("No target URL specified. Exiting.")
        sys.exit(1)

    if not args.competitors and not args.url:
        competitor_list = get_interactive_competitors()

    try:
        audit_single_target(
            raw_url=raw_url,
            cli_path=cli_path,
            args=args,
            competitor_list=competitor_list
        )
    except KeyboardInterrupt:
        print_warning("\nAudit interrupted by user (Ctrl+C). Cleaning up workspace...")
        sys.exit(130)


if __name__ == "__main__":
    main()



