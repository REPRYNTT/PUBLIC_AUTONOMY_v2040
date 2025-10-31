# Grokipedia Freedom Scraper 🦅🇺🇸

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)](https://selenium.dev/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-red.svg)](https://flask.palletsprojects.com/)

A patriotic American-themed web scraper for [Grokipedia](https://grokipedia.com/) that preserves freedoms by extracting truth and knowledge. Features a beautiful 1980s retro patriotic interface with eagles, flags, and freedom-inspired design.

![Freedom Scraper](https://img.shields.io/badge/FREEDOM-ENABLED-FF0000?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJDMTMuMSAyIDI0IDguOSA4IDE4QzMuMSAxOCAzIDIwIDMgMTJDMzEwIDkgMTIgMkMxMiAyIDEyIDJaIiBmaWxsPSIjRkYwMDAwIi8+CjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjMiIGZpbGw9IiNGRkZGRkYiLz4KPC9zdmc+)

> **"In knowledge we trust... but in freedom we believe!"** 🇺🇸⚖️

## ✨ Features

- **🇺🇸 Patriotic American Theme**: Red, white, and blue interface with eagle animations
- **🔍 Intelligent Search**: Find articles across Grokipedia's 800k+ knowledge base
- **📄 Full Article Extraction**: Scrape complete articles with sections and references
- **🌐 Web Interface**: Beautiful Flask-based UI with real-time progress
- **💾 JSON Export**: Download structured data for analysis
- **⚡ Browser Automation**: Selenium-powered scraping for JavaScript compatibility
- **🆓 Freedom-Focused**: Open source tool for knowledge liberation

## Available Scripts

### 1. Basic HTTP Scraper (`grokipedia_scraper.py`)
Extracts data from the main page and attempts various search patterns.

### 2. Browser-Based Scraper (`grokipedia_browser_scraper.py`)
Uses Selenium to interact with the JavaScript-based search interface for full functionality.

### 3. Web Interface (`grokipedia_web_app.py`)
Flask-based web application providing a user-friendly browser interface for scraping.

## Features

- Query specific subjects on Grokipedia
- Extract article content, sections, links, and metadata
- Output results in JSON or human-readable text format
- Handles different types of pages (articles, search results, main page)

## Installation

### Basic Scraper
```bash
pip install -r requirements.txt
```

### Browser-Based Scraper
```bash
pip install -r requirements_browser.txt
```

### Web Interface
```bash
pip install -r requirements_web.txt
```

**Note:** For browser-based tools, you also need:
- Google Chrome installed
- ChromeDriver (automatically managed by selenium, or download from https://chromedriver.chromium.org/)

## Usage

### Basic HTTP Scraper

#### Basic Usage
```bash
python grokipedia_scraper.py "subject name"
```

#### Examples
Query about a specific topic:
```bash
python grokipedia_scraper.py "artificial intelligence"
```

Save results to a file:
```bash
python grokipedia_scraper.py "machine learning" -o results.json
```

Output in text format:
```bash
python grokipedia_scraper.py "neural networks" -f text
```

### Browser-Based Scraper

#### Basic Usage
```bash
python grokipedia_browser_scraper.py "subject name"
```

#### Examples
Query with browser automation:
```bash
python grokipedia_browser_scraper.py "artificial intelligence"
```

Run in visible browser mode (see the search in action):
```bash
python grokipedia_browser_scraper.py "machine learning" --visible
```

Save results to a file:
```bash
python grokipedia_browser_scraper.py "neural networks" -o results.json
```

Scrape search results AND full article content:
```bash
python grokipedia_browser_scraper.py "quantum theory" --scrape-articles -o full_data.json
```

Scrape up to 5 articles with full content:
```bash
python grokipedia_browser_scraper.py "mars exploration" --scrape-articles --max-articles 5 -o mars_data.json
```

### Web Interface

#### Starting the Web App
```bash
# Option 1: Direct launcher
python start_web_app.py

# Option 2: Direct Flask app
python grokipedia_web_app.py
```

Then open your browser and go to: `http://localhost:5000`

#### Web Interface Features
- **Search Form**: Enter search queries directly in your browser
- **Options**: Choose whether to scrape full articles and set maximum article count
- **Real-time Progress**: See live updates during scraping
- **Results Display**: View search results and scraped articles in an organized interface
- **Download**: Download complete results as JSON files
- **No Command Line**: Everything done through the web interface

### Command Line Options

Both scripts support:
- `subject`: The subject to search for (required)
- `-o, --output`: Output file path (optional, defaults to stdout)
- `-f, --format`: Output format - 'json' or 'text' (default: json)

Browser scraper additional options:
- `--visible`: Run browser in visible mode (not headless)
- `--scrape-articles`: Also scrape the full content of individual articles
- `--max-articles`: Maximum number of articles to scrape (default: 3)

## Output Format

### JSON Output
Contains structured data including:
- `url`: The page URL
- `title`: Page title
- `content`: Full text content
- `sections`: List of headings with levels
- `links`: List of links found on the page
- `metadata`: Page metadata
- `results`: Array of search results (when applicable)

### Text Output
Human-readable format with:
- Subject and title information
- Content preview (first 1000 characters)
- Section headings
- Related links
- Search results summary

## Understanding Grokipedia's Search System

Grokipedia uses a modern Next.js application with client-side JavaScript search functionality. This means:

- **Basic HTTP Scraper**: Can access the main page but cannot perform searches (returns main page content)
- **Browser-Based Scraper**: Navigates directly to search result URLs (e.g., `/search?q=topic`) and extracts loaded content

### Search URL Structure

Grokipedia uses direct URL-based search:

1. **Search URLs**: `https://grokipedia.com/search?q=search+term`
2. **Direct Navigation**: Browser goes directly to search result pages
3. **Content Extraction**: Scrapes the fully loaded search results
4. **No JavaScript Interaction**: Avoids form interaction by using URL construction

## Error Handling

Both scripts handle various scenarios:
- Network errors and timeouts
- Missing pages or subjects
- Different website structures
- Browser automation failures

## Dependencies

### Basic Scraper
- `requests`: For HTTP requests
- `beautifulsoup4`: For HTML parsing
- `urllib3`: Included with requests for URL handling

### Browser Scraper
- `selenium`: For browser automation
- `requests`: For HTTP requests
- `beautifulsoup4`: For HTML parsing

### Web Interface
- `selenium`: For browser automation
- `requests`: For HTTP requests
- `beautifulsoup4`: For HTML parsing
- `flask`: For web application framework

## Troubleshooting

### Browser Scraper Issues
- Ensure Chrome is installed
- If ChromeDriver issues occur, try: `pip install webdriver-manager`
- For headless mode issues, use `--visible` flag to debug

### Search Not Working
The basic scraper may not find search results because Grokipedia's search is JavaScript-based. Use the browser-based scraper for full functionality.

### Dynamic Loading Issues
If the browser scraper returns "Page is still loading search results":
- Increase the timeout in the `WebDriverWait` call
- Check if the website has changed its loading patterns
- Try running in visible mode (`--visible`) to see what's happening
- The site might be experiencing high load or the search results might be empty

### No Results Found
- Verify that Grokipedia actually has articles available (check the main page counter)
- Try different search terms
- Some subjects might not have articles yet in the knowledge base
