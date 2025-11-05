#!/usr/bin/env python3
"""
ALGORITHM 3: UNIQUENESS DETECTION
Identifies originality, personal stories, and differentiation from generic content

This algorithm detects whether a post is ORIGINAL or just another cookie-cutter template.

It measures:
- Personal stories and experiences (your unique journey)
- Original thinking (fresh perspectives, not recycled wisdom)
- Specific details (real examples vs. vague platitudes)
- Similarity to other posts (is this different from what everyone else says?)

Think of the difference between:
- Generic: "Success comes from hard work and dedication 💪"
- Unique: "In 2019, I failed 3 product launches. Here's the counterintuitive lesson that saved my career..."
"""

import json  # For reading JSON files
import re    # For pattern matching in text
from collections import Counter  # For counting occurrences
from sklearn.feature_extraction.text import TfidfVectorizer  # For text similarity analysis
from sklearn.metrics.pairwise import cosine_similarity  # For comparing posts
import numpy as np  # For numerical operations

class UniquenessDetector:
    """
    This class detects uniqueness and originality in LinkedIn posts.
    
    "Uniqueness" = standing out from the crowd by:
    1. Sharing YOUR story (not generic advice)
    2. Having YOUR perspective (not recycled quotes)
    3. Being specific (not vague)
    4. Saying something different (not repeating what everyone else says)
    """
    
    def __init__(self):
        """
        Initialize the detector by setting up all the patterns we'll look for.
        
        We identify both POSITIVE indicators (signs of uniqueness) and
        NEGATIVE indicators (signs of generic/templated content).
        """
        
        # GENERIC PHRASES/TEMPLATES
        # These are overused opening lines that signal copy-paste content
        # If you've seen these a thousand times on LinkedIn, they're here
        self.generic_phrases = [
            'i was scrolling through linkedin',  # Overused narrative device
            'can we talk about',                 # Generic conversation starter
            'let me tell you',                   # Overused storytelling opener
            'here\'s the thing',                 # Cliché transition phrase
            'hot take',                          # Overused attention-grabber
            'unpopular opinion',                 # Often followed by popular opinions
            'change my mind',                    # Borrowed from meme culture
            'this is your sign',                 # Generic motivational template
            'normalize',                         # Overused call-to-action format
            'it\'s time to',                     # Generic manifesto opener
            'stop doing',                        # Common list format
            'start doing'                        # Common list format
        ]
        
        # PERSONAL STORY INDICATORS
        # These phrases signal the author is sharing THEIR experience
        # Personal stories are inherently more unique than generic advice
        self.personal_indicators = [
            'my story',        # Explicit personal narrative
            'i remember',      # Memory/reflection
            'years ago',       # Temporal marker for personal history
            'when i was',      # Start of personal anecdote
            'i learned',       # Personal lesson
            'i discovered',    # Personal insight
            'i failed',        # Vulnerability/personal struggle
            'i succeeded',     # Personal achievement
            'my first',        # First-time experience
            'my experience',   # Explicit reference to personal experience
            'i worked at',     # Specific career detail
            'at my company'    # Specific organizational detail
        ]
        
        # ORIGINAL THOUGHT INDICATORS
        # These phrases suggest the author is expressing THEIR viewpoint
        # Not just repeating what others say
        self.originality_indicators = [
            'i believe',       # Personal belief/opinion
            'in my view',      # Explicit perspective marker
            'i\'ve found',     # Personal discovery
            'i\'ve noticed',   # Personal observation
            'my approach',     # Personal methodology
            'i developed',     # Created something original
            'i created',       # Made something new
            'i built'          # Built something from scratch
        ]
        
        # These will be populated when we analyze a full dataset
        # They're used for comparing posts against each other
        self.all_posts_text = []      # List of all post texts
        self.tfidf_matrix = None      # Mathematical representation for comparison
        self.vectorizer = None        # Tool for creating the comparison matrix
    
    def prepare_corpus(self, posts):
        """
        Prepare the entire dataset for similarity analysis.
        
        This is a crucial step that lets us compare each post against ALL other posts
        to see if it's saying something different.
        
        HOW IT WORKS:
        We use TF-IDF (Term Frequency-Inverse Document Frequency), which is a way to:
        1. Identify which words are important in each post
        2. Figure out which words are unique vs. common across all posts
        3. Represent each post as a mathematical vector
        4. Compare vectors to find similar posts
        
        Think of it like: if everyone uses the word "success", it's not distinctive.
        But if only YOU mention "cold email deliverability", that's unique.
        
        Parameters:
            posts (list): List of all post dictionaries from JSON
        """
        # Extract just the text from each post
        self.all_posts_text = [post.get('text', '') for post in posts]
        
        # CREATE TF-IDF MATRIX
        # This converts all posts into numbers we can compare mathematically
        self.vectorizer = TfidfVectorizer(
            max_features=500,      # Only look at the 500 most important words
            stop_words='english',  # Ignore common words like "the", "and", "is"
            ngram_range=(1, 2),    # Look at single words AND two-word phrases
            min_df=2               # Ignore words that appear in fewer than 2 posts
        )
        
        try:
            # Transform all posts into a mathematical matrix
            # Each row = one post, each column = one word/phrase
            # Numbers represent how important each word is to each post
            self.tfidf_matrix = self.vectorizer.fit_transform(self.all_posts_text)
        except:
            # If this fails (e.g., not enough posts), just skip similarity analysis
            self.tfidf_matrix = None
    
    def analyze_post(self, text, post_index=None):
        """
        This is the MAIN function that analyzes a single post for uniqueness.
        
        HOW IT WORKS:
        1. Check if post is long enough (minimum 30 characters)
        2. Calculate 4 component scores:
           - Personal Story (0-25 points): Does this share YOUR experience?
           - Original Thinking (0-25 points): Is this YOUR perspective?
           - Specificity (0-25 points): Are you specific or vague?
           - Similarity Score (0-25 points): How different from other posts?
        3. Apply penalties for generic/templated content
        4. Add everything up for final score out of 100
        
        Parameters:
            text (string): The LinkedIn post content
            post_index (int): Position of this post in the dataset (for comparison)
            
        Returns:
            Dictionary with total score and component breakdowns
        """
        
        # STEP 1: Validate post length
        if not text or len(text.strip()) < 30:
            return self._create_result(0, "Too short")
        
        # Convert to lowercase for easier pattern matching
        text_lower = text.lower()
        
        # STEP 2: Calculate the 4 component scores
        
        personal_score = self._score_personal_story(text, text_lower)
        # ^ Does this share personal experience and stories?
        
        originality_score = self._score_originality(text, text_lower)
        # ^ Does this express original thinking and perspective?
        
        specificity_score = self._score_specificity(text, text_lower)
        # ^ Is this specific with details, or vague and generic?
        
        similarity_score = self._score_similarity(post_index) if post_index is not None else 12.5
        # ^ How different is this from all other posts in the dataset?
        # If we can't calculate (no post_index), give average score
        
        # STEP 3: Calculate penalties
        penalties = self._calculate_penalties(text_lower)
        # ^ Deduct points for generic phrases and overused templates
        
        # STEP 4: Calculate total score
        total_score = max(0, personal_score + originality_score + specificity_score + similarity_score - penalties)
        
        # Normalize to 0-100
        normalized_score = min(100, total_score)
        
        # STEP 5: Return all results
        return {
            'total_score': round(normalized_score, 2),           # Main score
            'personal_story': round(personal_score, 2),          # Component 1
            'original_thinking': round(originality_score, 2),    # Component 2
            'specificity': round(specificity_score, 2),          # Component 3
            'uniqueness_vs_corpus': round(similarity_score, 2),  # Component 4
            'penalties': round(penalties, 2),                    # Deductions
            'classification': self._classify_uniqueness(normalized_score)  # Label
        }
    
    def _score_personal_story(self, text, text_lower):
        """
        PERSONAL STORY SCORING (0-25 points possible)
        
        This measures whether the post shares PERSONAL experiences and stories.
        
        Personal content is inherently more unique because:
        - Your story is yours alone
        - Your experiences are specific to you
        - Your journey is different from everyone else's
        
        We look for:
        - Personal pronouns (I, my, me)
        - Story indicators (i remember, years ago)
        - Time references (specific dates and timeframes)
        - Named entities (real people, companies, places)
        """
        score = 0  # Start at 0 and add points
        
        # PERSONAL PRONOUNS
        # Using "I", "my", "me" indicates personal perspective
        # Generic advice often uses "you" or "we" instead
        
        # Find all instances of personal pronouns
        # Example: "I learned", "my experience", "taught me"
        personal_pronouns = len(re.findall(r'\b(i|my|me|i\'m|i\'ve|i\'ll)\b', text_lower))
        
        # Award 0.3 points per pronoun, up to 6 points max
        # Many personal pronouns = definitely personal perspective
        score += min(6, personal_pronouns * 0.3)
        
        # PERSONAL STORY INDICATORS
        # These phrases explicitly signal storytelling
        # "I remember when...", "Years ago, I...", "My first job..."
        
        # Count how many personal story phrases appear
        personal_count = sum(1 for phrase in self.personal_indicators if phrase in text_lower)
        
        # Award 2.5 points per indicator, up to 8 points max
        score += min(8, personal_count * 2.5)
        
        # SPECIFIC TIME REFERENCES
        # Dates and timeframes make stories concrete and real
        # Examples: "2019", "3 years ago", "last month", "in 2020"
        
        # Find time references matching these patterns:
        # - Four-digit years: 2019, 2020, etc.
        # - "years ago", "months ago"
        # - "last [week/month/year/etc]"
        # - "in [year]"
        time_refs = len(re.findall(r'\b(20\d{2}|years? ago|months? ago|last \w+|in \d{4})\b', text_lower))
        
        # Award 2 points per time reference, up to 5 points max
        score += min(5, time_refs * 2)
        
        # NAMED ENTITIES (People, Companies, Places)
        # Real names make stories specific and credible
        # Generic posts say "my manager" - unique posts say "Sarah at Google"
        
        # HEURISTIC APPROACH (without complex NLP):
        # Look for capitalized words that AREN'T at the start of sentences
        # These are likely proper nouns (names, companies, places)
        
        # Split text into sentences
        sentences = text.split('. ')
        potential_entities = []
        
        # For each sentence EXCEPT the first (to skip sentence-starting caps)
        for sent in sentences[1:]:
            # Find capitalized words (including multi-word names like "San Francisco")
            caps_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sent)
            potential_entities.extend(caps_words)
        
        # Count unique entities (using set() to remove duplicates)
        # Award 0.8 points per unique entity, up to 6 points max
        score += min(6, len(set(potential_entities)) * 0.8)
        
        # Cap at 25 points for this section
        return min(25, score)
    
    def _score_originality(self, text, text_lower):
        """
        ORIGINAL THINKING SCORING (0-25 points possible)
        
        This measures whether the post expresses ORIGINAL thoughts and perspectives.
        
        Original thinking means:
        - Expressing YOUR viewpoint, not quoting others
        - Taking a contrarian or unexpected angle
        - Making people think with questions
        - Using sophisticated/specific vocabulary (not generic platitudes)
        
        Generic posts recycle common wisdom.
        Original posts make you go "Huh, I never thought of it that way."
        """
        score = 0  # Start at 0 and add points
        
        # ORIGINAL THOUGHT INDICATORS
        # These phrases signal the author is expressing THEIR perspective
        # "I believe...", "In my view...", "I've found..."
        
        # Count how many originality indicators appear
        orig_count = sum(1 for phrase in self.originality_indicators if phrase in text_lower)
        
        # Award 2.5 points per indicator, up to 8 points max
        score += min(8, orig_count * 2.5)
        
        # CONTRARIAN OR THOUGHT-PROVOKING STATEMENTS
        # These phrases signal the author is challenging conventional wisdom
        # or offering a different perspective
        
        contrarian_markers = [
            'contrary to',        # "Contrary to popular belief..."
            'unlike most',        # "Unlike most advice..."
            'different from',     # "Different from what you hear..."
            'instead of',         # "Instead of doing X, try Y"
            'rather than',        # "Rather than following the crowd..."
            'not what you think', # Signals surprise/counterintuition
            'surprisingly'        # Indicates unexpected insight
        ]
        
        # Count contrarian markers
        contrarian_count = sum(1 for marker in contrarian_markers if marker in text_lower)
        
        # Award 3 points per contrarian marker, up to 6 points max
        # Contrarian thinking is a strong signal of originality
        score += min(6, contrarian_count * 3)
        
        # QUESTION-POSING
        # Questions stimulate thinking and engagement
        # They show the author is exploring ideas, not just stating facts
        
        # Count question marks in the text
        questions = text.count('?')
        
        # Award 1.5 points per question, up to 5 points max
        score += min(5, questions * 1.5)
        
        # NOVEL COMBINATIONS (Sophisticated Vocabulary)
        # Using longer, more specific words often indicates:
        # - Domain expertise
        # - Precise thinking
        # - Less generic, more nuanced content
        
        # Find all words longer than 12 characters
        # Examples: "implementation", "counterintuitive", "orchestration"
        words = text_lower.split()
        rare_words = [w for w in words if len(w) > 12]
        
        # Award 0.8 points per long word, up to 6 points max
        score += min(6, len(rare_words) * 0.8)
        
        # Cap at 25 points for this section
        return min(25, score)
    
    def _score_specificity(self, text, text_lower):
        """
        SPECIFICITY SCORING (0-25 points possible)
        
        This measures whether the post is SPECIFIC or VAGUE.
        
        Specific = unique:
        - "I increased revenue by 47% using this 3-step framework"
        - "At Salesforce, we implemented a new onboarding process"
        
        Vague = generic:
        - "Success takes hard work"
        - "Companies should focus on customers"
        
        We look for:
        - Numbers and statistics (concrete data)
        - Company/product names (real examples)
        - Specific action verbs (what you actually DID)
        - Technical/sophisticated vocabulary
        """
        score = 0  # Start at 0 and add points
        
        # NUMBERS AND STATISTICS
        # Numbers make claims specific and credible
        # "40% increase" is more unique than "big increase"
        
        # Find all numbers, including those with % or $
        # Examples: "47%", "$2M", "150", "3x"
        numbers = re.findall(r'\b\d+[%$]?\b|\$\d+', text)
        
        # Award 1.5 points per number, up to 8 points max
        score += min(8, len(numbers) * 1.5)
        
        # COMPANY/PRODUCT NAMES
        # Mentioning real companies/products indicates real examples
        # "At Salesforce, we..." vs. "At my company, we..."
        
        # HEURISTIC: Look for CamelCase or branded terms
        # Examples: "LinkedIn", "SaaS", "HubSpot", "ChatGPT"
        # Pattern: Capital letter followed by lowercase, then another capital
        branded_terms = re.findall(r'\b[A-Z][a-z]+[A-Z]\w*\b', text)
        
        # Count unique branded terms (using set())
        # Award 2 points per unique term, up to 5 points max
        score += min(5, len(set(branded_terms)) * 2)
        
        # SPECIFIC ACTION VERBS
        # What you ACTUALLY DID is more specific than vague "work" or "help"
        # "Implemented" vs. "worked on"
        # "Architected" vs. "built"
        
        specific_actions = [
            'implemented',  # Specific execution
            'designed',     # Specific creation
            'architected',  # Specific technical work
            'optimized',    # Specific improvement
            'analyzed',     # Specific investigation
            'developed',    # Specific creation
            'launched',     # Specific milestone
            'scaled',       # Specific growth
            'built'         # Specific construction
        ]
        
        # Count how many specific action verbs appear
        action_count = sum(1 for action in specific_actions if action in text_lower)
        
        # Award 2 points per action verb, up to 6 points max
        score += min(6, action_count * 2)
        
        # TECHNICAL TERMS / JARGON (Word Length as Proxy)
        # Longer average word length often indicates:
        # - Domain expertise
        # - Technical/specific content
        # - Not dumbed-down generic advice
        
        # Calculate average word length
        word_lengths = [len(w) for w in text_lower.split()]
        avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
        
        # Award points based on average word length
        if avg_word_length > 5.5:
            score += 6  # Sophisticated vocabulary
        elif avg_word_length > 5.0:
            score += 4  # Above average vocabulary
        # Below 5.0 gets 0 points (simple vocabulary)
        
        # Cap at 25 points for this section
        return min(25, score)
    
    def _score_similarity(self, post_index):
        """
        SIMILARITY SCORING (0-25 points possible)
        
        This is the MOST SOPHISTICATED part of uniqueness detection.
        
        We compare this post against ALL OTHER POSTS in the dataset to see:
        - Is this saying something different?
        - Or is this just repeating what everyone else says?
        
        HOW IT WORKS:
        1. We've already converted all posts into mathematical vectors (in prepare_corpus)
        2. We calculate "cosine similarity" between this post and all others
        3. Low similarity = high uniqueness = more points
        4. High similarity = low uniqueness = fewer points
        
        COSINE SIMILARITY explained:
        - 0.0 = completely different posts (no common words/themes)
        - 1.0 = identical posts (same words/themes)
        - 0.3 = somewhat similar (overlap in topics/vocabulary)
        
        Parameters:
            post_index (int): Position of this post in the dataset
            
        Returns:
            Score from 0-25 based on how different this post is
        """
        
        # If we don't have the comparison matrix OR no post index, can't calculate
        if self.tfidf_matrix is None or post_index is None:
            return 12.5  # Return average score
        
        try:
            # GET SIMILARITY TO ALL OTHER POSTS
            
            # Extract this post's vector from the matrix
            post_vector = self.tfidf_matrix[post_index]
            
            # Calculate similarity between this post and EVERY other post
            # Returns an array of similarity scores (one per post)
            similarities = cosine_similarity(post_vector, self.tfidf_matrix).flatten()
            
            # REMOVE SELF-SIMILARITY
            # A post is always 100% similar to itself - that's not useful
            # So we remove that value from the array
            similarities = np.delete(similarities, post_index)
            
            # CALCULATE AVERAGE SIMILARITY
            # This tells us: on average, how similar is this post to all others?
            avg_similarity = np.mean(similarities)
            
            # CONVERT SIMILARITY TO UNIQUENESS SCORE
            # Remember: LOW similarity = HIGH uniqueness
            # So we flip the scale
            
            if avg_similarity < 0.1:
                score = 25  # Very unique - almost nothing like other posts
            elif avg_similarity < 0.2:
                score = 20  # Quite unique - low overlap
            elif avg_similarity < 0.3:
                score = 15  # Moderately unique - some overlap
            elif avg_similarity < 0.4:
                score = 10  # Somewhat generic - significant overlap
            else:
                score = 5   # Very generic - highly similar to many posts
            
            return score
            
        except:
            # If calculation fails for any reason, return average score
            return 12.5
    
    def _calculate_penalties(self, text_lower):
        """
        PENALTIES (0-15 points deducted)
        
        This identifies and penalizes generic/templated content.
        
        We penalize:
        - Generic phrase templates (overused opening lines)
        - Overused buzzwords (corporate jargon)
        - Generic quotes without attribution
        - Copy-paste indicators (credit:, source:, via:)
        
        These reduce uniqueness because they're recycled from others.
        """
        penalty = 0  # Start at 0 and add penalties
        
        # GENERIC PHRASE TEMPLATES
        # These are overused opening lines we've all seen 1000x
        # "I was scrolling through LinkedIn...", "Hot take:", etc.
        
        # Count how many generic phrases appear
        generic_count = sum(1 for phrase in self.generic_phrases if phrase in text_lower)
        
        # Deduct 3 points per generic phrase
        penalty += generic_count * 3
        
        # OVERUSED BUZZWORDS
        # Corporate jargon that's been beaten to death
        # These make posts sound like everyone else
        
        buzzwords = [
            'game changer',        # Extremely overused
            'game-changer',        # Same as above
            'paradigm shift',      # Corporate cliché
            'disrupt',             # Overused in tech
            'synergy',             # Classic corporate nonsense
            'leverage',            # Often misused
            'circle back',         # Corporate meeting-speak
            'low hanging fruit',   # Overused metaphor
            'move the needle',     # Overused impact phrase
            'think outside the box' # Peak generic advice
        ]
        
        # Count buzzwords
        buzzword_count = sum(1 for buzz in buzzwords if buzz in text_lower)
        
        # Deduct 2 points per buzzword
        penalty += buzzword_count * 2
        
        # GENERIC MOTIVATIONAL QUOTES WITHOUT ATTRIBUTION
        # Short posts with quotes but no "said" (no attribution)
        # These are often recycled inspirational quotes
        # Example: "Success is a journey, not a destination" (no source)
        
        has_quotes = '"' in text_lower
        no_attribution = 'said' not in text_lower
        is_short = len(text_lower) < 200
        
        if has_quotes and no_attribution and is_short:
            penalty += 3  # Likely a recycled quote
        
        # COPY-PASTE INDICATORS
        # These words explicitly signal reposted content
        # "Credit: [someone]", "Source: [somewhere]", "Via: [link]"
        
        if 'credit:' in text_lower or 'source:' in text_lower or 'via:' in text_lower:
            penalty += 4  # This is literally someone else's content
        
        # Cap penalties at 15 points max
        return min(15, penalty)
    
    def _classify_uniqueness(self, score):
        """
        Convert numeric score to a text label for easier understanding.
        
        This helps people quickly grasp what the score means:
        - 80+: Highly Unique (rare, truly original)
        - 65-79: Very Unique (strong originality)
        - 50-64: Moderately Unique (some originality)
        - 35-49: Somewhat Generic (mostly recycled)
        - <35: Very Generic (cookie-cutter templates)
        """
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
        """
        Helper function to create a result dictionary with default values.
        
        Used when a post is too short to analyze properly.
        """
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
    """
    Analyze every post in a JSON file for uniqueness.
    
    This function:
    1. Loads the JSON file
    2. Creates a UniquenessDetector
    3. Prepares the corpus (for post-to-post comparison)
    4. Analyzes each post
    5. Returns results with scores and metadata
    
    Parameters:
        json_file_path (string): Path to the JSON file
        
    Returns:
        List of dictionaries with uniqueness scores for each post
    """
    
    # Create a new UniquenessDetector
    detector = UniquenessDetector()
    
    # Load the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    # PREPARE CORPUS FOR SIMILARITY ANALYSIS
    # This is crucial - it lets us compare posts against each other
    print("   Preparing corpus for similarity analysis...")
    detector.prepare_corpus(posts)
    
    # Create empty list for results
    results = []
    
    # Loop through each post with its index
    # We need the index (i) to compare this post against others
    for i, post in enumerate(posts):
        # Extract text and author info
        text = post.get('text', '')
        author = post.get('author', {})
        
        # Analyze this post's uniqueness
        # Pass the index so we can compare against other posts
        analysis = detector.analyze_post(text, post_index=i)
        
        # Combine analysis with metadata
        results.append({
            # Author information
            'author_name': f"{author.get('first_name', '')} {author.get('last_name', '')}".strip(),
            'username': author.get('username', ''),
            'post_url': post.get('url', ''),
            
            # Text preview
            'text_preview': text[:100] + '...' if len(text) > 100 else text,
            'word_count': len(text.split()),
            
            # Spread analysis results into this dictionary
            **analysis
        })
    
    return results


# MAIN EXECUTION BLOCK
# This runs only if you execute this file directly
if __name__ == "__main__":
    print("🦄 ALGORITHM 3: UNIQUENESS DETECTION")
    print("=" * 80)
    
    # Path to input data
    input_file = "/mnt/user-data/uploads/dataset_linkedin-batch-profile-posts-scraper_2025-11-04_02-03-34-812.json"
    
    print("\nDetecting uniqueness across all posts...")
    
    # Analyze all posts
    results = analyze_all_posts(input_file)
    
    # Sort by score (highest first)
    results_sorted = sorted(results, key=lambda x: x['total_score'], reverse=True)
    
    # Display top 10 most unique posts
    print("\n🏆 TOP 10 MOST UNIQUE POSTS:")
    print("-" * 80)
    for i, result in enumerate(results_sorted[:10], 1):
        print(f"\n{i}. {result['author_name']} (@{result['username']})")
        print(f"   Score: {result['total_score']}/100 - {result['classification']}")
        print(f"   Breakdown: Personal={result['personal_story']}, "
              f"Original={result['original_thinking']}, Specific={result['specificity']}, "
              f"Unique vs Corpus={result['uniqueness_vs_corpus']}")
        print(f"   Preview: {result['text_preview']}")
    
    # Print summary statistics
    print("\n\n✅ Uniqueness detection complete!")
    print(f"📊 Analyzed {len(results)} posts")
    print(f"📈 Average uniqueness score: {sum(r['total_score'] for r in results) / len(results):.2f}/100")
    
    # Save results to CSV
    import csv
    output_file = "/mnt/user-data/outputs/uniqueness_scores_commented.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        # Define CSV columns
        fieldnames = ['author_name', 'username', 'post_url', 'total_score', 'classification',
                     'word_count', 'personal_story', 'original_thinking', 'specificity',
                     'uniqueness_vs_corpus', 'penalties']
        
        # Create CSV writer
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write each result as a row
        for result in results_sorted:
            writer.writerow({k: v for k, v in result.items() if k in fieldnames})
    
    print(f"💾 Results saved to: {output_file}")