#!/usr/bin/env python3
"""
ALGORITHM 2: QUALITY ASSESSMENT
Evaluates writing quality, readability, structure, and professionalism
"""

import json
import re
import textstat
from collections import Counter

class QualityAssessor:
    """Assesses the quality of LinkedIn posts"""
    
    def __init__(self):
        # Clickbait patterns
        self.clickbait_patterns = [
            r'you won\'t believe',
            r'shocking',
            r'this one trick',
            r'what happened next',
            r'blown away',
            r'mind[\s-]?blown',
            r'game[\s-]?changer',
            r'the secret to',
            r'everyone is talking about'
        ]
        
        # Professional vocabulary
        self.professional_words = [
            'strategy', 'implement', 'framework', 'optimize', 'leverage',
            'scalable', 'metrics', 'efficiency', 'revenue', 'growth',
            'innovation', 'transformation', 'execution', 'alignment'
        ]
        
        # Spam/low-quality indicators
        self.spam_indicators = [
            'dm me', 'link in bio', 'click here', 'limited time',
            'act now', 'buy now', 'cheap', 'make money fast'
        ]
    
    def analyze_post(self, text):
        """
        Analyze a post for quality
        Returns dict with scores and details
        """
        if not text or len(text.strip()) < 30:
            return self._create_result(0, "Too short")
        
        text_lower = text.lower()
        
        # 1. Readability Score (0-25 points)
        readability = self._score_readability(text)
        
        # 2. Structure Score (0-25 points)
        structure = self._score_structure(text)
        
        # 3. Professionalism Score (0-25 points)
        professionalism = self._score_professionalism(text, text_lower)
        
        # 4. Grammar & Clarity Score (0-25 points)
        grammar = self._score_grammar_clarity(text)
        
        # Apply penalties
        penalties = self._calculate_penalties(text, text_lower)
        
        # Calculate total
        total_score = max(0, readability + structure + professionalism + grammar - penalties)
        
        # Normalize to 0-100
        normalized_score = min(100, total_score)
        
        return {
            'total_score': round(normalized_score, 2),
            'readability': round(readability, 2),
            'structure': round(structure, 2),
            'professionalism': round(professionalism, 2),
            'grammar_clarity': round(grammar, 2),
            'penalties': round(penalties, 2),
            'classification': self._classify_quality(normalized_score),
            'readability_grade': self._get_readability_grade(text)
        }
    
    def _score_readability(self, text):
        """Score based on readability (0-25)"""
        score = 0
        
        try:
            # Flesch Reading Ease (higher = easier to read)
            flesch = textstat.flesch_reading_ease(text)
            
            # Optimal range for professional content: 50-70
            if 50 <= flesch <= 70:
                score += 10
            elif 40 <= flesch < 50 or 70 < flesch <= 80:
                score += 7
            elif flesch > 30:
                score += 4
            
            # Flesch-Kincaid Grade Level (lower = easier)
            grade_level = textstat.flesch_kincaid_grade(text)
            
            # Ideal grade level: 8-12 (accessible but sophisticated)
            if 8 <= grade_level <= 12:
                score += 10
            elif 6 <= grade_level < 8 or 12 < grade_level <= 14:
                score += 7
            elif grade_level < 16:
                score += 4
            
            # Sentence length variation (good writing has variety)
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            if len(sentences) > 1:
                sentence_lengths = [len(s.split()) for s in sentences]
                std_dev = (sum((x - sum(sentence_lengths)/len(sentence_lengths))**2 
                          for x in sentence_lengths) / len(sentence_lengths))**0.5
                if std_dev > 5:  # Good variation
                    score += 5
        
        except:
            # If textstat fails, give average score
            score = 12
        
        return min(25, score)
    
    def _score_structure(self, text):
        """Score based on structure and formatting (0-25)"""
        score = 0
        
        # Paragraph breaks (prevents wall of text)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        line_breaks = text.count('\n')
        
        if len(paragraphs) >= 3:
            score += 6
        elif len(paragraphs) >= 2:
            score += 4
        
        if line_breaks >= 5:
            score += 4
        
        # Strong opening (short, punchy first line)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            first_line = lines[0]
            word_count_first = len(first_line.split())
            if 5 <= word_count_first <= 20:
                score += 5
        
        # Clear sections or lists
        has_bullets = '•' in text or text.count('\n-') >= 2
        has_numbers = bool(re.search(r'\n\d+[\.\)]\s', text))
        
        if has_bullets or has_numbers:
            score += 5
        
        # Logical flow markers
        transition_words = ['however', 'therefore', 'additionally', 'furthermore', 
                           'first', 'second', 'finally', 'in conclusion']
        transitions_found = sum(1 for word in transition_words if word in text.lower())
        score += min(5, transitions_found * 1.5)
        
        return min(25, score)
    
    def _score_professionalism(self, text, text_lower):
        """Score based on professional tone and vocabulary (0-25)"""
        score = 15  # Start with base score
        
        # Professional vocabulary usage
        prof_word_count = sum(1 for word in self.professional_words if word in text_lower)
        score += min(5, prof_word_count * 0.8)
        
        # Appropriate emoji usage (some is fine, too many is not professional)
        emoji_count = len(re.findall(r'[😀-🙏🌀-🗿🚀-🛿]', text))
        if emoji_count == 0:
            score += 3  # Clean, professional
        elif 1 <= emoji_count <= 5:
            score += 2  # Acceptable
        elif emoji_count > 10:
            score -= 3  # Excessive
        
        # Capitalization (excessive caps = unprofessional)
        caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
        if len(caps_words) > 5:
            score -= 3
        
        # Professional sign-off
        if 'p.s.' in text_lower or 'best regards' in text_lower or 'cheers' in text_lower:
            score += 2
        
        return min(25, max(0, score))
    
    def _score_grammar_clarity(self, text):
        """Score based on grammar and clarity indicators (0-25)"""
        score = 15  # Start with base score
        
        # Complete sentences (should end with punctuation)
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 10]
        complete_sentences = sum(1 for line in lines if line[-1] in '.!?')
        if complete_sentences / max(len(lines), 1) > 0.7:
            score += 5
        
        # Avoid run-on sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        long_sentences = sum(1 for s in sentences if len(s.split()) > 40)
        if long_sentences / max(len(sentences), 1) < 0.2:
            score += 3
        
        # Proper use of commas (not too many, not too few)
        words = len(text.split())
        commas = text.count(',')
        comma_ratio = commas / max(words, 1) * 100
        if 1 <= comma_ratio <= 4:  # Healthy range
            score += 3
        
        # Consistent tense/voice
        # Simple heuristic: count past vs present tense markers
        past_markers = len(re.findall(r'\b(was|were|had|did|went|got)\b', text.lower()))
        present_markers = len(re.findall(r'\b(is|are|have|do|goes|get)\b', text.lower()))
        
        # Consistency is good
        if past_markers + present_markers > 0:
            consistency = max(past_markers, present_markers) / (past_markers + present_markers)
            if consistency > 0.7:
                score += 4
        
        return min(25, score)
    
    def _calculate_penalties(self, text, text_lower):
        """Calculate penalties for quality issues (0-20)"""
        penalty = 0
        
        # Clickbait detection
        clickbait_count = sum(1 for pattern in self.clickbait_patterns 
                             if re.search(pattern, text_lower))
        penalty += clickbait_count * 4
        
        # Spam indicators
        spam_count = sum(1 for indicator in self.spam_indicators 
                        if indicator in text_lower)
        penalty += spam_count * 5
        
        # Excessive punctuation
        if text.count('!!!') > 0 or text.count('???') > 0:
            penalty += 3
        
        # All caps words (screaming)
        all_caps_words = re.findall(r'\b[A-Z]{4,}\b', text)
        if len(all_caps_words) > 3:
            penalty += 4
        
        # Typos/spelling (simple check for repeated letters)
        typo_patterns = re.findall(r'(\w)\1{3,}', text_lower)  # e.g., "sooooo"
        penalty += len(typo_patterns) * 2
        
        return min(20, penalty)
    
    def _classify_quality(self, score):
        """Classify the quality level"""
        if score >= 85:
            return "Exceptional Quality"
        elif score >= 70:
            return "High Quality"
        elif score >= 55:
            return "Good Quality"
        elif score >= 40:
            return "Moderate Quality"
        else:
            return "Low Quality"
    
    def _get_readability_grade(self, text):
        """Get readability grade level"""
        try:
            grade = textstat.flesch_kincaid_grade(text)
            return f"Grade {round(grade, 1)}"
        except:
            return "N/A"
    
    def _create_result(self, score, reason):
        """Create a minimal result object"""
        return {
            'total_score': score,
            'readability': 0,
            'structure': 0,
            'professionalism': 0,
            'grammar_clarity': 0,
            'penalties': 0,
            'classification': reason,
            'readability_grade': 'N/A'
        }


def analyze_all_posts(json_file_path):
    """Analyze all posts in the dataset"""
    assessor = QualityAssessor()
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    results = []
    for post in posts:
        text = post.get('text', '')
        author = post.get('author', {})
        
        analysis = assessor.analyze_post(text)
        
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
    print("✍️  ALGORITHM 2: QUALITY ASSESSMENT")
    print("=" * 80)
    
    input_file = "/mnt/user-data/uploads/dataset_linkedin-batch-profile-posts-scraper_2025-11-04_02-03-34-812.json"
    
    print("\nAssessing quality of all posts...")
    results = analyze_all_posts(input_file)
    
    # Sort by score
    results_sorted = sorted(results, key=lambda x: x['total_score'], reverse=True)
    
    # Show top 10
    print("\n🏆 TOP 10 POSTS BY QUALITY:")
    print("-" * 80)
    for i, result in enumerate(results_sorted[:10], 1):
        print(f"\n{i}. {result['author_name']} (@{result['username']})")
        print(f"   Score: {result['total_score']}/100 - {result['classification']}")
        print(f"   Readability: {result['readability_grade']}")
        print(f"   Breakdown: Readability={result['readability']}, "
              f"Structure={result['structure']}, Professional={result['professionalism']}, "
              f"Grammar={result['grammar_clarity']}")
        print(f"   Preview: {result['text_preview']}")
    
    print("\n\n✅ Quality assessment complete!")
    print(f"📊 Analyzed {len(results)} posts")
    print(f"📈 Average quality score: {sum(r['total_score'] for r in results) / len(results):.2f}/100")
    
    # Save results
    import csv
    output_file = "/mnt/user-data/outputs/quality_scores.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['author_name', 'username', 'post_url', 'total_score', 'classification',
                     'word_count', 'readability', 'structure', 'professionalism',
                     'grammar_clarity', 'penalties', 'readability_grade']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results_sorted:
            writer.writerow({k: v for k, v in result.items() if k in fieldnames})
    
    print(f"💾 Results saved to: {output_file}")