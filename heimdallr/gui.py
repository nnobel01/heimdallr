# heimdallr/gui.py

import sys
from pathlib import Path
from gooey import Gooey, GooeyParser

# Import the core logic and output functions from your CLI
from heimdallr.cli import execute_search, display_results_summary, save_results

@Gooey(
    program_name="Heimdallr Facial Recognition",
    program_description="An advanced facial recognition search tool for law enforcement.",
    default_size=(800, 600),
    progress_regex=r"^progress: (\d+)", # Regex to parse progress for the progress bar
    progress_expr="x", # Use the value of 'x' from the regex for the progress bar
    timing_options={'show_time_remaining': True},
    richtext_controls=True,
    requires_shell=False
)
def main():
    """
    This function wraps the original application logic with a Gooey GUI.
    """
    parser = GooeyParser(description="Heimdallr Search Parameters")

    # --- Define GUI fields ---
    parser.add_argument(
        "image_path",
        metavar="Image Path",
        help="Path to the input image file.",
        widget="FileChooser"
    )

    parser.add_argument(
        '--output', '-o',
        metavar="Output Directory",
        default='results',
        help='Output directory for results.',
        widget="DirChooser"
    )
    
    parser.add_argument(
        '--format', '-f',
        metavar="Output Format",
        choices=['json', 'csv', 'both'],
        default='both',
        help='Output format for the results.'
    )

    parser.add_argument(
        '--threshold', '-t',
        metavar="Similarity Threshold",
        default=80.0,
        help='Similarity threshold percentage (e.g., 80.0)',
        widget="DecimalSlider",
        gooey_options={'min': 50, 'max': 100}
    )

    parser.add_argument(
        '--platforms', '-p',
        metavar="Platforms",
        default='all',
        help='Platforms to search (all, social, web, or comma-separated list like "instagram,reddit")'
    )
    
    parser.add_argument(
        '--aggressive', '-a',
        metavar="Aggressive Mode",
        action='store_true',
        help='Enable aggressive search mode (faster, but higher risk of detection).'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        metavar="Verbose Logging",
        action='store_true',
        help='Enable verbose logging to see detailed steps in the console.'
    )

    args = parser.parse_args()

    # --- GUI-specific progress callback ---
    # This will print progress updates in a format that Gooey's progress bar understands.
    tasks = ["face_detection", "search_engine", "platform_search", "results_processing"]
    task_progress = {task: 0 for task in tasks}
    
    def gui_progress_callback(task_name: str, description: str, completed: float):
        if task_name in task_progress:
            task_progress[task_name] = completed
        
        # Calculate overall progress as an average of all tasks
        overall_progress = sum(task_progress.values()) / len(tasks)
        
        # Print the description and the progress value for Gooey to parse
        print(description)
        print(f"progress: {int(overall_progress)}")
        sys.stdout.flush()


    # --- Execute the search logic ---
    try:
        print("Starting Heimdallr search...")
        
        final_results = execute_search(
            image_path=args.image_path,
            output_dir_str=args.output,
            format_type=args.format,
            threshold=args.threshold,
            platforms=args.platforms,
            aggressive=args.aggressive,
            config_path=None,  # Config path can be added as a field if needed
            verbose=args.verbose,
            progress_callback=gui_progress_callback
        )
        
        # Display summary and save results (output will appear in the Gooey console)
        print("\n--- Search Summary ---")
        display_results_summary(final_results)
        save_results(final_results, Path(args.output), args.format, args.image_path)

        print(f"\nSearch complete! Results saved to '{args.output}'")

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        # In case of an error, set progress to -1 to turn the bar red in Gooey
        print("progress: -1")
        sys.exit(1)

    print("progress: 100") # Ensure progress bar completes

if __name__ == '__main__':
    main()