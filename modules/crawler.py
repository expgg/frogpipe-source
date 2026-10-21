"""
FrogPipe — Screaming Frog Headless Crawler Engine
Architected by Al Hossain Rifat
"""

import os
import sys
import subprocess
import time
from typing import Optional, Dict, Any

from modules.config import get_screaming_frog_cli, normalize_url
from modules.ui import HAS_RICH, console, print_step, print_success, print_error, print_warning


def run_headless_crawl(
    target_url: str,
    output_dir: str,
    verbose: bool = False
) -> bool:
    """
    Executes Screaming Frog SEO Spider CLI in headless mode.
    Exports the exact tabs and reports required for the 9-data audit suite.
    """
    frog_cli = get_screaming_frog_cli()
    if not frog_cli:
        print_error("Screaming Frog CLI executable not found on this machine.")
        print_warning("Checked: X:\\APPS\\Screaming Frog SEO Spider and C:\\Program Files...")
        return False

    target_url = normalize_url(target_url)
    os.makedirs(output_dir, exist_ok=True)

    # Required export tabs and reports
    export_tabs = (
        "Internal:All,"
        "Page Titles:All,"
        "Meta Description:All,"
        "H1:All,"
        "H2:All,"
        "Content:All,"
        "Images:All,"
        "Canonicals:All,"
        "Response Codes:All,"
        "Search Console:All"
    )
    save_reports = "Issues Overview"

    cmd = [
        frog_cli,
        "--crawl", target_url,
        "--headless",
        "--output-folder", output_dir,
        "--export-format", "csv",
        "--overwrite",
        "--export-tabs", export_tabs,
        "--save-report", save_reports,
    ]

    print_step("Headless Spider Engine Activated", f"Target: {target_url}")
    if verbose:
        print(f"Command: {' '.join(cmd)}")

    start_time = time.time()

    try:
        if HAS_RICH and not verbose:
            with console.status(f"[bold green]Crawling {target_url}...[/bold green] [dim](Running headless audit)[/dim]", spinner="dots"):
                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
        else:
            proc = subprocess.run(cmd)

        elapsed = time.time() - start_time

        if proc.returncode == 0:
            print_success(f"Crawl finished in {elapsed:.1f}s with status code 0.")
            return True
        else:
            print_error(f"Screaming Frog exited with non-zero return code: {proc.returncode}")
            if proc.stderr:
                print(proc.stderr[:500])
            return False

    except Exception as e:
        print_error(f"Execution failed with exception: {e}")
        return False
