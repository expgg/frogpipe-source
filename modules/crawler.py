"""
FrogPipe — Screaming Frog Headless Crawler Engine
Architected by Al Hossain Rifat
"""

import os
import sys
import re
import time
import shutil
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


def check_and_clean_disk_space() -> float:
    """
    Checks free disk space on the drive hosting Screaming Frog project data.
    If space is below 6.0 GB, automatically purges abandoned Derby instance databases.
    Returns available free space in GB.
    """
    spider_home = os.path.expanduser("~/.ScreamingFrogSEOSpider")
    try:
        check_path = spider_home if os.path.exists(spider_home) else os.path.expanduser("~")
        total, used, free = shutil.disk_usage(check_path)
        free_gb = free / (1024 ** 3)

        if free_gb < 6.0:
            inst_dir = os.path.join(spider_home, "ProjectInstanceData")
            if os.path.exists(inst_dir):
                cleaned_bytes = 0
                for item in os.listdir(inst_dir):
                    if item == "DO_NOT_MODIFY_THESE_FILES.txt":
                        continue
                    item_path = os.path.join(inst_dir, item)
                    if os.path.isdir(item_path):
                        try:
                            item_size = sum(os.path.getsize(os.path.join(r, f)) for r, d, files in os.walk(item_path) for f in files)
                            shutil.rmtree(item_path, ignore_errors=True)
                            cleaned_bytes += item_size
                        except Exception:
                            pass
                if cleaned_bytes > 0:
                    print_warning(f"Purged {cleaned_bytes / (1024**2):.1f} MB of orphaned Screaming Frog cache to free up disk space.")
                # Recalculate
                total, used, free = shutil.disk_usage(check_path)
                free_gb = free / (1024 ** 3)
        return free_gb
    except Exception:
        return 999.0


def extract_last_fatal_error(trace_path: str) -> Optional[str]:
    """
    Reads the tail of Screaming Frog's trace.txt to find the exact FATAL or ERROR reason.
    """
    if not os.path.exists(trace_path):
        return None
    try:
        with open(trace_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            for line in reversed(lines[-60:]):
                line_str = line.strip()
                if "FATAL -" in line_str or "Less than 5.0 GB left" in line_str:
                    return line_str
    except Exception:
        pass
    return None


def run_headless_crawl(
    target_url: str,
    output_dir: str,
    crawl_limit: Optional[int] = None,
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

    # Pre-flight disk space health check (Screaming Frog hard stops if free disk < 5.0 GB)
    free_gb = check_and_clean_disk_space()
    if free_gb < 5.2:
        print_error(f"Critical Disk Warning: Only {free_gb:.2f} GB free on system drive!")
        print_warning("Screaming Frog has a hardcoded emergency abort if free disk space drops below 5.0 GB.")

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
        "Directives:All,"
        "Meta Keywords:All,"
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

    print_step("Headless Spider Engine Activated", f"Target: {target_url}", phase=(1, 4))
    if verbose:
        print(f"Command: {' '.join(cmd)}")

    start_time = time.time()

    # Precompile regex for Screaming Frog SpiderProgress
    progress_pattern = re.compile(r"SpiderProgress\s*\[.*?mCompleted=([0-9,]+?),\s*mWaiting=([0-9,]+?),\s*mCompleted=([0-9.]+)%")

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL if not verbose else None,
            stderr=subprocess.DEVNULL if not verbose else None
        )

        # Real-time Progress Tracking using Rich
        if HAS_RICH and not verbose:
            with Progress(
                SpinnerColumn(spinner_name="dots12", style="bold bright_green"),
                TextColumn("[bold bright_white]{task.description}[/bold bright_white]"),
                BarColumn(bar_width=32, complete_style="bright_green", finished_style="bold green"),
                TaskProgressColumn(style="bold bright_yellow"),
                TextColumn("[bold cyan]{task.fields[status_info]}[/bold cyan]"),
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
                                m = progress_pattern.search(line)
                                if m:
                                    crawled = m.group(1).strip()
                                    waiting = m.group(2).strip()
                                    pct = float(m.group(3))
                                    progress.update(
                                        crawl_task,
                                        description="Crawling target DOM...",
                                        completed=pct,
                                        status_info=f"• {crawled} crawled ({waiting} in queue)"
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
            fatal_reason = extract_last_fatal_error(trace_path)
            if fatal_reason:
                if "Disk usage too high" in fatal_reason or "Less than 5.0 GB left" in fatal_reason:
                    print_error("Root Cause: Disk usage too high (C: drive dropped below 5.0 GB free threshold).")
                    print_warning("Screaming Frog requires at least 5.0 GB free disk space. Free up disk space or purge old project data.")
                elif "Unrecognized option" in fatal_reason:
                    print_error(f"Root Cause: {fatal_reason.split('FATAL -')[-1].strip()}")
                else:
                    print_error(f"Log Detail: {fatal_reason}")
            return False

    except Exception as e:
        print_error(f"Execution failed with exception: {e}")
        return False

