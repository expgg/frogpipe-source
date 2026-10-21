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
    get_temp_crawl_dir,
    extract_clean_domain
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


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="FrogPipe — Autonomous Screaming Frog SEO Audit Engine (Mark 1)"
    )
    parser.add_argument(
        "-u", "--url",
        type=str,
        help="Target website URL to audit (e.g. drstangale.com or https://example.com)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Custom output folder path (defaults to Desktop/SEO_<domain>)"
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
        url = Prompt.ask("[bold green]Enter Target Website URL[/bold green]", default="https://drstangale.com")
        return url.strip()
    else:
        url = input("\nEnter Target Website URL [https://drstangale.com]: ").strip()
        return url or "https://drstangale.com"


def main():
    print_banner()

    args = parse_arguments()

    # Verify Screaming Frog CLI path
    cli_path = get_screaming_frog_cli()
    if not cli_path:
        print_error("Screaming Frog CLI could not be located!")
        print_warning("Please verify Screaming Frog SEO Spider is installed at X:\\APPS\\Screaming Frog SEO Spider")
        sys.exit(1)
    else:
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

    # 2. Package and Normalize the 9 Audit Datasets
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

    # 4. Display Executive Summary
    print_files_summary(target_folder, datasets)


if __name__ == "__main__":
    main()
