import asyncio
import os
import sys
import time
from datetime import datetime

try:
    from rich.live import Live
    from rich.table import Table
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.console import Console
    from rich.text import Text
    from temporalio.client import Client, WorkflowExecutionStatus
except ImportError:
    print("Dependencies missing. Run: pip install temporalio rich")
    sys.exit(1)

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "100.95.165.3:7233")
NAMESPACE = "default"

console = Console()


async def fetch_stats(client: Client):
    try:
        workflows = client.list_workflows("ExecutionStatus='Running'")
        running_wfs = []
        async for wf in workflows:
            running_wfs.append(wf)

        return running_wfs
    except Exception as e:
        return []


def generate_dashboard(wfs) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )

    # Header
    header = Panel(
        f"🚀 Oyster AI Factory - L4 Autonomous Fleet Dashboard  |  Temporal Cluster: [cyan]{TEMPORAL_HOST}[/cyan]",
        style="bold magenta",
    )
    layout["header"].update(header)

    # Main Table
    table = Table(show_header=True, header_style="bold yellow", expand=True)
    table.add_column("Workflow ID")
    table.add_column("Type")
    table.add_column("Start Time")
    table.add_column("Status")
    table.add_column("Activities/Tasks")

    if not wfs:
        table.add_row(
            "[dim]No running workflows detected. Waiting for dispatch processing...[/dim]",
            "",
            "",
            "",
            "",
        )
    else:
        for wf in wfs:
            table.add_row(
                f"[bold cyan]{wf.id}[/bold cyan]",
                wf.workflow_type,
                wf.start_time.strftime("%H:%M:%S") if wf.start_time else "N/A",
                "[bold green]Running[/bold green]",
                "Polling Activities...",  # We could enrich this later
            )

    layout["main"].update(Panel(table, title="Active Operations"))

    # Footer
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    layout["footer"].update(
        Panel(
            f"Last updated: {timestamp} | Auto-refreshing every 2 seconds. Press Ctrl+C to exit.",
            style="dim",
        )
    )

    return layout


async def main():
    try:
        client = await Client.connect(TEMPORAL_HOST, namespace=NAMESPACE)
    except Exception as e:
        console.print(
            f"[bold red]Failed to connect to Temporal Server at {TEMPORAL_HOST}:[/bold red] {e}"
        )
        return

    with Live(refresh_per_second=2, screen=True) as live:
        while True:
            wfs = await fetch_stats(client)
            live.update(generate_dashboard(wfs))
            await asyncio.sleep(2)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
