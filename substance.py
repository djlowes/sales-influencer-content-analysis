#!/usr/bin/env python3
"""
ALGORITHM 1: SUBSTANCE DETECTION
Analyzes LinkedIn posts for information density, depth, and value

This algorithm measures how MEATY and VALUABLE a post is by looking at:
- Information density (how much actual content vs fluff)
- Depth (does it go beyond surface-level observations?)
- Value indicators (data, frameworks, examples, actionable advice)
- Structure (is it well-organized?)

Think of it like the difference between:
- Shallow: "Success is a mindset! Agree? 🚀"
- Substantive: "Here's the 5-step framework we used to increase revenue by 40%: [detailed explanation with data]"
"""

import json  # For reading JSON files (our LinkedIn data)
import re    # For pattern matching in text
from collections import Counter  # For counting things efficiently
import textstat  # Library for readability calculations (not heavily used here)

class SubstanceDetector:
    """
    This is the main class that detects substance in LinkedIn posts.
    
    "Substance" = the meat of the content. Posts with high substance:
    - Share specific insights, not generic platitudes
    - Include data, examples, or frameworks
    - Teach something actionable
    - Go deep rather than staying surface-level
    """
    
    def __init__(self):
        """
        Initialize the detector by setting up all the patterns we'll look for.
        
        We organize value indicators into categories because different types
        of substance show up in different ways.
        """
        
        # VALUE INDICATORS
        # These are grouped by type of substantial content
        # If a post has these, it's more likely to be meaty/valuable
        self.value_indicators = {
            # DATA & RESEARCH: Shows the post is evidence-based
            'data': ['data', 'statistics', 'study', 'research', 'survey', 'report', 'analysis'],
            
            # FRAMEWORKS: Indicates structured thinking and methodology
            'frameworks': ['framework', 'model', 'strategy', 'approach', 'method', 'process', 'system'],
            
            # EXAMPLES: Specific cases make abstract ideas concrete
            'examples': ['example', 'case study', 'instance', 'for example', 'e.g.', 'such as'],
            
            # ACTIONABLE ADVICE: Posts that help people DO something
            'actionable': ['how to', 'steps', 'tactics', 'tips', 'guide', 'implement', 'apply'],
            
            # METRICS: Numbers and measurements = specificity
            'metrics': ['%', 'percent', 'increase', 'decrease', 'roi', 'revenue', 'growth', '$'],
            
            # INSIGHTS: Shows learning and reflection
            'insights': ['learned', 'discovered', 'found', 'realized', 'insight', 'lesson'],
            
            # EXPERTISE: Signals real experience, not just theory
            'expertise': ['experience', 'years', 'worked', 'built', 'scaled', 'led', 'managed']
        }
        
        # SHALLOW CONTENT INDICATORS
        # These phrases signal engagement-bait rather than substance
        # They ask for interaction without providing value
        self.shallow_indicators = [
            'agree?',           # Generic question with no real content
            'thoughts?',        # Asking for engagement without adding value
            'what do you think', # Another engagement prompt
            'drop a',           # "Drop a comment" = fishing for engagement
            'comment below',    # Explicit engagement bait
            'tag someone',      # Viral tactic, not substantive content
            'follow for more',  # Self-promotion without value
            'repost if'         # Asking for shares without earning them
        ]
        
    def analyze_post(self, text):
        """
        This is the MAIN function that analyzes a single post for substance.
        
        HOW IT WORKS:
        1. Check if post is long enough to analyze (minimum 50 characters)
        2. Calculate 4 component scores:
           - Information Density (0-30 points): How much info per word?
           - Depth (0-25 points): Does it go beyond surface level?
           - Value Indicators (0-25 points): Does it include data, examples, frameworks?
           - Structure (0-20 points): Is it well-organized?
        3. Apply penalties for shallow tactics (engagement bait, etc.)
        4. Add everything up for a final score out of 100
        
        Parameters:
            text (string): The LinkedIn post content
            
        Returns:
            Dictionary with total score and component breakdowns
        """
        
        # STEP 1: Validate post length
        # Posts under 50 characters can't have much substance
        if not text or len(text.strip()) < 50:
            return self._create_result(0, "Too short")
        
        # Convert to lowercase for easier matching
        # This way "Framework" and "framework" are treated the same
        text_lower = text.lower()
        
        # STEP 2: Calculate the 4 component scores
        # Each function focuses on a different aspect of substance
        
        info_density = self._score_information_density(text, text_lower)
        # ^ How much information is packed into this post?
        
        depth_score = self._score_depth(text, text_lower)
        # ^ Does it go deep or stay surface-level?
        
        value_score = self._score_value_indicators(text_lower)
        # ^ Does it contain valuable elements (data, frameworks, examples)?
        
        structure_score = self._score_structure(text)
        # ^ Is it well-organized and easy to follow?
        
        # STEP 3: Calculate penalties
        # Deduct points for shallow tactics and engagement bait
        penalties = self._calculate_penalties(text_lower)
        
        # STEP 4: Calculate total score
        # Add positives, subtract penalties, ensure we don't go below 0
        total_score = max(0, info_density + depth_score + value_score + structure_score - penalties)
        
        # Make sure score doesn't exceed 100
        normalized_score = min(100, total_score)
        
        # STEP 5: Return all results
        return {
            'total_score': round(normalized_score, 2),           # Main score out of 100
            'information_density': round(info_density, 2),       # Component 1
            'depth_score': round(depth_score, 2),                # Component 2
            'value_indicators': round(value_score, 2),           # Component 3
            'structure_score': round(structure_score, 2),        # Component 4
            'penalties': round(penalties, 2),                    # Points deducted
            'classification': self._classify_substance(normalized_score)  # Text label
        }
    
    def _score_information_density(self, text, text_lower):
        """
        INFORMATION DENSITY SCORING (0-30 points possible)
        
        This measures how much actual INFORMATION is packed into the post.
        
        High density = lots of facts, data, and insights per word
        Low density = fluff, platitudes, generic statements
        
        We look at:
        - Word count (longer posts CAN have more substance, but not always)
        - Sentence complexity (too simple = shallow, too complex = hard to read)
        - Numbers and statistics (data = substance)
        - Formatting (lists and structure indicate organized thinking)
        """
        score = 0  # Start at 0 and add points
        
        # WORD COUNT
        # Longer posts have MORE POTENTIAL for substance
        # But length alone doesn't guarantee quality (hence other checks)
        words = len(text.split())
        
        if words > 500:
            score += 10  # Very long - lots of room for depth
        elif words > 300:
            score += 7   # Long - good potential
        elif words > 150:
            score += 5   # Medium - moderate potential
        elif words > 100:
            score += 3   # Short but workable
        # Under 100 words gets 0 points (hard to be substantive)
        
        # SENTENCE COMPLEXITY
        # We want sentences that are:
        # - Not too simple (sounds childish)
        # - Not too complex (becomes unreadable)
        # - The "sweet spot" is 15-25 words per sentence
        
        # Split text into sentences (breaking on . ! or ?)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if sentences:  # Make sure we have at least one sentence
            # Calculate average words per sentence
            avg_words_per_sentence = words / len(sentences)
            
            if 15 <= avg_words_per_sentence <= 25:
                score += 8  # Perfect complexity - full points
            elif 10 <= avg_words_per_sentence < 15:
                score += 5  # A bit simple but okay
            # Below 10 or above 25 gets 0 points
        
        # NUMBERS AND STATISTICS
        # Posts with data are more substantive than vague claims
        # Examples: "40%", "$2M", "150 customers", "3x increase"
        
        # Find all numbers, including those with % or $
        numbers = re.findall(r'\b\d+[%$]?\b|\$\d+', text)
        
        # Award 1.5 points per number found, up to 7 points max
        # This rewards data-driven content
        score += min(7, len(numbers) * 1.5)
        
        # PUNCTUATION VARIETY (Lists and Structure)
        # Well-organized posts often use:
        # - Bullet points (•)
        # - Numbered lists (1. 2. 3.)
        # - Dashed lists (- item)
        
        has_lists = (
            '•' in text or                          # Bullet points
            re.search(r'\n\d+\.', text) or         # Numbered list
            text.count('\n-') > 2                   # Multiple dashed items
        )
        
        if has_lists:
            score += 5  # Lists = organized thinking
        
        # Cap at 30 points for this section
        return min(30, score)
    
    def _score_depth(self, text, text_lower):
        """
        DEPTH SCORING (0-25 points possible)
        
        This measures whether the post goes DEEP or stays SHALLOW.
        
        Deep content:
        - Shares specific examples from experience
        - Explains the "why" and "how", not just "what"
        - Shows learning and reflection
        - Provides multi-step explanations
        - Uses sophisticated vocabulary
        
        Shallow content:
        - Generic platitudes ("Work hard!" "Believe in yourself!")
        - No examples or specifics
        - Surface-level observations
        """
        score = 0  # Start at 0 and add points
        
        # SPECIFIC EXAMPLES OR CASE STUDIES
        # These phrases indicate the author is sharing concrete experiences
        # rather than abstract theory
        example_patterns = [
            r'for example',  # Introducing a specific case
            r'for instance', # Another way to introduce examples
            r'case study',   # Formal example discussion
            r'i worked',     # Personal experience
            r'we built',     # Hands-on involvement
            r'i led',        # Leadership experience
            r'i managed'     # Management experience
        ]
        
        # Check if ANY of these patterns appear
        # We only award points once (not for each pattern)
        for pattern in example_patterns:
            if re.search(pattern, text_lower):
                score += 3  # Has at least one concrete example
                break       # Stop checking after first match
        
        # PERSONAL EXPERIENCE SIGNALS
        # Posts that share learning show depth of thought
        experience_words = ['learned', 'discovered', 'realized', 'found out', 'experience']
        
        # Count how many of these words appear
        # Award 2 points per word, up to 5 points max
        score += min(5, sum(2 for word in experience_words if word in text_lower))
        
        # PROBLEM-SOLUTION STRUCTURE
        # Posts that identify a problem AND offer a solution show deeper thinking
        # This is better than just complaining OR just suggesting solutions
        if 'problem' in text_lower and 'solution' in text_lower:
            score += 4  # Has both problem and solution
        
        # MULTI-STEP EXPLANATIONS
        # Numbered lists with multiple points indicate structured thinking
        # Example: "1. First step\n2. Second step\n3. Third step"
        
        # Find all numbered list items (matches "1. " or "1) ")
        numbered_items = len(re.findall(r'\n\d+[\.\)]\s', text))
        
        # Award 1.5 points per numbered item, up to 8 points max
        # More steps = more thorough explanation
        score += min(8, numbered_items * 1.5)
        
        # COMPLEXITY OF VOCABULARY
        # Sophisticated vocabulary often indicates expertise
        # We use word length as a proxy (longer words = more specific/technical)
        
        # Find all words longer than 10 characters
        long_words = [w for w in text.split() if len(w) > 10]
        
        # Award 0.3 points per long word, up to 5 points max
        score += min(5, len(long_words) * 0.3)
        
        # Cap at 25 points for this section
        return min(25, score)
    
    def _score_value_indicators(self, text_lower):
        """
        VALUE INDICATORS SCORING (0-25 points possible)
        
        This checks for specific types of valuable content.
        
        We organized value indicators into 7 categories (see __init__):
        1. Data & Research (statistics, studies)
        2. Frameworks (models, strategies)
        3. Examples (case studies, instances)
        4. Actionable advice (how-to, tactics)
        5. Metrics (numbers, percentages)
        6. Insights (lessons learned)
        7. Expertise (real experience)
        
        Posts that include multiple types of value score higher.
        """
        score = 0  # Start at 0 and add points
        
        # Loop through each category of value indicators
        for category, keywords in self.value_indicators.items():
            # For this category, count how many keywords appear
            # Example: If category is 'data', check for 'statistics', 'study', etc.
            found = sum(1 for keyword in keywords if keyword in text_lower)
            
            if found > 0:
                # This category has at least one keyword present
                # Award up to 4 points per category (1.5 points per keyword found)
                score += min(4, found * 1.5)
        
        # Cap at 25 points for this section
        return min(25, score)
    
    def _score_structure(self, text):
        """
        STRUCTURE SCORING (0-20 points possible)
        
        This evaluates how well the post is organized.
        
        Good structure helps readers:
        - Quickly grasp the main point (strong opening)
        - Follow the logic (clear sections)
        - Remember key takeaways (good conclusion)
        - Scan for relevant info (formatting)
        
        Even substantive content is less valuable if poorly organized.
        """
        score = 0  # Start at 0 and add points
        
        # CLEAR SECTIONS (PARAGRAPHS)
        # Breaking content into paragraphs makes it easier to digest
        # We look for double line breaks (\n\n) which indicate new paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if len(paragraphs) >= 3:
            score += 5  # Multiple sections = well-organized
        elif len(paragraphs) >= 2:
            score += 3  # At least some structure
        # Single paragraph gets 0 points (wall of text)
        
        # OPENING HOOK
        # The first line should grab attention without being too long
        # Too short (<20 chars) = incomplete
        # Too long (>150 chars) = loses impact
        first_line = text.split('\n')[0]
        
        if len(first_line) < 150 and len(first_line) > 20:
            score += 3  # Good opening hook
        
        # CONCLUSION/SUMMARY
        # Strong posts often end with a takeaway or call-to-action
        # Check if the last paragraph contains conclusion words
        last_paragraph = paragraphs[-1] if paragraphs else ""
        
        conclusion_words = [
            'in conclusion',  # Formal closing
            'summary',        # Recap
            'bottom line',    # Key point
            'key takeaway',   # Main lesson
            'p.s.'           # Additional note/CTA
        ]
        
        if any(word in last_paragraph.lower() for word in conclusion_words):
            score += 4  # Has a proper conclusion
        
        # PROPER FORMATTING (Not a Wall of Text)
        # Multiple line breaks indicate breathing room and organization
        if text.count('\n') > 5:
            score += 3  # Formatted with multiple breaks
        
        # CLEAR HEADERS OR SECTIONS
        # Look for:
        # - ALL CAPS HEADERS: "THE PROBLEM:"
        # - Em-dashes separating sections: "—"
        
        # Pattern: 10+ capital letters/spaces followed by colon
        has_headers = re.search(r'[A-Z\s]{10,}:', text)
        has_dashes = text.count('—') > 2
        
        if has_headers or has_dashes:
            score += 5  # Has clear section markers
        
        # Cap at 20 points for this section
        return min(20, score)
    
    def _calculate_penalties(self, text_lower):
        """
        PENALTIES (0-15 points deducted)
        
        This identifies and penalizes tactics that reduce substance:
        - Engagement bait ("Agree? Comment below!")
        - Excessive emojis (style over substance)
        - Posts that are too short to deliver on their claims
        
        These tactics prioritize virality over value.
        """
        penalty = 0  # Start at 0 and add penalties
        
        # ENGAGEMENT BAIT
        # These phrases are designed to get clicks/comments without adding value
        # Examples: "Agree?", "Thoughts?", "Tag someone who needs this"
        
        # Check if any shallow indicators appear in the text
        for indicator in self.shallow_indicators:
            if indicator in text_lower:
                penalty += 3  # Penalize each instance of engagement bait
        
        # EXCESSIVE EMOJIS
        # A few emojis add personality; too many replace substance
        # We check for common LinkedIn emojis
        emoji_count = len(re.findall(r'[🔥💪👇✨🚀💯🎯⚡️📈]', text_lower))
        
        if emoji_count > 10:
            penalty += 5  # Way too many - heavy penalty
        elif emoji_count > 5:
            penalty += 2  # Getting excessive - light penalty
        # 0-5 emojis is fine, no penalty
        
        # TOO SHORT FOR CLAIMED DEPTH
        # If a post is under 100 words, it can't really be substantive
        # (This is different from the 50-character minimum for analysis)
        word_count = len(text_lower.split())
        
        if word_count < 100:
            penalty += 5  # Can't have much substance in <100 words
        
        # Cap penalties at 15 points max
        return min(15, penalty)
    
    def _classify_substance(self, score):
        """
        Convert numeric score to a text label for easier understanding.
        
        This helps people quickly understand what the score means:
        - 80+: Exceptional (rare, truly meaty content)
        - 65-79: High (solid, valuable content)
        - 50-64: Moderate (some value, but could be deeper)
        - 35-49: Low (mostly surface-level)
        - <35: Minimal (fluff, engagement bait, platitudes)
        """
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
        """
        Helper function to create a result dictionary with default values.
        
        This is used when a post is too short to analyze properly.
        Returns a properly formatted result with zeros for all components.
        """
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
    """
    Analyze every post in a JSON file for substance.
    
    This function:
    1. Loads the JSON file containing LinkedIn posts
    2. Creates a SubstanceDetector object
    3. Analyzes each post
    4. Returns a list of results with scores and metadata
    
    Parameters:
        json_file_path (string): Path to the JSON file
        
    Returns:
        List of dictionaries, one per post, with substance scores
    """
    
    # Create a new SubstanceDetector object
    detector = SubstanceDetector()
    
    # Open and read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)  # Parse JSON into Python data
    
    # Create an empty list to store results
    results = []
    
    # Loop through each post and analyze it
    for post in posts:
        # Extract the text content
        text = post.get('text', '')
        
        # Extract author information
        author = post.get('author', {})
        
        # Analyze this post's substance
        analysis = detector.analyze_post(text)
        
        # Combine analysis with post metadata
        results.append({
            # Author information
            'author_name': f"{author.get('first_name', '')} {author.get('last_name', '')}".strip(),
            'username': author.get('username', ''),
            'post_url': post.get('url', ''),
            
            # Text preview (first 100 characters)
            'text_preview': text[:100] + '...' if len(text) > 100 else text,
            'word_count': len(text.split()),
            
            # Spread all analysis results into this dictionary
            **analysis  # The ** operator unpacks the dictionary
        })
    
    return results


# MAIN EXECUTION BLOCK
# This code only runs if you execute this file directly
if __name__ == "__main__":
    print("🔍 ALGORITHM 1: SUBSTANCE DETECTION")
    print("=" * 80)
    
    # Path to the input data file
    input_file = "/mnt/user-data/uploads/dataset_linkedin-batch-profile-posts-scraper_2025-11-04_02-03-34-812.json"
    
    print("\nAnalyzing substance of all posts...")
    
    # Analyze all posts
    results = analyze_all_posts(input_file)
    
    # Sort results by score (highest first)
    results_sorted = sorted(results, key=lambda x: x['total_score'], reverse=True)
    
    # Display top 10 posts
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
    
    # Print summary statistics
    print("\n\n✅ Substance analysis complete!")
    print(f"📊 Analyzed {len(results)} posts")
    print(f"📈 Average substance score: {sum(r['total_score'] for r in results) / len(results):.2f}/100")
    
    # Save results to CSV
    import csv
    output_file = "/mnt/user-data/outputs/substance_scores_commented.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        # Define columns for the CSV
        fieldnames = ['author_name', 'username', 'post_url', 'total_score', 'classification',
                     'word_count', 'information_density', 'depth_score', 'value_indicators',
                     'structure_score', 'penalties']
        
        # Create CSV writer
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header row
        writer.writeheader()
        
        # Write each result as a row
        for result in results_sorted:
            writer.writerow({k: v for k, v in result.items() if k in fieldnames})
    
    print(f"💾 Results saved to: {output_file}")