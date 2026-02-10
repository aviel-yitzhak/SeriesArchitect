/**
 * Series Architect - Main Application
 * Combines filter selection and series rating with real-time updates
 */

// State Management
const state = {
    // Filters
    languages: new Set(),  // Empty by default - show all
    decades: new Set(),
    genres: new Set(),

    // Series
    allSeries: [],
    displayedSeries: [],
    ratings: {},          // { tmdb_id: 1 or -1 }
    likedOrder: [],       // Array to track order of likes
    likedSeriesCache: {}, // Cache of all liked series data { tmdb_id: series_object }

    // UI
    currentPage: 0,
    pageSize: 32,
    loading: false,
    searchQuery: ''
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeFilters();
    loadInitialSeries();
    setupInfiniteScroll();
    setupThumbnailScroll();
});

/**
 * Toggle filter accordion - close first, then open
 */
function toggleFilter(contentId) {
    const content = document.getElementById(contentId);
    const header = content.previousElementSibling;
    const isCurrentlyActive = content.classList.contains('active');

    // First, close all filters
    document.querySelectorAll('.filter-content').forEach(c => {
        c.classList.remove('active');
        c.previousElementSibling.classList.add('collapsed');
    });

    // If it wasn't active, open it after a short delay
    if (!isCurrentlyActive) {
        setTimeout(() => {
            content.classList.add('active');
            header.classList.remove('collapsed');
        }, 150);
    }
}

/**
 * Clear category - remove all selections in a category
 */
function clearCategory(event, category) {
    event.stopPropagation(); // Don't trigger accordion toggle

    // Clear state
    state[category].clear();

    // Remove selected class from all buttons in category
    const categoryButtons = document.querySelectorAll(`[data-category="${category}"]`);
    categoryButtons.forEach(btn => btn.classList.remove('selected'));

    // Reload series
    applyFiltersAndReload();
}

/**
 * Initialize all filter button handlers
 */
function initializeFilters() {
    // Filter buttons
    const allButtons = document.querySelectorAll('[data-category]');
    allButtons.forEach(button => {
        button.addEventListener('click', () => handleFilterClick(button));
    });

    // Clear all button
    const clearAllBtn = document.getElementById('clear-all-btn');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', clearAllFilters);
    }

    // Search
    const searchInput = document.getElementById('search-input');
    const clearSearchBtn = document.getElementById('clear-search');

    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                searchInput.value = '';
                state.searchQuery = '';
                clearSearchBtn.style.display = 'none';
                applyFiltersAndReload();
            }
        });
    }

    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            state.searchQuery = '';
            clearSearchBtn.style.display = 'none';
            applyFiltersAndReload();
            searchInput.focus();
        });
    }
}

/**
 * Handle filter button click
 */
function handleFilterClick(button) {
    const category = button.dataset.category;
    const value = button.dataset.value;

    // Toggle this button
    if (state[category].has(value)) {
        state[category].delete(value);
        button.classList.remove('selected');
    } else {
        state[category].add(value);
        button.classList.add('selected');
    }

    // Apply filters and reload series
    applyFiltersAndReload();
}

/**
 * Handle search input
 */
function handleSearch(e) {
    const clearSearchBtn = document.getElementById('clear-search');
    state.searchQuery = e.target.value.toLowerCase().trim();

    if (state.searchQuery) {
        clearSearchBtn.style.display = 'block';
    } else {
        clearSearchBtn.style.display = 'none';
    }

    // Debounce: wait 300ms after typing stops
    clearTimeout(state.searchTimeout);
    state.searchTimeout = setTimeout(() => {
        filterDisplayedSeries();
    }, 300);
}

/**
 * Clear all filters
 */
function clearAllFilters() {
    // Clear state
    state.languages.clear();
    state.decades.clear();
    state.genres.clear();
    state.searchQuery = '';

    // Clear all button selections
    const allButtons = document.querySelectorAll('[data-category]');
    allButtons.forEach(btn => btn.classList.remove('selected'));

    // Clear search
    const searchInput = document.getElementById('search-input');
    const clearSearchBtn = document.getElementById('clear-search');
    if (searchInput) searchInput.value = '';
    if (clearSearchBtn) clearSearchBtn.style.display = 'none';

    // Reload with no filters
    applyFiltersAndReload();
}

/**
 * Apply filters and reload series from server
 */
function applyFiltersAndReload() {
    state.currentPage = 0;
    state.displayedSeries = [];
    loadInitialSeries();
}

/**
 * Load series from server based on current filters
 */
function loadInitialSeries() {
    if (state.loading) return;
    state.loading = true;

    const grid = document.getElementById('series-grid');
    grid.innerHTML = '<div class="loading">Loading series...</div>';

    // Prepare filters
    const filters = {
        languages: state.languages.has('any') ? [] : Array.from(state.languages),
        genres: state.genres.has('any') ? [] : Array.from(state.genres),
        decades: state.decades.has('any') ? [] : Array.from(state.decades).map(d => parseInt(d))
    };

    fetch('/api/get-series', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(filters)
    })
    .then(response => response.json())
    .then(data => {
        state.allSeries = data.series || [];
        state.loading = false;

        if (state.allSeries.length === 0) {
            grid.innerHTML = '<div class="loading">No series found matching your filters</div>';
        } else {
            state.currentPage = 0;
            displayNextPage();
        }
    })
    .catch(error => {
        console.error('Error loading series:', error);
        state.loading = false;
        grid.innerHTML = '<div class="loading">Error loading series. Please try again.</div>';
    });
}

/**
 * Display next page of series
 */
function displayNextPage() {
    const start = state.currentPage * state.pageSize;
    const end = start + state.pageSize;
    const nextBatch = state.allSeries.slice(start, end);

    if (nextBatch.length === 0) return;

    state.displayedSeries = state.displayedSeries.concat(nextBatch);
    state.currentPage++;

    renderSeries();
}

/**
 * Filter displayed series by search query
 */
function filterDisplayedSeries() {
    if (!state.searchQuery) {
        state.displayedSeries = state.allSeries.slice(0, state.currentPage * state.pageSize);
    } else {
        const filtered = state.allSeries.filter(series =>
            series.title.toLowerCase().includes(state.searchQuery)
        );
        state.displayedSeries = filtered;
    }

    renderSeries();

    if (state.displayedSeries.length === 0 && state.searchQuery) {
        const grid = document.getElementById('series-grid');
        grid.innerHTML = `<div class="loading">No series found for "${state.searchQuery}"</div>`;
    }
}

/**
 * Render series grid
 */
function renderSeries() {
    const grid = document.getElementById('series-grid');
    grid.innerHTML = '';

    state.displayedSeries.forEach((series, index) => {
        // Add row separator every 8 items
        if (index > 0 && index % 8 === 0) {
            const separator = document.createElement('div');
            separator.className = 'row-separator';
            grid.appendChild(separator);
        }

        const card = createSeriesCard(series);
        grid.appendChild(card);
    });
}

/**
 * Create a single series card
 */
function createSeriesCard(series) {
    const card = document.createElement('div');
    card.className = 'series-card';
    card.dataset.tmdbId = series.tmdb_id;

    // Poster
    const posterContainer = document.createElement('div');
    posterContainer.className = 'poster-container';

    if (series.poster) {
        const img = document.createElement('img');
        img.src = series.poster;
        img.alt = series.title;
        img.loading = 'lazy';
        posterContainer.appendChild(img);
    } else {
        const placeholder = document.createElement('div');
        placeholder.className = 'poster-placeholder';
        placeholder.textContent = 'No Image';
        posterContainer.appendChild(placeholder);
    }

    // Title
    const title = document.createElement('div');
    title.className = 'series-title';
    title.textContent = series.title;

    // Rating buttons
    const ratingButtons = document.createElement('div');
    ratingButtons.className = 'rating-buttons';

    const likeBtn = document.createElement('button');
    likeBtn.className = 'rating-btn like';
    likeBtn.innerHTML = '👍';
    likeBtn.onclick = () => rateSeries(series.tmdb_id, 1);

    const dislikeBtn = document.createElement('button');
    dislikeBtn.className = 'rating-btn dislike';
    dislikeBtn.innerHTML = '👎';
    dislikeBtn.onclick = () => rateSeries(series.tmdb_id, -1);

    // Apply existing rating
    const currentRating = state.ratings[series.tmdb_id];
    if (currentRating === 1) {
        likeBtn.classList.add('selected');
    } else if (currentRating === -1) {
        dislikeBtn.classList.add('selected');
    }

    ratingButtons.appendChild(likeBtn);
    ratingButtons.appendChild(dislikeBtn);

    // Assemble
    card.appendChild(posterContainer);
    card.appendChild(title);
    card.appendChild(ratingButtons);

    return card;
}

/**
 * Rate a series (like/dislike)
 */
function rateSeries(tmdbId, rating) {
    const currentRating = state.ratings[tmdbId];

    if (currentRating === rating) {
        delete state.ratings[tmdbId];
        // Remove from liked order
        state.likedOrder = state.likedOrder.filter(id => id !== tmdbId);
        // Remove from cache
        delete state.likedSeriesCache[tmdbId];
        updateRatingUI(tmdbId, null);
    } else {
        state.ratings[tmdbId] = rating;

        // Add to liked order if it's a like
        if (rating === 1) {
            if (!state.likedOrder.includes(tmdbId)) {
                state.likedOrder.push(tmdbId);
            }
            // Cache the series data
            const series = state.allSeries.find(s => s.tmdb_id === tmdbId);
            if (series) {
                state.likedSeriesCache[tmdbId] = series;
            }
        } else if (rating === -1) {
            // Remove from liked order if changing to dislike
            state.likedOrder = state.likedOrder.filter(id => id !== tmdbId);
            delete state.likedSeriesCache[tmdbId];
        }

        updateRatingUI(tmdbId, rating);
    }

    updateCounter();
    updateThumbnails();
    checkContinueButton();
}

/**
 * Update rating UI
 */
function updateRatingUI(tmdbId, rating) {
    const card = document.querySelector(`[data-tmdb-id="${tmdbId}"]`);
    if (!card) return;

    const likeBtn = card.querySelector('.rating-btn.like');
    const dislikeBtn = card.querySelector('.rating-btn.dislike');

    // Remove all states
    likeBtn.classList.remove('selected');
    dislikeBtn.classList.remove('selected');
    card.classList.remove('liked', 'disliked');

    // Add new state
    if (rating === 1) {
        likeBtn.classList.add('selected');
        card.classList.add('liked');
    } else if (rating === -1) {
        dislikeBtn.classList.add('selected');
        card.classList.add('disliked');
    }
}

/**
 * Update likes counter
 */
function updateCounter() {
    const likesCount = Object.values(state.ratings).filter(r => r === 1).length;
    document.getElementById('likes-count').textContent = likesCount;
}

/**
 * Update thumbnails - Show ALL liked series in insertion order
 */
function updateThumbnails() {
    const container = document.getElementById('liked-thumbnails');
    container.innerHTML = '';

    // Use likedOrder with cached series data
    state.likedOrder.forEach(tmdbId => {
        // Get series from cache (persists across filter changes)
        const series = state.likedSeriesCache[tmdbId];

        if (!series) return; // Skip if not in cache

        const thumbnail = document.createElement('div');
        thumbnail.className = 'thumbnail-card';
        thumbnail.dataset.tmdbId = series.tmdb_id;

        if (series.poster) {
            const img = document.createElement('img');
            img.src = series.poster;
            img.alt = series.title;
            thumbnail.appendChild(img);
        }

        const removeBtn = document.createElement('button');
        removeBtn.className = 'thumbnail-remove';
        removeBtn.innerHTML = '×';
        removeBtn.onclick = () => rateSeries(series.tmdb_id, 1);

        thumbnail.appendChild(removeBtn);
        container.appendChild(thumbnail);
    });

    setTimeout(() => {
        const event = new Event('scroll');
        container.dispatchEvent(event);
    }, 100);
}

/**
 * Check continue button
 */
function checkContinueButton() {
    const likesCount = Object.values(state.ratings).filter(r => r === 1).length;
    const continueBtn = document.getElementById('continue-btn');

    if (likesCount >= 10) {
        continueBtn.disabled = false;
        continueBtn.onclick = goToRecommendations;
    } else {
        continueBtn.disabled = true;
        continueBtn.onclick = null;
    }
}

/**
 * Navigate to recommendations
 */
function goToRecommendations() {
    // Save ratings to session
    fetch('/api/save-ratings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ratings: state.ratings })
    })
    .then(() => {
        window.location.href = '/screen-3';
    })
    .catch(error => console.error('Error saving ratings:', error));
}

/**
 * Setup infinite scroll
 */
function setupInfiniteScroll() {
    window.addEventListener('scroll', () => {
        if (state.loading || state.searchQuery) return;

        const scrollHeight = document.documentElement.scrollHeight;
        const scrollTop = document.documentElement.scrollTop;
        const clientHeight = document.documentElement.clientHeight;

        if (scrollTop + clientHeight >= scrollHeight - 200) {
            displayNextPage();
        }
    });
}

/**
 * Setup thumbnail scrolling
 */
function setupThumbnailScroll() {
    const container = document.getElementById('liked-thumbnails');
    const leftBtn = document.getElementById('scroll-left');
    const rightBtn = document.getElementById('scroll-right');

    if (!container || !leftBtn || !rightBtn) return;

    leftBtn.onclick = () => container.scrollBy({ left: -200, behavior: 'smooth' });
    rightBtn.onclick = () => container.scrollBy({ left: 200, behavior: 'smooth' });

    function checkScrollButtons() {
        const hasOverflow = container.scrollWidth > container.clientWidth;

        if (hasOverflow) {
            leftBtn.classList.remove('hidden');
            rightBtn.classList.remove('hidden');
            leftBtn.disabled = container.scrollLeft === 0;
            rightBtn.disabled = container.scrollLeft >= container.scrollWidth - container.clientWidth - 5;
        } else {
            leftBtn.classList.add('hidden');
            rightBtn.classList.add('hidden');
        }
    }

    container.addEventListener('scroll', checkScrollButtons);
    const observer = new MutationObserver(checkScrollButtons);
    observer.observe(container, { childList: true });
}