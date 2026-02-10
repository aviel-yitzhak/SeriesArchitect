"""
Series Architect - Filtering Module

Pre-filters the series catalog based on user preferences.
Reduces the candidate pool from thousands to hundreds before similarity calculation.
"""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from data_layer.db_utils import fetch_query

try:
    from .config import DEBUG_MODE, MAX_CANDIDATES
except ImportError:
    from config import DEBUG_MODE, MAX_CANDIDATES


def apply_filters(filters_dict):
    """
    Apply all filters and return list of candidate tmdb_ids.
    
    Args:
        filters_dict (dict): Filter criteria
            {
                'languages': ['en', 'ko'] or None,
                'status': ['Running', 'Ended'] or None,
                'decades': [2000, 2010, 2020] or None,
                'genres': [18, 80] or None
            }
    
    Returns:
        list: List of tmdb_ids that passed all filters
    
    Note:
        - None value means "don't filter" (include all)
        - All filters use OR logic (at least one match required)
    """
    # Start with base query
    query_parts = ["SELECT DISTINCT s.tmdb_id FROM series s"]
    where_clauses = []
    params = []
    
    # Filter 1: Languages (OR)
    if filters_dict.get('languages'):
        placeholders = ','.join(['%s'] * len(filters_dict['languages']))
        where_clauses.append(f"s.original_language IN ({placeholders})")
        params.extend(filters_dict['languages'])
    
    # Filter 2: Status (OR)
    if filters_dict.get('status'):
        placeholders = ','.join(['%s'] * len(filters_dict['status']))
        where_clauses.append(f"s.status IN ({placeholders})")
        params.extend(filters_dict['status'])
    
    # Filter 3: Decades (OR) - considers BOTH start and end dates
    if filters_dict.get('decades'):
        decade_conditions = []
        for decade in filters_dict['decades']:
            # Series is in decade if it started OR ended in that decade OR was running during it
            decade_conditions.append(
                f"""(
                    (EXTRACT(YEAR FROM s.first_air_date) >= %s AND EXTRACT(YEAR FROM s.first_air_date) < %s) OR
                    (s.last_air_date IS NOT NULL AND EXTRACT(YEAR FROM s.last_air_date) >= %s AND EXTRACT(YEAR FROM s.last_air_date) < %s) OR
                    (EXTRACT(YEAR FROM s.first_air_date) < %s AND (s.last_air_date IS NULL OR EXTRACT(YEAR FROM s.last_air_date) >= %s))
                )"""
            )
            params.extend([decade, decade + 10, decade, decade + 10, decade + 10, decade])

        where_clauses.append(f"({' OR '.join(decade_conditions)})")

    # Filter 4: Genres (OR) - requires join
    if filters_dict.get('genres'):
        query_parts.append("JOIN series_genres sg ON s.tmdb_id = sg.tmdb_id")
        placeholders = ','.join(['%s'] * len(filters_dict['genres']))
        where_clauses.append(f"sg.genre_id IN ({placeholders})")
        params.extend(filters_dict['genres'])

    # Combine query
    if where_clauses:
        query_parts.append("WHERE " + " AND ".join(where_clauses))

    # Add safety limit
    query_parts.append(f"LIMIT {MAX_CANDIDATES}")

    final_query = " ".join(query_parts)

    if DEBUG_MODE:
        print(f"[FILTERS] Query: {final_query}")
        print(f"[FILTERS] Params: {params}")

    # Execute query
    results = fetch_query(final_query, tuple(params) if params else None)

    candidate_ids = [row[0] for row in results]

    if DEBUG_MODE:
        print(f"[FILTERS] Found {len(candidate_ids)} candidates after filtering")

    return candidate_ids


def filter_by_language(language_list):
    """
    Filter series by original language.

    Args:
        language_list (list): List of language codes (e.g., ['en', 'ko'])

    Returns:
        list: List of tmdb_ids
    """
    if not language_list:
        return []

    placeholders = ','.join(['%s'] * len(language_list))
    query = f"SELECT tmdb_id FROM series WHERE original_language IN ({placeholders})"
    results = fetch_query(query, tuple(language_list))

    return [row[0] for row in results]


def filter_by_status(status_list):
    """
    Filter series by status (Running/Ended).

    Args:
        status_list (list): List of statuses (e.g., ['Running', 'Ended'])

    Returns:
        list: List of tmdb_ids
    """
    if not language_list:
        return []

    placeholders = ','.join(['%s'] * len(status_list))
    query = f"SELECT tmdb_id FROM series WHERE status IN ({placeholders})"
    results = fetch_query(query, tuple(status_list))

    return [row[0] for row in results]


def filter_by_decades(decades_list):
    """
    Filter series by release decades - considers both start and end dates.

    Args:
        decades_list (list): List of decades (e.g., [2000, 2010, 2020])

    Returns:
        list: List of tmdb_ids
    """
    if not decades_list:
        return []

    conditions = []
    params = []

    for decade in decades_list:
        conditions.append(
            """(
                (EXTRACT(YEAR FROM first_air_date) >= %s AND EXTRACT(YEAR FROM first_air_date) < %s) OR
                (last_air_date IS NOT NULL AND EXTRACT(YEAR FROM last_air_date) >= %s AND EXTRACT(YEAR FROM last_air_date) < %s) OR
                (EXTRACT(YEAR FROM first_air_date) < %s AND (last_air_date IS NULL OR EXTRACT(YEAR FROM last_air_date) >= %s))
            )"""
        )
        params.extend([decade, decade + 10, decade, decade + 10, decade + 10, decade])

    query = f"SELECT tmdb_id FROM series WHERE {' OR '.join(conditions)}"
    results = fetch_query(query, tuple(params))

    return [row[0] for row in results]


def filter_by_genres(genres_list):
    """
    Filter series by genres (OR logic - at least one genre match).

    Args:
        genres_list (list): List of genre_ids (e.g., [18, 80])

    Returns:
        list: List of tmdb_ids
    """
    if not genres_list:
        return []

    placeholders = ','.join(['%s'] * len(genres_list))
    query = f"""
        SELECT DISTINCT tmdb_id 
        FROM series_genres 
        WHERE genre_id IN ({placeholders})
    """
    results = fetch_query(query, tuple(genres_list))

    return [row[0] for row in results]


def get_all_series_ids():
    """
    Get all series IDs from database (no filtering).

    Returns:
        list: List of all tmdb_ids
    """
    query = f"SELECT tmdb_id FROM series LIMIT {MAX_CANDIDATES}"
    results = fetch_query(query)

    return [row[0] for row in results]