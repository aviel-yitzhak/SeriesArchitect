# Series Architect - UI Layer

## Overview

The UI Layer provides a responsive web interface for Series Architect, built with Flask. It handles user interactions, session management, and communication between the frontend and the recommendation engine.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Browser)                       │
│  • HTML Templates (Jinja2)                                  │
│  • CSS (Responsive Design)                                  │
│  • JavaScript (ES6+)                                        │
│  • AJAX API Calls                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Flask Application                         │
│                      (app.py)                               │
│  • Route Handlers                                           │
│  • Session Management                                       │
│  • JSON API Endpoints                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Logic Layer                               │
│  • Recommendation Engine                                    │
│  • Filtering Logic                                          │
│  • Database Access                                          │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
ui_layer/
├── app.py                      # Flask application
│
├── templates/                  # HTML templates (Jinja2)
│   ├── index.html             # Main screen: Filters + Rating
│   └── recommendations.html    # Recommendations display
│
├── static/                     # Static assets
│   ├── css/
│   │   ├── main.css           # Main screen styles
│   │   ├── recommendations.css # Recommendations screen styles
│   │   └── style.css          # Global styles
│   │
│   ├── js/
│   │   ├── main.js            # Main screen logic
│   │   └── recommendations.js  # Recommendations screen logic
│   │
│   └── assets/
│       ├── flags/             # Country flag icons
│       │   ├── israel.png
│       │   ├── japan.png
│       │   ├── spain.png
│       │   └── usa.png
│       │
│       └── streaming/         # Streaming provider logos
│           ├── amazon.png
│           ├── apple.png
│           ├── disney.png
│           ├── hbo.png
│           ├── netflix.png
│           ├── hot.svg
│           ├── mako.svg
│           └── yes.png
│
└── requirements.txt           # UI-specific dependencies
```

## Flask Application (`app.py`)

### Configuration

```python
app = Flask(__name__)
app.secret_key = 'series_architect_secret_key_2026'  # Change in production!
```

**Security Note**: The secret key should be set via environment variable in production:
```python
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-dev-key')
```

### Routes & Endpoints

#### 1. Main Screen

```python
@app.route('/')
def index()
```

**Purpose**: Render the main screen with filters and series rating interface

**Response**: HTML template with available genres

**Template Variables**:
```python
{
    'genres': ['Action & Adventure', 'Animation', 'Comedy', ...]
}
```

---

#### 2. Get Filtered Series

```python
@app.route('/api/get-series', methods=['POST'])
def get_series()
```

**Purpose**: Fetch series matching user-selected filters

**Request Body**:
```json
{
    "languages": ["en", "ja"],
    "genres": ["Drama", "Crime"],
    "decades": [2000, 2010, 2020]
}
```

**Response**:
```json
{
    "series": [
        {
            "tmdb_id": 1396,
            "title": "Breaking Bad",
            "poster": "https://image.tmdb.org/t/p/w500/ggFHVNu6...",
            "language": "en"
        },
        ...
    ]
}
```

**Error Response**:
```json
{
    "series": [],
    "error": "Error message"
}
```

**Processing Flow**:
1. Parse filter selections from request
2. Convert genre names to genre IDs using `GENRE_CATEGORIES`
3. Call `filters.apply_filters()` to get matching series IDs
4. Fetch series details from database
5. Sort by popularity
6. Return JSON response

**Genre Name to ID Conversion**:
```python
genre_ids = []
for genre_name in data['genres']:
    if genre_name in GENRE_CATEGORIES:
        category_ids = GENRE_CATEGORIES[genre_name]
        genre_ids.extend(category_ids)
```

Example:
- User selects: "Drama"
- System converts to: `[18, 10766]` (Drama + Soap Opera)

---

#### 3. Save User Ratings

```python
@app.route('/api/save-ratings', methods=['POST'])
def save_ratings()
```

**Purpose**: Save user ratings to Flask session

**Request Body**:
```json
{
    "ratings": {
        "1396": 1,    // Breaking Bad - Like
        "60059": 1,   // Better Call Saul - Like
        "1668": -1    // Friends - Dislike
    }
}
```

**Response**:
```json
{
    "success": true
}
```

**Session Storage**:
```python
session['ratings'] = {
    '1396': 1,
    '60059': 1,
    '1668': -1
}
```

---

#### 4. Recommendations Screen

```python
@app.route('/screen-3')
def screen_3()
```

**Purpose**: Render recommendations display page

**Response**: HTML template for showing recommendations

---

#### 5. Get Recommendations

```python
@app.route('/api/get-recommendations', methods=['POST'])
def get_recommendations()
```

**Purpose**: Generate personalized recommendations based on saved ratings

**Request**: POST (no body needed - uses session data)

**Response**:
```json
{
    "recommendations": [
        {
            "tmdb_id": 1438,
            "title_en": "The Wire",
            "title_he": "הוויר",
            "score": 0.847,
            "poster_path": "/oggnxmvofLtGQvXsO9bAFyCj3p6.jpg",
            "overview": "...",
            "popularity": 120.5,
            "first_air_date": "2002-06-02",
            "status": "Ended",
            "origin_country": "US",
            "number_of_seasons": 5,
            "number_of_episodes": 60,
            "content_rating": "TV-MA",
            "genres": ["Drama", "Crime"]
        },
        ...
    ]
}
```

**Error Responses**:

No ratings in session:
```json
{
    "recommendations": [],
    "error": "No ratings found in session"
}
```

Recommendation engine error:
```json
{
    "recommendations": [],
    "error": "Error message from engine"
}
```

**Processing Flow**:
1. Retrieve ratings from Flask session
2. Convert ratings dict to list of tuples:
   ```python
   user_ratings = [
       (1396, 1, False),
       (60059, 1, False),
       (1668, -1, False)
   ]
   ```
3. Call `recommender.get_recommendations()` with 14 results (top_n=14)
4. Return JSON response

**Why 14 recommendations?**
- Displays nicely in grid layout (7 per row on desktop, 2 rows)
- Provides variety without overwhelming user
- Can be adjusted in `app.py`

---

## Frontend Architecture

### Main Screen (`index.html` + `main.js`)

#### User Interface Components

**1. Sidebar Filters**
```html
<div class="filters-sidebar">
    <!-- Language Selection -->
    <div class="filter-group">
        <h3>Languages</h3>
        <label><input type="checkbox" name="language" value="en"> English</label>
        <label><input type="checkbox" name="language" value="he"> Hebrew</label>
        <label><input type="checkbox" name="language" value="es"> Spanish</label>
        <label><input type="checkbox" name="language" value="ja"> Japanese</label>
    </div>
    
    <!-- Genre Selection -->
    <div class="filter-group">
        <h3>Genres</h3>
        <label><input type="checkbox" name="genre" value="Drama"> Drama</label>
        <label><input type="checkbox" name="genre" value="Crime"> Crime</label>
        <!-- ... more genres -->
    </div>
    
    <!-- Decade Selection -->
    <div class="filter-group">
        <h3>Decades</h3>
        <label><input type="checkbox" name="decade" value="2020"> 2020s</label>
        <label><input type="checkbox" name="decade" value="2010"> 2010s</label>
        <label><input type="checkbox" name="decade" value="2000"> 2000s</label>
    </div>
</div>
```

**2. Series Display Grid**
```html
<div class="series-grid">
    <!-- Series cards populated by JavaScript -->
</div>
```

**3. Navigation Controls**
```html
<div class="navigation">
    <button id="get-series-btn">Show Series</button>
    <button id="get-recommendations-btn">Get Recommendations</button>
</div>
```

#### JavaScript Logic (`main.js`)

**Fetch Series**
```javascript
async function fetchSeries() {
    // 1. Collect selected filters
    const languages = getSelectedCheckboxes('language');
    const genres = getSelectedCheckboxes('genre');
    const decades = getSelectedCheckboxes('decade').map(Number);
    
    // 2. Send to API
    const response = await fetch('/api/get-series', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ languages, genres, decades })
    });
    
    // 3. Render series grid
    const data = await response.json();
    displaySeries(data.series);
}
```

**Display Series**
```javascript
function displaySeries(series) {
    const grid = document.querySelector('.series-grid');
    grid.innerHTML = '';
    
    series.forEach(show => {
        const card = createSeriesCard(show);
        grid.appendChild(card);
    });
}

function createSeriesCard(show) {
    const card = document.createElement('div');
    card.className = 'series-card';
    card.innerHTML = `
        <img src="${show.poster || 'placeholder.jpg'}" alt="${show.title}">
        <h3>${show.title}</h3>
        <div class="rating-buttons">
            <button class="like-btn" data-id="${show.tmdb_id}">👍</button>
            <button class="dislike-btn" data-id="${show.tmdb_id}">👎</button>
        </div>
    `;
    return card;
}
```

**Handle Ratings**
```javascript
const ratings = {};  // Global ratings object

function handleLike(tmdbId) {
    ratings[tmdbId] = 1;
    updateCardState(tmdbId, 'liked');
}

function handleDislike(tmdbId) {
    ratings[tmdbId] = -1;
    updateCardState(tmdbId, 'disliked');
}

function updateCardState(tmdbId, state) {
    const card = document.querySelector(`[data-id="${tmdbId}"]`).closest('.series-card');
    card.classList.remove('liked', 'disliked');
    if (state) card.classList.add(state);
}
```

**Save Ratings & Navigate**
```javascript
async function saveRatingsAndNavigate() {
    // 1. Validate minimum ratings
    const likes = Object.values(ratings).filter(r => r === 1).length;
    const total = Object.keys(ratings).length;
    
    if (likes < 5 || total < 10) {
        alert('Please rate at least 5 series positively and 10 total');
        return;
    }
    
    // 2. Save to session
    await fetch('/api/save-ratings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ratings })
    });
    
    // 3. Navigate to recommendations
    window.location.href = '/screen-3';
}
```

---

### Recommendations Screen (`recommendations.html` + `recommendations.js`)

#### User Interface

**Recommendations Grid**
```html
<div class="recommendations-container">
    <h1>Your Personalized Recommendations</h1>
    <div class="recommendations-grid">
        <!-- Recommendation cards populated by JavaScript -->
    </div>
    <button id="back-btn">Rate More Series</button>
</div>
```

#### JavaScript Logic (`recommendations.js`)

**Fetch Recommendations**
```javascript
async function fetchRecommendations() {
    try {
        const response = await fetch('/api/get-recommendations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            return;
        }
        
        displayRecommendations(data.recommendations);
    } catch (error) {
        showError('Failed to load recommendations');
    }
}
```

**Display Recommendations**
```javascript
function displayRecommendations(recommendations) {
    const grid = document.querySelector('.recommendations-grid');
    
    recommendations.forEach(rec => {
        const card = createRecommendationCard(rec);
        grid.appendChild(card);
    });
}

function createRecommendationCard(rec) {
    const card = document.createElement('div');
    card.className = 'recommendation-card';
    
    // Calculate score bar width
    const scorePercent = Math.round(rec.score * 100);
    
    card.innerHTML = `
        <img src="https://image.tmdb.org/t/p/w500${rec.poster_path}" 
             alt="${rec.title_en}">
        
        <div class="card-content">
            <h3>${rec.title_en}</h3>
            ${rec.title_he ? `<p class="hebrew-title">${rec.title_he}</p>` : ''}
            
            <div class="score-bar">
                <div class="score-fill" style="width: ${scorePercent}%"></div>
                <span class="score-text">${scorePercent}% Match</span>
            </div>
            
            <div class="metadata">
                <span class="year">${rec.first_air_date?.substring(0, 4) || 'N/A'}</span>
                <span class="seasons">${rec.number_of_seasons} Season${rec.number_of_seasons !== 1 ? 's' : ''}</span>
                <span class="status">${rec.status}</span>
                <span class="rating">${rec.content_rating}</span>
            </div>
            
            <div class="genres">
                ${rec.genres.map(g => `<span class="genre-tag">${g}</span>`).join('')}
            </div>
            
            <p class="overview">${truncate(rec.overview, 150)}</p>
        </div>
    `;
    
    return card;
}
```

**Score Visualization**
```javascript
function getScoreColor(score) {
    if (score >= 0.8) return '#10b981';  // Green - Excellent match
    if (score >= 0.6) return '#f59e0b';  // Orange - Good match
    return '#6b7280';                     // Gray - Fair match
}
```

---

## Styling (`CSS`)

### Global Styles (`style.css`)

**Color Scheme**
```css
:root {
    --primary-color: #2563eb;      /* Blue */
    --secondary-color: #10b981;    /* Green */
    --danger-color: #ef4444;       /* Red */
    --background: #0f172a;         /* Dark blue */
    --card-background: #1e293b;    /* Lighter blue */
    --text-primary: #f1f5f9;       /* Light gray */
    --text-secondary: #94a3b8;     /* Medium gray */
}
```

**Responsive Breakpoints**
```css
/* Mobile: < 768px */
@media (max-width: 768px) {
    .series-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Tablet: 768px - 1024px */
@media (min-width: 768px) and (max-width: 1024px) {
    .series-grid {
        grid-template-columns: repeat(4, 1fr);
    }
}

/* Desktop: > 1024px */
@media (min-width: 1024px) {
    .series-grid {
        grid-template-columns: repeat(6, 1fr);
    }
}
```

### Main Screen Styles (`main.css`)

**Sidebar Layout**
```css
.container {
    display: flex;
    height: 100vh;
}

.filters-sidebar {
    width: 250px;
    background: var(--card-background);
    padding: 20px;
    overflow-y: auto;
}

.main-content {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
}
```

**Series Cards**
```css
.series-card {
    background: var(--card-background);
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.2s;
}

.series-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

.series-card img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
}

.series-card.liked {
    border: 2px solid var(--secondary-color);
}

.series-card.disliked {
    border: 2px solid var(--danger-color);
    opacity: 0.5;
}
```

**Rating Buttons**
```css
.rating-buttons {
    display: flex;
    gap: 8px;
    padding: 12px;
}

.like-btn, .dislike-btn {
    flex: 1;
    padding: 8px;
    border: none;
    border-radius: 4px;
    font-size: 20px;
    cursor: pointer;
    transition: transform 0.1s;
}

.like-btn:hover {
    transform: scale(1.1);
    background: var(--secondary-color);
}

.dislike-btn:hover {
    transform: scale(1.1);
    background: var(--danger-color);
}
```

### Recommendations Styles (`recommendations.css`)

**Grid Layout**
```css
.recommendations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 24px;
    padding: 24px;
}
```

**Score Bar**
```css
.score-bar {
    position: relative;
    height: 24px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    overflow: hidden;
    margin: 12px 0;
}

.score-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    transition: width 0.3s ease;
}

.score-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-weight: bold;
    font-size: 12px;
}
```

**Metadata Tags**
```css
.metadata {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 12px 0;
}

.metadata span {
    background: rgba(255, 255, 255, 0.1);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.genre-tag {
    display: inline-block;
    background: var(--primary-color);
    color: white;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 12px;
    margin: 4px;
}
```

---

## Session Management

### Session Data Structure

```python
session = {
    'ratings': {
        '1396': 1,    # tmdb_id: rating (1 or -1)
        '60059': 1,
        '1668': -1
    }
}
```

### Session Lifecycle

1. **User rates series** → Saved to browser memory (JavaScript object)
2. **User clicks "Get Recommendations"** → POST to `/api/save-ratings`
3. **Server saves to Flask session** → `session['ratings'] = ratings`
4. **User navigates to recommendations** → GET `/screen-3`
5. **Recommendations page loads** → POST to `/api/get-recommendations`
6. **Server reads from session** → `ratings = session.get('ratings')`

### Session Security

**Current Implementation** (Development):
```python
app.secret_key = 'series_architect_secret_key_2026'
```

**Production Implementation**:
```python
import os
app.secret_key = os.getenv('FLASK_SECRET_KEY')
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Error Handling

### Frontend Error Display

```javascript
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    
    setTimeout(() => errorDiv.remove(), 5000);
}
```

### Backend Error Responses

**Filter API Error**:
```python
try:
    series_ids = filters_module.apply_filters(filters_dict)
    # ... process results
except Exception as e:
    print(f"Error fetching series: {e}")
    traceback.print_exc()
    return jsonify({'series': [], 'error': str(e)}), 500
```

**Recommendations API Error**:
```python
try:
    recommendations = recommender_module.get_recommendations(...)
    return jsonify({'recommendations': recommendations})
except Exception as e:
    print(f"Error getting recommendations: {e}")
    traceback.print_exc()
    return jsonify({'recommendations': [], 'error': str(e)}), 500
```

---

## Development Workflow

### Running the Application

```bash
cd src/ui_layer
python app.py
```

Server starts at `http://localhost:5000`

### Debug Mode

Enable Flask debug mode for auto-reload:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**Features**:
- Auto-reload on code changes
- Detailed error pages
- Interactive debugger

**Warning**: Never use `debug=True` in production!

### Testing API Endpoints

**Using curl**:
```bash
# Get series with filters
curl -X POST http://localhost:5000/api/get-series \
  -H "Content-Type: application/json" \
  -d '{"languages": ["en"], "genres": ["Drama"]}'

# Save ratings
curl -X POST http://localhost:5000/api/save-ratings \
  -H "Content-Type: application/json" \
  -d '{"ratings": {"1396": 1, "60059": 1}}'
```

**Using Postman**:
1. Create POST request to `http://localhost:5000/api/get-series`
2. Set header `Content-Type: application/json`
3. Set body (raw JSON):
   ```json
   {
       "languages": ["en"],
       "genres": ["Drama", "Crime"],
       "decades": [2010, 2020]
   }
   ```

---

## Performance Optimization

### Frontend Optimization

**Lazy Loading Images**:
```javascript
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}
```

**Debounced Filter Updates**:
```javascript
let filterTimeout;

function onFilterChange() {
    clearTimeout(filterTimeout);
    filterTimeout = setTimeout(() => {
        fetchSeries();
    }, 300);  // Wait 300ms after last change
}
```

### Backend Optimization

**Batch Database Queries**:
```python
# Instead of N queries
for series_id in series_ids:
    series = fetch_query("SELECT * FROM series WHERE tmdb_id = %s", (series_id,))

# Use single query with IN clause
placeholders = ','.join(['%s'] * len(series_ids))
query = f"SELECT * FROM series WHERE tmdb_id IN ({placeholders})"
all_series = fetch_query(query, tuple(series_ids))
```

**Response Compression**:
```python
from flask import Flask
from flask_compress import Compress

app = Flask(__name__)
Compress(app)  # Automatic gzip compression
```

---

## Deployment

### Production Configuration

**Environment Variables**:
```bash
export FLASK_SECRET_KEY="your-secure-random-key-here"
export FLASK_ENV=production
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
```

**Production WSGI Server** (Gunicorn):
```bash
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Nginx Reverse Proxy**:
```nginx
server {
    listen 80;
    server_name seriesarchitect.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/ui_layer/static;
        expires 30d;
    }
}
```

### Static File Serving

**Development**: Flask serves static files
**Production**: Nginx serves static files directly (faster)

---

## Known Issues & Limitations

### Session Persistence

- Sessions are server-side (Flask default)
- Server restart clears all sessions
- No cross-device session sharing

**Solution**: Use Redis or database-backed sessions

### TMDB Image Loading

- Images hosted on TMDB CDN
- May be slow for some users
- No local caching

**Solution**: Implement image proxy/cache

### No Real-Time Updates

- Series data is static until manual refresh
- Recommendations don't update live

**Solution**: WebSocket support for real-time updates

---

## Future Enhancements

### UI Improvements

1. **Advanced Filters**
   - Streaming provider filter
   - IMDb rating filter
   - Episode count filter

2. **Search Functionality**
   - Real-time series search
   - Autocomplete suggestions
   - Search by actor/creator

3. **User Profile**
   - Persistent account system
   - Rating history
   - Recommendation history

4. **Social Features**
   - Share recommendations
   - Compare with friends
   - Public watchlists

### Technical Improvements

1. **Progressive Web App (PWA)**
   - Offline support
   - Install to home screen
   - Push notifications

2. **API Rate Limiting**
   - Prevent abuse
   - Fair usage policies

3. **Analytics**
   - Track user behavior
   - A/B testing
   - Performance monitoring

4. **Internationalization**
   - Multi-language UI
   - RTL support for Hebrew
   - Localized content

---

## Troubleshooting

### Common Issues

**Issue**: Series images not loading

**Solution**: Check TMDB poster_path is valid
```javascript
const posterUrl = show.poster_path 
    ? `https://image.tmdb.org/t/p/w500${show.poster_path}`
    : '/static/assets/placeholder.jpg';
```

**Issue**: Ratings not persisting across page refresh

**Solution**: Ratings are session-based. Use `localStorage` for client-side persistence:
```javascript
// Save ratings to localStorage
localStorage.setItem('ratings', JSON.stringify(ratings));

// Load ratings on page load
const savedRatings = JSON.parse(localStorage.getItem('ratings') || '{}');
```

**Issue**: "No ratings found in session" error

**Solution**: Ensure ratings are saved before navigating:
```javascript
await fetch('/api/save-ratings', {
    method: 'POST',
    body: JSON.stringify({ ratings })
});
// Wait for response before navigating
```

---

## Browser Compatibility

**Supported Browsers**:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Features Requiring Polyfills**:
- Fetch API (IE11)
- Promise (IE11)
- CSS Grid (IE11)

**Recommendation**: Use modern browsers, no IE11 support needed for MVP.

---

## License & Attribution

This product uses the TMDB API but is not endorsed or certified by TMDB.

Series posters and metadata provided by [The Movie Database (TMDB)](https://www.themoviedb.org/).
