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

from modules.config import get_screaming_frog_cli, normalize_url, load_spider_config_path
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


def ensure_high_capacity_storage():
    """
    Ensures Screaming Frog's Derby database cache is placed on a high-capacity drive
    (e.g. X:\\ if available) instead of filling the user's C: drive under 5.0 GB.
    """
    config_path = os.path.expanduser("~/.ScreamingFrogSEOSpider/spider.config")
    if not os.path.exists(config_path):
        return
    try:
        with open(config_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        
        current_dir = ""
        for line in lines:
            if line.startswith("storage.db_dir="):
                current_dir = line.split("=", 1)[1].strip()
                break

        # If current_dir is on C: and drive X:\ exists with ample space (> 20 GB)
        if "c\\" in current_dir.lower() or "c:" in current_dir.lower() or not current_dir:
            drive_x = "X:\\"
            if os.path.exists(drive_x):
                try:
                    total_x, used_x, free_x = shutil.disk_usage(drive_x)
                    if (free_x / (1024 ** 3)) > 20.0:
                        x_db_dir = r"X:\ScreamingFrog_Cache"
                        os.makedirs(x_db_dir, exist_ok=True)
                        new_lines = []
                        found = False
                        for line in lines:
                            if line.startswith("storage.db_dir="):
                                new_lines.append(r"storage.db_dir=X\:\\ScreamingFrog_Cache" + "\n")
                                found = True
                            else:
                                new_lines.append(line)
                        if not found:
                            new_lines.append(r"storage.db_dir=X\:\\ScreamingFrog_Cache" + "\n")
                        with open(config_path, "w", encoding="utf-8") as f:
                            f.writelines(new_lines)
                        print_success(f"Storage Cache Relocated: [bold cyan]X:\\ScreamingFrog_Cache[/bold cyan] (Ample space on X: drive protects C: drive from filling up)")
                except Exception:
                    pass
    except Exception:
        pass


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

        # Always inspect ProjectInstanceData for abandoned instances
        for search_root in [spider_home, r"X:\ScreamingFrog_Cache"]:
            inst_dir = os.path.join(search_root, "ProjectInstanceData")
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


def inspect_robots_and_sitemap(target_url: str) -> dict:
    """
    Performs a 0.5s pre-flight check on target_domain/robots.txt and target_domain/sitemap.xml.
    Returns status indicators without blocking or slowing the crawl.
    """
    import urllib.parse
    import urllib.request

    parsed = urllib.parse.urlparse(target_url)
    base_origin = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{base_origin}/robots.txt"
    sitemap_url = f"{base_origin}/sitemap.xml"

    result = {
        "robots_ok": False,
        "robots_status": "Missing",
        "sitemap_ok": False,
        "sitemap_status": "Missing",
        "sitemaps_declared": []
    }

    # 1. Quick check robots.txt
    try:
        req = urllib.request.Request(
            robots_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FrogPipe/2.5"}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                result["robots_ok"] = True
                result["robots_status"] = "200 OK"
                content = resp.read().decode("utf-8", errors="replace")
                for line in content.splitlines():
                    if line.lower().startswith("sitemap:"):
                        declared = line.split(":", 1)[1].strip()
                        if declared:
                            result["sitemaps_declared"].append(declared)
    except Exception:
        result["robots_status"] = "404 Not Found"

    # 2. Quick check sitemap.xml
    try:
        req = urllib.request.Request(
            sitemap_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FrogPipe/2.5"}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                result["sitemap_ok"] = True
                result["sitemap_status"] = "Found (200 OK)"
    except Exception:
        if result["sitemaps_declared"]:
            result["sitemap_ok"] = True
            result["sitemap_status"] = f"Declared ({len(result['sitemaps_declared'])} map)"
        else:
            result["sitemap_status"] = "404 Missing"

    return result


def run_headless_crawl(
    target_url: str,
    output_dir: str,
    crawl_limit: Optional[int] = None,
    config_file: Optional[str] = None,
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

    # Proactive high-capacity storage optimization
    ensure_high_capacity_storage()

    # Pre-flight disk space health check (Screaming Frog hard stops if free disk < 5.0 GB)
    free_gb = check_and_clean_disk_space()
    if free_gb < 5.2:
        print_error(f"Critical Disk Warning: Only {free_gb:.2f} GB free on system drive!")
        print_warning("Screaming Frog has a hardcoded emergency abort if free disk space drops below 5.0 GB.")

    target_url = normalize_url(target_url)
    os.makedirs(output_dir, exist_ok=True)

    # Pre-flight Robots.txt & Sitemap Recon (0.3s)
    pre_recon = inspect_robots_and_sitemap(target_url)
    r_badge = f"[bold bright_green]robots.txt: {pre_recon['robots_status']}[/bold bright_green]" if pre_recon['robots_ok'] else f"[yellow]robots.txt: {pre_recon['robots_status']}[/yellow]"
    s_badge = f"[bold bright_green]sitemap: {pre_recon['sitemap_status']}[/bold bright_green]" if pre_recon['sitemap_ok'] else f"[yellow]sitemap: {pre_recon['sitemap_status']}[/yellow]"
    print_success(f"Pre-Flight Recon: {r_badge} • {s_badge}")


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

    # Optional custom .seospiderconfig profile support
    active_config = config_file or load_spider_config_path()
    if active_config and os.path.isfile(active_config):
        cmd.extend(["--config", active_config])
        print_success(f"Loaded Spider Config: [dim]{active_config}[/dim]")

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

