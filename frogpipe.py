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
        help="Custom output folder path (defaults to Desktop/SEO_<domain>)"
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
        "-v", "--verbose",
        action="store_true",
        help="Display verbose logging from Screaming Frog CLI"
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Retain raw crawl dump directory instead of cleaning up"
    )
    return parser.parse_args()



def get_interactive_url() -> str:
    """Prompts the user interactively for a website URL."""
    if HAS_RICH:
        from rich.prompt import Prompt
        console.print()
        url = Prompt.ask(
            f"[bold green]Enter Target Website URL[/bold green] [dim](e.g. [bold cyan]{DEFAULT_EXAMPLE_URL}[/bold cyan])[/dim]",
            default=DEFAULT_EXAMPLE_URL
        )
        return url.strip()
    else:
        url = input(f"\nEnter Target Website URL [{DEFAULT_EXAMPLE_URL}]: ").strip()
        return url or DEFAULT_EXAMPLE_URL


def main():
    print_banner()

    args = parse_arguments()

    # Verify or prompt for Screaming Frog CLI path
    cli_path = get_screaming_frog_cli()
    if not cli_path:
        cli_path = prompt_and_save_frog_cli()
        if not cli_path:
            print_error("Screaming Frog CLI path was not provided. Exiting.")
            sys.exit(1)

    print_success(f"Engine Linked: [dim]{cli_path}[/dim]")


    # Resolve target URL
    raw_url = args.url if args.url else get_interactive_url()
    if not raw_url:
        print_error("No target URL specified. Exiting.")
        sys.exit(1)

    target_url = normalize_url(raw_url)
    clean_domain = extract_clean_domain(target_url)

    # Temporary crawl workspace
    temp_dir = os.path.join(get_temp_crawl_dir(), f"crawl_{clean_domain}_{int(time.time())}")

    # 1. Execute Headless Crawl
    crawl_ok = run_headless_crawl(
        target_url=target_url,
        output_dir=temp_dir,
        verbose=args.verbose
    )

    if not crawl_ok:
        print_error("Crawl process terminated unexpectedly. Review logs.")
        sys.exit(1)

    # 2. Package and Normalize the 10 Audit Datasets (Zero Data Loss)
    target_folder, datasets = organize_audit_datasets(
        raw_crawl_dir=temp_dir,
        target_url=target_url,
        custom_output_dir=args.output
    )

    # 3. Clean up raw temporary crawl directory
    if not args.keep_temp:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

    # 4. Google Sheets Live Engine & Master Excel Builder
    sheet_url, excel_path = sync_to_google_sheet(
        target_folder=target_folder,
        domain=clean_domain,
        webhook_url=args.webhook,
        skip_webhook=args.no_sheet
    )

    # 5. Display Executive Summary
    print_files_summary(
        folder_path=target_folder,
        datasets=datasets,
        sheet_url=sheet_url,
        excel_path=excel_path
    )


if __name__ == "__main__":
    main()


