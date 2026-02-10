"""
Series Architect - Similarity Engine

Builds user profiles from ratings and calculates recommendations.
Handles like/dislike logic and exclusion filtering.
"""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from .feature_builder import (
        calculate_weighted_similarity,
        calculate_similarities_batch,
        get_series_data
    )
    from .config import (
        RATING_LIKE,
        RATING_DISLIKE,
        ANCHOR_MULTIPLIER,
        DISLIKE_EXCLUSION_THRESHOLD,
        MIN_LIKES,
        MIN_TOTAL_RATINGS,
        DEBUG_MODE
    )
except ImportError:
    from feature_builder import (
        calculate_weighted_similarity,
        calculate_similarities_batch,
        get_series_data
    )
    from config import (
        RATING_LIKE,
        RATING_DISLIKE,
        ANCHOR_MULTIPLIER,
        DISLIKE_EXCLUSION_THRESHOLD,
        MIN_LIKES,
        MIN_TOTAL_RATINGS,
        DEBUG_MODE
    )


# =====================================
# User Profile Building
# =====================================

def build_user_profile(user_ratings, weights=None):
    """
    Build a user profile from their ratings.
    
    This creates a "virtual series" that represents the user's taste
    by aggregating the features of their liked series.
    
    Args:
        user_ratings: List of tuples (tmdb_id, rating, is_anchor)
                     rating: 1 (like), -1 (dislike), 0 (neutral)
                     is_anchor: True if this is a key reference series
        weights: Custom feature weights (optional)
    
    Returns:
        dict: User profile containing:
            - liked_ids: List of liked series IDs (with anchors weighted)
            - disliked_ids: List of disliked series IDs
            - anchor_ids: List of anchor series IDs
    """
    liked_ids = []
    disliked_ids = []
    anchor_ids = []
    
    for rating_tuple in user_ratings:
        # Handle both (tmdb_id, rating) and (tmdb_id, rating, is_anchor)
        if len(rating_tuple) == 2:
            tmdb_id, rating = rating_tuple
            is_anchor = False
        else:
            tmdb_id, rating, is_anchor = rating_tuple
        
        if rating == RATING_LIKE:
            liked_ids.append(tmdb_id)
            if is_anchor:
                anchor_ids.append(tmdb_id)
                # Add anchor again to give it double weight
                liked_ids.append(tmdb_id)
        
        elif rating == RATING_DISLIKE:
            disliked_ids.append(tmdb_id)
    
    if DEBUG_MODE:
        print(f"[PROFILE] Likes: {len(set(liked_ids))} (anchors: {len(anchor_ids)})")
        print(f"[PROFILE] Dislikes: {len(disliked_ids)}")
    
    return {
        'liked_ids': liked_ids,  # May contain duplicates for anchors
        'disliked_ids': disliked_ids,
        'anchor_ids': anchor_ids
    }


def validate_user_ratings(user_ratings):
    """
    Validate that user has provided sufficient ratings.
    
    Args:
        user_ratings: List of rating tuples
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not user_ratings:
        return False, "No ratings provided"
    
    # Count likes and dislikes
    likes = sum(1 for r in user_ratings if r[1] == RATING_LIKE)
    dislikes = sum(1 for r in user_ratings if r[1] == RATING_DISLIKE)
    total = likes + dislikes
    
    if likes < MIN_LIKES:
        return False, f"Need at least {MIN_LIKES} likes (got {likes})"
    
    if total < MIN_TOTAL_RATINGS:
        return False, f"Need at least {MIN_TOTAL_RATINGS} total ratings (got {total})"
    
    return True, None


# =====================================
# Dislike Exclusion
# =====================================

def get_exclusion_list(disliked_ids, candidate_ids, threshold=None):
    """
    Find series to exclude based on similarity to disliked series.
    
    Args:
        disliked_ids: List of disliked series IDs
        candidate_ids: List of candidate series IDs to check
        threshold: Similarity threshold for exclusion (default from config)
    
    Returns:
        set: Set of series IDs to exclude
    """
    if threshold is None:
        threshold = DISLIKE_EXCLUSION_THRESHOLD
    
    if not disliked_ids:
        return set()
    
    exclusion_set = set()
    
    for disliked_id in disliked_ids:
        # Calculate similarity to all candidates
        similarities = calculate_similarities_batch(disliked_id, candidate_ids)
        
        # Exclude any series too similar to this disliked series
        for candidate_id, similarity in similarities:
            if similarity >= threshold:
                exclusion_set.add(candidate_id)
                if DEBUG_MODE:
                    print(f"[EXCLUSION] Excluding {candidate_id} (similar to disliked {disliked_id}: {similarity:.3f})")
    
    return exclusion_set


# =====================================
# Recommendation Calculation
# =====================================

def calculate_recommendation_scores(user_profile, candidate_ids, weights=None):
    """
    Calculate recommendation scores for candidates based on user profile.
    
    Strategy:
    1. For each candidate, calculate average similarity to all liked series
    2. Anchors are included twice in the average (giving them more weight)
    3. Sort by score descending
    
    Args:
        user_profile: User profile dict from build_user_profile()
        candidate_ids: List of candidate series IDs
        weights: Custom feature weights (optional)
    
    Returns:
        list: List of tuples (tmdb_id, score) sorted by score descending
    """
    liked_ids = user_profile['liked_ids']  # Contains duplicates for anchors
    
    if not liked_ids:
        return []
    
    scores = []
    
    for candidate_id in candidate_ids:
        # Skip if candidate is in the liked list
        if candidate_id in liked_ids:
            continue
        
        # Calculate similarity to each liked series (including anchor duplicates)
        similarities = []
        for liked_id in liked_ids:
            sim = calculate_weighted_similarity(candidate_id, liked_id, weights)
            similarities.append(sim)
        
        # Average similarity
        avg_score = sum(similarities) / len(similarities)
        scores.append((candidate_id, avg_score))
    
    # Sort by score descending
    scores.sort(key=lambda x: x[1], reverse=True)
    
    return scores


def get_recommendations(user_ratings, candidate_ids, filters=None, top_n=10, weights=None):
    """
    Main recommendation function.
    
    Args:
        user_ratings: List of (tmdb_id, rating, is_anchor?) tuples
        candidate_ids: List of pre-filtered candidate series IDs
        filters: Filter dict (for logging/debugging)
        top_n: Number of recommendations to return
        weights: Custom feature weights (optional)
    
    Returns:
        list: List of tuples (tmdb_id, score) - top N recommendations
    """
    # Validate ratings
    is_valid, error = validate_user_ratings(user_ratings)
    if not is_valid:
        if DEBUG_MODE:
            print(f"[ERROR] {error}")
        return []
    
    # Build user profile
    user_profile = build_user_profile(user_ratings, weights)
    
    # Apply dislike exclusion
    exclusion_list = get_exclusion_list(
        user_profile['disliked_ids'],
        candidate_ids
    )
    
    # Remove excluded series from candidates
    filtered_candidates = [
        cid for cid in candidate_ids 
        if cid not in exclusion_list
    ]
    
    if DEBUG_MODE:
        print(f"[FILTER] Candidates: {len(candidate_ids)} → {len(filtered_candidates)} (excluded {len(exclusion_list)})")
    
    # Calculate scores
    scores = calculate_recommendation_scores(user_profile, filtered_candidates, weights)
    
    # Return top N
    return scores[:top_n]


# =====================================
# Similarity Matrix (for analysis)
# =====================================

def build_similarity_matrix(series_ids, weights=None):
    """
    Build a full similarity matrix for a list of series.
    Useful for analysis and debugging.
    
    Args:
        series_ids: List of series IDs
        weights: Custom feature weights (optional)
    
    Returns:
        dict: Nested dict {id_a: {id_b: similarity}}
    """
    matrix = {}
    
    for i, id_a in enumerate(series_ids):
        matrix[id_a] = {}
        
        for id_b in series_ids:
            if id_a == id_b:
                matrix[id_a][id_b] = 1.0  # Perfect self-similarity
            elif id_b in matrix and id_a in matrix[id_b]:
                # Use already calculated value (symmetric)
                matrix[id_a][id_b] = matrix[id_b][id_a]
            else:
                # Calculate new similarity
                sim = calculate_weighted_similarity(id_a, id_b, weights)
                matrix[id_a][id_b] = sim
        
        if DEBUG_MODE and (i + 1) % 10 == 0:
            print(f"[MATRIX] Processed {i + 1}/{len(series_ids)} series")
    
    return matrix


# =====================================
# Utility Functions
# =====================================

def find_most_similar(tmdb_id, candidate_ids, top_n=10, weights=None):
    """
    Find the most similar series to a given series.
    Simple wrapper for TMDB-style "similar" functionality.
    
    Args:
        tmdb_id: Reference series ID
        candidate_ids: List of candidates to compare against
        top_n: Number of results to return
        weights: Custom feature weights (optional)
    
    Returns:
        list: List of tuples (candidate_id, similarity_score)
    """
    similarities = calculate_similarities_batch(tmdb_id, candidate_ids, weights)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_n]
