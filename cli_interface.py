"""
Command Line Interface for Password Analyzer and Wordlist Generator
"""

import sys
import os
from typing import List, Optional
from password_analyzer import PasswordAnalyzer
from wordlist_generator import WordlistGenerator
from utils import format_analysis_output, get_user_input, validate_file_path


class CLIInterface:
    """Command-line interface for the password analysis and wordlist generation tool"""
    
    def __init__(self):
        self.analyzer = PasswordAnalyzer()
        self.generator = WordlistGenerator()
        self.banner = """
╔══════════════════════════════════════════════════════════════╗
║           Password Strength Analyzer & Wordlist Generator    ║
║                     Security Testing Tool                    ║
╚══════════════════════════════════════════════════════════════╝
        """
    
    def interactive_mode(self):
        """Run interactive CLI mode"""
        print(self.banner)
        print("===Welcome Choose an option===")
        
        while True:
            print("\n" + "="*60)
            print("MAIN MENU")
            print("="*60)
            print("1. Analyze Password Strength")
            print("2. Generate Custom Wordlist")
            print("3. Batch Analyze Passwords from File")
            print("4. Help")
            print("5. Exit")
            
            choice = get_user_input("Enter your choice (1-5): ").strip()
            
            try:
                if choice == '1':
                    self._interactive_password_analysis()
                elif choice == '2':
                    self._interactive_wordlist_generation()
                elif choice == '3':
                    self._batch_password_analysis()
                elif choice == '4':
                    self._show_help()
                elif choice == '5':
                    print("Thank you for using Password Analyzer! Stay secure!")
                    break
                else:
                    print("Invalid choice. Please enter 1-5.")
            except KeyboardInterrupt:
                print("\n\nOperation cancelled. Returning to main menu...")
                continue
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print("Please try again.")
    
    def _interactive_password_analysis(self):
        """Interactive password analysis"""
        print("\n" + "="*60)
        print("PASSWORD STRENGTH ANALYSIS")
        print("="*60)
        
        while True:
            password = get_user_input("\nEnter password to analyze (or 'back' to return): ", hide_input=True)
            
            if password.lower() == 'back':
                break
            
            if not password:
                print("Password cannot be empty. Please try again.")
                continue
            
            self.analyze_password(password)
            
            another = get_user_input("\nAnalyze another password? (y/n): ").lower()
            if another not in ['y', 'yes']:
                break
    
    def _interactive_wordlist_generation(self):
        """Interactive wordlist generation"""
        print("\n" + "="*60)
        print("CUSTOM WORDLIST GENERATION")
        print("="*60)
        print("Provide personal information to generate a custom wordlist for security testing.")
        print("Leave fields empty if not applicable.\n")
        
        # Collect user inputs
        names_input = get_user_input("Names (comma-separated): ")
        names = [name.strip() for name in names_input.split(',') if name.strip()]
        dates_input = get_user_input("Important dates/years (comma-separated): ")
        dates = [date.strip() for date in dates_input.split(',') if date.strip()]
        
        pets_input = get_user_input("Pet names (comma-separated): ")
        pets = [pet.strip() for pet in pets_input.split(',') if pet.strip()]
        
        interests_input = get_user_input("Interests/hobbies (comma-separated): ")
        interests = [interest.strip() for interest in interests_input.split(',') if interest.strip()]
        
        # Advanced options
        print("\nAdvanced Options:")
        include_years = get_user_input("Include years in combinations? (y/n, default: y): ").lower()
        include_years = include_years != 'n'
        
        include_leet = get_user_input("Include leetspeak variations? (y/n, default: y): ").lower()
        include_leet = include_leet != 'n'
        
        include_combinations = get_user_input("Include word combinations? (y/n, default: y): ").lower()
        include_combinations = include_combinations != 'n'
        
        max_words_input = get_user_input("Maximum words to generate (default: 10000): ").strip()
        try:
            max_words = int(max_words_input) if max_words_input else 10000
        except ValueError:
            max_words = 10000
            print("Invalid number, using default: 10000")
        
        # Output file
        output_file = get_user_input("Output filename (default: wordlist.txt): ").strip()
        if not output_file:
            output_file = "wordlist.txt"
        
        # Validate inputs
        if not any([names, dates, pets, interests]):
            print("Error: At least one type of information must be provided.")
            return
        
        # Generate wordlist
        self.generate_wordlist(
            names=names,
            dates=dates,
            pets=pets,
            interests=interests,
            include_years=include_years,
            include_leet=include_leet,
            include_combinations=include_combinations,
            max_words=max_words,
            output_file=output_file
        )
    
    def _batch_password_analysis(self):
        """Analyze passwords from a file"""
        print("\n" + "="*60)
        print("BATCH PASSWORD ANALYSIS")
        print("="*60)
        
        input_file = get_user_input("Enter path to password file: ").strip()
        
        if not validate_file_path(input_file):
            print(f"Error: File '{input_file}' not found or not accessible.")
            return
        
        output_file = get_user_input("Output file for results (optional): ").strip()
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                passwords = [line.strip() for line in f if line.strip()]
            
            if not passwords:
                print("No passwords found in the file.")
                return
            
            print(f"\nAnalyzing {len(passwords)} passwords...")
            
            results = []
            for i, password in enumerate(passwords, 1):
                analysis = self.analyzer.analyze_password(password)
                results.append((password, analysis))
                
                # Show progress for large files
                if len(passwords) > 10 and i % max(1, len(passwords) // 10) == 0:
                    print(f"Progress: {i}/{len(passwords)} ({i*100//len(passwords)}%)")
            
            # Display summary
            self._display_batch_results(results, output_file)
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
    
    def _display_batch_results(self, results: List[tuple], output_file: Optional[str]):
        """Display batch analysis results"""
        if not results:
            return
        
        # Calculate statistics
        scores = [analysis['strength_score'] for _, analysis in results]
        avg_score = sum(scores) / len(scores)
        
        strength_counts = {}
        for _, analysis in results:
            level = analysis['strength_level']
            strength_counts[level] = strength_counts.get(level, 0) + 1
        
        # Display summary
        print(f"\n" + "="*60)
        print("BATCH ANALYSIS RESULTS")
        print("="*60)
        print(f"Total passwords analyzed: {len(results)}")
        print(f"Average strength score: {avg_score:.1f}/100")
        print(f"\nStrength distribution:")
        for level, count in sorted(strength_counts.items()):
            percentage = (count / len(results)) * 100
            print(f"  {level}: {count} ({percentage:.1f}%)")
        
        # Show weakest passwords
        weak_passwords = [(pwd, analysis) for pwd, analysis in results 
                         if analysis['strength_score'] < 40]
        
        if weak_passwords:
            print(f"\nWeakest passwords ({len(weak_passwords)} found):")
            for i, (pwd, analysis) in enumerate(weak_passwords[:10], 1):
                print(f"  {i}. '{pwd}' - {analysis['strength_level']} ({analysis['strength_score']}/100)")
            if len(weak_passwords) > 10:
                print(f"  ... and {len(weak_passwords) - 10} more")
        
        # Save detailed results if requested
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("Password Analysis Results\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for password, analysis in results:
                        f.write(f"Password: {password}\n")
                        f.write(f"Strength: {analysis['strength_level']} ({analysis['strength_score']}/100)\n")
                        f.write(f"Entropy: {analysis['entropy']} bits\n")
                        f.write(f"Time to crack: {analysis['time_to_crack']}\n")
                        
                        if analysis['patterns_found']:
                            f.write(f"Patterns: {', '.join(analysis['patterns_found'])}\n")
                        
                        f.write(f"Recommendations: {'; '.join(analysis['recommendations'])}\n")
                        f.write("-" * 50 + "\n")
                
                print(f"\nDetailed results saved to: {output_file}")
                
            except Exception as e:
                print(f"Error saving results: {str(e)}")
    
    def _show_help(self):
        """Display help information"""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                             HELP                             ║
╚══════════════════════════════════════════════════════════════╝

OVERVIEW:
This tool provides two main functions:
1. Password Strength Analysis - Evaluate password security
2. Custom Wordlist Generation - Create wordlists for security testing

PASSWORD ANALYSIS:
• Analyzes password entropy and patterns
• Detects common weaknesses (keyboard patterns, leetspeak, etc.)
• Provides time-to-crack estimates
• Offers specific improvement recommendations

WORDLIST GENERATION:
• Creates custom wordlists based on personal information
• Includes variations: leetspeak, numbers, years, combinations
• Useful for penetration testing and security assessments
• Exports to standard .txt format

SECURITY NOTES:
• Passwords entered are not stored or transmitted
• Generated wordlists are for authorized security testing only
• Use only on systems you own or have permission to test

COMMAND LINE USAGE:
python main.py --analyze "password"           # Analyze single password
python main.py --gui                          # Launch GUI interface
python main.py --name "John" --output list.txt # Generate wordlist

For more examples, run: python main.py --help
        """
        print(help_text)
        
        input("\nPress Enter to continue...")
    
    def analyze_password(self, password: str):
        """Analyze a single password and display results"""
        if not password:
            print("Error: Password cannot be empty.")
            return
        
        print(f"\nAnalyzing password...")
        analysis = self.analyzer.analyze_password(password)
        format_analysis_output(analysis)
    
    def generate_wordlist(self, names: List[str] = None, dates: List[str] = None,
                         pets: List[str] = None, interests: List[str] = None,
                         include_years: bool = True, include_leet: bool = True,
                         include_combinations: bool = True, max_words: int = 10000,
                         output_file: str = "wordlist.txt"):
        """Generate and export custom wordlist"""
        
        print(f"\nGenerating wordlist...")
        
        # Show what we're working with
        inputs_summary = []
        if names:
            inputs_summary.append(f"Names: {', '.join(names)}")
        if dates:
            inputs_summary.append(f"Dates: {', '.join(dates)}")
        if pets:
            inputs_summary.append(f"Pets: {', '.join(pets)}")
        if interests:
            inputs_summary.append(f"Interests: {', '.join(interests)}")
        
        if inputs_summary:
            print("Input data:")
            for summary in inputs_summary:
                print(f"  • {summary}")
        
        print(f"Options: Years={include_years}, Leet={include_leet}, Combinations={include_combinations}")
        print(f"Max words: {max_words}")
        
        # Generate wordlist
        wordlist = self.generator.generate_wordlist(
            names=names or [],
            dates=dates or [],
            pets=pets or [],
            interests=interests or [],
            include_years=include_years,
            include_leet=include_leet,
            include_combinations=include_combinations,
            max_words=max_words
        )
        
        if not wordlist:
            print("Error: No words generated. Please check your input data.")
            return
        
        # Display statistics
        stats = self.generator.get_wordlist_stats(wordlist)
        print(f"\nWordlist Statistics:")
        print(f"  Total words: {stats['total_words']}")
        print(f"  Average length: {stats['avg_length']}")
        print(f"  Length range: {stats['min_length']}-{stats['max_length']}")
        print(f"  Unique words: {stats['unique_words']}")
        
        # Show sample words
        print(f"\nSample words (first 10):")
        for i, word in enumerate(wordlist[:10], 1):
            print(f"  {i:2d}. {word}")
        
        if len(wordlist) > 10:
            print(f"  ... and {len(wordlist) - 10} more")
        
        # Export to file
        if self.generator.export_wordlist(wordlist, output_file):
            print(f"\n✓ Wordlist exported to: {output_file}")
            print(f"  File size: {os.path.getsize(output_file)} bytes")
        else:
            print(f"\n✗ Failed to export wordlist to: {output_file}")


# Example usage
if __name__ == "__main__":
    cli = CLIInterface()
    cli.interactive_mode()
