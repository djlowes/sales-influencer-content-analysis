#!/usr/bin/env python3
"""
ALGORITHM 3: UNIQUENESS DETECTION
Identifies originality, personal stories, and differentiation from generic content
"""

import json
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class UniquenessDetector:
    """Detects uniqueness and originality in LinkedIn posts"""
    
    def __init__(self):
        # Common generic phrases/templates
        self.generic_phrases = [
            'i was scrolling through linkedin',
            'can we talk about',
            'let me tell you',
            'here\'s the thing',
            'hot take',
            'unpopular opinion',
            'change my mind',
            'this is your sign',
            'normalize',
            'it\'s time to',
            'stop doing',
            'start doing'
        ]
        
        # Personal story indicators
        self.personal_indicators = [
            'my story', 'i remember', 'years ago', 'when i was',
            'i learned', 'i discovered', 'i failed', 'i succeeded',
            'my first', 'my experience', 'i worked at', 'at my company'
        ]
        
        # Original thought indicators
        self.originality_indicators = [
            'i believe', 'in my view', 'i\'ve found', 'i\'ve noticed',
            'my approach', 'i developed', 'i created', 'i built'
        ]
        
        self.all_posts_text = []
        self.tfidf_matrix = None
        self.vectorizer = None
    
    def prepare_corpus(self, posts):
        """Prepare the corpus for similarity analysis"""
        self.all_posts_text = [post.get('text', '') for post in posts]
        
        # Create TF-IDF matrix
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        try:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.all_posts_text)
        except:
            self.tfidf_matrix = None
    
    def analyze_post(self, text, post_index=None):
        """
        Analyze a single post for uniqueness
        Returns dict with scores and details
        """
        if not text or len(text.strip()) < 30:
            return self._create_result(0, "Too short")
        
        text_lower = text.lower()
        
        # 1. Personal Story Score (0-25 points)
        personal_score = self._score_personal_story(text, text_lower)
        
        # 2. Original Thinking Score (0-25 points)
        originality_score = self._score_originality(text, text_lower)
        
        # 3. Specific Details Score (0-25 points)
        specificity_score = self._score_specificity(text, text_lower)
        
        # 4. Content Similarity Score (0-25 points)
        # Higher uniqueness = lower similarity to other posts
        similarity_score = self._score_similarity(post_index) if post_index is not None else 12.5
        
        # Apply penalties
        penalties = self._calculate_penalties(text_lower)
        
        # Calculate total
        total_score = max(0, personal_score + originality_score + specificity_score + similarity_score - penalties)
        
        # Normalize to 0-100
        normalized_score = min(100, total_score)
        
        return {
            'total_score': round(normalized_score, 2),
            'personal_story': round(personal_score, 2),
            'original_thinking': round(originality_score, 2),
            'specificity': round(specificity_score, 2),
            'uniqueness_vs_corpus': round(similarity_score, 2),
            'penalties': round(penalties, 2),
            'classification': self._classify_uniqueness(normalized_score)
        }
    
    def _score_personal_story(self, text, text_lower):
        """Score based on personal story elements (0-25)"""
        score = 0
        
        # Personal pronouns (I, my, me) - indicates personal perspective
        personal_pronouns = len(re.findall(r'\b(i|my|me|i\'m|i\'ve|i\'ll)\b', text_lower))
        score += min(6, personal_pronouns * 0.3)
        
        # Personal story indicators
        personal_count = sum(1 for phrase in self.personal_indicators if phrase in text_lower)
        score += min(8, personal_count * 2.5)
        
        # Specific time references (dates, years, timeframes)
        time_refs = len(re.findall(r'\b(20\d{2}|years? ago|months? ago|last \w+|in \d{4})\b', text_lower))
        score += min(5, time_refs * 2)
        
        # Named entities (people, companies, places - without actually using NER)
        # Heuristic: capitalized words that aren't at sentence starts
        sentences = text.split('. ')
        potential_entities = []
        for sent in sentences[1:]:  # Skip first sentence
            caps_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sent)
            potential_entities.extend(caps_words)
        score += min(6, len(set(potential_entities)) * 0.8)
        
        return min(25, score)
    
    def _score_originality(self, text, text_lower):
        """Score based on original thinking indicators (0-25)"""
        score = 0
        
        # Original thought indicators
        orig_count = sum(1 for phrase in self.originality_indicators if phrase in text_lower)
        score += min(8, orig_count * 2.5)
        
        # Contrarian or thought-provoking statements
        contrarian_markers = [
            'contrary to', 'unlike most', 'different from', 'instead of',
            'rather than', 'not what you think', 'surprisingly'
        ]
        contrarian_count = sum(1 for marker in contrarian_markers if marker in text_lower)
        score += min(6, contrarian_count * 3)
        
        # Question-posing (stimulates thinking)
        questions = text.count('?')
        score += min(5, questions * 1.5)
        
        # Novel combinations (using unusual word pairs)
        # This is a simplified heuristic
        words = text_lower.split()
        rare_words = [w for w in words if len(w) > 12]  # Long words often more specific
        score += min(6, len(rare_words) * 0.8)
        
        return min(25, score)
    
    def _score_specificity(self, text, text_lower):
        """Score based on specific details vs. generic statements (0-25)"""
        score = 0
        
        # Numbers and statistics (specific data)
        numbers = re.findall(r'\b\d+[%$]?\b|\$\d+', text)
        score += min(8, len(numbers) * 1.5)
        
        # Company/product names (indicates real examples)
        # Heuristic: words with internal caps or all caps (but not ALL CAPS YELLING)
        branded_terms = re.findall(r'\b[A-Z][a-z]+[A-Z]\w*\b', text)
        score += min(5, len(set(branded_terms)) * 2)
        
        # Specific action verbs (not generic ones)
        specific_actions = [
            'implemented', 'designed', 'architected', 'optimized',
            'analyzed', 'developed', 'launched', 'scaled', 'built'
        ]
        action_count = sum(1 for action in specific_actions if action in text_lower)
        score += min(6, action_count * 2)
        
        # Technical terms or jargon (indicates domain expertise)
        # Length of words as proxy for specificity
        word_lengths = [len(w) for w in text_lower.split()]
        avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
        if avg_word_length > 5.5:
            score += 6
        elif avg_word_length > 5.0:
            score += 4
        
        return min(25, score)
    
    def _score_similarity(self, post_index):
        """Score based on how different this post is from others (0-25)"""
        if self.tfidf_matrix is None or post_index is None:
            return 12.5  # Average score if we can't calculate
        
        try:
            # Get similarity to all other posts
            post_vector = self.tfidf_matrix[post_index]
            similarities = cosine_similarity(post_vector, self.tfidf_matrix).flatten()
            
            # Remove self-similarity
            similarities = np.delete(similarities, post_index)
            
            # Calculate average similarity to other posts
            avg_similarity = np.mean(similarities)
            
            # Convert to uniqueness score (inverse of similarity)
            # Lower similarity = higher uniqueness
            if avg_similarity < 0.1:
                score = 25  # Very unique
            elif avg_similarity < 0.2:
                score = 20
            elif avg_similarity < 0.3:
                score = 15
            elif avg_similarity < 0.4:
                score = 10
            else:
                score = 5
            
            return score
        except:
            return 12.5
    
    def _calculate_penalties(self, text_lower):
        """Calculate penalties for generic/templated content (0-15)"""
        penalty = 0
        
        # Generic phrase templates
        generic_count = sum(1 for phrase in self.generic_phrases if phrase in text_lower)
        penalty += generic_count * 3
        
        # Overused buzzwords
        buzzwords = [
            'game changer', 'game-changer', 'paradigm shift', 'disrupt',
            'synergy', 'leverage', 'circle back', 'low hanging fruit',
            'move the needle', 'think outside the box'
        ]
        buzzword_count = sum(1 for buzz in buzzwords if buzz in text_lower)
        penalty += buzzword_count * 2
        
        # Generic motivational quotes without attribution
        if '"' in text_lower and 'said' not in text_lower and len(text_lower) < 200:
            penalty += 3
        
        # Copy-paste indicators
        if 'credit:' in text_lower or 'source:' in text_lower or 'via:' in text_lower:
            penalty += 4
        
        return min(15, penalty)
    
    def _classify_uniqueness(self, score):
        """Classify the uniqueness level"""
        if score >= 80:
            return "Highly Unique"
        elif score >= 65:
            return "Very Unique"
        elif score >= 50:
            return "Moderately Unique"
        elif score >= 35:
            return "Somewhat Generic"
        else:
            return "Very Generic"
    
    def _create_result(self, score, reason):
        """Create a minimal result object"""
        return {
            'total_score': score,
            'personal_story': 0,
            'original_thinking': 0,
            'specificity': 0,
            'uniqueness_vs_corpus': 0,
            'penalties': 0,
            'classification': reason
        }


def analyze_all_posts(json_file_path):
    """Analyze all posts in the dataset"""
    detector = UniquenessDetector()
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    # Prepare corpus for similarity analysis
    print("   Preparing corpus for similarity analysis...")
    detector.prepare_corpus(posts)
    
    results = []
    for i, post in enumerate(posts):
        text = post.get('text', '')
        author = post.get('author', {})
        
        analysis = detector.analyze_post(text, post_index=i)
        
        results.append({
            'author_name': f"{author.get('first_name', '')} {author.get('last_name', '')}".strip(),
            'username': author.get('username', ''),
            'post_url': post.get('url', ''),
            'text_preview': text[:100] + '...' if len(text) > 100 else text,
            'word_count': len(text.split()),
            **analysis
        })
    
    return results


if __name__ == "__main__":
    print("🦄 ALGORITHM 3: UNIQUENESS DETECTION")
    print("=" * 80)
    
    input_file = "/mnt/user-data/uploads/dataset_linkedin-batch-profile-posts-scraper_2025-11-04_02-03-34-812.json"
    
    print("\nDetecting uniqueness across all posts...")
    results = analyze_all_posts(input_file)
    
    # Sort by score
    results_sorted = sorted(results, key=lambda x: x['total_score'], reverse=True)
    
    # Show top 10
    print("\n🏆 TOP 10 MOST UNIQUE POSTS:")
    print("-" * 80)
    for i, result in enumerate(results_sorted[:10], 1):
        print(f"\n{i}. {result['author_name']} (@{result['username']})")
        print(f"   Score: {result['total_score']}/100 - {result['classification']}")
        print(f"   Breakdown: Personal={result['personal_story']}, "
              f"Original={result['original_thinking']}, Specific={result['specificity']}, "
              f"Unique vs Corpus={result['uniqueness_vs_corpus']}")
        print(f"   Preview: {result['text_preview']}")
    
    print("\n\n✅ Uniqueness detection complete!")
    print(f"📊 Analyzed {len(results)} posts")
    print(f"📈 Average uniqueness score: {sum(r['total_score'] for r in results) / len(results):.2f}/100")
    
    # Save results
    import csv
    output_file = "/mnt/user-data/outputs/uniqueness_scores.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['author_name', 'username', 'post_url', 'total_score', 'classification',
                     'word_count', 'personal_story', 'original_thinking', 'specificity',
                     'uniqueness_vs_corpus', 'penalties']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results_sorted:
            writer.writerow({k: v for k, v in result.items() if k in fieldnames})
    
    print(f"💾 Results saved to: {output_file}")