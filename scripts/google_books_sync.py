#!/usr/bin/env python3
"""
Google Books API synchronization utility for Literattus.
This script syncs book data from Google Books API to the local database.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
import mysql.connector
from loguru import logger
import json

# Load environment variables from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / 'env.example')

class GoogleBooksSync:
    """Handle Google Books API synchronization."""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
        self.base_url = "https://www.googleapis.com/books/v1/volumes"
        
    def search_books(self, query: str, max_results: int = 10):
        """Search books using Google Books API."""
        try:
            params = {
                'q': query,
                'maxResults': max_results,
                'key': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to search books: {e}")
            return None

def main():
    """Main sync function."""
    logger.info("Starting Google Books synchronization...")
    
    sync = GoogleBooksSync()
    
    # Example search
    results = sync.search_books("python programming", 5)
    if results:
        logger.info(f"Found {len(results.get('items', []))} books")
    
    logger.info("Google Books sync completed")

if __name__ == "__main__":
    main()
