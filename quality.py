#!/usr/bin/env python3
"""
ALGORITHM 2: QUALITY ASSESSMENT
Evaluates writing quality, readability, structure, and professionalism

This algorithm analyzes LinkedIn posts and gives them a score from 0-100 based on:
- How easy they are to read
- How well they're structured (paragraphs, lists, formatting)
- How professional they sound
- Grammar and clarity

Think of it like a writing teacher grading essays, but automated!
"""

import json  # For reading JSON files (our LinkedIn data)
import re    # For pattern matching in text (finding emojis, caps, etc.)
import textstat  # A library that calculates readability scores
from collections import Counter  # For counting things efficiently

class QualityAssessor:
    """
    This is the main class that does all the quality assessment work.
    
    A "class" is like a blueprint for creating an object that has both:
    - Data (the patterns and words we look for)
    - Functions (the methods that analyze posts)
    """
    
    def __init__(self):
        """
        This function runs when we create a new QualityAssessor.
        It sets up all the patterns and keywords we'll use to evaluate posts.
        
        Think of this as preparing your toolkit before starting work.
        """
        
        # CLICKBAIT PATTERNS
        # These are phrases that make content feel spammy or sensationalist
        # We'll penalize posts that use these
        self.clickbait_patterns = [
            r'you won\'t believe',      # "You won't believe what happened!"
            r'shocking',                # "Shocking news!"
            r'this one trick',          # "This one trick will change everything"
            r'what happened next',      # Classic clickbait phrase
            r'blown away',              # "I was blown away by..."
            r'mind[\s-]?blown',        # "Mind-blown" or "mind blown"
            r'game[\s-]?changer',      # Overused buzzword
            r'the secret to',           # "The secret to success is..."
            r'everyone is talking about'# Bandwagon appeal
        ]
        
        # PROFESSIONAL VOCABULARY
        # These words indicate sophisticated business writing
        # Using these appropriately = higher score
        self.professional_words = [
            'strategy', 'implement', 'framework', 'optimize', 'leverage',
            'scalable', 'metrics', 'efficiency', 'revenue', 'growth',
            'innovation', 'transformation', 'execution', 'alignment'
        ]
        
        # SPAM/LOW-QUALITY INDICATORS
        # These phrases scream "sales pitch" or "spam"
        # We heavily penalize these
        self.spam_indicators = [
            'dm me',           # "DM me for more info"
            'link in bio',     # Instagram-style call to action
            'click here',      # Generic spam phrase
            'limited time',    # Artificial urgency
            'act now',         # Pressure tactic
            'buy now',         # Direct sales pitch
            'cheap',           # Low-quality indicator
            'make money fast'  # Classic spam phrase
        ]
    
    def analyze_post(self, text):
        """
        This is the MAIN function that analyzes a single post.
        
        HOW IT WORKS:
        1. Check if the post is too short (minimum 30 characters)
        2. Calculate 4 different scores:
           - Readability (how easy to read)
           - Structure (formatting and organization)
           - Professionalism (tone and vocabulary)
           - Grammar & Clarity (sentence quality)
        3. Apply penalties for bad practices (clickbait, spam, etc.)
        4. Add everything up to get a final score out of 100
        
        Parameters:
            text (string): The content of the LinkedIn post
            
        Returns:
            A dictionary with the score and breakdown
        """
        
        # STEP 1: Check if post is too short to analyze
        if not text or len(text.strip()) < 30:
            return self._create_result(0, "Too short")
        
        # Convert text to lowercase for easier matching
        # (We do this because "HELLO" and "hello" should be treated the same)
        text_lower = text.lower()
        
        # STEP 2: Calculate the 4 component scores
        # Each function returns a score from 0-25 points
        
        readability = self._score_readability(text)
        # ^ How easy is this to read? Grade level appropriate?
        
        structure = self._score_structure(text)
        # ^ Is it formatted well? Has paragraphs, lists, etc.?
        
        professionalism = self._score_professionalism(text, text_lower)
        # ^ Does it sound professional? Right vocabulary? Not too many emojis?
        
        grammar = self._score_grammar_clarity(text)
        # ^ Are sentences complete? Good use of commas? Consistent tense?
        
        # STEP 3: Calculate penalties for bad practices
        penalties = self._calculate_penalties(text, text_lower)
        # ^ Deduct points for clickbait, spam, excessive caps, etc.
        
        # STEP 4: Calculate total score
        # Add up all the positive scores, subtract penalties
        # Use max(0, ...) to ensure score never goes below 0
        total_score = max(0, readability + structure + professionalism + grammar - penalties)
        
        # Make sure score doesn't exceed 100
        normalized_score = min(100, total_score)
        
        # STEP 5: Return all the results in a dictionary
        return {
            'total_score': round(normalized_score, 2),  # Main score (rounded to 2 decimals)
            'readability': round(readability, 2),        # Breakdown: readability component
            'structure': round(structure, 2),            # Breakdown: structure component
            'professionalism': round(professionalism, 2),# Breakdown: professionalism component
            'grammar_clarity': round(grammar, 2),        # Breakdown: grammar component
            'penalties': round(penalties, 2),            # How many points were deducted
            'classification': self._classify_quality(normalized_score),  # Label like "High Quality"
            'readability_grade': self._get_readability_grade(text)       # Reading level (e.g., "Grade 8")
        }
    
    def _score_readability(self, text):
        """
        READABILITY SCORING (0-25 points possible)
        
        This measures how easy the text is to read and understand.
        
        We use established readability formulas:
        - Flesch Reading Ease: Higher score = easier to read
        - Flesch-Kincaid Grade Level: What grade level is needed to understand this?
        
        We also check for sentence length variety (good writers mix short and long sentences)
        """
        score = 0  # Start at 0 and add points
        
        try:
            # FLESCH READING EASE SCORE
            # This gives a score from 0-100, where:
            # - 90-100 = Very easy (5th grade level)
            # - 60-70 = Easy (8th-9th grade)
            # - 30-50 = Difficult (college level)
            # - 0-30 = Very difficult (graduate level)
            flesch = textstat.flesch_reading_ease(text)
            
            # For LinkedIn business content, we want 50-70 (fairly easy)
            # This is readable but still sophisticated
            if 50 <= flesch <= 70:
                score += 10  # Perfect range - full points
            elif 40 <= flesch < 50 or 70 < flesch <= 80:
                score += 7   # Close to ideal - most points
            elif flesch > 30:
                score += 4   # Readable enough - some points
            # If flesch is below 30, we give 0 points (too difficult)
            
            # FLESCH-KINCAID GRADE LEVEL
            # This tells us what US grade level is needed to understand the text
            # Examples: 8.0 = 8th grade, 12.0 = high school senior
            grade_level = textstat.flesch_kincaid_grade(text)
            
            # We want grade 8-12 (accessible but sophisticated)
            if 8 <= grade_level <= 12:
                score += 10  # Ideal range
            elif 6 <= grade_level < 8 or 12 < grade_level <= 14:
                score += 7   # Close to ideal
            elif grade_level < 16:
                score += 4   # Not terrible
            # Above grade 16 gets 0 points (too academic for LinkedIn)
            
            # SENTENCE LENGTH VARIATION
            # Good writers vary their sentence length (mix of short and long)
            # Bad writers use only short sentences or only long ones
            
            # Split text into sentences (splitting on . ! or ?)
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            
            if len(sentences) > 1:  # Need at least 2 sentences to compare
                # Count words in each sentence
                sentence_lengths = [len(s.split()) for s in sentences]
                
                # Calculate standard deviation (how much the lengths vary)
                # Higher std_dev = more variety = better
                avg_length = sum(sentence_lengths) / len(sentence_lengths)
                variance = sum((x - avg_length)**2 for x in sentence_lengths) / len(sentence_lengths)
                std_dev = variance**0.5
                
                if std_dev > 5:  # Good variety in sentence length
                    score += 5
        
        except:
            # If textstat fails for any reason, give an average score
            # This happens rarely but we want the code to keep running
            score = 12
        
        # Make sure we don't exceed 25 points for this section
        return min(25, score)
    
    def _score_structure(self, text):
        """
        STRUCTURE SCORING (0-25 points possible)
        
        This evaluates how well the post is organized and formatted.
        
        Good structure means:
        - Paragraph breaks (not a wall of text)
        - A strong opening line
        - Use of lists or bullet points
        - Logical flow with transition words
        """
        score = 0  # Start at 0 and add points
        
        # PARAGRAPH BREAKS
        # Posts split into paragraphs are easier to read than walls of text
        # We look for double line breaks (\n\n) which indicate new paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Also count total line breaks (single \n)
        line_breaks = text.count('\n')
        
        # Award points based on number of paragraphs
        if len(paragraphs) >= 3:
            score += 6  # Multiple paragraphs = well organized
        elif len(paragraphs) >= 2:
            score += 4  # At least split into sections
        
        # Award points for having line breaks
        if line_breaks >= 5:
            score += 4  # Formatted with breathing room
        
        # STRONG OPENING
        # The first line should be short and punchy to grab attention
        # Too short (<5 words) = incomplete thought
        # Too long (>20 words) = loses impact
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            first_line = lines[0]
            word_count_first = len(first_line.split())
            
            if 5 <= word_count_first <= 20:
                score += 5  # Sweet spot for opening line
        
        # CLEAR SECTIONS OR LISTS
        # Look for bullet points (•) or dashed lists (-)
        has_bullets = '•' in text or text.count('\n-') >= 2
        
        # Look for numbered lists (1. 2. or 1) 2))
        has_numbers = bool(re.search(r'\n\d+[\.\)]\s', text))
        
        if has_bullets or has_numbers:
            score += 5  # Lists make content scannable
        
        # LOGICAL FLOW MARKERS
        # Transition words show logical progression of ideas
        # Examples: "however" (contrast), "therefore" (conclusion), "first" (sequence)
        transition_words = [
            'however', 'therefore', 'additionally', 'furthermore', 
            'first', 'second', 'finally', 'in conclusion'
        ]
        
        # Count how many transition words appear
        transitions_found = sum(1 for word in transition_words if word in text.lower())
        
        # Award up to 5 points (1.5 points per transition word found)
        score += min(5, transitions_found * 1.5)
        
        # Cap at 25 points
        return min(25, score)
    
    def _score_professionalism(self, text, text_lower):
        """
        PROFESSIONALISM SCORING (0-25 points possible)
        
        This measures how professional and business-appropriate the post sounds.
        
        We look at:
        - Use of professional vocabulary
        - Appropriate emoji usage (some is fine, too many is not)
        - Proper capitalization (not SHOUTING)
        - Professional sign-offs
        """
        score = 15  # Start with a base score (assume reasonably professional)
        
        # PROFESSIONAL VOCABULARY USAGE
        # Count how many professional business words appear
        # Words like "strategy", "implement", "framework" signal expertise
        prof_word_count = sum(1 for word in self.professional_words if word in text_lower)
        
        # Award up to 5 points (0.8 points per professional word)
        score += min(5, prof_word_count * 0.8)
        
        # EMOJI USAGE
        # Emojis can add personality, but too many look unprofessional
        # We use Unicode ranges to detect common emojis
        emoji_count = len(re.findall(r'[😀-🙏🌀-🗿🚀-🛿]', text))
        
        if emoji_count == 0:
            score += 3  # Clean and professional
        elif 1 <= emoji_count <= 5:
            score += 2  # Acceptable - adds personality without overdoing it
        elif emoji_count > 10:
            score -= 3  # Excessive - looks unprofessional
        # 6-10 emojis get 0 bonus points (neutral)
        
        # CAPITALIZATION ISSUES
        # ALL CAPS WORDS look like SHOUTING
        # Find words that are 3+ characters and all capitals
        caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
        
        if len(caps_words) > 5:
            score -= 3  # Too much shouting - penalize
        
        # PROFESSIONAL SIGN-OFF
        # Posts that end with "P.S.", "Best regards", or "Cheers" show polish
        if 'p.s.' in text_lower or 'best regards' in text_lower or 'cheers' in text_lower:
            score += 2  # Bonus for professional closing
        
        # Keep score in valid range (0-25)
        return min(25, max(0, score))
    
    def _score_grammar_clarity(self, text):
        """
        GRAMMAR & CLARITY SCORING (0-25 points possible)
        
        This evaluates the grammatical correctness and clarity of writing.
        
        We check for:
        - Complete sentences (ending with punctuation)
        - Avoiding run-on sentences
        - Proper comma usage
        - Consistent verb tense
        """
        score = 15  # Start with base score (assume decent grammar)
        
        # COMPLETE SENTENCES
        # Each line should end with proper punctuation (. ! or ?)
        # This indicates complete thoughts, not fragments
        
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 10]
        # ^ Get all lines that aren't empty and have at least 10 characters
        
        # Count how many lines end with punctuation
        complete_sentences = sum(1 for line in lines if line[-1] in '.!?')
        
        # If >70% of lines are complete sentences, that's good
        if complete_sentences / max(len(lines), 1) > 0.7:
            score += 5
        
        # AVOID RUN-ON SENTENCES
        # Sentences over 40 words are usually run-ons (too long without breaks)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        long_sentences = sum(1 for s in sentences if len(s.split()) > 40)
        
        # If <20% of sentences are too long, that's good
        if long_sentences / max(len(sentences), 1) < 0.2:
            score += 3
        
        # PROPER COMMA USAGE
        # Too many commas = choppy writing
        # Too few commas = confusing writing
        # Sweet spot: 1-4 commas per 100 words
        
        words = len(text.split())
        commas = text.count(',')
        comma_ratio = commas / max(words, 1) * 100  # Commas per 100 words
        
        if 1 <= comma_ratio <= 4:  # Healthy range
            score += 3
        
        # CONSISTENT TENSE/VOICE
        # Good writing maintains consistent verb tense (past vs. present)
        # We count common past and present tense verb markers
        
        past_markers = len(re.findall(r'\b(was|were|had|did|went|got)\b', text.lower()))
        present_markers = len(re.findall(r'\b(is|are|have|do|goes|get)\b', text.lower()))
        
        # Calculate consistency
        # If you use mostly past OR mostly present (>70%), that's consistent
        if past_markers + present_markers > 0:
            dominant = max(past_markers, present_markers)
            total = past_markers + present_markers
            consistency = dominant / total
            
            if consistency > 0.7:  # Consistent tense usage
                score += 4
        
        # Cap at 25 points
        return min(25, score)
    
    def _calculate_penalties(self, text, text_lower):
        """
        PENALTIES (0-20 points deducted)
        
        This identifies and penalizes bad practices that harm quality.
        
        We penalize:
        - Clickbait phrases
        - Spam indicators
        - Excessive punctuation
        - All caps words (shouting)
        - Typos (repeated letters like "sooooo")
        """
        penalty = 0  # Start at 0 and add penalties
        
        # CLICKBAIT DETECTION
        # Count how many clickbait patterns appear in the text
        clickbait_count = sum(1 for pattern in self.clickbait_patterns 
                             if re.search(pattern, text_lower))
        
        # Deduct 4 points per clickbait phrase
        penalty += clickbait_count * 4
        
        # SPAM INDICATORS
        # Count how many spam phrases appear
        spam_count = sum(1 for indicator in self.spam_indicators 
                        if indicator in text_lower)
        
        # Deduct 5 points per spam indicator (heavy penalty)
        penalty += spam_count * 5
        
        # EXCESSIVE PUNCTUATION
        # Multiple exclamation or question marks look unprofessional
        # "This is amazing!!!" or "Really???"
        if text.count('!!!') > 0 or text.count('???') > 0:
            penalty += 3
        
        # ALL CAPS WORDS (SCREAMING)
        # Find words that are 4+ characters and all capitals
        all_caps_words = re.findall(r'\b[A-Z]{4,}\b', text)
        
        if len(all_caps_words) > 3:
            penalty += 4  # Too much shouting
        
        # TYPOS/SPELLING ERRORS
        # Simple check: look for repeated letters (4+ times)
        # Examples: "sooooo", "nooooo", "yessss"
        typo_patterns = re.findall(r'(\w)\1{3,}', text_lower)
        
        # Deduct 2 points per typo-like pattern
        penalty += len(typo_patterns) * 2
        
        # Cap penalties at 20 points max
        return min(20, penalty)
    
    def _classify_quality(self, score):
        """
        Convert numeric score to a text label.
        
        This makes it easier to understand what the score means:
        - 85+: Exceptional (top tier content)
        - 70-84: High Quality (very good)
        - 55-69: Good Quality (solid)
        - 40-54: Moderate Quality (okay but needs work)
        - <40: Low Quality (poor)
        """
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
        """
        Get the reading grade level as a formatted string.
        
        Example: "Grade 8.5" means you need 8th grade reading skills.
        """
        try:
            grade = textstat.flesch_kincaid_grade(text)
            return f"Grade {round(grade, 1)}"
        except:
            return "N/A"  # If calculation fails, return "Not Available"
    
    def _create_result(self, score, reason):
        """
        Helper function to create a result dictionary with default values.
        Used when a post is too short to analyze.
        """
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
    """
    Analyze every post in a JSON file and return results.
    
    This function:
    1. Loads the JSON file containing LinkedIn posts
    2. Creates a QualityAssessor object
    3. Runs analysis on each post
    4. Returns a list of results
    
    Parameters:
        json_file_path (string): Path to the JSON file
        
    Returns:
        List of dictionaries, one per post, with scores and metadata
    """
    
    # Create a new QualityAssessor object
    assessor = QualityAssessor()
    
    # Open and read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)  # Parse JSON into Python data structure
    
    # Create an empty list to store results
    results = []
    
    # Loop through each post in the data
    for post in posts:
        # Extract the text content
        text = post.get('text', '')  # get('text', '') means "get 'text', or '' if missing"
        
        # Extract author information
        author = post.get('author', {})
        
        # Analyze this post
        analysis = assessor.analyze_post(text)
        
        # Combine the analysis with post metadata
        results.append({
            # Author information
            'author_name': f"{author.get('first_name', '')} {author.get('last_name', '')}".strip(),
            'username': author.get('username', ''),
            'post_url': post.get('url', ''),
            
            # Text preview (first 100 characters)
            'text_preview': text[:100] + '...' if len(text) > 100 else text,
            'word_count': len(text.split()),
            
            # Spread all analysis results into this dictionary
            **analysis  # The ** operator unpacks the analysis dictionary
        })
    
    return results


# MAIN EXECUTION BLOCK
# This code only runs if you execute this file directly
# (It won't run if you import this file into another program)
if __name__ == "__main__":
    print("✍️  ALGORITHM 2: QUALITY ASSESSMENT")
    print("=" * 80)
    
    # Path to the input data file
    input_file = "/mnt/user-data/uploads/dataset_linkedin-batch-profile-posts-scraper_2025-11-04_02-03-34-812.json"
    
    print("\nAssessing quality of all posts...")
    
    # Analyze all posts in the file
    results = analyze_all_posts(input_file)
    
    # Sort results by score (highest first)
    results_sorted = sorted(results, key=lambda x: x['total_score'], reverse=True)
    
    # Display the top 10 posts
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
    
    # Print summary statistics
    print("\n\n✅ Quality assessment complete!")
    print(f"📊 Analyzed {len(results)} posts")
    print(f"📈 Average quality score: {sum(r['total_score'] for r in results) / len(results):.2f}/100")
    
    # Save results to CSV file
    import csv
    output_file = "/mnt/user-data/outputs/quality_scores_commented.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        # Define which columns to include in the CSV
        fieldnames = ['author_name', 'username', 'post_url', 'total_score', 'classification',
                     'word_count', 'readability', 'structure', 'professionalism',
                     'grammar_clarity', 'penalties', 'readability_grade']
        
        # Create a CSV writer object
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write each result as a row
        for result in results_sorted:
            # Only include the fields we defined above
            writer.writerow({k: v for k, v in result.items() if k in fieldnames})
    
    print(f"💾 Results saved to: {output_file}")