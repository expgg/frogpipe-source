"""
FrogPipe — Screaming Frog Headless Crawler Engine
Architected by Al Hossain Rifat
"""

import os
import sys
import re
import time
import subprocess
from typing import Optional, Dict, Any

from modules.config import get_screaming_frog_cli, normalize_url
from modules.ui import (
    HAS_RICH,
    console,
    print_step,
    print_success,
    print_error,
    print_warning
)

if HAS_RICH:
    from rich.progress import (
        Progress,
        SpinnerColumn,
        BarColumn,
        TextColumn,
        TaskProgressColumn,
        TimeElapsedColumn
    )


def run_headless_crawl(
    target_url: str,
    output_dir: str,
    verbose: bool = False
) -> bool:
    """
    Executes Screaming Frog SEO Spider CLI in headless mode with real-time
    terminal progress bar and live metric streaming.
    """
    frog_cli = get_screaming_frog_cli()
    if not frog_cli:
        print_error("Screaming Frog CLI executable not found on this machine.")
        print_warning("Checked: X:\\APPS\\Screaming Frog SEO Spider and C:\\Program Files...")
        return False

    target_url = normalize_url(target_url)
    os.makedirs(output_dir, exist_ok=True)

    # Path to Screaming Frog live trace log
    trace_path = os.path.expanduser(r"~/.ScreamingFrogSEOSpider/trace.txt")
    init_trace_size = os.path.getsize(trace_path) if os.path.exists(trace_path) else 0

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
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL if not verbose else None,
            stderr=subprocess.DEVNULL if not verbose else None
        )

        # Real-time Progress Tracking using Rich
        if HAS_RICH and not verbose:
            with Progress(
                SpinnerColumn(spinner_name="dots"),
                TextColumn("[bold bright_green]{task.description}[/bold bright_green]"),
                BarColumn(bar_width=28, complete_style="bright_green", finished_style="bold green"),
                TaskProgressColumn(),
                TextColumn("[cyan]{task.fields[status_info]}[/cyan]"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                crawl_task = progress.add_task(
                    "Initializing Spider...",
                    total=100.0,
                    status_info="Starting crawl engine"
                )

                # Tail trace.txt for real-time spider progress
                last_pos = init_trace_size
                while proc.poll() is None:
                    time.sleep(0.2)
                    if not os.path.exists(trace_path):
                        continue

                    try:
                        with open(trace_path, "r", encoding="utf-8", errors="replace") as f:
                            f.seek(last_pos)
                            new_lines = f.readlines()
                            last_pos = f.tell()

                            for line in new_lines:
                                line = line.strip()
                                # Spider Progress match
                                m = re.search(r"SpiderProgress\s*\[.*mCompleted=(\d+).*mCompleted=([\d.]+)%\]", line)
                                if m:
                                    crawled = m.group(1)
                                    pct = float(m.group(2))
                                    progress.update(
                                        crawl_task,
                                        description="Crawling target DOM...",
                                        completed=pct,
                                        status_info=f"• {crawled} URLs crawled"
                                    )
                                elif "Writing report" in line:
                                    rep_name = line.split("Writing report")[-1].split("to")[0].strip()
                                    progress.update(
                                        crawl_task,
                                        description=f"Exporting: {rep_name}",
                                        completed=100.0,
                                        status_info="• Generating CSV"
                                    )
                    except Exception:
                        pass

                progress.update(crawl_task, description="Audit Complete", completed=100.0, status_info="• Packaging data")
        else:
            proc.wait()

        elapsed = time.time() - start_time
        return_code = proc.poll()

        if return_code == 0:
            print_success(f"Crawl finished in {elapsed:.1f}s with status code 0.")
            return True
        else:
            print_error(f"Screaming Frog exited with non-zero return code: {return_code}")
            return False

    except Exception as e:
        print_error(f"Execution failed with exception: {e}")
        return False
