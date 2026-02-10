"""
Series Architect - Benchmark Module

Compares our recommendation engine with TMDB's Similar API.
Helps validate that our algorithm produces reasonable results.
"""

import sys
import os
import requests
import time

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

from data_layer.db_utils import fetch_query
from data_layer.etl_processor import HEADERS

try:
    from .recommender import get_recommendations
    from .similarity_engine import find_most_similar
    from .filters import get_all_series_ids
except ImportError:
    from recommender import get_recommendations
    from similarity_engine import find_most_similar
    from filters import get_all_series_ids


# =====================================
# TMDB Similar API
# =====================================

def get_tmdb_similar(tmdb_id, limit=10):
    """
    Get similar series from TMDB API.
    
    Args:
        tmdb_id: Series ID
        limit: Number of results
    
    Returns:
        list: List of similar series IDs from TMDB
    """
    url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/similar"
    params = {
        "language": "en-US",
        "page": 1
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        
        results = response.json().get('results', [])
        similar_ids = [s['id'] for s in results[:limit]]
        
        return similar_ids
    
    except Exception as e:
        print(f"Error fetching TMDB similar for {tmdb_id}: {e}")
        return []


# =====================================
# Benchmark Functions
# =====================================

def calculate_overlap(our_recommendations, tmdb_recommendations):
    """
    Calculate overlap between our recommendations and TMDB's.
    
    Args:
        our_recommendations: List of tmdb_ids
        tmdb_recommendations: List of tmdb_ids
    
    Returns:
        dict: Overlap statistics
    """
    our_set = set(our_recommendations)
    tmdb_set = set(tmdb_recommendations)
    
    overlap = our_set & tmdb_set
    overlap_count = len(overlap)
    overlap_percentage = (overlap_count / len(tmdb_set) * 100) if tmdb_set else 0
    
    return {
        'overlap_count': overlap_count,
        'overlap_percentage': round(overlap_percentage, 1),
        'our_total': len(our_set),
        'tmdb_total': len(tmdb_set),
        'matching_series': list(overlap)
    }


def benchmark_single_series(tmdb_id, top_n=10):
    """
    Benchmark recommendations for a single series.
    
    Compares:
    - Our find_most_similar() vs TMDB Similar API
    
    Args:
        tmdb_id: Series to test
        top_n: Number of recommendations
    
    Returns:
        dict: Benchmark results
    """
    print(f"\n{'='*60}")
    print(f"Benchmarking Series ID: {tmdb_id}")
    print(f"{'='*60}")
    
    # Get series name
    query = "SELECT title_en FROM series WHERE tmdb_id = %s"
    result = fetch_query(query, (tmdb_id,))
    series_name = result[0][0] if result else "Unknown"
    
    print(f"Series: {series_name}")
    
    # Get all series IDs as candidates
    candidate_ids = get_all_series_ids()
    
    # Our recommendations
    print(f"\nCalculating our recommendations...")
    our_recs = find_most_similar(tmdb_id, candidate_ids, top_n=top_n)
    our_ids = [rec[0] for rec in our_recs]
    
    # TMDB recommendations
    print(f"Fetching TMDB similar series...")
    tmdb_ids = get_tmdb_similar(tmdb_id, limit=top_n)
    
    # Calculate overlap
    overlap = calculate_overlap(our_ids, tmdb_ids)
    
    # Print results
    print(f"\n--- Results ---")
    print(f"Our recommendations: {len(our_ids)}")
    print(f"TMDB recommendations: {len(tmdb_ids)}")
    print(f"Overlap: {overlap['overlap_count']}/{top_n} ({overlap['overlap_percentage']}%)")
    
    if overlap['matching_series']:
        print(f"\nMatching series IDs: {overlap['matching_series']}")
    
    # Get names for comparison
    print(f"\n--- Our Top {top_n} ---")
    for i, (rec_id, score) in enumerate(our_recs, 1):
        query = "SELECT title_en FROM series WHERE tmdb_id = %s"
        result = fetch_query(query, (rec_id,))
        name = result[0][0] if result else "Unknown"
        match = "✓" if rec_id in tmdb_ids else " "
        print(f"{i}. [{match}] {name} (score: {score:.3f})")
    
    print(f"\n--- TMDB Top {top_n} ---")
    for i, rec_id in enumerate(tmdb_ids, 1):
        query = "SELECT title_en FROM series WHERE tmdb_id = %s"
        result = fetch_query(query, (rec_id,))
        name = result[0][0] if result else "Unknown"
        match = "✓" if rec_id in our_ids else " "
        print(f"{i}. [{match}] {name}")
    
    return {
        'series_id': tmdb_id,
        'series_name': series_name,
        'our_recommendations': our_ids,
        'tmdb_recommendations': tmdb_ids,
        'overlap': overlap
    }


def benchmark_user_recommendations(user_ratings, filters=None, top_n=10):
    """
    Benchmark user-based recommendations.
    
    This is harder to compare to TMDB since TMDB doesn't have
    a "based on multiple likes" endpoint, but we can still
    check if our recommendations make sense.
    
    Args:
        user_ratings: List of (tmdb_id, rating, is_anchor) tuples
        filters: Filter dict
        top_n: Number of recommendations
    
    Returns:
        dict: Benchmark results
    """
    print(f"\n{'='*60}")
    print(f"Benchmarking User-Based Recommendations")
    print(f"{'='*60}")
    
    # Get liked series names
    print(f"\nUser's Liked Series:")
    liked_series = []
    for rating_tuple in user_ratings:
        tmdb_id = rating_tuple[0]
        rating = rating_tuple[1]
        is_anchor = rating_tuple[2] if len(rating_tuple) > 2 else False
        
        if rating == 1:  # Like
            query = "SELECT title_en FROM series WHERE tmdb_id = %s"
            result = fetch_query(query, (tmdb_id,))
            name = result[0][0] if result else "Unknown"
            anchor_mark = " (ANCHOR)" if is_anchor else ""
            print(f"  👍 {name}{anchor_mark}")
            liked_series.append(name)
    
    # Get our recommendations
    print(f"\nCalculating recommendations...")
    recommendations = get_recommendations(user_ratings, filters, top_n=top_n)
    
    print(f"\n--- Our Top {top_n} Recommendations ---")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title_en']}")
        print(f"   Score: {rec['score']:.3f}")
        print(f"   Genres: {', '.join(rec['genres'])}")
        print(f"   Year: {rec['first_air_date'][:4] if rec['first_air_date'] else 'N/A'}")
        print()
    
    # For each liked series, show TMDB similar and check overlap
    print(f"\n--- TMDB Similar to Each Liked Series ---")
    all_tmdb_suggestions = set()
    
    for rating_tuple in user_ratings:
        if rating_tuple[1] == 1:  # Like only
            tmdb_id = rating_tuple[0]
            query = "SELECT title_en FROM series WHERE tmdb_id = %s"
            result = fetch_query(query, (tmdb_id,))
            name = result[0][0] if result else "Unknown"
            
            tmdb_similar = get_tmdb_similar(tmdb_id, limit=5)
            all_tmdb_suggestions.update(tmdb_similar)
            
            print(f"\nSimilar to '{name}':")
            for sim_id in tmdb_similar[:3]:
                query = "SELECT title_en FROM series WHERE tmdb_id = %s"
                result = fetch_query(query, (sim_id,))
                sim_name = result[0][0] if result else "Unknown"
                print(f"  - {sim_name}")
            
            time.sleep(0.3)  # Rate limiting
    
    # Check overlap with TMDB suggestions
    our_ids = [rec['tmdb_id'] for rec in recommendations]
    overlap = calculate_overlap(our_ids, list(all_tmdb_suggestions))
    
    print(f"\n--- Overall Overlap with TMDB Suggestions ---")
    print(f"Our recommendations: {len(our_ids)}")
    print(f"TMDB suggestions (combined): {len(all_tmdb_suggestions)}")
    print(f"Overlap: {overlap['overlap_count']} ({overlap['overlap_percentage']}%)")
    
    return {
        'liked_series': liked_series,
        'recommendations': recommendations,
        'tmdb_suggestions': list(all_tmdb_suggestions),
        'overlap': overlap
    }


def run_benchmark_suite():
    """
    Run a suite of benchmark tests on popular series.
    
    Tests our algorithm against TMDB Similar API on well-known series.
    """
    print("\n" + "="*60)
    print("RUNNING BENCHMARK SUITE")
    print("="*60)
    
    # Test cases: well-known series
    test_cases = [
        (1396, "Breaking Bad"),
        (60059, "Better Call Saul"),
        (1399, "Game of Thrones"),
        (1668, "Friends"),
        (1408, "House")
    ]
    
    results = []
    total_overlap = 0
    
    for tmdb_id, expected_name in test_cases:
        # Verify series exists in our DB
        query = "SELECT title_en FROM series WHERE tmdb_id = %s"
        result = fetch_query(query, (tmdb_id,))
        
        if not result:
            print(f"\n⚠️  Skipping {expected_name} (ID: {tmdb_id}) - not in database")
            continue
        
        # Run benchmark
        benchmark_result = benchmark_single_series(tmdb_id, top_n=10)
        results.append(benchmark_result)
        
        total_overlap += benchmark_result['overlap']['overlap_percentage']
        
        time.sleep(0.5)  # Rate limiting for TMDB API
    
    # Calculate average overlap
    if results:
        avg_overlap = total_overlap / len(results)
        
        print(f"\n{'='*60}")
        print(f"BENCHMARK SUMMARY")
        print(f"{'='*60}")
        print(f"Tests run: {len(results)}")
        print(f"Average overlap with TMDB: {avg_overlap:.1f}%")
        print(f"\nInterpretation:")
        if avg_overlap >= 50:
            print("  ✅ Excellent! High agreement with TMDB")
        elif avg_overlap >= 30:
            print("  ✅ Good! Reasonable agreement with TMDB")
        elif avg_overlap >= 20:
            print("  ⚠️  Fair. Some differences from TMDB")
        else:
            print("  ❌ Low agreement. Algorithm may need tuning")
        
        print(f"\nNote: TMDB uses collaborative filtering (user behavior)")
        print(f"      We use content-based filtering (series features)")
        print(f"      30-50% overlap is expected and healthy!")
    
    return results


# =====================================
# Main Execution
# =====================================

if __name__ == "__main__":
    print("\nSeries Architect - Benchmark Tool")
    print("=" * 60)
    
    # Option 1: Run full benchmark suite
    print("\n1. Run full benchmark suite")
    print("2. Benchmark single series")
    print("3. Benchmark user recommendations")
    
    choice = input("\nSelect option (1/2/3): ").strip()
    
    if choice == "1":
        run_benchmark_suite()
    
    elif choice == "2":
        tmdb_id = int(input("Enter series TMDB ID: ").strip())
        benchmark_single_series(tmdb_id)
    
    elif choice == "3":
        print("\nExample user ratings:")
        print("  (1396, 1, True)   # Breaking Bad - Like (Anchor)")
        print("  (60059, 1, False) # Better Call Saul - Like")
        print("  (1668, -1, False) # Friends - Dislike")
        
        user_ratings = [
            (1396, 1, True),
            (60059, 1, False),
            (1408, 1, False),
            (1668, -1, False)
        ]
        
        benchmark_user_recommendations(user_ratings)
    
    else:
        print("Invalid choice")
