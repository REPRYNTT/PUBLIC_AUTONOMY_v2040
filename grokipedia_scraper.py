#!/usr/bin/env python3
"""
Grokipedia Data Extractor
A script to query subjects on grokipedia.com and extract data.
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import argparse
from urllib.parse import urljoin, quote
import time

class GrokipediaScraper:
    def __init__(self, base_url="https://grokipedia.com/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_subject(self, subject):
        """
        Search for a subject on Grokipedia using the search form
        """
        try:
            # First, get the main page to understand the search mechanism
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code != 200:
                return {"error": f"Failed to load main page: {response.status_code}"}

            # Try to search by simulating form submission
            # Based on the HTML, this appears to be a Next.js app with client-side search
            search_data = {
                'query': subject,  # Try different parameter names
            }

            # Try POST to main page (common for Next.js apps)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': self.base_url,
                'Origin': self.base_url.rstrip('/'),
            }

            # Update session headers for search
            self.session.headers.update(headers)

            # Try posting to the main page (Next.js apps often handle search this way)
            response = self.session.post(self.base_url, data=search_data, timeout=10)
            if response.status_code == 200:
                return self.extract_search_results(response.text, subject)

            # Try GET with query parameter
            search_url = f"{self.base_url}?q={quote(subject)}"
            print(f"Trying search URL: {search_url}")
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                return self.extract_search_results(response.text, subject)

            # Try /search endpoint
            search_endpoint = urljoin(self.base_url, "search")
            search_params = {'q': subject}
            print(f"Trying search endpoint: {search_endpoint}")
            response = self.session.get(search_endpoint, params=search_params, timeout=10)
            if response.status_code == 200:
                return self.extract_search_results(response.text, subject)

            # Try POST to /search
            response = self.session.post(search_endpoint, data={'q': subject}, timeout=10)
            if response.status_code == 200:
                return self.extract_search_results(response.text, subject)

            # Fallback: try direct wiki URL pattern (just in case)
            direct_url = urljoin(self.base_url, f"wiki/{quote(subject.replace(' ', '_'))}")
            print(f"Trying direct URL: {direct_url}")
            response = self.session.get(direct_url, timeout=10)
            if response.status_code == 200:
                return self.extract_article_data(response.text, direct_url)

        except requests.RequestException as e:
            return {"error": f"Network error: {str(e)}"}

        return {"error": "Could not find the requested subject"}

    def extract_article_data(self, html_content, url):
        """
        Extract data from an article page
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        data = {
            'url': url,
            'title': '',
            'content': '',
            'sections': [],
            'links': [],
            'metadata': {}
        }

        # Extract title
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            data['title'] = title_elem.get_text().strip()

        # Extract main content
        content_div = soup.find('div', {'id': 'content'}) or soup.find('div', {'class': 'content'})
        if not content_div:
            # Try common content selectors
            content_div = soup.find('main') or soup.find('article') or soup.find('div', {'class': 'mw-content'})

        if content_div:
            # Extract text content
            data['content'] = content_div.get_text().strip()

            # Extract sections (headings)
            headings = content_div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in headings:
                data['sections'].append({
                    'level': int(heading.name[1]),
                    'text': heading.get_text().strip()
                })

            # Extract links
            links = content_div.find_all('a', href=True)
            for link in links:
                href = link['href']
                if not href.startswith(('http://', 'https://', '#', 'javascript:')):
                    href = urljoin(self.base_url, href)
                data['links'].append({
                    'text': link.get_text().strip(),
                    'url': href
                })

        # Extract metadata
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                data['metadata'][name] = content

        return data

    def extract_search_results(self, html_content, subject):
        """
        Extract search results from a search page (Next.js application)
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        results = {
            'search_term': subject,
            'results': [],
            'page_info': {}
        }

        # Check if we got search results or redirected to an article
        title_tag = soup.find('title')
        if title_tag and subject.lower() not in title_tag.get_text().lower():
            # Might be an article page, try to extract article data instead
            return self.extract_article_data(html_content, soup.find('meta', property='og:url')['content'] if soup.find('meta', property='og:url') else self.base_url)

        # Look for search results in various formats
        # Check for JSON data in script tags (Next.js often embeds data)
        script_tags = soup.find_all('script', {'type': 'application/json'})
        for script in script_tags:
            try:
                if script.string:
                    json_data = json.loads(script.string)
                    # Look for search results in the JSON data
                    if isinstance(json_data, dict):
                        self._extract_from_json(json_data, results)
            except (json.JSONDecodeError, TypeError):
                continue

        # Look for search results in HTML structure
        # Common patterns for search results
        search_containers = soup.find_all(['div', 'section', 'ul', 'ol'], class_=lambda x: x and any(term in x.lower() for term in ['search', 'result', 'list', 'item']))
        for container in search_containers:
            links = container.find_all('a', href=True)
            for link in links:
                href = link['href']
                text = link.get_text().strip()
                if text and len(text) > 3:  # Filter out very short links
                    if not href.startswith(('http://', 'https://')):
                        href = urljoin(self.base_url, href)
                    results['results'].append({
                        'title': text,
                        'url': href,
                        'snippet': self._get_link_context(link)
                    })

        # Look for any links that might be articles
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href']
            text = link.get_text().strip()
            # Filter for potentially relevant links
            if (text and len(text) > 10 and
                not href.startswith(('#', 'javascript:', 'mailto:')) and
                not any(skip in href.lower() for skip in ['/legal/', '/images/', '/favicon', '/manifest'])):
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(self.base_url, href)
                # Avoid duplicates
                if not any(r['url'] == href for r in results['results']):
                    results['results'].append({
                        'title': text,
                        'url': href,
                        'snippet': self._get_link_context(link)
                    })

        # Extract page metadata
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            results['page_info']['description'] = meta_desc.get('content', '')

        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title:
            results['page_info']['og_title'] = og_title.get('content', '')

        return results

    def _extract_from_json(self, json_data, results):
        """
        Extract search results from JSON data embedded in the page
        """
        def recursive_search(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if key.lower() in ['results', 'articles', 'search', 'data']:
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    title = item.get('title', item.get('name', ''))
                                    url = item.get('url', item.get('link', ''))
                                    if title and url:
                                        results['results'].append({
                                            'title': title,
                                            'url': url,
                                            'snippet': item.get('description', item.get('snippet', ''))
                                        })
                    recursive_search(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    recursive_search(item, f"{path}[{i}]")

        recursive_search(json_data)

    def _get_link_context(self, link_element):
        """
        Get context around a link element for snippet generation
        """
        context = ""
        # Get text from parent elements
        parent = link_element.parent
        if parent:
            context = parent.get_text().strip()
            # Remove the link text itself to avoid duplication
            link_text = link_element.get_text().strip()
            if link_text in context:
                context = context.replace(link_text, '').strip()
        return context[:200] if len(context) > 200 else context

    def extract_main_page_data(self, html_content, subject):
        """
        Extract data from the main page related to a subject
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        data = {
            'subject': subject,
            'main_page_info': {},
            'related_content': []
        }

        # Extract page title
        title = soup.find('title')
        if title:
            data['main_page_info']['title'] = title.get_text().strip()

        # Look for any mentions of the subject
        text_content = soup.get_text().lower()
        if subject.lower() in text_content:
            data['main_page_info']['subject_mentioned'] = True
        else:
            data['main_page_info']['subject_mentioned'] = False

        # Extract all links that might be related
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            text = link.get_text().strip()
            if subject.lower() in text.lower():
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(self.base_url, href)
                data['related_content'].append({
                    'text': text,
                    'url': href
                })

        return data

def main():
    parser = argparse.ArgumentParser(description='Query subjects on Grokipedia and extract data')
    parser.add_argument('subject', help='The subject to search for')
    parser.add_argument('-o', '--output', help='Output file (default: print to stdout)')
    parser.add_argument('-f', '--format', choices=['json', 'text'], default='json',
                       help='Output format (default: json)')

    args = parser.parse_args()

    scraper = GrokipediaScraper()
    result = scraper.search_subject(args.subject)

    if args.format == 'json':
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        # Simple text format
        output = f"Subject: {args.subject}\n"
        output += "=" * 50 + "\n"

        if 'error' in result:
            output += f"Error: {result['error']}\n"
        elif 'title' in result:
            output += f"Title: {result['title']}\n"
            output += f"URL: {result['url']}\n\n"
            output += f"Content:\n{result['content'][:1000]}{'...' if len(result['content']) > 1000 else ''}\n\n"

            if result['sections']:
                output += "Sections:\n"
                for section in result['sections']:
                    output += f"  {'#' * section['level']} {section['text']}\n"
                output += "\n"

            if result['links']:
                output += "Links:\n"
                for link in result['links'][:10]:  # Limit to first 10 links
                    output += f"  {link['text']}: {link['url']}\n"
        else:
            output += "Search results or general information:\n"
            output += json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Results saved to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()
