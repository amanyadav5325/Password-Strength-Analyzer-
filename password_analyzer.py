"""
Password Strength Analyzer
Implements custom entropy calculations and pattern detection
"""

import re
import math
from typing import Dict, List, Tuple, Any


class PasswordAnalyzer:
    """Analyzes password strength using entropy calculations and pattern detection"""
    
    def __init__(self):
        # Common password patterns
        self.common_patterns = [
            r'\d{4}',  # 4 consecutive digits (years)
            r'123+',   # Sequential numbers
            r'abc+',   # Sequential letters
            r'qwerty', # Keyboard patterns
            r'password', # Common words
            r'admin',
            r'root',
            r'user',
        ]
        
        # Character sets for entropy calculation
        self.charset_sizes = {
            'lowercase': 26,
            'uppercase': 26,
            'digits': 10,
            'symbols': 32,  # Common symbols
            'space': 1
        }
        
        # Common weak passwords and patterns
        self.weak_passwords = {
            'password', '123456', 'password123', 'admin', 'qwerty',
            'letmein', 'welcome', 'monkey', 'dragon', 'master',
            'hello', 'login', 'pass', 'shadow', 'jordan'
        }
    
    def analyze_password(self, password: str) -> Dict[str, Any]:
        """
        Comprehensive password analysis
        
        Args:
            password: Password to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        if not password:
            return {
                'strength_score': 0,
                'strength_level': 'Very Weak',
                'entropy': 0,
                'length': 0,
                'character_sets': [],
                'patterns_found': [],
                'recommendations': ['Password cannot be empty'],
                'time_to_crack': 'Instant'
            }
        
        # Basic metrics
        length = len(password)
        character_sets = self._identify_character_sets(password)
        entropy = self._calculate_entropy(password, character_sets)
        patterns = self._detect_patterns(password)
        
        # Calculate strength score (0-100)
        strength_score = self._calculate_strength_score(
            length, character_sets, entropy, patterns, password
        )
        
        # Determine strength level
        strength_level = self._get_strength_level(strength_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            length, character_sets, patterns, password
        )
        
        # Estimate time to crack
        time_to_crack = self._estimate_crack_time(entropy)
        
        return {
            'strength_score': strength_score,
            'strength_level': strength_level,
            'entropy': round(entropy, 2),
            'length': length,
            'character_sets': character_sets,
            'patterns_found': patterns,
            'recommendations': recommendations,
            'time_to_crack': time_to_crack
        }
    
    def _identify_character_sets(self, password: str) -> List[str]:
        """Identify which character sets are used in the password"""
        sets_used = []
        
        if re.search(r'[a-z]', password):
            sets_used.append('lowercase')
        if re.search(r'[A-Z]', password):
            sets_used.append('uppercase')
        if re.search(r'[0-9]', password):
            sets_used.append('digits')
        if re.search(r'[^a-zA-Z0-9\s]', password):
            sets_used.append('symbols')
        if ' ' in password:
            sets_used.append('space')
            
        return sets_used
    
    def _calculate_entropy(self, password: str, character_sets: List[str]) -> float:
        """
        Calculate password entropy using Shannon entropy formula
        
        Args:
            password: Password to analyze
            character_sets: List of character sets used
            
        Returns:
            Entropy value in bits
        """
        if not password or not character_sets:
            return 0.0
        
        # Calculate charset size
        charset_size = sum(self.charset_sizes[cs] for cs in character_sets)
        
        # Basic entropy calculation: log2(charset_size^length)
        basic_entropy = len(password) * math.log2(charset_size)
        
        # Adjust for character frequency (Shannon entropy)
        char_counts = {}
        for char in password:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        shannon_entropy = 0
        for count in char_counts.values():
            probability = count / len(password)
            shannon_entropy -= probability * math.log2(probability)
        
        # Combine both metrics (weighted average)
        combined_entropy = (basic_entropy * 0.7) + (shannon_entropy * len(password) * 0.3)
        
        return combined_entropy
    
    def _detect_patterns(self, password: str) -> List[str]:
        """Detect common weak patterns in password"""
        patterns_found = []
        password_lower = password.lower()
        
        # Check for common patterns
        for pattern in self.common_patterns:
            if re.search(pattern, password_lower):
                patterns_found.append(f"Contains pattern: {pattern}")
        
        # Check for repetitive characters
        if re.search(r'(.)\1{2,}', password):
            patterns_found.append("Repetitive characters")
        
        # Check for keyboard patterns
        keyboard_rows = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
        for row in keyboard_rows:
            for i in range(len(row) - 2):
                if row[i:i+3] in password_lower:
                    patterns_found.append("Keyboard pattern detected")
                    break
        
        # Check for common substitutions (leetspeak)
        leet_patterns = {'@': 'a', '3': 'e', '1': 'i', '0': 'o', '5': 's', '7': 't'}
        leet_count = sum(1 for char in password if char in leet_patterns)
        if leet_count > 0:
            patterns_found.append("Leetspeak substitutions detected")
        
        # Check for dates
        if re.search(r'(19|20)\d{2}', password):
            patterns_found.append("Contains year")
        
        # Check for common weak passwords
        if password_lower in self.weak_passwords:
            patterns_found.append("Common weak password")
        
        return patterns_found
    
    def _calculate_strength_score(self, length: int, character_sets: List[str], 
                                entropy: float, patterns: List[str], password: str) -> int:
        """Calculate overall strength score (0-100)"""
        score = 0
        
        # Length scoring (40 points max)
        if length >= 12:
            score += 40
        elif length >= 8:
            score += 30
        elif length >= 6:
            score += 20
        else:
            score += length * 2
        
        # Character set diversity (30 points max)
        charset_score = len(character_sets) * 7.5
        score += min(charset_score, 30)
        
        # Entropy bonus (20 points max)
        if entropy >= 60:
            score += 20
        elif entropy >= 40:
            score += 15
        elif entropy >= 25:
            score += 10
        else:
            score += entropy / 4
        
        # Pattern penalties
        pattern_penalty = len(patterns) * 5
        score -= pattern_penalty
        
        # Special penalties for very weak passwords
        if password.lower() in self.weak_passwords:
            score -= 30
        
        # Ensure score is within bounds
        return max(0, min(100, int(score)))
    
    def _get_strength_level(self, score: int) -> str:
        """Convert numeric score to descriptive strength level"""
        if score >= 80:
            return "Very Strong"
        elif score >= 60:
            return "Strong"
        elif score >= 40:
            return "Moderate"
        elif score >= 20:
            return "Weak"
        else:
            return "Very Weak"
    
    def _generate_recommendations(self, length: int, character_sets: List[str], 
                                patterns: List[str], password: str) -> List[str]:
        """Generate specific recommendations for password improvement"""
        recommendations = []
        
        if length < 8:
            recommendations.append("Use at least 8 characters (12+ recommended)")
        elif length < 12:
            recommendations.append("Consider using 12+ characters for better security")
        
        if 'uppercase' not in character_sets:
            recommendations.append("Add uppercase letters")
        if 'lowercase' not in character_sets:
            recommendations.append("Add lowercase letters")
        if 'digits' not in character_sets:
            recommendations.append("Add numbers")
        if 'symbols' not in character_sets:
            recommendations.append("Add special characters (!@#$%^&*)")
        
        if patterns:
            recommendations.append("Avoid predictable patterns")
            if any("keyboard" in p.lower() for p in patterns):
                recommendations.append("Avoid keyboard patterns (qwerty, asdf, etc.)")
            if any("repetitive" in p.lower() for p in patterns):
                recommendations.append("Avoid repetitive characters")
            if any("year" in p.lower() for p in patterns):
                recommendations.append("Avoid using years or dates")
        
        if password.lower() in self.weak_passwords:
            recommendations.append("Avoid common passwords")
        
        if not recommendations:
            recommendations.append("Your password is strong! Consider using a password manager.")
        
        return recommendations
    
    def _estimate_crack_time(self, entropy: float) -> str:
        """Estimate time to crack password based on entropy"""
        if entropy <= 0:
            return "Instant"
        
        # Assume 10^9 guesses per second (modern hardware)
        guesses_per_second = 1e9
        total_combinations = 2 ** entropy
        seconds_to_crack = total_combinations / (2 * guesses_per_second)  # Average case
        
        if seconds_to_crack < 1:
            return "Instant"
        elif seconds_to_crack < 60:
            return f"{int(seconds_to_crack)} seconds"
        elif seconds_to_crack < 3600:
            return f"{int(seconds_to_crack / 60)} minutes"
        elif seconds_to_crack < 86400:
            return f"{int(seconds_to_crack / 3600)} hours"
        elif seconds_to_crack < 31536000:
            return f"{int(seconds_to_crack / 86400)} days"
        elif seconds_to_crack < 31536000000:
            return f"{int(seconds_to_crack / 31536000)} years"
        else:
            return "Centuries"


# Example usage and testing
if __name__ == "__main__":
    analyzer = PasswordAnalyzer()
    
    test_passwords = [
        "password",
        "Password123",
        "MyStr0ng!P@ssw0rd",
        "correcthorsebatterystaple",
        "12345",
        "Tr0ub4dor&3"
    ]
    
    for pwd in test_passwords:
        result = analyzer.analyze_password(pwd)
        print(f"\nPassword: {pwd}")
        print(f"Strength: {result['strength_level']} ({result['strength_score']}/100)")
        print(f"Entropy: {result['entropy']} bits")
        print(f"Time to crack: {result['time_to_crack']}")
        if result['patterns_found']:
            print(f"Patterns: {', '.join(result['patterns_found'])}")
        print(f"Recommendations: {'; '.join(result['recommendations'])}")
