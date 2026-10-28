import os
import json
from flask import Flask, request, jsonify, render_template_string, send_from_directory, redirect

app = Flask(__name__)


def load_books_data():
    """Loads dataset from booksmain.json or books.json if present."""
    for file_name in ['booksmain.json', 'books.json']:
        if os.path.exists(file_name):
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {file_name}: {e}")
    return []


@app.route('/images/<path:filename>')
def serve_images(filename):
    """
    Maps HTML requested image paths to your local WhatsApp images in root
    or provides fallback URLs to fix 404 errors instantly.
    """
    
    local_image_map = {
        'hero-book.png': 'WhatsApp Image 2026-08-08 at 11.49.54 AM.jpeg',
        'atomic-habits.jpg': 'WhatsApp Image 2026-08-08 at 11.49.53 AM.jpeg',
        'hobbit.jpg': 'WhatsApp Image 2026-08- AM.jpeg',
        'ikigai.jpg': 'WhatsApp Image 2026-08-08 at 11.49.55 AM.jpeg',
        'dune.jpg': 'WhatsApp Image 2026-08.jpeg'
    }

    target_file = local_image_map.get(filename, filename)

    
    if os.path.exists(target_file):
        return send_from_directory(os.getcwd(), target_file)

    
    images_dir = os.path.join(os.getcwd(), 'images')
    if os.path.exists(os.path.join(images_dir, filename)):
        return send_from_directory(images_dir, filename)


    if filename == 'logo.png':
        return redirect('https://cdn-icons-png.flaticon.com/512/3389/3389081.png')

    
    return redirect('https://via.placeholder.com/300x450?text=Book+Cover')

@app.route('/script.js')
def serve_script():
    """Serves script.js or script (1).js to eliminate 404 script error."""
    if os.path.exists('script.js'):
        return send_from_directory(os.getcwd(), 'script.js')
    elif os.path.exists('script (1).js'):
        return send_from_directory(os.getcwd(), 'script (1).js')
    return "", 404

@app.route('/style.css')
def serve_style():
    """Serves the main CSS file."""
    return send_from_directory(os.getcwd(), 'style.css')

@app.route('/favicon.ico')
def favicon():
    """Prevents favicon 404 logs in terminal."""
    return "", 204


@app.route('/')
def home():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        return "<h1>Error: index.html not found!</h1>"

    
    dynamic_script = """
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const searchInput = document.querySelector('.search-box input');
            const searchBtn = document.querySelector('.search-box button');
            const exploreBtn = document.querySelector('.explore-btn');
            const navLinks = document.querySelectorAll('.nav-links a');
            const featuredSection = document.querySelector('.featured-books');

            // --- Function: Render Books to Grid ---
            function renderBooks(books, sectionTitle, subtitle) {
                const grid = document.querySelector('.books-grid');
                const titleH2 = document.querySelector('.section-title h2');
                const titleP = document.querySelector('.section-title p');

                if (titleH2) titleH2.innerText = sectionTitle || 'Recommended Books';
                if (titleP) titleP.innerText = subtitle || 'Handpicked titles from our collection';

                if (!grid) return;
                grid.innerHTML = '';

                if (!books || books.length === 0) {
                    grid.innerHTML = '<p style="color:#bdbdbd; font-size:18px; text-align:center; grid-column: 1/-1;">No matching books found. Try searching for "Science Fiction", "Fantasy", or "Asimov"!</p>';
                    return;
                }

                books.forEach(book => {
                    grid.innerHTML += `
                        <div class="book-card" style="animation: navbarFade 0.4s ease;">
                            <img src="${book.coverImage || 'https://via.placeholder.com/300x450?text=No+Cover'}" 
                                 alt="${book.title}" 
                                 onerror="this.src='https://via.placeholder.com/300x450?text=No+Cover'">
                            <div class="book-info">
                                <h3 style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${book.title}">${book.title}</h3>
                                <p style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${book.author}">${book.author || 'Unknown Author'}</p>
                                <span class="rating">⭐ ${book.rating || '4.0'}</span>
                                <span class="genre">${book.genre || 'General'}</span>
                            </div>
                        </div>
                    `;
                });
            }

            // --- Function: Fetch Recommendations from Flask Backend ---
            function getRecommendations(queryText) {
                fetch('/recommend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: queryText })
                })
                .then(res => res.json())
                .then(data => {
                    const subText = queryText ? `Results matching: "${queryText}"` : 'Top rated recommendations';
                    renderBooks(data, 'Recommended For You', subText);
                    if (featuredSection) featuredSection.scrollIntoView({ behavior: 'smooth' });
                })
                .catch(err => console.error("API Error:", err));
            }

            // --- 1. Search Bar & Explore Button Handlers ---
            if (searchBtn && searchInput) {
                searchBtn.addEventListener('click', () => getRecommendations(searchInput.value.trim()));
                searchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') getRecommendations(searchInput.value.trim());
                });
            }

            if (exploreBtn) {
                exploreBtn.addEventListener('click', () => {
                    if (searchInput) searchInput.value = 'Science Fiction';
                    getRecommendations('Science Fiction');
                });
            }

            // --- 2. Navbar Interactivity (Home, Books, Genres, About, Contact) ---
            navLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    
                    navLinks.forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                    
                    const target = link.innerText.trim();

                    if (target === 'Home') {
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    } 
                    else if (target === 'Books') {
                        getRecommendations('');
                    } 
                    else if (target === 'Genres') {
                        if (searchInput) searchInput.value = 'Fantasy';
                        getRecommendations('Fantasy');
                    } 
                    else if (target === 'About' || target === 'Contact') {
                        alert(`${target} Section:\\nBookVerse is an AI-powered Rule-Based Recommendation System developed for exploring top literature across genres!`);
                    }
                });
            });
        });
    </script>
    </body>
    """
    return render_template_string(html_content.replace('</body>', dynamic_script))


@app.route('/recommend', methods=['POST'])
def recommend_books():
    data = request.json or {}
    query = data.get("query", "").lower().strip()
    
    all_books = load_books_data()
    scored_books = []

    for book in all_books:
        title = str(book.get("title", "")).lower()
        author = str(book.get("author", "")).lower()
        genre = str(book.get("genre", "")).lower()
        rating = book.get("rating") or 0.0
        
        score = 0

       
        if not query:
            score = rating * 2
        else:
            
            if query in genre:
                score += 50
           
            if query in author:
                score += 40
            
            if query in title:
                score += 30
            
            if score > 0:
                score += (rating * 2)

        if score > 0:
            scored_books.append({"book": book, "score": score})

    
    scored_books.sort(key=lambda x: x["score"], reverse=True)

    
    results = [item["book"] for item in scored_books[:8]]
    return jsonify(results)

if __name__ == '__main__':
    print("Starting BookVerse Server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)