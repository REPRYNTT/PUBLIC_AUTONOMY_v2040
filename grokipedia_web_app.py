#!/usr/bin/env python3
"""
Grokipedia Web Interface
A Flask web application providing a user-friendly interface to the Grokipedia scraper.
"""

import os
import json
import time
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import tempfile
import threading

# Get the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Import our scraper
from grokipedia_browser_scraper import GrokipediaBrowserScraper

app = Flask(__name__)
app.secret_key = 'grokipedia_scraper_secret_key_2024'

# Global variables to track scraping progress
current_scraping_status = {
    'is_running': False,
    'progress': '',
    'result': None,
    'error': None
}

@app.route('/')
def home():
    """Home page with search interface"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests"""
    global current_scraping_status

    if current_scraping_status['is_running']:
        flash('A search is already in progress. Please wait.', 'warning')
        return redirect(url_for('home'))

    # Get form data
    search_query = request.form.get('query', '').strip()
    scrape_articles = 'scrape_articles' in request.form
    max_articles = int(request.form.get('max_articles', 3))
    output_format = request.form.get('format', 'json')

    if not search_query:
        flash('Please enter a search query.', 'error')
        return redirect(url_for('home'))

    # Start scraping in background thread
    current_scraping_status = {
        'is_running': True,
        'progress': f'Starting search for "{search_query}"...',
        'result': None,
        'error': None
    }

    # Run scraping in background
    def run_scraping():
        global current_scraping_status
        try:
            current_scraping_status['progress'] = f'Initializing browser for "{search_query}"...'

            scraper = GrokipediaBrowserScraper(headless=True)

            if not scraper.setup_driver():
                current_scraping_status['error'] = 'Failed to initialize browser. Make sure Chrome is installed.'
                current_scraping_status['is_running'] = False
                return

            current_scraping_status['progress'] = f'Searching for "{search_query}"...'

            # Get search results
            search_result = scraper.search_subject(search_query)

            if scrape_articles and 'results' in search_result and search_result['results']:
                current_scraping_status['progress'] = f'Found {len(search_result["results"])} results. Scraping up to {max_articles} articles...'

                articles_data = []
                for i, result_item in enumerate(search_result['results'][:max_articles]):
                    current_scraping_status['progress'] = f'Scraping article {i+1}/{min(max_articles, len(search_result["results"]))}...'
                    article_data = scraper.scrape_article(result_item['url'])
                    if 'error' not in article_data:
                        articles_data.append(article_data)

                # Combine results
                result = {
                    'search_query': search_query,
                    'search_results': search_result,
                    'articles': articles_data,
                    'scraped_at': str(time.time())
                }
            else:
                result = search_result

            current_scraping_status['progress'] = 'Search completed successfully!'
            current_scraping_status['result'] = result
            current_scraping_status['is_running'] = False

            scraper.cleanup()

        except Exception as e:
            current_scraping_status['error'] = f'Search failed: {str(e)}'
            current_scraping_status['is_running'] = False

    # Start background thread
    thread = threading.Thread(target=run_scraping)
    thread.daemon = True
    thread.start()

    return redirect(url_for('results'))

@app.route('/progress')
def get_progress():
    """Get current scraping progress"""
    return jsonify(current_scraping_status)

@app.route('/results')
def results():
    """Display search results"""
    if current_scraping_status['error']:
        flash(current_scraping_status['error'], 'error')
        return redirect(url_for('home'))

    if current_scraping_status['is_running']:
        return render_template('loading.html')

    if not current_scraping_status['result']:
        flash('No results available. Please try a search first.', 'warning')
        return redirect(url_for('home'))

    return render_template('results.html', result=current_scraping_status['result'])

@app.route('/download')
def download():
    """Download results as JSON file"""
    if not current_scraping_status['result']:
        flash('No results available to download.', 'error')
        return redirect(url_for('home'))

    # Save file to project directory
    search_query = current_scraping_status['result'].get('search_query', 'grokipedia_results')
    filename = f"{search_query.replace(' ', '_')}_results.json"
    filepath = os.path.join(PROJECT_DIR, filename)

    # Write the file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(current_scraping_status['result'], f, indent=2, ensure_ascii=False)

    # Send file for download
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/clear')
def clear_results():
    """Clear current results"""
    global current_scraping_status
    current_scraping_status = {
        'is_running': False,
        'progress': '',
        'result': None,
        'error': None
    }
    flash('Results cleared.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    print("Starting Grokipedia Web Scraper...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)
