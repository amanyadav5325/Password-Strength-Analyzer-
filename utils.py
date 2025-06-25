"""
Utility functions for the Password Analyzer and Wordlist Generator
"""

import os
import sys
import getpass
from typing import Any, Dict


def format_analysis_output(analysis: Dict[str, Any]) -> str:
    """
    Format and display password analysis results in a readable format
    
    Args:
        analysis: Dictionary containing analysis results
    """
    print("\n" + "="*60)
    print("PASSWORD ANALYSIS RESULTS")
    print("="*60)
    
    # Basic metrics
    print(f"Password Length: {analysis['length']} characters")
    print(f"Character Sets: {', '.join(analysis['character_sets']) if analysis['character_sets'] else 'None'}")
    print(f"Entropy: {analysis['entropy']} bits")
    print(f"Time to Crack: {analysis['time_to_crack']}")
    
    # Strength assessment with color coding if supported
    strength_level = analysis['strength_level']
    score = analysis['strength_score']
    strength_color = get_strength_color_code(score)
    
    print(f"\n{strength_color}Strength: {strength_level} ({score}/100){get_reset_color()}")
    
    # Display strength bar
    display_strength_bar(score)
    
    # Security issues
    if analysis['patterns_found']:
        print(f"\n⚠️  SECURITY ISSUES DETECTED:")
        for i, pattern in enumerate(analysis['patterns_found'], 1):
            print(f"   {i}. {pattern}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    for i, recommendation in enumerate(analysis['recommendations'], 1):
        print(f"   {i}. {recommendation}")
    
    print("="*60)


def display_strength_bar(score: int, width: int = 40) -> None:
    """
    Display a visual strength bar
    
    Args:
        score: Strength score (0-100)
        width: Width of the bar in characters
    """
    filled = int((score / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    
    # Color coding
    color = get_strength_color_code(score)
    reset = get_reset_color()
    
    print(f"\nStrength Bar: {color}[{bar}] {score}%{reset}")


def get_strength_color_code(score: int) -> str:
    """
    Get ANSI color code based on strength score
    
    Args:
        score: Strength score (0-100)
        
    Returns:
        ANSI color code string
    """
    if not supports_color():
        return ""
    
    if score >= 80:
        return "\033[92m"  # Green
    elif score >= 60:
        return "\033[94m"  # Blue
    elif score >= 40:
        return "\033[93m"  # Yellow
    else:
        return "\033[91m"  # Red


def get_reset_color() -> str:
    """Get ANSI reset color code"""
    return "\033[0m" if supports_color() else ""


def supports_color() -> bool:
    """
    Check if the terminal supports ANSI color codes
    
    Returns:
        True if colors are supported, False otherwise
    """
    # Check if we're in a terminal that supports colors
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    
    # Check for common environment variables
    term = os.environ.get('TERM', '').lower()
    if 'color' in term or 'ansi' in term or term in ['xterm', 'xterm-256color', 'screen']:
        return True
    
    # Windows command prompt usually doesn't support colors
    if os.name == 'nt':
        return False
    
    return True


def get_user_input(prompt: str, hide_input: bool = False) -> str:
    """
    Get user input with optional password hiding
    
    Args:
        prompt: Input prompt text
        hide_input: Whether to hide input (for passwords)
        
    Returns:
        User input string
    """
    try:
        if hide_input:
            return getpass.getpass(prompt)
        else:
            return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled by user.")
        sys.exit(0)


def validate_file_path(file_path: str) -> bool:
    """
    Validate that a file path exists and is accessible
    
    Args:
        file_path: Path to validate
        
    Returns:
        True if file exists and is readable, False otherwise
    """
    try:
        return os.path.isfile(file_path) and os.access(file_path, os.R_OK)
    except (OSError, IOError):
        return False


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    size = size_bytes
    unit_index = 0
    
    while size >= 1024 and unit_index < len(size_names) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {size_names[unit_index]}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = "wordlist"
    
    return filename


def create_backup_filename(original_path: str) -> str:
    """
    Create a backup filename if the original exists
    
    Args:
        original_path: Original file path
        
    Returns:
        Backup filename that doesn't exist
    """
    if not os.path.exists(original_path):
        return original_path
    
    base, ext = os.path.splitext(original_path)
    counter = 1
    
    while True:
        backup_path = f"{base}_{counter}{ext}"
        if not os.path.exists(backup_path):
            return backup_path
        counter += 1


def print_banner(title: str, width: int = 60) -> None:
    """
    Print a formatted banner
    
    Args:
        title: Banner title
        width: Banner width
    """
    border = "=" * width
    padding = (width - len(title) - 2) // 2
    centered_title = f"{'=' * padding} {title} {'=' * padding}"
    
    # Adjust for odd widths
    if len(centered_title) < width:
        centered_title += "="
    
    print(f"\n{border}")
    print(centered_title)
    print(f"{border}\n")


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user for confirmation
    
    Args:
        message: Confirmation message
        default: Default response if user just presses enter
        
    Returns:
        True if confirmed, False otherwise
    """
    default_text = "[Y/n]" if default else "[y/N]"
    response = get_user_input(f"{message} {default_text}: ").lower().strip()
    
    if not response:
        return default
    
    return response in ['y', 'yes', 'true', '1']


def calculate_entropy_simple(text: str) -> float:
    """
    Calculate simple Shannon entropy of text
    
    Args:
        text: Input text
        
    Returns:
        Entropy value
    """
    if not text:
        return 0.0
    
    # Count character frequencies
    char_counts = {}
    for char in text:
        char_counts[char] = char_counts.get(char, 0) + 1
    
    # Calculate entropy
    import math
    entropy = 0.0
    text_length = len(text)
    
    for count in char_counts.values():
        probability = count / text_length
        entropy -= probability * math.log2(probability)
    
    return entropy


def format_time_duration(seconds: float) -> str:
    """
    Format time duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return "Less than 1 second"
    elif seconds < 60:
        return f"{int(seconds)} second{'s' if seconds != 1 else ''}"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''}"
    elif seconds < 31536000:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''}"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years != 1 else ''}"


def is_common_password(password: str) -> bool:
    """
    Check if password is in common password list
    
    Args:
        password: Password to check
        
    Returns:
        True if it's a common password, False otherwise
    """
    common_passwords = {
        'password', '123456', '123456789', 'qwerty', 'abc123',
        'password123', 'admin', 'letmein', 'welcome', 'monkey',
        'dragon', 'master', 'hello', 'login', 'pass', 'shadow',
        '12345', '1234', '12345678', 'football', 'baseball',
        'trustno1', 'superman', 'batman', 'jordan', 'harley'
    }
    
    return password.lower() in common_passwords


# Test utility functions
if __name__ == "__main__":
    # Test color support
    print(f"Color support: {supports_color()}")
    
    # Test strength display
    test_analysis = {
        'strength_level': 'Strong',
        'strength_score': 75,
        'entropy': 45.2,
        'length': 12,
        'character_sets': ['lowercase', 'uppercase', 'digits', 'symbols'],
        'patterns_found': ['Contains year'],
        'recommendations': ['Consider using a longer password'],
        'time_to_crack': '2 years'
    }
    
    format_analysis_output(test_analysis)
    
    # Test file size formatting
    print(f"\nFile size tests:")
    print(f"1024 bytes: {format_file_size(1024)}")
    print(f"1048576 bytes: {format_file_size(1048576)}")
    print(f"1073741824 bytes: {format_file_size(1073741824)}")
    
    # Test entropy calculation
    print(f"\nEntropy test: {calculate_entropy_simple('password123'):.2f}")
