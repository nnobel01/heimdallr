#!/usr/bin/env python3
"""
Heimdallr CLI - Main command line interface for facial recognition search
"""

import click
import os
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table
from typing import Callable, Optional, Dict, Any

from .core.face_detector import FaceDetector
from .core.search_engine import SearchEngine
from .core.results_processor import ResultsProcessor
from .utils.config import Config
from .utils.logger import setup_logger

console = Console()
logger = setup_logger()


def execute_search(
    image_path: str,
    output_dir_str: str,
    format_type: str,
    threshold: float,
    platforms: str,
    aggressive: bool,
    config_path: Optional[str],
    verbose: bool,
    progress_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Core logic for executing a Heimdallr search.
    This function is UI-agnostic and can be called from a CLI, GUI, or other script.
    """
    # Setup configuration
    config_obj = Config(config_path=config_path)
    if verbose:
        config_obj.set_verbose(True)

    # Create output directory
    output_dir = Path(output_dir_str)
    output_dir.mkdir(exist_ok=True)

    # Phase 1: Face Detection
    if progress_callback:
        progress_callback("face_detection", "🔍 Detecting faces in image...", 0)
    face_detector = FaceDetector(threshold=threshold / 100)
    faces_data = face_detector.process_image(image_path)
    if progress_callback:
        progress_callback("face_detection", "🔍 Face detection complete.", 100)

    if not faces_data['faces_found']:
        raise click.ClickException("No faces detected in the input image.")
    console.print(f"✅ [green]Found {faces_data['face_count']} face(s) in image[/green]")

    # Phase 2: Search Engine Setup
    if progress_callback:
        progress_callback("search_engine", "🚀 Initializing search engines...", 0)
    search_engine = SearchEngine(
        config=config_obj,
        aggressive_mode=aggressive,
        platforms=platforms
    )
    if progress_callback:
        progress_callback("search_engine", "🚀 Search engines initialized.", 100)
    
    # Phase 3: Multi-platform Search
    # Define a new callback for the search engine's progress
    def search_progress_updater(p_val):
        if progress_callback:
            progress_callback("platform_search", f"🌐 Searching across platforms... {int(p_val)}%", p_val)

    search_results = search_engine.search_all_platforms(
        faces_data,
        progress_callback=search_progress_updater
    )
    if progress_callback:
        progress_callback("platform_search", "🌐 Search complete.", 100)

    # Phase 4: Results Processing
    if progress_callback:
        progress_callback("results_processing", "📊 Processing and ranking results...", 0)
    processor = ResultsProcessor(threshold=threshold)
    final_results = processor.process_results(search_results, faces_data)
    if progress_callback:
        progress_callback("results_processing", "📊 Results processing complete.", 100)

    return final_results


@click.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--output', '-o', default='results', help='Output directory for results')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'both']), default='both', help='Output format')
@click.option('--threshold', '-t', default=80.0, help='Similarity threshold percentage (default: 80%)')
@click.option('--platforms', '-p', default='all', help='Platforms to search: all, social, web, or comma-separated list')
@click.option('--aggressive', '-a', is_flag=True, help='Enable aggressive search mode (max speed, risk of detection)')
@click.option('--config', '-c', type=click.Path(), help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(image_path, output, format, threshold, platforms, aggressive, config, verbose):
    """
    Heimdallr - Advanced Facial Recognition Search Tool
    
    Search for faces across social media and the web with high accuracy.
    
    Examples:
        heimdallr photo.jpg
        heimdallr photo.jpg --aggressive --threshold 85
        heimdallr photo.jpg --platforms instagram,facebook --format json
    """
    # Display banner
    console.print(Panel.fit(
        "[bold cyan]🔍 HEIMDALLR[/bold cyan]\n"
        "[dim]Advanced Facial Recognition Search[/dim]\n"
        "[yellow]⚠️  Use responsibly and respect privacy[/yellow]",
        border_style="cyan"
    ))

    try:
        final_results = None
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            tasks = {
                "face_detection": progress.add_task("", total=100),
                "search_engine": progress.add_task("", total=100),
                "platform_search": progress.add_task("", total=100),
                "results_processing": progress.add_task("", total=100),
            }

            def cli_progress_callback(task_name: str, description: str, completed: float):
                progress.update(tasks[task_name], description=description, completed=completed)

            final_results = execute_search(
                image_path=image_path,
                output_dir_str=output,
                format_type=format,
                threshold=threshold,
                platforms=platforms,
                aggressive=aggressive,
                config_path=config,
                verbose=verbose,
                progress_callback=cli_progress_callback
            )

        # Display results summary and save
        display_results_summary(final_results)
        save_results(final_results, Path(output), format, image_path)

        console.print(f"\n✅ [green]Search completed! Results saved to '{output}'[/green]")

    except (click.ClickException, Exception) as e:
        console.print(f"\n❌ [red]An error occurred: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


def display_results_summary(results):
    """Display a summary table of search results"""
    table = Table(title="🎯 Search Results Summary")
    table.add_column("Platform", style="cyan")
    table.add_column("Matches Found", justify="right", style="green")
    table.add_column("Best Match", justify="right", style="yellow")
    table.add_column("Status", style="white")
    
    for platform, data in results['platform_results'].items():
        matches = len(data.get('matches', []))
        best_score = max([m['similarity_score'] for m in data.get('matches', [])], default=0)
        status = "✅ Success" if matches > 0 else "❌ No matches"
        
        table.add_row(
            platform.title(),
            str(matches),
            f"{best_score:.1f}%" if best_score > 0 else "N/A",
            status
        )
    
    console.print(table)


def save_results(results, output_dir, format_type, image_path):
    """Save results in specified format(s)"""
    base_name = Path(image_path).stem
    timestamp = results.get('case_metadata', {}).get('timestamp', '').replace(':', '-')
    if not timestamp:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_type in ['json', 'both']:
        json_file = output_dir / f"heimdallr_results_{base_name}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        console.print(f"📄 [blue]JSON results saved: {json_file}[/blue]")
    
    if format_type in ['csv', 'both']:
        csv_file = output_dir / f"heimdallr_results_{base_name}_{timestamp}.csv"
        processor = ResultsProcessor()
        processor.save_csv(results, csv_file)
        console.print(f"📊 [blue]CSV results saved: {csv_file}[/blue]")


if __name__ == '__main__':
    main()