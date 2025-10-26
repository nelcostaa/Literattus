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
from loguru import logger
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

# Load environment variables from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / 'env')

@dataclass
class BookData:
    """Structured book data from Google Books API."""
    google_books_id: str
    title: str
    authors: str
    description: str
    isbn: str
    page_count: Optional[int]
    language: str
    categories: str
    thumbnail_url: Optional[str]
    published_date: Optional[str]
    publisher: Optional[str]
    etag: Optional[str]
    self_link: Optional[str]
    
    @classmethod
    def from_google_api(cls, item: Dict[str, Any]) -> 'BookData':
        """Create BookData from Google Books API response."""
        volume_info = item.get('volumeInfo', {})
        image_links = volume_info.get('imageLinks', {})
        
        # Extract ISBN
        isbn = ''
        for identifier in volume_info.get('industryIdentifiers', []):
            if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                isbn = identifier.get('identifier', '')
                break
        
        return cls(
            google_books_id=item.get('id', ''),
            title=volume_info.get('title', 'Unknown Title'),
            authors=', '.join(volume_info.get('authors', ['Unknown Author'])),
            description=volume_info.get('description', 'No description available'),
            isbn=isbn,
            page_count=volume_info.get('pageCount'),
            language=volume_info.get('language', 'en'),
            categories=', '.join(volume_info.get('categories', [])),
            thumbnail_url=image_links.get('thumbnail'),
            published_date=volume_info.get('publishedDate'),
            publisher=volume_info.get('publisher'),
            etag=item.get('etag'),
            self_link=item.get('selfLink')
        )

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
    
    def parse_books(self, items: List[Dict[str, Any]]) -> List[BookData]:
        """Parse multiple Google Books API items into structured data."""
        books = []
        for item in items:
            try:
                book = BookData.from_google_api(item)
                books.append(book)
            except Exception as e:
                logger.warning(f"Failed to parse book item: {e}")
        return books
    
    def display_book(self, book: BookData):
        """Display book data in a nice format."""
        print(f"📚 {book.title}")
        print(f"👤 Authors: {book.authors}")
        print(f"📖 Pages: {book.page_count or 'Unknown'}")
        print(f"🌍 Language: {book.language}")
        print(f"📝 Description: {book.description[:100]}...")
        print(f"🖼️  Thumbnail: {book.thumbnail_url or 'No image'}")
        print(f"📊 Categories: {book.categories or 'No categories'}")
        print(f"📅 Published: {book.published_date or 'Unknown'}")
        print(f"🏢 Publisher: {book.publisher or 'Unknown'}")
        print("-" * 50)

def main():
    """Main sync function."""
    logger.info("Starting Google Books synchronization...")
    
    sync = GoogleBooksSync()
    
    results = sync.search_books("Budismo", 10)
    if results and 'items' in results:
        logger.info(f"Found {len(results['items'])} books")
        
        # Parse all books at once
        books = sync.parse_books(results['items'])
        logger.info(f"Successfully parsed {len(books)} books")
        
        # Display each book
        for book in books:
            sync.display_book(book)
    else:
        logger.warning("No books found or API error")
    
    logger.info("Google Books sync completed")

if __name__ == "__main__":
    main()
