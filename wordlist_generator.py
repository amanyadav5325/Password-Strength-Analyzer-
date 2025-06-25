"""
Custom Wordlist Generator
Generates wordlists for security testing based on user inputs
"""

import re
import itertools
from typing import List, Set, Dict, Any
from datetime import datetime, timedelta


class WordlistGenerator:
    """Generates custom wordlists based on personal information and common patterns"""
    
    def __init__(self):
        # Common number suffixes
        self.common_numbers = ['1', '12', '123', '1234', '01', '001', '2024', '2025']
        
        # Current and recent years
        current_year = datetime.now().year
        self.years = [str(year) for year in range(current_year - 50, current_year + 5)]
        
        # Common prefixes and suffixes
        self.prefixes = ['', 'my', 'the', 'i', 'love']
        self.suffixes = ['', '!', '!!', '123', '12', '1', '01', '001', '@', '#']
        
        # Leetspeak substitutions
        self.leet_substitutions = {
            'a': ['@', '4'],
            'e': ['3'],
            'i': ['1', '!'],
            'o': ['0'],
            's': ['5', '$'],
            't': ['7'],
            'l': ['1'],
            'g': ['9'],
            'b': ['6']
        }
        
        # Common separators
        self.separators = ['', '_', '-', '.', '!', '@', '#']
        
        # Season and month variations
        self.seasons = ['spring', 'summer', 'autumn', 'fall', 'winter']
        self.months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                      'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
                      'january', 'february', 'march', 'april', 'may', 'june',
                      'july', 'august', 'september', 'october', 'november', 'december']
    
    def generate_wordlist(self, **kwargs) -> List[str]:
        """
        Generate custom wordlist based on provided information
        
        Args:
            names: List of names
            dates: List of dates
            pets: List of pet names
            interests: List of interests/hobbies
            include_years: Include common years (default: True)
            include_leet: Include leetspeak variations (default: True)
            include_combinations: Include word combinations (default: True)
            max_words: Maximum number of words to generate
            
        Returns:
            List of generated words
        """
        names = kwargs.get('names', [])
        dates = kwargs.get('dates', [])
        pets = kwargs.get('pets', [])
        interests = kwargs.get('interests', [])
        include_years = kwargs.get('include_years', True)
        include_leet = kwargs.get('include_leet', True)
        include_combinations = kwargs.get('include_combinations', True)
        max_words = kwargs.get('max_words', 10000)
        
        wordlist = set()
        
        # Base words from user input
        base_words = []
        base_words.extend([name.strip() for name in names if name.strip()])
        base_words.extend([pet.strip() for pet in pets if pet.strip()])
        base_words.extend([interest.strip() for interest in interests if interest.strip()])
        
        # Process dates
        date_words = self._process_dates(dates)
        base_words.extend(date_words)
        
        # Generate variations for each base word
        for word in base_words:
            if not word:
                continue
                
            # Add original word and variations
            wordlist.update(self._generate_word_variations(word, include_leet, include_years))
        
        # Add common combinations if requested
        if include_combinations and base_words:
            combinations = self._generate_combinations(base_words[:5], include_leet, include_years)
            wordlist.update(combinations)
        
        # Convert to sorted list and limit size
        final_wordlist = sorted(list(wordlist))
        
        if max_words and len(final_wordlist) > max_words:
            # Prioritize shorter, more common variations
            final_wordlist = self._prioritize_words(final_wordlist, max_words)
        
        return final_wordlist
    
    def _process_dates(self, dates: List[str]) -> List[str]:
        """Process and extract date-related words"""
        date_words = []
        
        for date_str in dates:
            if not date_str.strip():
                continue
                
            # Try to parse various date formats
            date_formats = [
                r'(\d{4})',  # Year
                r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
                r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
                r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
                r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # MM.DD.YYYY
            ]
            
            for pattern in date_formats:
                matches = re.findall(pattern, date_str.strip())
                for match in matches:
                    if isinstance(match, tuple):
                        date_words.extend(match)
                    else:
                        date_words.append(match)
        
        return [word for word in date_words if word.isdigit()]
    
    def _generate_word_variations(self, word: str, include_leet: bool, include_years: bool) -> Set[str]:
        """Generate variations of a single word"""
        variations = set()
        
        # Clean the word
        clean_word = re.sub(r'[^\w]', '', word.lower())
        if not clean_word:
            return variations
        
        # Base word variations
        variations.add(clean_word)
        variations.add(clean_word.capitalize())
        variations.add(clean_word.upper())
        
        # Add prefixes and suffixes
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                if prefix or suffix:  # Don't add empty prefix+suffix (already have base word)
                    variations.add(f"{prefix}{clean_word}{suffix}")
                    variations.add(f"{prefix}{clean_word.capitalize()}{suffix}")
        
        # Add numbers
        for num in self.common_numbers:
            variations.add(f"{clean_word}{num}")
            variations.add(f"{clean_word.capitalize()}{num}")
            variations.add(f"{num}{clean_word}")
        
        # Add years if requested
        if include_years:
            for year in self.years:
                variations.add(f"{clean_word}{year}")
                variations.add(f"{clean_word.capitalize()}{year}")
        
        # Add leetspeak variations if requested
        if include_leet:
            leet_variations = self._generate_leet_variations(clean_word)
            variations.update(leet_variations)
        
        # Remove empty strings and very short words
        return {v for v in variations if len(v) >= 3}
    
    def _generate_leet_variations(self, word: str) -> Set[str]:
        """Generate leetspeak variations of a word"""
        variations = set()
        
        # Generate all possible leetspeak combinations
        leet_chars = []
        for char in word.lower():
            if char in self.leet_substitutions:
                # Include original character and all substitutions
                leet_chars.append([char] + self.leet_substitutions[char])
            else:
                leet_chars.append([char])
        
        # Generate combinations (limit to reasonable number)
        if len(leet_chars) <= 6:  # Prevent explosion of combinations
            for combination in itertools.product(*leet_chars):
                leet_word = ''.join(combination)
                if leet_word != word.lower():  # Don't include original
                    variations.add(leet_word)
                    variations.add(leet_word.capitalize())
        else:
            # For longer words, just do simple substitutions
            for char, subs in self.leet_substitutions.items():
                for sub in subs:
                    leet_word = word.lower().replace(char, sub)
                    if leet_word != word.lower():
                        variations.add(leet_word)
                        variations.add(leet_word.capitalize())
        
        return variations
    
    def _generate_combinations(self, words: List[str], include_leet: bool, include_years: bool) -> Set[str]:
        """Generate combinations of multiple words"""
        combinations = set()
        
        if len(words) < 2:
            return combinations
        
        # Generate 2-word combinations
        for i, word1 in enumerate(words):
            for j, word2 in enumerate(words):
                if i != j:
                    clean_word1 = re.sub(r'[^\w]', '', word1.lower())
                    clean_word2 = re.sub(r'[^\w]', '', word2.lower())
                    
                    if not clean_word1 or not clean_word2:
                        continue
                    
                    # Different separator combinations
                    for sep in self.separators:
                        combo = f"{clean_word1}{sep}{clean_word2}"
                        combinations.add(combo)
                        combinations.add(combo.capitalize())
                        
                        # Add with numbers
                        for num in self.common_numbers[:3]:  # Limit for combinations
                            combinations.add(f"{combo}{num}")
                        
                        # Add with years
                        if include_years:
                            for year in self.years[:5]:  # Limit for combinations
                                combinations.add(f"{combo}{year}")
        
        # Limit combination size to prevent explosion
        return set(list(combinations)[:1000])
    
    def _prioritize_words(self, wordlist: List[str], max_words: int) -> List[str]:
        """Prioritize words based on likelihood and common patterns"""
        
        def word_score(word):
            score = 0
            
            # Prefer shorter words (more likely to be used)
            score += max(0, 20 - len(word))
            
            # Prefer words with numbers at the end
            if re.search(r'\d+$', word):
                score += 10
            
            # Prefer capitalized words
            if word[0].isupper() and word[1:].islower():
                score += 5
            
            # Prefer words with common years
            for year in self.years[:10]:
                if year in word:
                    score += 15
                    break
            
            # Prefer words with simple leetspeak
            leet_count = sum(1 for char in word if char in '@31057!')
            score += min(leet_count * 3, 10)
            
            return score
        
        # Sort by score (descending) and return top words
        scored_words = [(word, word_score(word)) for word in wordlist]
        scored_words.sort(key=lambda x: x[1], reverse=True)
        
        return [word for word, score in scored_words[:max_words]]
    
    def export_wordlist(self, wordlist: List[str], filename: str) -> bool:
        """
        Export wordlist to file
        
        Args:
            wordlist: List of words to export
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for word in wordlist:
                    f.write(f"{word}\n")
            return True
        except Exception as e:
            print(f"Error exporting wordlist: {str(e)}")
            return False
    
    def get_wordlist_stats(self, wordlist: List[str]) -> Dict[str, Any]:
        """Get statistics about the generated wordlist"""
        if not wordlist:
            return {
                'total_words': 0,
                'avg_length': 0,
                'min_length': 0,
                'max_length': 0,
                'unique_words': 0
            }
        
        lengths = [len(word) for word in wordlist]
        
        return {
            'total_words': len(wordlist),
            'avg_length': round(sum(lengths) / len(lengths), 2),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'unique_words': len(set(wordlist)),
            'charset_distribution': self._analyze_charset_distribution(wordlist)
        }
    
    def _analyze_charset_distribution(self, wordlist: List[str]) -> Dict[str, int]:
        """Analyze character set distribution in wordlist"""
        distribution = {
            'lowercase_only': 0,
            'uppercase_only': 0,
            'mixed_case': 0,
            'with_numbers': 0,
            'with_symbols': 0
        }
        
        for word in wordlist:
            has_lower = any(c.islower() for c in word)
            has_upper = any(c.isupper() for c in word)
            has_digit = any(c.isdigit() for c in word)
            has_symbol = any(not c.isalnum() for c in word)
            
            if has_lower and not has_upper:
                distribution['lowercase_only'] += 1
            elif has_upper and not has_lower:
                distribution['uppercase_only'] += 1
            elif has_lower and has_upper:
                distribution['mixed_case'] += 1
            
            if has_digit:
                distribution['with_numbers'] += 1
            if has_symbol:
                distribution['with_symbols'] += 1
        
        return distribution


# Example usage and testing
if __name__ == "__main__":
    generator = WordlistGenerator()
    
    # Test wordlist generation
    wordlist = generator.generate_wordlist(
        names=['John', 'Smith'],
        dates=['1990', '12/15/1990'],
        pets=['Buddy', 'Max'],
        interests=['football', 'music'],
        max_words=100
    )
    
    print(f"Generated {len(wordlist)} words:")
    for i, word in enumerate(wordlist[:20]):  # Show first 20
        print(f"{i+1:2d}. {word}")
    
    if len(wordlist) > 20:
        print(f"... and {len(wordlist) - 20} more words")
    
    # Show stats
    stats = generator.get_wordlist_stats(wordlist)
    print(f"\nWordlist Statistics:")
    print(f"Total words: {stats['total_words']}")
    print(f"Average length: {stats['avg_length']}")
    print(f"Length range: {stats['min_length']}-{stats['max_length']}")
