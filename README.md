# Series Architect

A personalized TV series recommendation system powered by advanced machine learning algorithms and collaborative filtering techniques.

## Overview

Series Architect is a three-tier application that helps users discover TV series tailored to their unique tastes. Unlike simple genre-based recommendations, it uses a sophisticated similarity engine that analyzes multiple dimensions including genres, keywords, release years, production countries, popularity metrics, content ratings, and series length.

The system learns from user preferences (likes and dislikes) to generate personalized recommendations while intelligently filtering out series similar to those disliked.

## Key Features

- **Multi-Factor Similarity Analysis**: Combines 7 different feature dimensions with configurable weights
- **Smart Filtering**: Pre-filters catalog by language, genre, decade, and status before recommendation
- **Dislike-Based Exclusion**: Automatically excludes series similar to user dislikes
- **Anchor Series Support**: Allows marking key reference series for stronger weighting
- **Real-Time TMDB Integration**: Keeps catalog updated with latest series data
- **Dual Language Support**: Displays titles in both Hebrew and English
- **Israeli Streaming Focus**: Shows availability on Israeli streaming platforms

## Architecture

Series Architect follows a clean three-tier architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer (Flask)                       │
│  • Web Interface                                            │
│  • User Rating Collection                                   │
│  • Recommendation Display                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Logic Layer (Python)                      │
│  • Recommendation Engine                                    │
│  • Similarity Calculations                                  │
│  • Feature Vector Building                                  │
│  • User Profile Management                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Data Layer (PostgreSQL)                    │
│  • TMDB API Integration                                     │
│  • ETL Processing                                           │
│  • Database Operations                                      │
│  • Catalog Management                                       │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.11+
- Flask 3.1.2 (Web framework)
- PostgreSQL (Database)
- psycopg2 (Database driver)

**Data Processing:**
- NumPy (Numerical operations)
- pandas (Data manipulation)
- scikit-learn (Machine learning utilities)

**External APIs:**
- TMDB API (The Movie Database)

**Frontend:**
- HTML5/CSS3
- JavaScript (ES6+)
- Responsive design

## Project Structure

```
SeriesArchitect/
├── src/
│   ├── data_layer/          # Data management and ETL
│   │   ├── db_utils.py      # Database utilities
│   │   ├── etl_processor.py # TMDB API integration
│   │   ├── data_manager.py  # Catalog maintenance
│   │   └── DATA_LAYER_README.md
│   │
│   ├── logic_layer/         # Recommendation engine
│   │   ├── recommender.py   # Main recommendation API
│   │   ├── similarity_engine.py # Similarity calculations
│   │   ├── feature_builder.py   # Feature extraction
│   │   ├── filters.py       # Pre-filtering logic
│   │   ├── config.py        # Configuration constants
│   │   └── LOGIC_LAYER_README.md
│   │
│   └── ui_layer/            # Web interface
│       ├── app.py           # Flask application
│       ├── templates/       # HTML templates
│       ├── static/          # CSS, JS, assets
│       └── UI_LAYER_README.md
│
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 12 or higher
- TMDB API key (free from themoviedb.org)

### 1. Clone the Repository

```bash
git clone https://github.com/aviel-yitzhak/SeriesArchitect.git
cd SeriesArchitect
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Create the PostgreSQL database:

```bash
createdb series_architect
psql -d series_architect -f src/data_layer/series_architect_backup.sql
```

### 4. Environment Configuration

Create a `.env` file in `src/data_layer/`:

```env
# TMDB API
TMDB_TOKEN=your_tmdb_bearer_token_here

# Database
DB_HOST=localhost
DB_NAME=series_architect
DB_USER=postgres
DB_PASS=your_password_here
```

To get a TMDB API token:
1. Create a free account at [themoviedb.org](https://www.themoviedb.org/)
2. Go to Settings → API
3. Request an API key (choose "Developer" option)
4. Copy the "API Read Access Token" (Bearer token)

### 5. Initial Data Population

Populate the database with series data:

```bash
cd src/data_layer
python data_manager.py
```

You can modify `data_manager.py` to import specific languages:

```python
# Example: Import top 100 English series
update_catalog_by_language('en', pages=5)

# Import top 60 Korean series
update_catalog_by_language('ko', pages=3)

# Import top 40 Japanese series
update_catalog_by_language('ja', pages=2)
```

## Running the Application

### Start the Flask Server

```bash
cd src/ui_layer
python app.py
```

The application will be available at `http://localhost:5000`

### Usage Flow

1. **Select Filters** (Optional)
   - Choose languages (English, Hebrew, Spanish, Japanese)
   - Select genres (Drama, Crime, Comedy, etc.)
   - Pick decades (2000s, 2010s, 2020s)

2. **Rate Series**
   - Browse series matching your filters
   - Like (👍) series you enjoy
   - Dislike (👎) series you don't like
   - Minimum: 5 likes, 10 total ratings

3. **Get Recommendations**
   - View personalized recommendations
   - See similarity scores
   - Check streaming availability

## How It Works

### Recommendation Algorithm

Series Architect uses a weighted feature similarity approach:

1. **Feature Extraction**: Each series is represented as a feature vector containing:
   - Genre overlap (30% weight)
   - Keywords similarity (35% weight)
   - Year proximity (10% weight)
   - Origin country (10% weight)
   - Popularity level (8% weight)
   - Content rating (4% weight)
   - Number of seasons (3% weight)

2. **User Profile Building**: 
   - Aggregates liked series into a "virtual series"
   - Anchor series get 2x weight
   - Disliked series are tracked separately

3. **Similarity Calculation**:
   - Calculates weighted similarity to user profile
   - Uses Jaccard similarity for categorical features
   - Normalized distance for numerical features

4. **Dislike Exclusion**:
   - Identifies series too similar to dislikes (>0.7 threshold)
   - Removes them from candidates

5. **Ranking & Results**:
   - Sorts by similarity score
   - Returns top N recommendations
   - Enriches with metadata

### Configuration

All algorithm parameters are configurable in `src/logic_layer/config.py`:

```python
# Feature weights (must sum to 1.0)
FEATURE_WEIGHTS = {
    'genres': 0.30,
    'keywords': 0.35,
    'year_proximity': 0.10,
    'origin_country': 0.10,
    'popularity': 0.08,
    'content_rating': 0.04,
    'number_of_seasons': 0.03
}

# Minimum requirements
MIN_LIKES = 5
MIN_TOTAL_RATINGS = 10

# Dislike exclusion threshold
DISLIKE_EXCLUSION_THRESHOLD = 0.7
```

## Database Schema

The system uses 7 main tables:

**Core Tables:**
- `series` - Main series catalog
- `genres` - Genre definitions
- `keywords` - Keyword/theme definitions
- `streaming_providers` - Streaming service providers

**Relationship Tables:**
- `series_genres` - Series-to-genre mapping
- `series_keywords` - Series-to-keyword mapping
- `series_availability` - Series availability per provider/country

See `src/data_layer/DATA_LAYER_README.md` for complete schema details.

## Performance Optimization

- **Caching**: Series data, genres, and keywords are cached in memory
- **Batch Queries**: Database queries are optimized to fetch in batches
- **Pre-filtering**: Reduces candidate pool before expensive similarity calculations
- **Indexed Lookups**: Database indexes on frequently queried columns

## Maintenance

### Update Existing Series

Update all series with latest TMDB data:

```bash
cd src/data_layer
python -c "from data_manager import run_maintenance_repair; run_maintenance_repair()"
```

### Add More Series

Expand catalog with additional languages:

```bash
cd src/data_layer
python -c "from data_manager import update_catalog_by_language; update_catalog_by_language('es', pages=3)"
```

## API Reference

### Main Recommendation Function

```python
from logic_layer.recommender import get_recommendations

user_ratings = [
    (1396, 1, True),   # Breaking Bad - Like (Anchor)
    (60059, 1, False), # Better Call Saul - Like
    (1668, -1, False)  # Friends - Dislike
]

filters = {
    'languages': ['en'],
    'status': ['Running', 'Ended'],
    'decades': [2000, 2010, 2020],
    'genres': [18, 80]  # Drama, Crime
}

recommendations = get_recommendations(
    user_ratings=user_ratings,
    filters=filters,
    top_n=10
)
```

See `src/logic_layer/LOGIC_LAYER_README.md` for complete API documentation.

## Development

### Running Tests

```bash
cd src/logic_layer
python test_recommendations.py
```

### Benchmarking

```bash
cd src/logic_layer
python benchmark.py
```

### Debug Mode

Enable verbose logging in `src/logic_layer/config.py`:

```python
DEBUG_MODE = True
```

## Known Limitations

1. **Single Country Focus**: Currently optimized for Israeli market (streaming providers)
2. **No User Accounts**: All ratings are session-based (no persistence across sessions)
3. **Cold Start Problem**: Requires minimum 5 likes to generate recommendations
4. **Language Limitation**: TMDB data primarily in Hebrew and English

## Future Enhancements

- **User Authentication**: Persistent user accounts and rating history
- **Collaborative Filtering**: Learn from similar users' preferences
- **Deep Learning**: Neural network-based embeddings for better similarity
- **Multi-Country Support**: Configurable streaming provider regions
- **Mobile App**: Native iOS/Android applications
- **Social Features**: Share recommendations with friends
- **Watch History Integration**: Import from streaming services

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Attribution

This product uses the TMDB API but is not endorsed or certified by TMDB.

Data provided by [The Movie Database (TMDB)](https://www.themoviedb.org/).

## Contact

Aviel Yitzhak - [GitHub](https://github.com/aviel-yitzhak)

Project Link: [https://github.com/aviel-yitzhak/SeriesArchitect](https://github.com/aviel-yitzhak/SeriesArchitect)
