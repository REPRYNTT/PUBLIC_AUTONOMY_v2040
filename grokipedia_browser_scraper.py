#!/usr/bin/env python3
"""
Grokipedia Browser-Based Data Extractor
Uses Selenium to interact with the JavaScript-based search interface.
"""

import json
import sys
import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class GrokipediaBrowserScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None

    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Make sure Chrome and chromedriver are installed.")
            print("Install with: pip install selenium")
            print("Download chromedriver from: https://chromedriver.chromium.org/")
            return False

    def search_subject(self, subject):
        """
        Search for a subject using direct URL construction
        """
        if not self.driver:
            return {"error": "Driver not initialized"}

        try:
            # Construct search URL directly (like https://grokipedia.com/search?q=quantum%20theory%20expansion)
            from urllib.parse import quote
            search_url = f"https://grokipedia.com/search?q={quote(subject)}"

            # Navigate directly to the search results page
            self.driver.get(search_url)

            # Wait for the page to load and search results to appear
            time.sleep(3)

            # Extract search results from the loaded page
            results = self.extract_search_results(subject)

            return results

        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}

    def scrape_article(self, url):
        """
        Scrape the content of an individual article page
        """
        if not self.driver:
            return {"error": "Driver not initialized"}

        try:
            # Navigate to the article page
            self.driver.get(url)

            # Wait for the page to load
            time.sleep(3)

            article_data = {
                'url': url,
                'title': '',
                'description': '',
                'author': '',
                'content': '',
                'sections': [],
                'table_of_contents': [],
                'references': []
            }

            try:
                # Get title
                title_elem = self.driver.find_element(By.TAG_NAME, 'title')
                article_data['title'] = title_elem.get_attribute('innerText')

                # Get meta description
                meta_desc = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
                article_data['description'] = meta_desc.get_attribute('content')

                # Get author
                try:
                    author_elem = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="author"]')
                    article_data['author'] = author_elem.get_attribute('content')
                except:
                    pass

                # Get table of contents
                toc_links = self.driver.find_elements(By.CSS_SELECTOR, 'nav a[href^="#"]')
                for link in toc_links:
                    href = link.get_attribute('href')
                    text = link.get_attribute('innerText').strip()
                    if text and href:
                        # Remove the # from href to get section ID
                        section_id = href.split('#')[-1] if '#' in href else ''
                        article_data['table_of_contents'].append({
                            'text': text,
                            'section_id': section_id
                        })

                # Get main article content
                try:
                    article_elem = self.driver.find_element(By.TAG_NAME, 'article')
                    article_data['content'] = article_elem.get_attribute('innerText')

                    # Extract sections from the article
                    headings = article_elem.find_elements(By.CSS_SELECTOR, 'h1, h2, h3, h4, h5, h6')
                    for heading in headings:
                        level = int(heading.tag_name[1])  # h1 -> 1, h2 -> 2, etc.
                        text = heading.get_attribute('innerText')
                        section_id = heading.get_attribute('id') or ''
                        article_data['sections'].append({
                            'level': level,
                            'text': text,
                            'id': section_id
                        })

                except:
                    # Fallback: get content from body if article tag not found
                    body = self.driver.find_element(By.TAG_NAME, 'body')
                    article_data['content'] = body.get_attribute('innerText')

                # Get references (superscript numbers)
                ref_elements = self.driver.find_elements(By.CSS_SELECTOR, 'sup')
                for ref in ref_elements:
                    text = ref.get_attribute('innerText').strip()
                    if text and text.replace('[', '').replace(']', '').isdigit():
                        article_data['references'].append(text)

            except Exception as e:
                article_data['error'] = f"Content extraction failed: {str(e)}"

            return article_data

        except Exception as e:
            return {"error": f"Article scraping failed: {str(e)}"}

    def extract_search_results(self, subject):
        """
        Extract search results from the current page
        """
        results = {
            'search_term': subject,
            'results': [],
            'page_info': {}
        }

        try:
            # Get page title
            results['page_info']['title'] = self.driver.title

            # Wait for search results to load (handle skeleton loading)
            try:
                # Wait for skeleton loaders to disappear or actual content to appear
                WebDriverWait(self.driver, 10).until(
                    lambda driver: len(driver.find_elements(By.CSS_SELECTOR, '.animate-pulse')) == 0 or
                                   len(driver.find_elements(By.CSS_SELECTOR, 'article, .card, [class*="result" i]')) > 0
                )
            except TimeoutException:
                # If timeout, continue anyway - might have partial results
                pass

            # Look for search results containers (based on HTML structure)
            result_selectors = [
                '.search-results',
                '.results',
                '[class*="result" i]',
                '[class*="search" i] li',
                '[class*="list" i] a',
                'article',
                '.card',
                '[data-testid*="result" i]',
                # Look for content that appears after loading
                '[class*="content" i] a',
                '.main a',
                # Generic link selectors for article links
                'a[href*="/article/"]',
                'a[href*="/wiki/"]'
            ]

            found_results = False

            # First, let's try to find ALL links on the page that might be results
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')

            result_links = []
            for link in all_links:
                href = link.get_attribute('href')
                text = link.text.strip()

                if text and len(text) > 2 and href:  # Lower threshold for link text
                    # Skip navigation/internal links
                    if not any(skip in href.lower() for skip in ['#', 'javascript:', 'mailto:', '/legal/', '/images/', '/favicon', '/manifest', '/login', '/toggle']):
                        # Include links that look like they could be article titles
                        if ('/article/' in href or '/wiki/' in href or
                            not href.startswith(('http://', 'https://')) or
                            'grokipedia.com' in href):
                            result_links.append((text, href))

            # If we found result links, add them to results
            for text, href in result_links[:20]:  # Limit to first 20 results
                results['results'].append({
                    'title': text,
                    'url': href if href.startswith('http') else f'https://grokipedia.com{href}',
                    'snippet': ''
                })
                found_results = True

            # If no links found, try to extract results from text content
            if not found_results:
                page_text = self.driver.find_element(By.TAG_NAME, 'body').text

                # Look for the results pattern
                if 'yielded' in page_text and 'results:' in page_text:
                    lines = page_text.split('\n')

                    # Find the results section
                    results_start = -1
                    for i, line in enumerate(lines):
                        if 'yielded' in line and 'results:' in line:
                            results_start = i + 1
                            break

                    if results_start != -1:
                        # Extract result titles (skip pagination and navigation)
                        result_count = 0
                        for line in lines[results_start:]:
                            line = line.strip()
                            if (line and len(line) > 3 and
                                not line.isdigit() and  # Skip page numbers
                                not any(nav in line.lower() for nav in ['previous', 'next', '�', '...', 'login', 'toggle']) and
                                not line.startswith('http')):  # Skip URLs

                                # Create a result entry
                                # Since these aren't links, we'll construct potential URLs
                                title = line
                                # Construct URL with /page/ and preserve original capitalization
                                # Replace spaces with underscores but keep original case
                                clean_title = title.replace('(', '').replace(')', '').replace(',', '').strip()
                                url_slug = clean_title.replace(' ', '_')
                                potential_url = f"https://grokipedia.com/page/{url_slug}"

                                results['results'].append({
                                    'title': title,
                                    'url': potential_url,
                                    'snippet': f"Search result for '{subject}'"
                                })
                                result_count += 1

                                if result_count >= 20:  # Limit results
                                    break

                        found_results = result_count > 0

            # If no structured results found, look for any relevant content
            if not found_results:
                # Look for any links that might be articles
                all_links = self.driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href')
                    text = link.text.strip()

                    if (text and len(text) > 10 and href and
                        subject.lower() in text.lower() and
                        not any(skip in href.lower() for skip in ['legal', 'images', 'favicon', 'manifest', '#', 'javascript:'])):
                        results['results'].append({
                            'title': text,
                            'url': href,
                            'snippet': self.get_element_context(link)
                        })

            # Extract page metadata
            try:
                meta_desc = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
                results['page_info']['description'] = meta_desc.get_attribute('content')
            except:
                pass

            # Check if we got actual results or just loading states
            if not results['results']:
                # Check if page still has loading skeletons
                loading_elements = self.driver.find_elements(By.CSS_SELECTOR, '.animate-pulse')
                if loading_elements:
                    results['status'] = 'loading'
                    results['message'] = 'Page is still loading search results'
                else:
                    results['status'] = 'no_results'
                    results['message'] = 'No search results found'
            else:
                results['status'] = 'success'
                results['message'] = f'Found {len(results["results"])} search results'

        except Exception as e:
            results['error'] = f"Extraction failed: {str(e)}"

        return results

    def get_element_context(self, element):
        """
        Get context around an element for snippet generation
        """
        try:
            # Get text from parent element
            parent = element.find_element(By.XPATH, '..')
            context = parent.text
            element_text = element.text

            # Remove the element text to get context
            if element_text in context:
                context = context.replace(element_text, '').strip()

            return context[:200] if len(context) > 200 else context
        except:
            return ""

    def cleanup(self):
        """Clean up the browser driver"""
        if self.driver:
            self.driver.quit()

def main():
    parser = argparse.ArgumentParser(description='Query subjects on Grokipedia using browser automation')
    parser.add_argument('subject', help='The subject to search for')
    parser.add_argument('-o', '--output', help='Output file (default: print to stdout)')
    parser.add_argument('-f', '--format', choices=['json', 'text'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--visible', action='store_true',
                       help='Run browser in visible mode (not headless)')
    parser.add_argument('--scrape-articles', action='store_true',
                       help='Also scrape the full content of individual articles')
    parser.add_argument('--max-articles', type=int, default=3,
                       help='Maximum number of articles to scrape when using --scrape-articles (default: 3)')

    args = parser.parse_args()

    scraper = GrokipediaBrowserScraper(headless=not args.visible)

    if not scraper.setup_driver():
        sys.exit(1)

    try:
        # First, get search results
        search_result = scraper.search_subject(args.subject)

        if args.scrape_articles and 'results' in search_result:
            # Scrape individual articles
            print(f"Found {len(search_result['results'])} search results. Scraping up to {args.max_articles} articles...")

            articles_data = []
            for i, result_item in enumerate(search_result['results'][:args.max_articles]):
                print(f"Scraping article {i+1}/{min(args.max_articles, len(search_result['results']))}: {result_item['title']}")
                article_data = scraper.scrape_article(result_item['url'])
                if 'error' not in article_data:
                    articles_data.append(article_data)
                else:
                    print(f"  Warning: Failed to scrape article: {article_data['error']}")

            # Combine search results with article data
            result = {
                'search_query': args.subject,
                'search_results': search_result,
                'articles': articles_data,
                'scraped_at': str(time.time())
            }
        else:
            result = search_result

        if args.format == 'json':
            output = json.dumps(result, indent=2, ensure_ascii=False)
        else:
            # Simple text format
            output = f"Subject: {args.subject}\n"
            output += "=" * 50 + "\n"

            if 'error' in result:
                output += f"Error: {result['error']}\n"
            else:
                # Show search results
                if 'results' in result:
                    output += f"Search Results found: {len(result.get('results', []))}\n\n"
                    for i, res in enumerate(result.get('results', []), 1):
                        output += f"{i}. {res['title']}\n"
                        output += f"   URL: {res['url']}\n"
                        if res.get('snippet'):
                            output += f"   Snippet: {res['snippet']}\n"
                        output += "\n"

                # Show scraped articles if available
                if 'articles' in result and result['articles']:
                    output += "\n" + "=" * 50 + "\n"
                    output += f"SCRAPED ARTICLES ({len(result['articles'])}):\n"
                    output += "=" * 50 + "\n\n"

                    for i, article in enumerate(result['articles'], 1):
                        output += f"ARTICLE {i}: {article.get('title', 'Unknown')}\n"
                        output += f"URL: {article.get('url', '')}\n"
                        if article.get('description'):
                            output += f"Description: {article.get('description', '')}\n"
                        if article.get('author'):
                            output += f"Author: {article.get('author', '')}\n"
                        output += f"Content Length: {len(article.get('content', ''))} characters\n"
                        output += f"Sections: {len(article.get('sections', []))}\n"
                        output += f"References: {len(article.get('references', []))}\n"
                        output += "-" * 30 + "\n\n"

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Results saved to {args.output}")
        else:
            print(output)

    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
