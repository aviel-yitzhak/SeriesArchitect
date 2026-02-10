# Series Architect - Data Layer

## Overview
The Data Layer is responsible for managing the TV series catalog by integrating with The Movie Database (TMDB) API and maintaining a PostgreSQL database. It provides clean data access for the recommendation engine without containing any business logic.

## Architecture

### Components

#### 1. `db_utils.py` - Database Utilities
Core database connectivity and query execution layer.

**Functions:**
- `get_connection()` - Establishes PostgreSQL connection using environment variables
- `execute_query(query, params, fetch)` - Executes modification queries (INSERT/UPDATE/DELETE)
  - Returns `RealDictRow` (dictionaries) when `fetch=True`
- `fetch_query(query, params)` - Executes read-only queries (SELECT)
  - Returns `Tuples` (access by index: `row[0]`)
- `test_connection()` - Verifies database connectivity

**Environment Variables Required:**
```
DB_HOST=your_host
DB_NAME=series_architect
DB_USER=your_user
DB_PASS=your_password
```

---

#### 2. `etl_processor.py` - ETL Pipeline
Handles data extraction, transformation, and loading from TMDB API.

**Functions:**

**`discover_series_ids(lang_code, sort_by, pages)`**
- Discovers series by language and popularity
- Parameters:
  - `lang_code`: Language filter (e.g., 'en', 'es', 'he', 'ko', 'ja')
  - `sort_by`: Sorting criterion (default: 'popularity.desc')
  - `pages`: Number of pages to fetch (20 series per page)
- Returns: List of TMDB IDs

**`fetch_raw_data(tmdb_id)`**
- Fetches comprehensive data for a single series from 5 TMDB endpoints:
  1. Details (Hebrew) - `tv/{id}?language=he-IL`
  2. Details (English) - `tv/{id}?language=en-US`
  3. Keywords - `tv/{id}/keywords`
  4. Watch Providers - `tv/{id}/watch/providers`
  5. Content Ratings - `tv/{id}/content_ratings`

**Data Transformation Logic:**
- **Status Normalization:**
  - "Returning Series" → "Running"
  - "Ended" / "Canceled" → "Ended"
- **Origin Country Fixing:**
  - Safely extracts first country from `origin_country` array
  - Defaults to "Unknown" if missing
- **TBA Provider Support:**
  - If no Israeli providers exist, creates virtual provider:
    ```python
    {'provider_id': 0, 'provider_name': 'TBA', 'logo_path': None}
    ```
- **Content Rating Priority:**
  - Prefers Israeli rating ('IL')
  - Falls back to US rating ('US')
  - Defaults to "NR" (Not Rated)

**`save_to_db(data)`**
- Saves processed data using **UPSERT** logic (ON CONFLICT DO UPDATE)
- Updates 4 tables:
  1. `series` - Main series data
  2. `genres` + `series_genres` - Genre relationships
  3. `keywords` + `series_keywords` - Keyword relationships
  4. `streaming_providers` + `series_availability` - Provider availability

---

#### 3. `data_manager.py` - Management Layer
High-level operations for catalog maintenance.

**Functions:**

**`update_catalog_by_language(lang_code, pages)`**
- Expands catalog by discovering new series
- Use cases:
  - Add Korean series: `update_catalog_by_language('ko', pages=3)`
  - Add Spanish series: `update_catalog_by_language('es', pages=5)`
- Flow:
  1. Discover series IDs by language
  2. Fetch raw data for each
  3. Save to database with rate limiting (0.1s delay)

**`run_maintenance_repair()`**
- Updates all existing series in the database
- Essential for:
  - Fixing data bugs (e.g., missing countries)
  - Updating series status (Running → Ended)
  - Applying new transformation logic
- Flow:
  1. Fetch all TMDB IDs from database
  2. Re-fetch and re-save each series
  3. Progress logging every 10 items

---

#### 4. `series_architect_backup.sql` - Database Schema

**Core Tables:**

**`series`** - Main series catalog
```sql
tmdb_id (PK), title_he, title_en, overview, popularity,
poster_path, original_language, origin_country, status,
adult, first_air_date, last_air_date, number_of_seasons,
number_of_episodes, content_rating
```

**`genres`** - Genre definitions
```sql
genre_id (PK), genre_name, main_category
```

**`series_genres`** - Many-to-Many relationship
```sql
tmdb_id (FK), genre_id (FK)
```

**`keywords`** - Keyword definitions
```sql
keyword_id (PK), name
```

**`series_keywords`** - Many-to-Many relationship
```sql
tmdb_id (FK), keyword_id (FK)
```

**`streaming_providers`** - Provider catalog
```sql
provider_id (PK), provider_name, logo_path
```

**`series_availability`** - Provider availability by country
```sql
tmdb_id (FK), provider_id (FK), country_code (default: 'IL')
```

**User Tables (for future use):**
- `users` - User accounts
- `personal_ratings` - User ratings (1-10 scale, anchor support)
- `recommendation_history` - User interaction tracking

---

## Usage Examples

### Initial Setup
```python
from data_manager import update_catalog_by_language

# Add top 100 English series
update_catalog_by_language('en', pages=5)

# Add top 60 Korean series
update_catalog_by_language('ko', pages=3)

# Add top 40 Japanese series
update_catalog_by_language('ja', pages=2)
```

### Maintenance
```python
from data_manager import run_maintenance_repair

# Update all existing series (fixes bugs, updates status)
run_maintenance_repair()
```

### Direct Database Access
```python
from db_utils import fetch_query

# Get all running series
query = "SELECT tmdb_id, title_en FROM series WHERE status = 'Running'"
results = fetch_query(query)

for row in results:
    print(f"ID: {row[0]}, Title: {row[1]}")
```

---

## Data Quality Features

### 1. Rate Limiting
- 0.1 second delay between API calls to respect TMDB limits
- Prevents API blocking

### 2. Error Handling
- Try-catch blocks in all API calls
- Continues processing if individual series fails
- Logs errors without crashing

### 3. Upsert Logic
- `ON CONFLICT DO UPDATE` prevents duplicates
- Allows safe re-running of imports
- Updates existing records with fresh data

### 4. Data Completeness
- Dual-language support (Hebrew + English)
- Fallback mechanisms (e.g., English overview if Hebrew missing)
- TBA providers when none available

---

## Environment Setup

### Required Dependencies
```bash
pip install psycopg2-binary requests python-dotenv
```

### .env Configuration
```
TMDB_TOKEN=your_tmdb_bearer_token
DB_HOST=localhost
DB_NAME=series_architect
DB_USER=postgres
DB_PASS=your_password
```

### Database Initialization
```bash
psql -U postgres -d series_architect -f series_architect_backup.sql
```

---

## Known Limitations

### 1. Legacy Column
- `series.genre_ids` (text column) is deprecated
- Use `series_genres` table instead
- Will be removed in future schema migration

### 2. Missing Indexes
Recommended indexes for performance:
```sql
CREATE INDEX idx_series_popularity ON series(popularity DESC);
CREATE INDEX idx_series_status ON series(status);
CREATE INDEX idx_series_language ON series(original_language);
CREATE INDEX idx_series_genres_genre ON series_genres(genre_id);
```

### 3. Single Country Support
- Currently optimized for Israeli market ('IL')
- Provider availability focused on Israel
- Can be extended for multi-country support

---

## Integration with Logic Layer

The Data Layer provides **raw, clean data** to the Logic Layer. It does NOT contain:
- ❌ Recommendation algorithms
- ❌ Filtering logic
- ❌ Feature vector calculations
- ❌ Similarity computations

**What it DOES provide:**
- ✅ Complete series catalog with all metadata
- ✅ Genre and keyword relationships
- ✅ Provider availability data
- ✅ Reliable data updates and maintenance

---

## Future Enhancements

### Recommended Additions:
1. **Schema Migration Script**
   - Remove deprecated `genre_ids` column
   - Add performance indexes
   
2. **Validation Layer**
   - Input validation for ratings (1-10 range)
   - TMDB ID validation
   
3. **Batch Operations**
   - Bulk insert support
   - Transaction batching for large imports

4. **Monitoring**
   - API usage tracking
   - Data freshness indicators
   - Error rate monitoring

---

## License & Attribution

Data provided by [The Movie Database (TMDB)](https://www.themoviedb.org/).  
This product uses the TMDB API but is not endorsed or certified by TMDB.
