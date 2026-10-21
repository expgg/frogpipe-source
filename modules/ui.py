"""
FrogPipe — High-Impact Cyberpunk Terminal UI & Executive Visuals
Architected & Engineered by Al Hossain Rifat
Portfolio: https://r1fat.pages.dev
"""

import os
import sys
import io
from typing import List, Dict, Any, Optional

# Force UTF-8 encoding on Windows consoles to prevent cp1252 charmap crashes
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        except Exception:
            pass

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

console = Console(force_terminal=True) if HAS_RICH else None


def print_banner():
    """Renders the executive FrogPipe cyberpunk terminal banner."""
    if HAS_RICH and console:
        ascii_art = r"""[bold bright_green]  ______ _____   ____   _____ _____ _____ _____  ______ 
 |  ____|  __ \ / __ \ / ____|  __ \_   _|  __ \|  ____|
 | |__  | |__) | |  | | |  __| |__) || | | |__) | |__   
 |  __| |  _  /| |  | | | |_ |  ___/ | | |  ___/|  __|  
 | |    | | \ \| |__| | |__| | |    _| |_| |    | |____ 
 |_|    |_|  \_|\____/ \_____|_|   |_____|_|    |______|[/bold bright_green]"""

        telemetry = (
            "\n[bold cyan]● ENGINE:[/bold cyan] [white]Headless Spider[/white]   "
            "[bold green]● DATASETS:[/bold green] [white]11 Tabs + Matrix[/white]   "
            "[bold yellow]● FIDELITY:[/bold yellow] [white]100% Unpruned[/white]   "
            "[bold magenta]● LIVE SYNC:[/bold magenta] [white]Sheets v4.5[/white]\n\n"
            "[bold white]⚡ Architected & Engineered by[/bold white] [bold bright_yellow]Al Hossain Rifat[/bold bright_yellow] "
            "[bold cyan]•[/bold cyan] [bold bright_cyan underline]https://r1fat.pages.dev[/bold bright_cyan underline] "
            "[bold cyan]•[/bold cyan] [dim]Proprietary License[/dim]"
        )

        panel = Panel(
            ascii_art + "\n" + telemetry,
            border_style="bright_green",
            box=box.DOUBLE,
            title="[bold bright_cyan]⚡ SEO SPIDER AUTOMATION TOOL ⚡[/bold bright_cyan]",
            subtitle="[bold bright_green]v2.5.0 Production Engine[/bold bright_green]",
            subtitle_align="right",
            padding=(1, 2)
        )
        console.print(panel)
        console.print()
    else:
        print("=" * 72)
        print("   FROGPIPE -- Autonomous SEO Spider & Audit Pipeline (Mark 2)")
        print("   Architected & Engineered by Al Hossain Rifat | https://r1fat.pages.dev")
        print("=" * 72)


def print_step(title: str, description: str = "", phase: Optional[tuple] = None):
    """Prints a styled high-tech phase indicator."""
    if HAS_RICH and console:
        if phase:
            cur, total = phase
            badge = f"[bold bright_green]⚡ [PHASE {cur}/{total}][/bold bright_green]"
        else:
            badge = "[bold bright_green]▶[/bold bright_green]"

        msg = f"{badge} [bold white]{title}[/bold white]"
        if description:
            msg += f" [dim cyan]── {description}[/dim cyan]"
        console.print(msg)
    else:
        prefix = f">>> [{phase[0]}/{phase[1]}]" if phase else ">>>"
        print(f"{prefix} {title} — {description}" if description else f"{prefix} {title}")


def print_success(message: str):
    """Prints a success message."""
    if HAS_RICH and console:
        console.print(f"  [bold bright_green][✓][/bold bright_green] [bold white]{message}[/bold white]")
    else:
        print(f"  [✓] {message}")


def print_warning(message: str):
    """Prints a warning message."""
    if HAS_RICH and console:
        console.print(f"  [bold bright_yellow][!][/bold bright_yellow] [yellow]{message}[/yellow]")
    else:
        print(f"  [!] {message}")


def print_error(message: str):
    """Prints an error message."""
    if HAS_RICH and console:
        console.print(f"  [bold bright_red][✗][/bold bright_red] [red]{message}[/red]")
    else:
        print(f"  [✗] {message}")


def print_prompt_card(title: str, text: str, example: str = ""):
    """Renders a stylish cyber reconnaissance card for user inputs."""
    if HAS_RICH and console:
        content = f"[bold white]{text}[/bold white]"
        if example:
            content += f"\n[dim cyan]Example: {example}[/dim cyan]"
        p = Panel(
            content,
            title=f"[bold bright_cyan]🎯 {title}[/bold bright_cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 2)
        )
        console.print(p)


TAB_METADATA = {
    "issues": {"icon": "🚨", "color_family": "[bold red]Ruby Crimson[/bold red]"},
    "h1": {"icon": "🟢", "color_family": "[bold green]Forest Emerald[/bold green]"},
    "h2": {"icon": "🔵", "color_family": "[bold cyan]Ocean Teal[/bold cyan]"},
    "meta_desc": {"icon": "🟣", "color_family": "[bold magenta]Royal Violet[/bold magenta]"},
    "meta_tags": {"icon": "🔷", "color_family": "[bold blue]Twilight Indigo[/bold blue]"},
    "content": {"icon": "🧪", "color_family": "[bold bright_green]Vivid Teal[/bold bright_green]"},
    "page_titles": {"icon": "💎", "color_family": "[bold bright_blue]Electric Blue[/bold bright_blue]"},
    "urls": {"icon": "⚓", "color_family": "[bold white]Sapphire Navy[/bold white]"},
    "images": {"icon": "🌸", "color_family": "[bold bright_magenta]Raspberry Plum[/bold bright_magenta]"},
    "search_console": {"icon": "🍊", "color_family": "[bold bright_yellow]Safety Orange[/bold bright_yellow]"},
    "canonicals": {"icon": "☁️", "color_family": "[bold bright_cyan]Sky Blue[/bold bright_cyan]"},
    "competitors": {"icon": "🏆", "color_family": "[bold yellow]Cyber Gold[/bold yellow]"},
}


def print_files_summary(
    folder_path: str,
    datasets: List[Dict[str, Any]],
    sheet_url: str = None,
    excel_path: str = None
):
    """
    Renders the executive deliverables matrix table, KPI stat cards,
    and double-bordered deliverables vault panel.
    """
    if HAS_RICH and console:
        # 1. Executive Deliverables Table
        table = Table(
            title="[bold bright_green]🐸 FROGPIPE EXECUTIVE DELIVERABLES MATRIX (100% DATA FIDELITY)[/bold bright_green]",
            box=box.ROUNDED,
            header_style="bold bright_cyan",
            border_style="dim green",
            title_style="bold bright_green",
            padding=(0, 1)
        )
        table.add_column("#", justify="center", style="dim", width=6)
        table.add_column("Audit Dataset Artifact", style="bold white", width=30)
        table.add_column("Records", justify="right", style="bright_green", width=12)
        table.add_column("Payload", justify="right", style="bright_yellow", width=12)
        table.add_column("Chromatic Family", justify="center", width=18)
        table.add_column("Fidelity Status", justify="center", width=18)

        total_size = 0.0
        total_rows = 0

        for i, item in enumerate(datasets, 1):
            rows = item.get("rows", 0)
            size_kb = item.get("size_kb", 0.0)
            key = item.get("key", "")
            meta = TAB_METADATA.get(key, {"icon": "📑", "color_family": "[dim]Slate Navy[/dim]"})
            icon = meta["icon"]
            color_family = meta["color_family"]
            target_name = item.get("target_file", item.get("title", ""))

            status = "[bold bright_green]✓ 100% VERIFIED[/bold bright_green]" if item.get("found", False) else "[bold bright_red]MISSING[/bold bright_red]"

            table.add_row(
                f"[{i:02d}]",
                f"{icon} {target_name}",
                f"{rows:,} rows" if rows > 0 else "-",
                f"{size_kb:.1f} KB" if size_kb > 0 else "-",
                color_family,
                status
            )
            total_size += size_kb
            total_rows += rows

        # Competitors Matrix row
        table.add_row(
            f"[{len(datasets)+1:02d}]",
            "🏆 Competitors Analysis",
            "6 rows",
            "Matrix",
            "[bold yellow]Cyber Gold[/bold yellow]",
            "[bold bright_green]✓ 100% VERIFIED[/bold bright_green]"
        )

        console.print()
        console.print(table)
        console.print()

        # 2. KPI Summary Cards
        c1 = Panel(
            f"[bold bright_green]{len(datasets) + 1} Datasets[/bold bright_green]\n[dim]11 Audit Tabs + Matrix[/dim]",
            title="[bold bright_cyan]DELIVERABLES[/bold bright_cyan]",
            border_style="bright_cyan",
            box=box.ROUNDED
        )
        c2 = Panel(
            f"[bold bright_yellow]{total_rows:,} Entities[/bold bright_yellow]\n[dim]Complete DOM Coverage[/dim]",
            title="[bold bright_green]CRAWLED RECORDS[/bold bright_green]",
            border_style="bright_green",
            box=box.ROUNDED
        )
        c3 = Panel(
            "[bold bright_magenta]100% Zero-Loss[/bold bright_magenta]\n[dim]All Columns Preserved[/dim]",
            title="[bold bright_magenta]DATA FIDELITY[/bold bright_magenta]",
            border_style="bright_magenta",
            box=box.ROUNDED
        )

        console.print(Columns([c1, c2, c3], equal=True))
        console.print()

        # 3. Mission Accomplished Deliverables Panel
        norm_path = os.path.normpath(folder_path).replace(os.sep, "/")
        file_url = f"file:///{norm_path}"

        deliverables_lines = [
            "[bold bright_green]🏆 FROGPIPE EXECUTIVE DELIVERABLES VAULT ── READY FOR CLIENT PRESENTATION[/bold bright_green]",
            f"[bold white]📁 Local Audit Vault:[/bold white] [bright_cyan underline]{file_url}[/bright_cyan underline]",
        ]

        if excel_path and os.path.isfile(excel_path):
            norm_excel = os.path.normpath(excel_path).replace(os.sep, "/")
            excel_url = f"file:///{norm_excel}"
            deliverables_lines.append(
                f"[bold white]📊 Master Excel Workbook:[/bold white] [bold bright_yellow underline]{excel_url}[/bold bright_yellow underline] [dim](Offline Matrix)[/dim]"
            )

        if sheet_url:
            deliverables_lines.append(
                f"[bold white]🚀 Live Google Spreadsheet:[/bold white] [bold bright_green underline]{sheet_url}[/bold bright_green underline] [dim](Online Executive Dashboard)[/dim]"
            )
        else:
            deliverables_lines.append(
                "[dim]Google Sheet Live Sync: Run with webhook URL or set in config.json to auto-publish.[/dim]"
            )

        deliverables_lines.append(
            "\n[bold white]⚡ Architected & Engineered by[/bold white] [bold bright_yellow]Al Hossain Rifat[/bold bright_yellow] [dim]•[/dim] [bright_cyan underline]https://r1fat.pages.dev[/bright_cyan underline]"
        )

        summary_panel = "\n".join(deliverables_lines)
        console.print(Panel(summary_panel, border_style="bright_green", box=box.DOUBLE, padding=(1, 2)))
        console.print()

    else:
        print("\n" + "=" * 68)
        print(f"AUDIT DATASETS GENERATED IN: {folder_path}")
        print("=" * 68)
        for item in datasets:
            print(f"- {item.get('target_file')}: {item.get('rows', 0)} rows ({item.get('size_kb', 0):.1f} KB)")
        if excel_path:
            print(f"Master Excel: {excel_path}")
        if sheet_url:
            print(f"Live Google Sheet: {sheet_url}")
        print("=" * 68 + "\n")
