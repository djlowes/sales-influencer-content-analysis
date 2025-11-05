#!/usr/bin/env python3
"""
ALGORITHM 1: SUBSTANCE DETECTION
Analyzes LinkedIn posts for information density, depth, and value
"""

import json
import re
from collections import Counter
import textstat

class SubstanceDetector:
    """Detects and scores the substance/depth of LinkedIn posts"""
    
    def __init__(self):
        # Keywords that indicate substantial content
        self.value_indicators = {
            'data': ['data', 'statistics', 'study', 'research', 'survey', 'report', 'analysis'],
            'frameworks': ['framework', 'model', 'strategy', 'approach', 'method', 'process', 'system'],
            'examples': ['example', 'case study', 'instance', 'for example', 'e.g.', 'such as'],
            'actionable': ['how to', 'steps', 'tactics', 'tips', 'guide', 'implement', 'apply'],
            'metrics': ['%', 'percent', 'increase', 'decrease', 'roi', 'revenue', 'growth', '$'],
            'insights': ['learned', 'discovered', 'found', 'realized', 'insight', 'lesson'],
            'expertise': ['experience', 'years', 'worked', 'built', 'scaled', 'led', 'managed']
        }
        
        # Shallow content indicators
        self.shallow_indicators = [
            'agree?', 'thoughts?', 'what do you think',
            'drop a', 'comment below', 'tag someone',
            'follow for more', 'repost if'
        ]
        
    def analyze_post(self, text):
        """
        Analyze a single post for substance
        Returns dict with scores and details
        """
        if not text or len(text.strip()) < 50:
            return self._create_result(0, "Too short")
        
        text_lower = text.lower()
        
        # 1. Information Density Score (0-30 points)
        info_density = self._score_information_density(text, text_lower)
        
        # 2. Depth Score (0-25 points)
        depth_score = self._score_depth(text, text_lower)
        
        # 3. Value Indicators Score (0-25 points)
        value_score = self._score_value_indicators(text_lower)
        
        # 4. Structure Score (0-20 points)
        structure_score = self._score_structure(text)
        
        # Apply penalties
        penalties = self._calculate_penalties(text_lower)
        
        # Calculate total
        total_score = max(0, info_density + depth_score + value_score + structure_score - penalties)
        
        # Normalize to 0-100
        normalized_score = min(100, total_score)
        
        return {
            'total_score': round(normalized_score, 2),
            'information_density': round(info_density, 2),
            'depth_score': round(depth_score, 2),
            'value_indicators': round(value_score, 2),
            'structure_score': round(structure_score, 2),
            'penalties': round(penalties, 2),
            'classification': self._classify_substance(normalized_score)
        }
    
    def _score_information_density(self, text, text_lower):
        """Score based on information density (0-30)"""
        score = 0
        
        # Word count (longer = more potential substance)
        words = len(text.split())
        if words > 500:
            score += 10
        elif words > 300:
            score += 7
        elif words > 150:
            score += 5
        elif words > 100:
            score += 3
        
        # Sentence complexity
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if sentences:
            avg_words_per_sentence = words / len(sentences)
            if 15 <= avg_words_per_sentence <= 25:  # Sweet spot
                score += 8
            elif 10 <= avg_words_per_sentence < 15:
                score += 5
        
        # Numbers and statistics (indicates data-driven)
        numbers = re.findall(r'\b\d+[%$]?\b|\$\d+', text)
        score += min(7, len(numbers) * 1.5)
        
        # Punctuation variety (lists, structure)
        has_lists = '•' in text or re.search(r'\n\d+\.', text) or text.count('\n-') > 2
        if has_lists:
            score += 5
        
        return min(30, score)
    
    def _score_depth(self, text, text_lower):
        """Score based on depth and expertise signals (0-25)"""
        score = 0
        
        # Check for specific examples or case studies
        example_patterns = [
            r'for example', r'for instance', r'case study',
            r'i worked', r'we built', r'i led', r'i managed'
        ]
        for pattern in example_patterns:
            if re.search(pattern, text_lower):
                score += 3
                break
        
        # Personal experience signals
        experience_words = ['learned', 'discovered', 'realized', 'found out', 'experience']
        score += min(5, sum(2 for word in experience_words if word in text_lower))
        
        # Problem-solution structure
        if 'problem' in text_lower and 'solution' in text_lower:
            score += 4
        
        # Multi-step explanations
        numbered_items = len(re.findall(r'\n\d+[\.\)]\s', text))
        score += min(8, numbered_items * 1.5)
        
        # Complexity of vocabulary
        long_words = [w for w in text.split() if len(w) > 10]
        score += min(5, len(long_words) * 0.3)
        
        return min(25, score)
    
    def _score_value_indicators(self, text_lower):
        """Score based on value-adding content indicators (0-25)"""
        score = 0
        
        for category, keywords in self.value_indicators.items():
            found = sum(1 for keyword in keywords if keyword in text_lower)
            if found > 0:
                # Each category worth up to 4 points
                score += min(4, found * 1.5)
        
        return min(25, score)
    
    def _score_structure(self, text):
        """Score based on organization and formatting (0-20)"""
        score = 0
        
        # Has clear sections
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3:
            score += 5
        elif len(paragraphs) >= 2:
            score += 3
        
        # Has opening hook
        first_line = text.split('\n')[0]
        if len(first_line) < 150 and len(first_line) > 20:
            score += 3
        
        # Has conclusion/summary
        last_paragraph = paragraphs[-1] if paragraphs else ""
        conclusion_words = ['in conclusion', 'summary', 'bottom line', 'key takeaway', 'p.s.']
        if any(word in last_paragraph.lower() for word in conclusion_words):
            score += 4
        
        # Proper formatting (not wall of text)
        if text.count('\n') > 5:
            score += 3
        
        # Clear headers or sections
        if re.search(r'[A-Z\s]{10,}:', text) or text.count('—') > 2:
            score += 5
        
        return min(20, score)
    
    def _calculate_penalties(self, text_lower):
        """Calculate penalties for shallow content (0-15)"""
        penalty = 0
        
        # Engagement bait
        for indicator in self.shallow_indicators:
            if indicator in text_lower:
                penalty += 3
        
        # Excessive emojis
        emoji_count = len(re.findall(r'[🔥💪👇✨🚀💯🎯⚡️📈]', text_lower))
        if emoji_count > 10:
            penalty += 5
        elif emoji_count > 5:
            penalty += 2
        
        # Too short for claimed depth
        word_count = len(text_lower.split())
        if word_count < 100:
            penalty += 5
        
        return min(15, penalty)
    
    def _classify_substance(self, score):
        """Classify the substance level"""
        if score >= 80:
            return "Exceptional Substance"
        elif score >= 65:
            return "High Substance"
        elif score >= 50:
            return "Moderate Substance"
        elif score >= 35:
            return "Low Substance"
        else:
            return "Minimal Substance"
    
    def _create_result(self, score, reason):
        """Create a minimal result object"""
        return {
            'total_score': score,
            'information_density': 0,
            'depth_score': 0,
            'value_indicators': 0,
            'structure_score': 0,
            'penalties': 0,
            'classification': reason
        }


def analyze_all_posts(json_file_path):
    """Analyze all posts in the dataset"""
    detector = SubstanceDetector()
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    results = []
    for post in posts:
        text = post.get('text', '')
        author = post.get('author', {})
        
        analysis = detector.analyze_post(text)
        
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
    print("🔍 ALGORITHM 1: SUBSTANCE DETECTION")
    print("=" * 80)
    
    input_file = "/mnt/user-data/uploads/dataset_linkedin-batch-profile-posts-scraper_2025-11-04_02-03-34-812.json"
    
    print("\nAnalyzing substance of all posts...")
    results = analyze_all_posts(input_file)
    
    # Sort by score
    results_sorted = sorted(results, key=lambda x: x['total_score'], reverse=True)
    
    # Show top 10
    print("\n🏆 TOP 10 POSTS BY SUBSTANCE:")
    print("-" * 80)
    for i, result in enumerate(results_sorted[:10], 1):
        print(f"\n{i}. {result['author_name']} (@{result['username']})")
        print(f"   Score: {result['total_score']}/100 - {result['classification']}")
        print(f"   Words: {result['word_count']}")
        print(f"   Breakdown: Info Density={result['information_density']}, "
              f"Depth={result['depth_score']}, Value={result['value_indicators']}, "
              f"Structure={result['structure_score']}")
        print(f"   Preview: {result['text_preview']}")
    
    print("\n\n✅ Substance analysis complete!")
    print(f"📊 Analyzed {len(results)} posts")
    print(f"📈 Average substance score: {sum(r['total_score'] for r in results) / len(results):.2f}/100")
    
    # Save results
    import csv
    output_file = "/mnt/user-data/outputs/substance_scores.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['author_name', 'username', 'post_url', 'total_score', 'classification',
                     'word_count', 'information_density', 'depth_score', 'value_indicators',
                     'structure_score', 'penalties']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results_sorted:
            writer.writerow({k: v for k, v in result.items() if k in fieldnames})
    
    print(f"💾 Results saved to: {output_file}")
