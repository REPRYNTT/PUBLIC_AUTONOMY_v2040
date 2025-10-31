#!/usr/bin/env python3
"""
Simple launcher for the Grokipedia Web Scraper
"""

import os
import sys

def main():
    print("🚀 Starting Grokipedia Web Scraper...")
    print("=" * 50)
    print("This will start a web server on http://localhost:5000")
    print("Open your browser and navigate to that URL to use the scraper.")
    print("")
    print("Press Ctrl+C to stop the server.")
    print("=" * 50)
    print("")

    # Import and run the web app
    try:
        from grokipedia_web_app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Make sure you have installed the required dependencies:")
        print("pip install -r requirements_web.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Web server stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
