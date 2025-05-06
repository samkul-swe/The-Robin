"""
Text analysis utilities for fake job detection
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter

# Download NLTK resources if needed
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('punkt')

class TextAnalyzer:
    """Analyze text for suspicious patterns"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Suspicious patterns
        self.urgency_phrases = [
            'apply now', 'urgent hiring', 'immediate start',
            'limited positions', 'act fast', 'don\'t miss this',
            'once in a lifetime', 'apply today', 'hurry',
            'last chance', 'time is running out'
        ]
        
        self.unrealistic_promises = [
            'unlimited income', 'unlimited earning', 'financial freedom',
            'be your own boss', 'work from home millionaire', 'get rich',
            'earn thousands', 'easy money', 'quick money', 'fast cash',
            'passive income', 'earn while you sleep', 'effortless income'
        ]
        
        self.vague_job_indicators = [
            'flexible position', 'various duties', 'multiple roles',
            'different tasks', 'etc', 'and more', 'as needed',
            'whatever is needed', 'and so on', 'general duties'
        ]
        
        self.excessive_punctuation_re = re.compile(r'[!?.]{2,}')
    
    def analyze_text(self, text):
        """
        Analyze text for suspicious patterns
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Tokenize and lemmatize
        tokens = word_tokenize(text_lower)
        lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        
        # Count word frequencies
        word_freq = Counter(lemmatized)
        
        # Calculate analysis metrics
        results = {
            'urgency_score': self._calculate_pattern_score(text_lower, self.urgency_phrases),
            'promise_score': self._calculate_pattern_score(text_lower, self.unrealistic_promises),
            'vagueness_score': self._calculate_pattern_score(text_lower, self.vague_job_indicators),
            'excessive_punctuation': bool(self.excessive_punctuation_re.search(text)),
            'repeated_words': self._find_repeated_words(word_freq),
            'word_count': len(tokens),
            'unique_word_count': len(word_freq),
            'lexical_diversity': len(word_freq) / len(tokens) if tokens else 0,
            'avg_word_length': sum(len(word) for word in tokens) / len(tokens) if tokens else 0
        }
        
        # Calculate an overall suspicion score
        results['suspicious_score'] = (
            results['urgency_score'] * 2 +
            results['promise_score'] * 3 +
            results['vagueness_score'] * 1.5 +
            (1 if results['excessive_punctuation'] else 0) * 1 +
            min(len(results['repeated_words']), 5) * 0.5 +
            max(0, (5 - results['lexical_diversity']) * 0.5 if results['lexical_diversity'] > 0 else 2.5)
        )
        
        return results
    
    def _calculate_pattern_score(self, text, patterns):
        """Calculate score based on occurrence of suspicious patterns"""
        score = 0
        for pattern in patterns:
            if pattern in text:
                score += 1
        return score
    
    def _find_repeated_words(self, word_freq, threshold=5):
        """Find words that are repeated frequently"""
        repeated = []
        
        for word, count in word_freq.items():
            if len(word) > 3 and count >= threshold:  # Only consider meaningful words
                repeated.append((word, count))
        
        # Sort by frequency (descending)
        repeated.sort(key=lambda x: x[1], reverse=True)
        
        return repeated[:10]  # Return top 10 repeated words