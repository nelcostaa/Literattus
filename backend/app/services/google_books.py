"""
Google Books API integration service.
Provides methods to search and fetch book data from Google Books API.
"""

from typing import List, Optional, Dict, Any
import httpx
from loguru import logger

from app.core.config import settings


class GoogleBooksService:
    """Service for interacting with Google Books API."""
    
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google Books service.
        
        Args:
            api_key: Google Books API key (optional)
        """
        self.api_key = api_key or settings.GOOGLE_BOOKS_API_KEY
    
    async def search_books(
        self,
        query: str,
        max_results: int = 10,
        start_index: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search for books using Google Books API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            start_index: Index of first result to return
            
        Returns:
            List[Dict]: List of book data dictionaries
        """
        try:
            params = {
                "q": query,
                "maxResults": min(max_results, 40),  # Google Books API limit
                "startIndex": start_index,
            }
            
            if self.api_key:
                params["key"] = self.api_key
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.BASE_URL, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                books = []
                
                for item in data.get("items", []):
                    book_data = self._parse_book_data(item)
                    if book_data:
                        books.append(book_data)
                
                logger.info(f"Found {len(books)} books for query: {query}")
                return books
                
        except httpx.HTTPError as e:
            logger.error(f"Google Books API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in book search: {e}")
            return []
    
    async def get_book_by_id(self, google_books_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed book information by Google Books ID.
        
        Args:
            google_books_id: Google Books volume ID
            
        Returns:
            Dict: Book data dictionary or None if not found
        """
        try:
            url = f"{self.BASE_URL}/{google_books_id}"
            params = {}
            
            if self.api_key:
                params["key"] = self.api_key
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                
                item = response.json()
                return self._parse_book_data(item)
                
        except httpx.HTTPError as e:
            logger.error(f"Google Books API error for ID {google_books_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching book {google_books_id}: {e}")
            return None
    
    def _parse_book_data(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse book data from Google Books API response.
        
        Args:
            item: Raw book item from API
            
        Returns:
            Dict: Parsed book data or None if parsing fails
        """
        try:
            volume_info = item.get("volumeInfo", {})
            
            # Extract ISBN
            isbn = None
            for identifier in volume_info.get("industryIdentifiers", []):
                if identifier.get("type") in ["ISBN_13", "ISBN_10"]:
                    isbn = identifier.get("identifier")
                    break
            
            # Extract cover image (prefer high resolution)
            image_links = volume_info.get("imageLinks", {})
            cover_image = (
                image_links.get("extraLarge") or
                image_links.get("large") or
                image_links.get("medium") or
                image_links.get("thumbnail") or
                image_links.get("smallThumbnail")
            )
            
            # Parse authors
            authors = volume_info.get("authors", [])
            author_str = ", ".join(authors) if authors else "Unknown Author"
            
            # Extract genres/categories
            genres = volume_info.get("categories", [])
            
            return {
                "googleBooksId": item.get("id"),
                "title": volume_info.get("title", "Unknown Title"),
                "author": author_str,
                "isbn": isbn,
                "description": volume_info.get("description"),
                "coverImage": cover_image,
                "publishedDate": volume_info.get("publishedDate"),
                "pageCount": volume_info.get("pageCount"),
                "genres": genres,
                "averageRating": volume_info.get("averageRating", 0.0) or 0.0,
            }
        except Exception as e:
            logger.error(f"Error parsing book data: {e}")
            return None


# Global service instance
google_books_service = GoogleBooksService()

