"""
FrogPipe — High-Impact Terminal UI & Visuals
Architected by Al Hossain Rifat
"""

import os
from typing import List, Dict, Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

console = Console() if HAS_RICH else None


def print_banner():
    """Renders the executive FrogPipe cyberpunk terminal banner."""
    if HAS_RICH:
        # Aligned raw string ASCII art for FROGPIPE with zero font drift
        ascii_art = r"""[bold bright_green]  ______ _____   ____   _____ _____ _____ _____  ______ 
 |  ____|  __ \ / __ \ / ____|  __ \_   _|  __ \|  ____|
 | |__  | |__) | |  | | |  __| |__) || | | |__) | |__   
 |  __| |  _  /| |  | | | |_ |  ___/ | | |  ___/|  __|  
 | |    | | \ \| |__| | |__| | |    _| |_| |    | |____ 
 |_|    |_|  \_|\____/ \_____|_|   |_____|_|    |______|[/bold bright_green]"""

        meta_info = (
            "\n\n[bold white] Autonomous SEO Spider & 9-Data Audit Pipeline [green]--[/green] Mark 1[/bold white]\n"
            "[bold cyan] Architected & Engineered by[/bold cyan] [bold bright_yellow]Al Hossain Rifat[/bold bright_yellow] "
            "[bold bright_cyan]|[/bold bright_cyan] [bold bright_magenta underline]r1fat.pages.dev[/bold bright_magenta underline]"
        )

        console.print(Panel(
            ascii_art + meta_info,
            border_style="bright_green",
            box=box.DOUBLE,
            subtitle="[dim green]v1.0.0 | Production Engine[/dim green]",
            subtitle_align="right"
        ))
    else:
        print("=" * 70)
        print("   FROGPIPE -- Autonomous SEO Spider & Audit Pipeline (Mark 1)")
        print("   Architected & Engineered by Al Hossain Rifat | r1fat.pages.dev")
        print("=" * 70)




def print_step(title: str, description: str = ""):
    """Prints a styled step indicator."""
    if HAS_RICH:
        msg = f"[bold green]▶[/bold green] [bold white]{title}[/bold white]"
        if description:
            msg += f" [dim]— {description}[/dim]"
        console.print(msg)
    else:
        print(f">>> {title} — {description}" if description else f">>> {title}")


def print_success(message: str):
    """Prints a success message."""
    if HAS_RICH:
        console.print(f"  [bold green][✓][/bold green] {message}")
    else:
        print(f"  [✓] {message}")


def print_warning(message: str):
    """Prints a warning message."""
    if HAS_RICH:
        console.print(f"  [bold yellow][!][/bold yellow] [yellow]{message}[/yellow]")
    else:
        print(f"  [!] {message}")


def print_error(message: str):
    """Prints an error message."""
    if HAS_RICH:
        console.print(f"  [bold red][✗][/bold red] [red]{message}[/red]")
    else:
        print(f"  [✗] {message}")


def print_files_summary(folder_path: str, datasets: List[Dict[str, Any]]):
    """Prints a high-contrast executive table summarizing the 9 generated audit files."""
    if HAS_RICH:
        table = Table(
            title="[bold green]🐸 FrogPipe Packaged Audit Deliverables[/bold green]",
            box=box.ROUNDED,
            header_style="bold cyan",
            border_style="dim green"
        )
        table.add_column("#", justify="center", style="dim", width=4)
        table.add_column("Audit Tab / File Name", style="bold white")
        table.add_column("Rows", justify="right", style="green")
        table.add_column("Size", justify="right", style="yellow")
        table.add_column("Status", justify="center")

        total_size = 0
        total_rows = 0

        for i, item in enumerate(datasets, 1):
            rows = item.get("rows", 0)
            size_kb = item.get("size_kb", 0.0)
            status = "[bold green]VERIFIED[/bold green]" if item.get("found", False) else "[bold red]MISSING[/bold red]"
            
            table.add_row(
                str(i),
                item.get("target_file", item.get("title", "")),
                f"{rows:,}" if rows > 0 else "-",
                f"{size_kb:.1f} KB" if size_kb > 0 else "-",
                status
            )
            total_size += size_kb
            total_rows += rows

        console.print()
        console.print(table)
        
        # Clickable folder link panel
        norm_path = os.path.normpath(folder_path)
        file_url = f"file:///{norm_path.replace(os.sep, '/')}"
        
        summary_panel = (
            f"[bold green]✔ Mark 1 Audit Packaging Completed Successfully![/bold green]\n\n"
            f"[bold white]Target Folder:[/bold white] [cyan underline]{file_url}[/cyan underline]\n"
            f"[dim]Total Dataset Size: {total_size:.2f} KB | Total Entries: {total_rows:,}[/dim]\n"
            f"[dim green]Ready for Step 2 (Google Sheets live synchronization).[/dim green]"
        )
        console.print(Panel(summary_panel, border_style="green", box=box.ROUNDED))
    else:
        print("\n" + "=" * 60)
        print(f"AUDIT DATASETS GENERATED IN: {folder_path}")
        print("=" * 60)
        for item in datasets:
            print(f"- {item.get('target_file')}: {item.get('rows', 0)} rows ({item.get('size_kb', 0):.1f} KB)")
        print("=" * 60 + "\n")
