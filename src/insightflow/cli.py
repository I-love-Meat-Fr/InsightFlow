from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from insightflow.config.loader import load_targets_file
from insightflow.config.settings import Settings
from insightflow.logging_config import setup_logging
from insightflow.pipeline import run_pipeline

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


@app.callback()
def _cli() -> None:
    """InsightFlow — scrape, analyze, report."""


@app.command("run")
def run(
    config: Path = typer.Option(Path("config/targets.yaml"), "--config", "-c", help="Path to targets YAML"),
    no_send: bool = typer.Option(False, "--no-send", help="Do not send Telegram/email"),
    no_llm: bool = typer.Option(False, "--no-llm", help="Skip LLM; stub digest in PDF"),
) -> None:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(settings.logs_dir, settings.log_level)
    log = logging.getLogger("insightflow.cli")

    if not config.exists():
        console.print(f"[red]Config not found:[/red] {config}")
        raise typer.Exit(1)

    tf = load_targets_file(config)
    crawl_total = max(1, len(tf.targets))

    async def _go() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console,
            transient=False,
        ) as progress:
            task_id = progress.add_task("Crawling targets", total=crawl_total)
            result = await run_pipeline(
                config,
                settings,
                no_send=no_send,
                no_llm=no_llm,
                progress=progress,
                crawl_task=task_id,
            )
        tbl = Table(title="Run summary")
        tbl.add_column("Metric", style="cyan")
        tbl.add_column("Value", style="white")
        tbl.add_row("PDF", result["pdf_path"])
        tbl.add_row("Products", str(result["products_count"]))
        tbl.add_row("News", str(result["news_count"]))
        tbl.add_row("Reviews", str(result["reviews_count"]))
        console.print(tbl)
        log.info("Run complete pdf=%s", result["pdf_path"])

    asyncio.run(_go())


def main() -> None:
    app()


if __name__ == "__main__":
    main()
