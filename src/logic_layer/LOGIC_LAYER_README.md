# Series Architect - Logic Layer

## Overview

The Logic Layer is the brain of Series Architect - a sophisticated recommendation engine that calculates personalized TV series recommendations based on user preferences. It implements a weighted feature similarity algorithm with intelligent filtering and exclusion logic.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    UI/API Layer                              │
│              (Flask, User Requests)                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   RECOMMENDER.PY                            │
│              Main Entry Point & Orchestration               │
│  • get_recommendations() - Main API                         │
│  • enrich_recommendations() - Add metadata                  │
│  • search_series() - Series search                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
                   ┌────────┴────────┐
                   ↓                 ↓
┌──────────────────────────┐  ┌──────────────────────────┐
│    FILTERS.PY            │  │  SIMILARITY_ENGINE.PY    │
│  Pre-filtering Logic     │  │  Core Algorithm          │
│  • Language filtering    │  │  • User profile building │
│  • Genre filtering       │  │  • Dislike exclusion     │
│  • Decade filtering      │  │  • Score calculation     │
│  • Status filtering      │  │  • Ranking & sorting     │
└──────────────────────────┘  └──────────────────────────┘
                   ↓                 ↓
                   └────────┬────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  FEATURE_BUILDER.PY                         │
│              Feature Extraction & Similarity                │
│  • Genre similarity (Jaccard)                               │
│  • Keywords similarity (Jaccard)                            │
│  • Year proximity (Normalized distance)                     │
│  • Country matching (Binary)                                │
│  • Popularity similarity (Log-normalized)                   │
│  • Content rating (Ordinal distance)                        │
│  • Seasons similarity (Normalized distance)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      CONFIG.PY                              │
│              Configuration & Constants                      │
│  • Feature weights                                          │
│  • Algorithm parameters                                     │
│  • Genre/Language mappings                                  │
└─────────────────────────────────────────────────────────────┘
```

## Core Modules

### 1. `recommender.py` - Main API

The primary interface for the recommendation system.

#### Main Function

```python
def get_recommendations(user_ratings, filters=None, top_n=10, weights=None)
```

**Parameters:**
- `user_ratings`: List of tuples `[(tmdb_id, rating, is_anchor), ...]`
  - `rating`: 1 (like), -1 (dislike)
  - `is_anchor`: True/False (optional, default False)
- `filters`: Dict of filter criteria (optional)
  ```python
  {
      'languages': ['en', 'ko', ...],  # or None
      'status': ['Running', 'Ended'],  # or None
      'decades': [2000, 2010, 2020],   # or None
      'genres': [18, 80, ...]          # genre_ids, or None
  }
  ```
- `top_n`: Number of recommendations to return (default: 10)
- `weights`: Custom feature weights (optional, uses defaults from config)

**Returns:**
```python
[
    {
        'tmdb_id': 1396,
        'title_en': 'Breaking Bad',
        'title_he': 'ברקינג בד',
        'score': 0.847,
        'poster_path': '/ggFHVNu6YYI5L9pCfOacjizRGt.jpg',
        'overview': '...',
        'popularity': 450.32,
        'first_air_date': '2008-01-20',
        'status': 'Ended',
        'origin_country': 'US',
        'number_of_seasons': 5,
        'number_of_episodes': 62,
        'content_rating': 'TV-MA',
        'genres': ['Drama', 'Crime']
    },
    # ... more recommendations
]
```

**Example Usage:**
```python
from logic_layer.recommender import get_recommendations

# User ratings
user_ratings = [
    (1396, 1, True),   # Breaking Bad - Like (Anchor)
    (60059, 1, False), # Better Call Saul - Like
    (1668, -1, False)  # Friends - Dislike
]

# Optional filters
filters = {
    'languages': ['en'],
    'status': ['Running', 'Ended'],
    'decades': [2010, 2020],
    'genres': [18, 80]  # Drama, Crime
}

# Get recommendations
recommendations = get_recommendations(
    user_ratings=user_ratings,
    filters=filters,
    top_n=10
)

for rec in recommendations:
    print(f"{rec['title_en']}: {rec['score']:.3f}")
```

#### Utility Functions

**`get_series_details(tmdb_id)`**
Get full metadata for a single series.

**`search_series(query, limit=10)`**
Search for series by title (English or Hebrew).

**`get_popular_series(limit=20, language=None)`**
Get most popular series for initial rating selection.

**`reset_cache()`**
Clear all caches (useful between sessions or for testing).

**`get_recommendation_stats()`**
Get statistics about the database and system.

---

### 2. `similarity_engine.py` - Core Algorithm

Implements the recommendation algorithm logic.

#### User Profile Building

```python
def build_user_profile(user_ratings, weights=None)
```

Creates a user profile by aggregating liked series. Anchor series are included twice in the profile for stronger weighting.

**Returns:**
```python
{
    'liked_ids': [1396, 1396, 60059],  # Anchors appear twice
    'disliked_ids': [1668],
    'anchor_ids': [1396]
}
```

#### Validation

```python
def validate_user_ratings(user_ratings)
```

Ensures minimum requirements:
- At least 5 likes
- At least 10 total ratings (likes + dislikes)

#### Dislike Exclusion

```python
def get_exclusion_list(disliked_ids, candidate_ids, threshold=0.7)
```

Identifies series to exclude based on similarity to disliked series. Any candidate with >0.7 similarity to a disliked series is excluded.

#### Score Calculation

```python
def calculate_recommendation_scores(user_profile, candidate_ids, weights=None)
```

For each candidate:
1. Calculate similarity to each liked series (including anchor duplicates)
2. Average the similarities
3. Sort by score descending

#### Main Recommendation Function

```python
def get_recommendations(user_ratings, candidate_ids, filters=None, top_n=10, weights=None)
```

Complete recommendation pipeline:
1. Validate ratings
2. Build user profile
3. Apply dislike exclusion
4. Calculate scores
5. Return top N

---

### 3. `feature_builder.py` - Feature Extraction

Calculates individual feature similarities between series.

#### Similarity Functions

**Genre Similarity (Jaccard)**
```python
def calculate_genres_similarity(tmdb_id_a, tmdb_id_b)
```
Calculates overlap of genre sets: `|A ∩ B| / |A ∪ B|`

**Keywords Similarity (Top-K Jaccard)**
```python
def calculate_keywords_similarity(tmdb_id_a, tmdb_id_b)
```
Uses top 10 keywords per series, then calculates Jaccard similarity.

**Year Proximity (Normalized Distance)**
```python
def calculate_year_proximity(tmdb_id_a, tmdb_id_b)
```
Formula: `max(0, 1 - year_diff / 10)`
- Same year = 1.0
- 10+ years apart = 0.0

**Origin Country (Binary)**
```python
def calculate_origin_country_similarity(tmdb_id_a, tmdb_id_b)
```
Returns 1.0 if same country, 0.0 otherwise.

**Popularity (Log-Normalized)**
```python
def calculate_popularity_similarity(tmdb_id_a, tmdb_id_b)
```
Uses log scale to reduce impact of extreme popularity differences.

**Content Rating (Ordinal Distance)**
```python
def calculate_content_rating_similarity(tmdb_id_a, tmdb_id_b)
```
Rating hierarchy: TV-Y < TV-Y7 < TV-G < TV-PG < TV-14 < TV-MA

**Seasons Similarity (Normalized Distance)**
```python
def calculate_seasons_similarity(tmdb_id_a, tmdb_id_b)
```
Formula: `max(0, 1 - season_diff / 5)`

#### Weighted Combination

```python
def calculate_weighted_similarity(tmdb_id_a, tmdb_id_b, weights=None)
```

Combines all features using configured weights:

```python
FEATURE_WEIGHTS = {
    'genres': 0.30,              # 30% - Genre overlap
    'keywords': 0.35,            # 35% - Theme/keyword similarity
    'year_proximity': 0.10,      # 10% - Release year proximity
    'origin_country': 0.10,      # 10% - Same production country
    'popularity': 0.08,          # 8% - Similar popularity level
    'content_rating': 0.04,      # 4% - Similar age rating
    'number_of_seasons': 0.03    # 3% - Similar length
}
```

**Total similarity = Σ(feature_similarity × weight)**

#### Caching

All data fetching is cached in memory:
- `_SERIES_CACHE` - Series metadata
- `_GENRES_CACHE` - Genre sets
- `_KEYWORDS_CACHE` - Keyword sets

```python
def clear_cache()
```
Clears all caches. Call between sessions or when testing.

---

### 4. `filters.py` - Pre-filtering

Reduces the candidate pool before expensive similarity calculations.

#### Main Filter Function

```python
def apply_filters(filters_dict)
```

Applies all filters with **AND** logic (series must match ALL filters):

**Filter Types:**

1. **Languages** (OR within filter)
   ```python
   {'languages': ['en', 'ko']}  # English OR Korean
   ```

2. **Status** (OR within filter)
   ```python
   {'status': ['Running', 'Ended']}  # Running OR Ended
   ```

3. **Decades** (OR within filter)
   ```python
   {'decades': [2000, 2010, 2020]}  # 2000s OR 2010s OR 2020s
   ```
   Includes series that started, ended, or ran during the decade.

4. **Genres** (OR within filter)
   ```python
   {'genres': [18, 80]}  # Drama OR Crime
   ```

**Returns:**
List of `tmdb_id`s matching all filters (up to `MAX_CANDIDATES` limit)

**Example:**
```python
from logic_layer.filters import apply_filters

filters = {
    'languages': ['en'],
    'status': ['Running'],
    'decades': [2020],
    'genres': [18, 80]  # Drama, Crime
}

candidate_ids = apply_filters(filters)
# Returns IDs of English Drama/Crime series from 2020s that are still running
```

---

### 5. `config.py` - Configuration

Central configuration file for all algorithm parameters.

#### Feature Weights

```python
FEATURE_WEIGHTS = {
    'genres': 0.30,
    'keywords': 0.35,
    'year_proximity': 0.10,
    'origin_country': 0.10,
    'popularity': 0.08,
    'content_rating': 0.04,
    'number_of_seasons': 0.03
}
```
**Must sum to 1.0** (validated on import)

#### User Rating Settings

```python
RATING_LIKE = 1
RATING_DISLIKE = -1
RATING_NEUTRAL = 0

MIN_LIKES = 5               # Minimum likes required
MIN_TOTAL_RATINGS = 10      # Minimum total ratings

ANCHOR_MULTIPLIER = 2.0     # Weight multiplier for anchors
```

#### Similarity Settings

```python
DISLIKE_EXCLUSION_THRESHOLD = 0.7  # Exclude if similarity > 0.7
TOP_N_DEFAULT = 10                 # Default number of recommendations
```

#### Feature Calculation Parameters

```python
TOP_KEYWORDS_COUNT = 10      # Use top 10 keywords per series
DECADE_DIFF_MAX = 10         # Max year difference (10+ years = 0 similarity)
SEASONS_DIFF_MAX = 5         # Max season difference (5+ seasons = 0 similarity)
```

#### Genre Mappings

```python
GENRE_CATEGORIES = {
    'Action & Adventure': [10759, 37],
    'Animation': [16],
    'Comedy': [35],
    'Crime': [80],
    'Documentary': [99],
    'Drama': [18, 10766],
    # ... more genres
}

GENRE_ID_TO_NAME = {
    10759: "Action & Adventure",
    16: "Animation",
    35: "Comedy",
    # ... more mappings
}
```

#### Language Mappings

```python
VALID_LANGUAGES = ['en', 'he', 'es', 'ja']

LANGUAGE_NAMES = {
    'en': 'English',
    'he': 'Hebrew',
    'es': 'Spanish',
    'ja': 'Japanese'
}
```

#### Debug Settings

```python
DEBUG_MODE = False                    # Verbose output
LOG_SIMILARITY_SCORES = False         # Log individual calculations
```

---

## Algorithm Deep Dive

### How Recommendations Work

#### Step 1: Pre-Filtering

Filter the entire catalog by user preferences:
```python
filters = {
    'languages': ['en'],
    'status': ['Running'],
    'decades': [2020],
    'genres': [18, 80]
}
candidate_ids = apply_filters(filters)
# Reduces 10,000 series → 800 candidates
```

#### Step 2: User Profile Building

Create a weighted representation of user taste:
```python
user_ratings = [
    (1396, 1, True),   # Breaking Bad - Anchor
    (60059, 1, False), # Better Call Saul
    (1668, -1, False)  # Friends - Dislike
]

profile = {
    'liked_ids': [1396, 1396, 60059],  # Anchor appears twice
    'disliked_ids': [1668],
    'anchor_ids': [1396]
}
```

#### Step 3: Dislike Exclusion

Exclude series too similar to dislikes:
```python
# For each disliked series (Friends)
# Calculate similarity to all candidates
# Exclude any with similarity > 0.7

exclusion_list = get_exclusion_list(
    disliked_ids=[1668],
    candidate_ids=candidate_ids,
    threshold=0.7
)
# Excludes sitcoms similar to Friends
```

#### Step 4: Similarity Calculation

For each remaining candidate, calculate average similarity to liked series:

```python
# Candidate: The Wire (tmdb_id = 1438)

similarities = []
for liked_id in [1396, 1396, 60059]:  # Anchors counted twice
    sim = calculate_weighted_similarity(1438, liked_id)
    # 1438 vs 1396: 0.85 (high similarity - both crime dramas)
    # 1438 vs 1396: 0.85 (counted twice because anchor)
    # 1438 vs 60059: 0.78 (similar themes)
    similarities.append(sim)

avg_score = sum(similarities) / len(similarities)
# avg_score = (0.85 + 0.85 + 0.78) / 3 = 0.827
```

#### Step 5: Ranking

Sort all candidates by their average score and return top N.

---

## Performance Optimization

### Caching Strategy

All database queries are cached:
- **Series metadata**: Cached on first access
- **Genre sets**: Cached per series
- **Keyword sets**: Cached per series

Clear cache between user sessions:
```python
from logic_layer.recommender import reset_cache
reset_cache()
```

### Batch Operations

```python
def calculate_similarities_batch(reference_id, candidate_ids, weights=None)
```
Calculates similarities to multiple candidates efficiently.

### Database Optimization

Pre-filtering reduces database load:
- Without filters: 10,000+ series to process
- With filters: 100-1,000 candidates
- **10-100x reduction** in similarity calculations

---

## Testing & Debugging

### Test Recommendations

```bash
cd src/logic_layer
python test_recommendations.py
```

Tests the complete recommendation pipeline with sample data.

### Benchmark Performance

```bash
cd src/logic_layer
python benchmark.py
```

Measures:
- Filtering speed
- Similarity calculation time
- Memory usage
- Recommendation quality

### Debug Mode

Enable verbose logging in `config.py`:
```python
DEBUG_MODE = True
```

Output example:
```
=========================================================
STARTING RECOMMENDATION ENGINE
=========================================================
User Ratings: 12
Filters: {'languages': ['en'], 'genres': [18, 80]}
Top N: 10

[STEP 1] Applying filters...
[FILTERS] Found 847 candidates after filtering

[STEP 2] Calculating similarities...
[PROFILE] Likes: 10 (anchors: 2)
[PROFILE] Dislikes: 2
[EXCLUSION] Excluding 23 series similar to dislikes
[FILTER] Candidates: 847 → 824 (excluded 23)

[STEP 3] Enriching with metadata...
[STEP 3] Enriched 10 recommendations

=========================================================
RECOMMENDATION ENGINE COMPLETE
=========================================================
```

---

## Advanced Usage

### Custom Feature Weights

Override default weights:

```python
custom_weights = {
    'genres': 0.40,        # Increase genre importance
    'keywords': 0.30,      # Decrease keywords
    'year_proximity': 0.15,
    'origin_country': 0.05,
    'popularity': 0.05,
    'content_rating': 0.03,
    'number_of_seasons': 0.02
}

recommendations = get_recommendations(
    user_ratings=user_ratings,
    weights=custom_weights
)
```

### Find Similar Series

Find series similar to a specific series:

```python
from logic_layer.similarity_engine import find_most_similar

# Find series similar to Breaking Bad
similar = find_most_similar(
    tmdb_id=1396,
    candidate_ids=all_series_ids,
    top_n=10
)
```

### Build Similarity Matrix

For analysis and debugging:

```python
from logic_layer.similarity_engine import build_similarity_matrix

series_ids = [1396, 60059, 1668, 1438]
matrix = build_similarity_matrix(series_ids)

# matrix = {
#     1396: {1396: 1.0, 60059: 0.82, 1668: 0.15, 1438: 0.85},
#     60059: {1396: 0.82, 60059: 1.0, 1668: 0.12, 1438: 0.78},
#     ...
# }
```

---

## Error Handling

### Insufficient Ratings

```python
recommendations = get_recommendations(
    user_ratings=[(1396, 1, False)],  # Only 1 like
    top_n=10
)
# Returns: []
# Reason: Need minimum 5 likes
```

### No Candidates After Filtering

```python
filters = {
    'languages': ['xx'],  # Invalid language
    'genres': [99999]     # Non-existent genre
}
recommendations = get_recommendations(
    user_ratings=user_ratings,
    filters=filters
)
# Returns: []
# Reason: No series match the filters
```

### Missing Series Data

If a series has incomplete data, similarity calculations handle gracefully:
- Missing genres: 0.0 similarity
- Missing keywords: 0.0 similarity
- Missing dates: 0.0 year proximity
- Missing country: 0.0 country similarity

---

## Integration with Other Layers

### From UI Layer

```python
# UI Layer (Flask app)
from logic_layer.recommender import get_recommendations, search_series

# Search for series
results = search_series("breaking", limit=10)

# Get recommendations
recommendations = get_recommendations(
    user_ratings=user_ratings,
    filters=filters,
    top_n=14
)
```

### From Data Layer

Logic layer depends on Data Layer for:
- Series metadata
- Genre/keyword relationships
- Database queries

```python
from data_layer.db_utils import fetch_query

# Logic layer uses db_utils for all database access
query = "SELECT tmdb_id, title_en FROM series WHERE status = %s"
results = fetch_query(query, ('Running',))
```

---

## Known Limitations

### Cold Start Problem

- Requires minimum 5 likes to generate recommendations
- New users must rate series before getting recommendations
- No content-based fallback for new users

**Potential Solution**: Offer popular series by genre as starting point

### Genre Granularity

- TMDB genres are broad (e.g., "Drama" covers many sub-genres)
- Keywords help but are inconsistent across series

**Potential Solution**: Add custom genre taxonomy or sub-genre classification

### Popularity Bias

- Popular series get recommended more often
- Niche series may be underrepresented

**Potential Solution**: Add diversity boosting or exploration factor

### Computation Scaling

- Similarity calculations are O(n) per candidate
- 10,000 candidates × 10 liked series = 100,000 calculations

**Current Mitigation**: Pre-filtering reduces n by 90%+  
**Future Solution**: Pre-compute similarity matrix, use approximate nearest neighbors

---

## Future Enhancements

### Algorithm Improvements

1. **Deep Learning Embeddings**
   - Use neural networks to learn series representations
   - Capture complex patterns beyond hand-crafted features

2. **Collaborative Filtering**
   - Learn from other users with similar tastes
   - "Users who liked X also liked Y"

3. **Temporal Dynamics**
   - Consider when series was watched
   - Account for changing user preferences over time

4. **Diversity Boosting**
   - Ensure recommendations span different genres/types
   - Avoid recommendation bubble

### Feature Additions

1. **Actor/Creator Similarity**
   - Match based on cast and crew
   - "More from this director"

2. **Network/Studio Patterns**
   - HBO shows tend to be similar
   - Netflix originals share characteristics

3. **Mood/Tone Analysis**
   - Dark vs light
   - Serious vs comedic
   - Slow-burn vs action-packed

4. **Episode Structure**
   - Procedural vs serialized
   - Anthology vs continuous narrative

---

## References

### Algorithms

- **Jaccard Similarity**: [Wikipedia](https://en.wikipedia.org/wiki/Jaccard_index)
- **Cosine Similarity**: [Wikipedia](https://en.wikipedia.org/wiki/Cosine_similarity)
- **Content-Based Filtering**: [Wikipedia](https://en.wikipedia.org/wiki/Recommender_system#Content-based_filtering)

### Libraries

- NumPy Documentation: https://numpy.org/doc/
- pandas Documentation: https://pandas.pydata.org/docs/
- scikit-learn: https://scikit-learn.org/

---

## License & Attribution

This product uses the TMDB API but is not endorsed or certified by TMDB.
