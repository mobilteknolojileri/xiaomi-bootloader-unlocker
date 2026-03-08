"""
Xiaomi Bootloader Unlock Tool
Automated bootloader unlock application with NTP time sync and millisecond precision.
"""

import argparse
import sys

__version__ = "1.0.0"
__author__ = "mobilteknolojileri"


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Xiaomi Bootloader Unlock Tool - Automated unlock application with NTP time sync',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py                  # Interactive mode (prompts for delay)
  python main.py --delay 888      # Use 888ms delay
  python main.py -d 500           # Use 500ms delay
        '''
    )
    parser.add_argument(
        '-d', '--delay',
        type=float,
        default=None,
        metavar='MS',
        help='Delay in milliseconds before midnight (default: 888)'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the application."""
    args = parse_arguments()
    
    from logger import setup_logging
    log_path = setup_logging()
    print(f"📝 Log dosyası: {log_path}\n")

    from auth import authenticate_user
    from config import get_feed_time_configuration, DEFAULT_FEED_TIME_MS
    from bootloader import run_bootloader_unlock

    token = authenticate_user()
    
    if args.delay is not None:
        feed_time_shift = args.delay
        print(f"[Config] Using delay: {feed_time_shift} ms\n")
    else:
        feed_time_shift = get_feed_time_configuration()
    
    run_bootloader_unlock(token, feed_time_shift)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exit] Operation cancelled by user.")
        sys.exit(0)

