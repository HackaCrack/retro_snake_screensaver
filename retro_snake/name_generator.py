"""
Name generator module for Retro Snake Screensaver
Combines syllable-based generation with Markov chains from real names
"""

import random
import re
from collections import defaultdict


# Corpus of real names to learn syllable patterns from
# Easy to edit - just add more names here!
# Focus on medium-length names (5-8 letters) for better syllable patterns
NAME_CORPUS = [
    "Alexander", "Benjamin", "Christopher", "Daniel", "Edward", "Franklin",
    "Gabriel", "Harrison", "Isaac", "Jackson", "Katherine", "Lucas",
    "Madison", "Nathaniel", "Olivia", "Patrick", "Quinn", "Rachel",
    "Samuel", "Thomas", "Victoria", "William", "Xavier", "Yasmine",
    "Zachary", "Amelia", "Blake", "Catherine", "David", "Elizabeth",
    "Felix", "Grace", "Henry", "Isabella", "James", "Katherine",
    "Liam", "Mia", "Noah", "Olivia", "Penelope", "Quinn",
    "Ryan", "Sophia", "Tyler", "Uma", "Vincent", "Willow",
    "Xander", "Yara", "Zoe", "Aiden", "Bella", "Caleb",
    "Diana", "Ethan", "Fiona", "George", "Hannah", "Ian",
    "Julia", "Kevin", "Luna", "Mason", "Nora", "Owen",
    "Piper", "Quincy", "Ruby", "Sebastian", "Tessa", "Ulysses",
    "Violet", "Wyatt", "Xara", "Yuki", "Zara", "Aria",
    "Brody", "Chloe", "Derek", "Emma", "Finn", "Gwen",
    "Hugo", "Iris", "Jake", "Kira", "Leo", "Maya",
    "Nate", "Oscar", "Paige", "Quinn", "Rex", "Sage",
    "Tara", "Uri", "Vera", "Wade", "Xena", "Yara",
    "Zane", "Ava", "Ben", "Cora", "Dean", "Eva",
    "Fox", "Gia", "Hank", "Ivy", "Jax", "Kai",
    "Lane", "Max", "Nyx", "Ora", "Pax", "Rue",
    "Sky", "Tia", "Uma", "Vex", "Wren", "Xia",
    "Yin", "Zoe", "Aaron", "Brianna", "Cameron", "Dakota",
    "Elena", "Forrest", "Giselle", "Harper", "Ivan", "Jasmine",
    "Kendall", "Lillian", "Marcus", "Natalie", "Orion", "Phoebe",
    "Quentin", "Raven", "Sierra", "Tristan", "Ursula", "Vivian",
    "Winston", "Ximena", "Yvette", "Zander", "Adrian", "Brooke",
    "Carter", "Delilah", "Emmett", "Freya", "Gideon", "Hazel",
    "Iris", "Jasper", "Kiera", "Landon", "Morgan", "Nolan"
]

# Awkward consonant clusters to avoid
BAD_CLUSTERS = [
    "xq", "qx", "zx", "xz", "qk", "kq", "jq", "qj",
    "xw", "wx", "zw", "wz", "qg", "gq", "jz", "zj"
]

# Patterns that are hard to pronounce
BAD_PATTERNS = [
    r'[bcdfghjklmnpqrstvwxyz]{4,}',  # 4+ consecutive consonants
    r'[aeiouy]{4,}',  # 4+ consecutive vowels
]


def extract_syllables(name):
    """
    Extract syllables from a name using improved vowel-based splitting.
    Handles names starting with vowels and consonant clusters better.
    Returns a list of syllables.
    """
    # Convert to lowercase for consistency
    name = name.lower()
    syllables = []
    
    # Handle names starting with vowels
    if name and name[0] in 'aeiouy':
        # Find the first consonant group
        match = re.search(r'[bcdfghjklmnpqrstvwxyz]+', name)
        if match:
            # First syllable is the vowel(s) + first consonant(s)
            vowel_part = name[:match.start()]
            consonant_part = match.group()
            syllables.append(vowel_part + consonant_part)
            name = name[match.end():]
        else:
            # All vowels, treat as single syllable
            return [name] if name else []
    
    # Now process the rest: consonant-vowel patterns
    # This regex finds consonant groups followed by vowel groups
    pattern = r'[bcdfghjklmnpqrstvwxyz]+[aeiouy]+'
    matches = re.finditer(pattern, name)
    
    for match in matches:
        syllables.append(match.group())
        # Remove processed part
        name = name[match.end():]
    
    # Handle trailing consonants (attach to last syllable if reasonable)
    if name and syllables:
        # If trailing part is short (1-2 chars), attach to last syllable
        if len(name) <= 2:
            syllables[-1] += name
        elif len(name) <= 3 and name[0] in 'aeiouy':
            # Trailing vowel + consonant(s) - make new syllable
            syllables.append(name)
        # Otherwise, trailing consonants are too long, skip them
    
    # Fallback: if no syllables found, try simpler vowel-based split
    if not syllables:
        # Split by vowels, keeping vowels with preceding consonants
        parts = re.split(r'([aeiouy]+)', name)
        syllables = []
        i = 0
        while i < len(parts):
            if parts[i] and parts[i][0] in 'bcdfghjklmnpqrstvwxyz':
                # Consonant part
                if i + 1 < len(parts) and parts[i + 1]:
                    # Combine with next vowel part
                    syllables.append(parts[i] + parts[i + 1])
                    i += 2
                else:
                    # Trailing consonants - attach to previous if exists
                    if syllables:
                        syllables[-1] += parts[i]
                    i += 1
            elif parts[i] and parts[i][0] in 'aeiouy':
                # Vowel-only part at start
                if i + 1 < len(parts) and parts[i + 1]:
                    syllables.append(parts[i] + parts[i + 1])
                    i += 2
                else:
                    syllables.append(parts[i])
                    i += 1
            else:
                i += 1
    
    # Final fallback: split into reasonable chunks
    if not syllables:
        # Split into 2-3 char chunks, but try to keep vowel-consonant together
        i = 0
        while i < len(name):
            chunk_size = 2
            # Prefer 3 if it makes sense (has vowel)
            if i + 3 <= len(name) and any(c in 'aeiouy' for c in name[i:i+3]):
                chunk_size = 3
            syllables.append(name[i:i+chunk_size])
            i += chunk_size
    
    return [s for s in syllables if s and len(s) >= 1]  # Remove empty strings, keep at least 1 char


def build_markov_chain(corpus, order=1):
    """
    Build a Markov chain from the name corpus.
    order=1 means we look at transitions between adjacent syllables.
    Returns a dict: {syllable: [list of possible next syllables]}
    """
    chain = defaultdict(list)
    
    for name in corpus:
        syllables = extract_syllables(name)
        if len(syllables) < 2:
            continue
        
        # Add transitions
        for i in range(len(syllables) - order):
            current = tuple(syllables[i:i+order])
            next_syllable = syllables[i + order]
            chain[current].append(next_syllable)
        
        # Add start markers (empty tuple means start)
        chain[()].append(syllables[0])
    
    return chain


def is_pronounceable(name):
    """
    Check if a name is pronounceable by validating against bad patterns.
    Returns True if the name seems pronounceable.
    """
    name_lower = name.lower()
    
    # Check for bad consonant clusters
    for cluster in BAD_CLUSTERS:
        if cluster in name_lower:
            return False
    
    # Check for bad patterns (too many consecutive consonants/vowels)
    for pattern in BAD_PATTERNS:
        if re.search(pattern, name_lower):
            return False
    
    # Must have at least one vowel
    if not re.search(r'[aeiouy]', name_lower):
        return False
    
    # Must have at least one consonant
    if not re.search(r'[bcdfghjklmnpqrstvwxyz]', name_lower):
        return False
    
    return True


class NameGenerator:
    """Generates realistic-sounding names using Markov chains and syllables"""
    
    def __init__(self, corpus=None, min_length=4, max_length=12):
        """
        Initialize the name generator.
        
        Args:
            corpus: List of names to learn from (defaults to NAME_CORPUS)
            min_length: Minimum name length in characters
            max_length: Maximum name length in characters
        """
        self.corpus = corpus or NAME_CORPUS
        self.min_length = min_length
        self.max_length = max_length
        self.chain = build_markov_chain(self.corpus)
        self.generated_names = set()  # Track generated names to avoid duplicates
    
    def generate(self, max_attempts=100):
        """
        Generate a single name.
        
        Args:
            max_attempts: Maximum attempts to generate a valid name
            
        Returns:
            A generated name string, or None if generation fails
        """
        for _ in range(max_attempts):
            name = self._generate_one()
            if name and self.min_length <= len(name) <= self.max_length:
                # Validate pronounceability
                if is_pronounceable(name) and name not in self.generated_names:
                    self.generated_names.add(name)
                    return name.capitalize()
        
        # Fallback: generate a simple name if Markov fails
        return self._generate_fallback()
    
    def _generate_one(self):
        """Generate one name using the Markov chain"""
        if not self.chain:
            return None
        
        # Start with a random starting syllable
        if () not in self.chain or not self.chain[()]:
            return None
        
        syllables = [random.choice(self.chain[()])]
        
        # Follow the chain - ensure at least 2 syllables for better names
        max_syllables = (self.max_length // 2) + 3  # Rough estimate, allow a bit more
        min_syllables = 2  # Minimum syllables for better names
        
        for _ in range(max_syllables):
            current = (syllables[-1],)
            if current not in self.chain or not self.chain[current]:
                break
            
            next_syllable = random.choice(self.chain[current])
            syllables.append(next_syllable)
            
            # Check if we've reached a good length
            current_name = ''.join(syllables)
            
            # Must have at least min_syllables before considering stopping
            if len(syllables) >= min_syllables:
                if len(current_name) >= self.min_length:
                    # Stop if we're in the valid range and random chance
                    # Higher chance to stop as we get closer to max_length
                    if len(current_name) <= self.max_length:
                        # Progressive stopping probability based on length
                        stop_chance = 0.3
                        if len(current_name) >= self.max_length - 2:
                            stop_chance = 0.7  # More likely to stop near max
                        elif len(current_name) >= self.min_length + 2:
                            stop_chance = 0.4  # Moderate chance in middle range
                        
                        if random.random() < stop_chance:
                            break
                    else:
                        # Over max length, need to trim or start over
                        # Try to use what we have if it's close
                        if len(current_name) <= self.max_length + 2:
                            # Use current syllables but might be slightly over
                            break
        
        name = ''.join(syllables)
        
        # Final validation: must meet minimum requirements
        if name and len(syllables) >= min_syllables:
            return name
        return None
    
    def _generate_fallback(self):
        """Fallback generator using simple syllable combinations"""
        # Well-tested syllable combinations that sound natural
        prefixes = ["al", "ka", "ze", "mi", "to", "ri", "sa", "na", "el", "jo", 
                   "be", "ca", "da", "fi", "ga", "ha", "li", "ma", "ne", "pa"]
        suffixes = ["ron", "lex", "ton", "ara", "vin", "den", "mar", "lan", "ris", "bel",
                   "ian", "ael", "iel", "ora", "ina", "ena", "ira", "ara", "ela", "ina"]
        middles = ["ex", "an", "in", "on", "er", "ar", "or", "en", "al", "el",
                  "am", "em", "im", "om", "um", "ad", "ed", "id", "od", "ud"]
        
        # Try different combinations
        for _ in range(50):  # More attempts for better results
            parts = [random.choice(prefixes)]
            
            # Sometimes add a middle syllable (based on target length)
            target_length = (self.min_length + self.max_length) // 2
            if len(parts[0]) + len(random.choice(suffixes)) < target_length:
                if random.random() < 0.6:  # More likely to add middle for longer names
                    parts.append(random.choice(middles))
            
            parts.append(random.choice(suffixes))
            name = ''.join(parts)
            
            # Validate pronounceability and length
            if (self.min_length <= len(name) <= self.max_length and 
                is_pronounceable(name) and 
                name not in self.generated_names):
                self.generated_names.add(name)
                return name.capitalize()
        
        # Last resort: simple 2-syllable combination
        for _ in range(20):
            name = random.choice(prefixes) + random.choice(suffixes)
            if (self.min_length <= len(name) <= self.max_length and 
                is_pronounceable(name) and 
                name not in self.generated_names):
                self.generated_names.add(name)
                return name.capitalize()
        
        # Ultimate fallback
        return "Snake"
    
    def reset_cache(self):
        """Clear the cache of generated names (useful for testing)"""
        self.generated_names.clear()


# Global generator instance for easy use
_generator = None


def get_generator():
    """Get or create the global name generator instance"""
    global _generator
    if _generator is None:
        _generator = NameGenerator()
    return _generator


def generate_name(min_length=4, max_length=12):
    """
    Convenience function to generate a single name.
    
    Args:
        min_length: Minimum name length (default: 4)
        max_length: Maximum name length (default: 12)
        
    Returns:
        A generated name string
    """
    gen = get_generator()
    gen.min_length = min_length
    gen.max_length = max_length
    return gen.generate()

