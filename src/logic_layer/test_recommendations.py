"""
Series Architect - Quick Test Script

Simple script for manual testing of the recommendation engine.
No benchmarking, just quick results to verify everything works.
"""

import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

from recommender import get_recommendations, search_series, get_popular_series


# =====================================
# Test Scenarios
# =====================================

def test_crime_drama_fan():
    """
    Test: User who likes crime dramas.
    Expected: More crime/drama recommendations.
    """
    print("\n" + "="*60)
    print("TEST 1: Crime Drama Fan")
    print("="*60)
    
    user_ratings = [
        (1396, 1, True),   # Breaking Bad - Like (Anchor)
        (60059, 1, False), # Better Call Saul - Like
        (1408, 1, False),  # House - Like
        (1412, 1, False),  # The Sopranos - Like
        (46952, 1, False), # The Blacklist - Like
        (1668, -1, False), # Friends - Dislike
        (1402, -1, False), # The Walking Dead - Dislike
        (1404, -1, False), # Supernatural - Dislike
        (60735, -1, False), # The Flash - Dislike
        (1399, -1, False)  # Game of Thrones - Dislike
    ]
    
    filters = {
        'languages': ['en'],
        'status': None,  # Any status
        'decades': [2000, 2010, 2020],
        'genres': [18, 80]  # Drama, Crime
    }
    
    print("\n👤 User Profile:")
    print("  Likes: Breaking Bad (anchor), Better Call Saul, House, The Sopranos, The Blacklist")
    print("  Dislikes: Friends, TWD, Supernatural, The Flash, GoT")
    
    print("\n🎛️  Filters:")
    print("  Language: English")
    print("  Decades: 2000s, 2010s, 2020s")
    print("  Genres: Drama, Crime")
    
    recommendations = get_recommendations(user_ratings, filters, top_n=10)
    
    print("\n🎯 Top 10 Recommendations:")
    print_recommendations(recommendations)
    
    return recommendations


def test_diverse_taste():
    """
    Test: User with diverse taste (different genres).
    Expected: Varied recommendations.
    """
    print("\n" + "="*60)
    print("TEST 2: Diverse Taste")
    print("="*60)
    
    user_ratings = [
        (1396, 1, False),  # Breaking Bad - Drama/Crime
        (1668, 1, False),  # Friends - Comedy
        (1399, 1, True),   # Game of Thrones - Fantasy (Anchor)
        (60735, 1, False), # The Flash - Sci-Fi
        (46648, 1, False), # Mindhunter - Crime
        (1408, 1, False),  # House - Medical Drama
        (100, -1, False),  # I Am Not Okay - Dislike
        (76479, -1, False), # The Boys - Dislike
        (84958, -1, False), # Loki - Dislike
        (71712, -1, False)  # The Good Doctor - Dislike
    ]
    
    filters = {
        'languages': ['en'],
        'status': None,
        'decades': None,
        'genres': None  # No genre filter - let diversity show
    }
    
    print("\n👤 User Profile:")
    print("  Likes: Breaking Bad, Friends, GoT (anchor), The Flash, Mindhunter, House")
    print("  Dislikes: I Am Not Okay, The Boys, Loki, The Good Doctor")
    
    print("\n🎛️  Filters:")
    print("  Language: English")
    print("  No other filters (show diversity)")
    
    recommendations = get_recommendations(user_ratings, filters, top_n=10)
    
    print("\n🎯 Top 10 Recommendations:")
    print_recommendations(recommendations)
    
    return recommendations


def test_anime_fan():
    """
    Test: User who likes Japanese anime.
    Expected: More anime recommendations.
    """
    print("\n" + "="*60)
    print("TEST 3: Anime Fan")
    print("="*60)
    
    # Get some Japanese series for testing
    print("\nSearching for Japanese series...")
    
    user_ratings = [
        (1429, 1, True),   # Attack on Titan - Like (Anchor) - if exists
        (37854, 1, False), # One Punch Man - Like
        (60572, 1, False), # My Hero Academia - Like
        (46260, 1, False), # Demon Slayer - Like
        (85937, 1, False), # Demon Slayer Season 2 - Like
        (1668, -1, False), # Friends - Dislike
        (1396, -1, False), # Breaking Bad - Dislike
        (1399, -1, False), # Game of Thrones - Dislike
        (1408, -1, False), # House - Dislike
        (60059, -1, False) # Better Call Saul - Dislike
    ]
    
    filters = {
        'languages': ['ja'],
        'status': None,
        'decades': [2010, 2020],
        'genres': [16]  # Animation
    }
    
    print("\n👤 User Profile:")
    print("  Likes: Attack on Titan (anchor), One Punch Man, MHA, Demon Slayer")
    print("  Dislikes: Friends, Breaking Bad, GoT, House, BCS")
    
    print("\n🎛️  Filters:")
    print("  Language: Japanese")
    print("  Decades: 2010s, 2020s")
    print("  Genres: Animation")
    
    recommendations = get_recommendations(user_ratings, filters, top_n=10)
    
    print("\n🎯 Top 10 Recommendations:")
    print_recommendations(recommendations)
    
    return recommendations


def test_minimal_filters():
    """
    Test: Minimal filtering, let the algorithm work.
    """
    print("\n" + "="*60)
    print("TEST 4: Minimal Filters (Algorithm-Driven)")
    print("="*60)
    
    user_ratings = [
        (1396, 1, True),   # Breaking Bad - Anchor
        (60059, 1, False), # Better Call Saul
        (1399, 1, False),  # Game of Thrones
        (1668, 1, False),  # Friends
        (1408, 1, False),  # House
        (100, -1, False),  # Dislike
        (200, -1, False),  # Dislike
        (300, -1, False),  # Dislike
        (400, -1, False),  # Dislike
        (500, -1, False)   # Dislike
    ]
    
    filters = {
        'languages': None,  # Any language
        'status': None,     # Any status
        'decades': None,    # Any decade
        'genres': None      # Any genre
    }
    
    print("\n👤 User Profile:")
    print("  Likes: Breaking Bad (anchor), BCS, GoT, Friends, House")
    print("  Dislikes: 5 random series")
    
    print("\n🎛️  Filters:")
    print("  No filters - pure algorithm!")
    
    recommendations = get_recommendations(user_ratings, filters, top_n=10)
    
    print("\n🎯 Top 10 Recommendations:")
    print_recommendations(recommendations)
    
    return recommendations


# =====================================
# Helper Functions
# =====================================

def print_recommendations(recommendations):
    """Print recommendations in a nice format."""
    if not recommendations:
        print("  ❌ No recommendations generated!")
        return
    
    for i, rec in enumerate(recommendations, 1):
        year = rec['first_air_date'][:4] if rec['first_air_date'] else 'N/A'
        genres = ', '.join(rec['genres'][:3])  # First 3 genres
        
        print(f"\n  {i}. {rec['title_en']} ({year})")
        print(f"     Score: {rec['score']:.3f} | {genres}")
        print(f"     Status: {rec['status']} | Seasons: {rec['number_of_seasons']}")


def interactive_test():
    """
    Interactive testing - let user build their own test.
    """
    print("\n" + "="*60)
    print("INTERACTIVE TEST MODE")
    print("="*60)
    
    print("\nSearch for series to rate:")
    
    user_ratings = []
    
    while len(user_ratings) < 10:
        query = input(f"\nSearch ({len(user_ratings)}/10, or 'done'): ").strip()
        
        if query.lower() == 'done':
            if len(user_ratings) >= 10:
                break
            else:
                print(f"Need at least 10 ratings! (currently: {len(user_ratings)})")
                continue
        
        results = search_series(query, limit=5)
        
        if not results:
            print("No results found.")
            continue
        
        print("\nResults:")
        for i, series in enumerate(results, 1):
            year = series['first_air_date'][:4] if series['first_air_date'] else 'N/A'
            print(f"  {i}. {series['title_en']} ({year})")
        
        try:
            choice = int(input("Select (1-5, or 0 to skip): ").strip())
            if choice == 0:
                continue
            if 1 <= choice <= len(results):
                series = results[choice - 1]
                rating = int(input("Rate: 1 (like) / -1 (dislike): ").strip())
                
                if rating in [1, -1]:
                    is_anchor = False
                    if rating == 1:
                        anchor_input = input("Is this an anchor? (y/n): ").strip().lower()
                        is_anchor = anchor_input == 'y'
                    
                    user_ratings.append((series['tmdb_id'], rating, is_anchor))
                    emoji = "👍" if rating == 1 else "👎"
                    anchor_mark = " ⭐" if is_anchor else ""
                    print(f"{emoji} Added: {series['title_en']}{anchor_mark}")
        except:
            print("Invalid input.")
    
    # Get filters
    print("\n" + "="*60)
    print("FILTERS")
    print("="*60)
    
    filters = {}
    
    lang_input = input("\nLanguages (en,he,ja,es or Enter for all): ").strip()
    filters['languages'] = lang_input.split(',') if lang_input else None
    
    status_input = input("Status (Running,Ended or Enter for all): ").strip()
    filters['status'] = status_input.split(',') if status_input else None
    
    # Run recommendations
    print("\n🤖 Calculating recommendations...")
    recommendations = get_recommendations(user_ratings, filters, top_n=10)
    
    print("\n🎯 Your Personalized Recommendations:")
    print_recommendations(recommendations)


# =====================================
# Main Execution
# =====================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SERIES ARCHITECT - RECOMMENDATION ENGINE TEST")
    print("="*60)
    
    print("\nSelect test:")
    print("  1. Crime Drama Fan")
    print("  2. Diverse Taste")
    print("  3. Anime Fan")
    print("  4. Minimal Filters")
    print("  5. Interactive Test")
    print("  6. Run All Tests")
    
    choice = input("\nChoice (1-6): ").strip()
    
    if choice == "1":
        test_crime_drama_fan()
    elif choice == "2":
        test_diverse_taste()
    elif choice == "3":
        test_anime_fan()
    elif choice == "4":
        test_minimal_filters()
    elif choice == "5":
        interactive_test()
    elif choice == "6":
        test_crime_drama_fan()
        test_diverse_taste()
        test_anime_fan()
        test_minimal_filters()
    else:
        print("\nRunning default test (Crime Drama Fan)...")
        test_crime_drama_fan()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")
