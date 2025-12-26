#!/usr/bin/env python
"""
Demo: Gap Detector Analysis
===========================

Demonstrates the core Gap Detector functionality of AI Risk Sentinel.

Usage:
    python scripts/demo_gap_detector.py
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from ai_risk_sentinel import GapDetector
from ai_risk_sentinel.models import MITCategory


def main():
    console = Console()
    
    console.print(Panel.fit(
        "[bold blue]🛡️ AI Risk Sentinel - Gap Detector Demo[/bold blue]\n"
        "[dim]Analyzing blind spots in AI risk documentation[/dim]",
        border_style="blue"
    ))
    console.print()
    
    # Initialize Gap Detector with reference data
    console.print("[yellow]Initializing Gap Detector with reference data...[/yellow]")
    detector = GapDetector(bsi_threshold=0.15, use_reference_data=True)
    
    # Run analysis
    console.print("[yellow]Running gap analysis...[/yellow]\n")
    report = detector.analyze()
    
    # Display Global Metrics
    console.print(Panel(
        f"[bold green]Global Blind Spot Index: {report.global_bsi:.3f}[/bold green]\n"
        f"Documentation Quality Score: {report.documentation_quality_score:.1f}%\n"
        f"Model Cards Analyzed: {report.model_cards_analyzed:,}\n"
        f"Incidents Analyzed: {report.incident_count:,}\n"
        f"Unique Risks in Catalog: {report.catalog_size:,}",
        title="📊 Global Metrics",
        border_style="green"
    ))
    console.print()
    
    # Display Category Breakdown
    table = Table(
        title="📈 Risk Category Analysis",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("Category", style="dim", width=35)
    table.add_column("Documented %", justify="right")
    table.add_column("Incidents %", justify="right")
    table.add_column("Gap (pts)", justify="right")
    table.add_column("BSI", justify="right")
    table.add_column("Status", justify="center")
    
    for metrics in report.by_category:
        # Color coding based on BSI
        if metrics.blind_spot_index > 0.5:
            status = "[red]🔴 CRITICAL[/red]"
            bsi_color = "red"
        elif metrics.blind_spot_index > 0.3:
            status = "[yellow]🟡 HIGH[/yellow]"
            bsi_color = "yellow"
        elif metrics.blind_spot_index > 0.15:
            status = "[orange3]🟠 MEDIUM[/orange3]"
            bsi_color = "orange3"
        else:
            status = "[green]🟢 LOW[/green]"
            bsi_color = "green"
        
        # Format category name
        cat_name = metrics.category.value.replace("_", " ").title()
        
        # Gap direction indicator
        gap_str = f"{metrics.gap:+.1f}"
        if metrics.gap < -5:
            gap_str = f"[red]{gap_str}[/red]"
        elif metrics.gap > 5:
            gap_str = f"[green]{gap_str}[/green]"
        
        table.add_row(
            cat_name,
            f"{metrics.documented_percentage:.1f}%",
            f"{metrics.incident_percentage:.1f}%",
            gap_str,
            f"[{bsi_color}]{metrics.blind_spot_index:.3f}[/{bsi_color}]",
            status
        )
    
    console.print(table)
    console.print()
    
    # Display High Risk Categories
    if report.high_risk_categories:
        console.print(Panel(
            "\n".join([
                f"[red]⚠️  {cat.value.replace('_', ' ').title()}[/red]"
                for cat in report.high_risk_categories
            ]),
            title="🚨 High Risk Blind Spots (BSI > 0.15, Under-documented)",
            border_style="red"
        ))
        console.print()
    
    # Display Priority Gaps
    priority_gaps = detector.get_priority_gaps(limit=3)
    
    if priority_gaps:
        console.print("[bold cyan]📋 Priority Gaps to Address:[/bold cyan]\n")
        
        for i, gap in enumerate(priority_gaps, 1):
            priority_color = {
                "CRITICAL": "red",
                "HIGH": "yellow",
                "MEDIUM": "orange3"
            }.get(gap["priority"], "white")
            
            console.print(Panel(
                f"[bold]Category:[/bold] {gap['category'].replace('_', ' ').title()}\n"
                f"[bold]Priority:[/bold] [{priority_color}]{gap['priority']}[/{priority_color}]\n"
                f"[bold]Blind Spot Index:[/bold] {gap['blind_spot_index']:.3f}\n"
                f"[bold]Gap:[/bold] {gap['gap_points']:+.1f} percentage points\n\n"
                f"[bold]Recommendation:[/bold]\n{gap['recommendation']}",
                title=f"Gap #{i}",
                border_style=priority_color
            ))
            console.print()
    
    # Summary
    console.print(Panel(
        "[bold]Key Findings:[/bold]\n\n"
        "• [red]Malicious Actors & Misuse[/red] shows the largest blind spot (BSI: 0.82)\n"
        "  - Only 4% documented vs 22.4% of real incidents\n\n"
        "• [yellow]Privacy & Security[/yellow] is under-documented relative to incidents\n"
        "  - Requires attention for EU AI Act compliance\n\n"
        "• [green]Discrimination & Toxicity[/green] is well-documented but over-represented\n"
        "  - 44.5% documented vs 27.5% of incidents\n\n"
        "[dim]Based on AI Model Risk Catalog (Rao et al., AAAI 2025)[/dim]",
        title="💡 Summary",
        border_style="blue"
    ))
    
    console.print("\n[dim]Demo complete. For full analysis, use the API or dashboard.[/dim]")


if __name__ == "__main__":
    main()
