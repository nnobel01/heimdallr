# heimdallr/gui.py

from gooey import Gooey, GooeyParser
from heimdallr.cli import main as heimdallr_cli

@Gooey(
    program_name="Heimdallr Facial Recognition",
    program_description="An advanced facial recognition search tool for law enforcement.",
    default_size=(800, 600),
    progress_regex=r"^progress: (\d+)%$", # Regex to parse progress for the progress bar
    timing_options={'show_time_remaining': True}
)
def main():
    """
    This function wraps the original Click CLI command with the Gooey decorator
    to generate a GUI.
    """
    # Gooey works by parsing argparse, so we create a small bridge.
    # The Click command will be run with the arguments parsed by Gooey.
    # Note: This is a simplified bridge. Gooey has better native support for argparse.
    # For a quick GUI, we can map the options manually.
    
    parser = GooeyParser(description="Heimdallr Search Parameters")

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
        help='Platforms to search (e.g., all, social, or "instagram,reddit")'
    )
    
    parser.add_argument(
        '--aggressive', '-a',
        metavar="Aggressive Mode",
        action='store_true',
        help='Enable aggressive search mode (faster, but higher risk of detection).'
    )

    # We are not running the parser here, as Gooey handles it.
    # The decorator is enough to build the GUI. For a more robust integration,
    # you would refactor the main CLI logic to be callable with these args.
    
    # Since the original main is a click command, we can't call it directly.
    # The most direct way to build a GUI without refactoring the original `cli.py`
    # would be to reconstruct the command and run it as a subprocess.
    
    print("This is a placeholder for the GUI wrapper.")
    print("To fully integrate Gooey, the main logic in `heimdallr/cli.py` would need to be refactored")
    print("out of the Click command function into a separate callable function.")


if __name__ == '__main__':
    # This will launch the GUI window.
    main()