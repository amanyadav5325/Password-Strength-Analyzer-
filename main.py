#!/usr/bin/env python3
"""
Password Strength Analyzer and Custom Wordlist Generator
Main entry point for both CLI and GUI interfaces
"""

import sys
import argparse
from cli_interface import CLIInterface
from gui_interface import GUIInterface


def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(
        description="Password Strength Analyzer and Custom Wordlist Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --gui                          # Launch GUI interface
  python main.py --analyze "MyPassword123"     # Analyze password strength
  python main.py --generate-wordlist           # Generate wordlist interactively
  python main.py --name "John" --dates "1990,2000" --output wordlist.txt
        """
    )
    
    # Interface selection
    interface_group = parser.add_mutually_exclusive_group()
    interface_group.add_argument('--gui', action='store_true', 
                                help='Launch GUI interface')
    interface_group.add_argument('--cli', action='store_true', 
                                help='Use CLI interface (default)')
    
    # Password analysis options
    parser.add_argument('--analyze', metavar='PASSWORD', 
                       help='Analyze password strength')
    
    # Wordlist generation options
    parser.add_argument('--generate-wordlist', action='store_true',
                       help='Generate custom wordlist')
    parser.add_argument('--name', metavar='NAME', 
                       help='Name(s) for wordlist generation (comma-separated)')
    parser.add_argument('--dates', metavar='DATES',
                       help='Dates for wordlist generation (comma-separated)')
    parser.add_argument('--pets', metavar='PETS',
                       help='Pet names for wordlist generation (comma-separated)')
    parser.add_argument('--interests', metavar='INTERESTS',
                       help='Interests/hobbies for wordlist generation (comma-separated)')
    parser.add_argument('--output', '-o', metavar='FILE',
                       help='Output file for wordlist (default: wordlist.txt)')
    parser.add_argument('--max-words', type=int, default=10000,
                       help='Maximum number of words to generate (default: 10000)')
    
    args = parser.parse_args()
    
    # Default to CLI if no interface specified
    if not args.gui:
        args.cli = True
    
    try:
        if args.gui:
            # Launch GUI interface
            gui = GUIInterface()
            gui.run()
        else:
            # Use CLI interface
            cli = CLIInterface()
            
            if args.analyze:
                cli.analyze_password(args.analyze)
            elif args.generate_wordlist or any([args.name, args.dates, args.pets, args.interests]):
                cli.generate_wordlist(
                    names=args.name.split(',') if args.name else [],
                    dates=args.dates.split(',') if args.dates else [],
                    pets=args.pets.split(',') if args.pets else [],
                    interests=args.interests.split(',') if args.interests else [],
                    output_file=args.output or 'wordlist.txt',
                    max_words=args.max_words
                )
            else:
                # Interactive CLI mode
                cli.interactive_mode()
                
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
