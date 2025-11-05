#!/usr/bin/env python3
"""
MASTER CONTENT ANALYSIS SYSTEM
Runs all three algorithms and creates comprehensive scoring
"""

import json
import csv
from substance_detector import SubstanceDetector
from quality_assessor import QualityAssessor
from uniqueness_detector import UniquenessDetector

def analyze_all_content(json_file_path):
    """Run all three algorithms and combine results"""
    
    print("\n" + "="*80)
    print("🚀 COMPREHENSIVE LINKEDIN CONTENT ANALYSIS SYSTEM")
    print("="*80)
    
    # Load data
    print("\n📂 Loading data...")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    print(f"   ✓ Loaded {len(posts)} posts")
    
    # Initialize detectors
    print("\n🔧 Initializing analysis engines...")
    substance_detector = SubstanceDetector()
    quality_assessor = QualityAssessor()
    uniqueness_detector = UniquenessDetector()
    
    # Prepare uniqueness corpus
    print("   ✓ Preparing uniqueness corpus...")
    uniqueness_detector.prepare_corpus(posts)
    
    # Analyze all posts
    print("\n🔍 Analyzing posts...")
    all_results = []
    
    for i, post in enumerate(posts):
        if (i + 1) % 500 == 0:
            print(f"   Progress: {i + 1}/{len(posts)} posts analyzed...")
        
        text = post.get('text', '')
        author = post.get('author', {})
        stats = post.get('stats', {})
        
        # Run all three algorithms
        substance = substance_detector.analyze_post(text)
        quality = quality_assessor.analyze_post(text)
        uniqueness = uniqueness_detector.analyze_post(text, post_index=i)
        
        # Calculate composite score (weighted average)
        composite_score = (
            substance['total_score'] * 0.35 +  # 35% weight
            quality['total_score'] * 0.30 +     # 30% weight
            uniqueness['total_score'] * 0.35    # 35% weight
        )
        
        # Combine all results
        result = {
            # Author info
            'author_name': f"{author.get('first_name', '')} {author.get('last_name', '')}".strip(),
            'username': author.get('username', ''),
            'post_url': post.get('url', ''),
            'post_date': post.get('posted_at', {}).get('date', ''),
            
            # Text info
            'word_count': len(text.split()),
            'text_preview': text[:150] + '...' if len(text) > 150 else text,
            
            # Engagement metrics
            'likes': stats.get('total_reactions', 0),
            'comments': stats.get('comments', 0),
            'reposts': stats.get('reposts', 0),
            'engagement_total': stats.get('total_reactions', 0) + stats.get('comments', 0) + stats.get('reposts', 0),
            
            # Composite score
            'composite_score': round(composite_score, 2),
            
            # Algorithm 1: Substance
            'substance_score': substance['total_score'],
            'substance_classification': substance['classification'],
            'info_density': substance['information_density'],
            'depth': substance['depth_score'],
            'value_indicators': substance['value_indicators'],
            
            # Algorithm 2: Quality
            'quality_score': quality['total_score'],
            'quality_classification': quality['classification'],
            'readability': quality['readability'],
            'structure': quality['structure'],
            'professionalism': quality['professionalism'],
            'readability_grade': quality['readability_grade'],
            
            # Algorithm 3: Uniqueness
            'uniqueness_score': uniqueness['total_score'],
            'uniqueness_classification': uniqueness['classification'],
            'personal_story': uniqueness['personal_story'],
            'original_thinking': uniqueness['original_thinking'],
            'specificity': uniqueness['specificity'],
            'uniqueness_vs_corpus': uniqueness['uniqueness_vs_corpus']
        }
        
        all_results.append(result)
    
    print(f"   ✓ Analyzed all {len(posts)} posts!")
    
    return all_results


def generate_reports(results):
    """Generate comprehensive reports"""
    
    print("\n📊 GENERATING REPORTS...")
    print("-" * 80)
    
    # Sort by composite score
    results_sorted = sorted(results, key=lambda x: x['composite_score'], reverse=True)
    
    # 1. Overall Statistics
    print("\n📈 OVERALL STATISTICS:")
    print(f"   Total Posts Analyzed: {len(results)}")
    print(f"   Average Composite Score: {sum(r['composite_score'] for r in results) / len(results):.2f}/100")
    print(f"   Average Substance Score: {sum(r['substance_score'] for r in results) / len(results):.2f}/100")
    print(f"   Average Quality Score: {sum(r['quality_score'] for r in results) / len(results):.2f}/100")
    print(f"   Average Uniqueness Score: {sum(r['uniqueness_score'] for r in results) / len(results):.2f}/100")
    
    # 2. Top 10 Overall Posts
    print("\n\n🏆 TOP 10 POSTS (COMPOSITE SCORE):")
    print("-" * 80)
    for i, result in enumerate(results_sorted[:10], 1):
        print(f"\n{i}. {result['author_name']} (@{result['username']})")
        print(f"   🎯 Composite: {result['composite_score']}/100")
        print(f"   📊 Substance: {result['substance_score']}/100 ({result['substance_classification']})")
        print(f"   ✍️  Quality: {result['quality_score']}/100 ({result['quality_classification']})")
        print(f"   🦄 Uniqueness: {result['uniqueness_score']}/100 ({result['uniqueness_classification']})")
        print(f"   💬 Engagement: {result['engagement_total']:,} (👍{result['likes']} 💬{result['comments']} 🔄{result['reposts']})")
        print(f"   🔗 {result['post_url']}")
    
    # 3. Best in each category
    print("\n\n🎖️  CATEGORY LEADERS:")
    print("-" * 80)
    
    best_substance = max(results, key=lambda x: x['substance_score'])
    print(f"\n🔬 Highest Substance: {best_substance['author_name']}")
    print(f"   Score: {best_substance['substance_score']}/100")
    print(f"   {best_substance['post_url']}")
    
    best_quality = max(results, key=lambda x: x['quality_score'])
    print(f"\n✨ Highest Quality: {best_quality['author_name']}")
    print(f"   Score: {best_quality['quality_score']}/100")
    print(f"   {best_quality['post_url']}")
    
    best_uniqueness = max(results, key=lambda x: x['uniqueness_score'])
    print(f"\n💎 Most Unique: {best_uniqueness['author_name']}")
    print(f"   Score: {best_uniqueness['uniqueness_score']}/100")
    print(f"   {best_uniqueness['post_url']}")
    
    # 4. Engagement vs. Content Quality Analysis
    print("\n\n📊 ENGAGEMENT VS. CONTENT QUALITY:")
    print("-" * 80)
    
    # Find posts with high scores but low engagement
    high_quality_low_engagement = [
        r for r in results 
        if r['composite_score'] > 70 and r['engagement_total'] < 200
    ][:5]
    
    if high_quality_low_engagement:
        print("\n💎 Hidden Gems (High Quality, Low Engagement):")
        for post in high_quality_low_engagement:
            print(f"   • {post['author_name']}: {post['composite_score']:.0f} score, {post['engagement_total']} engagement")
    
    # Find posts with high engagement
    high_engagement = sorted(results, key=lambda x: x['engagement_total'], reverse=True)[:5]
    print("\n🔥 Most Engaged Posts:")
    for post in high_engagement:
        print(f"   • {post['author_name']}: {post['engagement_total']:,} engagement, {post['composite_score']:.0f} quality score")
    
    # 5. Save comprehensive CSV
    print("\n\n💾 SAVING RESULTS...")
    
    # Main comprehensive report
    output_file = "/mnt/user-data/outputs/comprehensive_analysis.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'author_name', 'username', 'post_url', 'post_date', 'word_count',
            'composite_score', 
            'substance_score', 'substance_classification',
            'quality_score', 'quality_classification',
            'uniqueness_score', 'uniqueness_classification',
            'likes', 'comments', 'reposts', 'engagement_total',
            'info_density', 'depth', 'value_indicators',
            'readability', 'structure', 'professionalism', 'readability_grade',
            'personal_story', 'original_thinking', 'specificity', 'uniqueness_vs_corpus'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results_sorted:
            writer.writerow({k: v for k, v in result.items() if k in fieldnames})
    
    print(f"   ✓ Comprehensive analysis: {output_file}")
    
    # Author summary
    author_summary = {}
    for result in results:
        author = result['author_name']
        if author not in author_summary:
            author_summary[author] = {
                'username': result['username'],
                'post_count': 0,
                'avg_composite': 0,
                'avg_substance': 0,
                'avg_quality': 0,
                'avg_uniqueness': 0,
                'total_engagement': 0
            }
        
        author_summary[author]['post_count'] += 1
        author_summary[author]['avg_composite'] += result['composite_score']
        author_summary[author]['avg_substance'] += result['substance_score']
        author_summary[author]['avg_quality'] += result['quality_score']
        author_summary[author]['avg_uniqueness'] += result['uniqueness_score']
        author_summary[author]['total_engagement'] += result['engagement_total']
    
    # Calculate averages
    for author in author_summary:
        count = author_summary[author]['post_count']
        author_summary[author]['avg_composite'] = round(author_summary[author]['avg_composite'] / count, 2)
        author_summary[author]['avg_substance'] = round(author_summary[author]['avg_substance'] / count, 2)
        author_summary[author]['avg_quality'] = round(author_summary[author]['avg_quality'] / count, 2)
        author_summary[author]['avg_uniqueness'] = round(author_summary[author]['avg_uniqueness'] / count, 2)
    
    # Save author summary
    author_file = "/mnt/user-data/outputs/author_summary.csv"
    with open(author_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['author_name', 'username', 'post_count', 'avg_composite', 
                     'avg_substance', 'avg_quality', 'avg_uniqueness', 'total_engagement']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        author_list = [
            {'author_name': name, **data} 
            for name, data in author_summary.items()
        ]
        author_list_sorted = sorted(author_list, key=lambda x: x['avg_composite'], reverse=True)
        
        for author in author_list_sorted:
            writer.writerow(author)
    
    print(f"   ✓ Author summary: {author_file}")
    
    print("\n\n" + "="*80)
    print("✅ ANALYSIS COMPLETE!")
    print("="*80)
    print("\n📁 Output Files Created:")
    print("   1. comprehensive_analysis.csv - Detailed analysis of every post")
    print("   2. author_summary.csv - Aggregated scores by author")
    print("   3. substance_scores.csv - Substance algorithm results")
    print("   4. quality_scores.csv - Quality algorithm results")
    print("   5. uniqueness_scores.csv - Uniqueness algorithm results")
    print("\n")


if __name__ == "__main__":
    input_file = "/mnt/user-data/uploads/dataset_linkedin-batch-profile-posts-scraper_2025-11-04_02-03-34-812.json"
    
    # Run comprehensive analysis
    results = analyze_all_content(input_file)
    
    # Generate reports
    generate_reports(results)
    