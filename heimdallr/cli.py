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

from .core.face_detector import FaceDetector
from .core.search_engine import SearchEngine
from .core.results_processor import ResultsProcessor
from .utils.config import Config
from .utils.logger import setup_logger

console = Console()
logger = setup_logger()

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
    
    # Validate input
    if not os.path.exists(image_path):
        console.print(f"❌ [red]Error: Image file '{image_path}' not found[/red]")
        sys.exit(1)
    
    # Setup configuration
    config_obj = Config(config_path=config if config else None)
    if verbose:
        config_obj.set_verbose(True)
    
    # Create output directory
    output_dir = Path(output)
    output_dir.mkdir(exist_ok=True)
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            # Phase 1: Face Detection
            task1 = progress.add_task("[cyan]🔍 Detecting faces in image...", total=100)
            face_detector = FaceDetector(threshold=threshold/100)
            faces_data = face_detector.process_image(image_path)
            progress.update(task1, advance=100)
            
            if not faces_data['faces_found']:
                console.print("❌ [red]No faces detected in the input image[/red]")
                sys.exit(1)
            
            console.print(f"✅ [green]Found {faces_data['face_count']} face(s) in image[/green]")
            
            # Phase 2: Search Engine Setup
            task2 = progress.add_task("[cyan]🚀 Initializing search engines...", total=100)
            search_engine = SearchEngine(
                config=config_obj,
                aggressive_mode=aggressive,
                platforms=platforms
            )
            progress.update(task2, advance=100)
            
            # Phase 3: Multi-platform Search
            task3 = progress.add_task("[cyan]🌐 Searching across platforms...", total=100)
            search_results = search_engine.search_all_platforms(
                faces_data, 
                progress_callback=lambda p: progress.update(task3, completed=p)
            )
            progress.update(task3, advance=100)
            
            # Phase 4: Results Processing
            task4 = progress.add_task("[cyan]📊 Processing and ranking results...", total=100)
            processor = ResultsProcessor(threshold=threshold)
            final_results = processor.process_results(search_results, faces_data)
            progress.update(task4, advance=100)
        
        # Display results summary
        display_results_summary(final_results)
        
        # Save results
        save_results(final_results, output_dir, format, image_path)
        
        console.print(f"\n✅ [green]Search completed! Results saved to '{output_dir}'[/green]")
        
    except KeyboardInterrupt:
        console.print("\n⚠️ [yellow]Search interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ [red]Error during search: {str(e)}[/red]")
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
        # Simple CSV creation for now
        import csv
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Platform', 'Similarity_Score', 'URL', 'Context'])
            
            # Extract matches from all confidence levels
            all_matches = (
                results.get('high_confidence_matches', []) +
                results.get('medium_confidence_matches', []) +
                results.get('low_confidence_matches', [])
            )
            
            for match in all_matches:
                writer.writerow([
                    match.get('platform', ''),
                    match.get('similarity_score', ''),
                    match.get('url', ''),
                    match.get('context', '')
                ])
        
        console.print(f"📊 [blue]CSV results saved: {csv_file}[/blue]")

if __name__ == '__main__':
    main()
