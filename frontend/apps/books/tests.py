"""
Tests for the books app views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock


class BookViewsTestCase(TestCase):
    """Test suite for book views."""

    def setUp(self):
        self.client = Client()
        # Mock session for jwt_login_required decorator
        session = self.client.session
        session['access_token'] = 'test_token'
        session.save()

    @patch('apps.books.views.requests.get')
    def test_book_detail_view_success(self, mock_get):
        """Test the book detail view successfully retrieves and displays a book."""
        # Mock the successful API response
        mock_book_data = {
            'id': 'testbook123',
            'title': 'A Test Book',
            'author': 'Test Author',
            'description': 'A fascinating description.',
            'coverImage': 'http://example.com/cover.jpg',
            'isbn': '9781234567890',
            'publishedDate': '2023-01-01',
            'pageCount': 350,
            'averageRating': 4.5,
            'categories': ['Fiction', 'Testing'],
            'language': 'en'
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_book_data
        mock_get.return_value = mock_response

        # Call the view
        url = reverse('books:detail', kwargs={'book_id': 'testbook123'})
        response = self.client.get(url)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/detail.html')
        self.assertIn('book', response.context)
        self.assertEqual(response.context['book']['title'], 'A Test Book')
        self.assertEqual(response.context['book']['pageCount'], 350)
        mock_get.assert_called_once()

    @patch('apps.books.views.requests.get')
    def test_book_detail_view_not_found(self, mock_get):
        """Test the book detail view handles a 404 from the API."""
        # Mock the 404 API response for both DB and fallback
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Call the view
        url = reverse('books:detail', kwargs={'book_id': 'nonexistent'})
        response = self.client.get(url)

        # Assertions
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('books:catalog'), fetch_redirect_response=False)
        # Allow multiple calls due to fallback behavior
        self.assertGreaterEqual(mock_get.call_count, 1)

    @patch('apps.books.views.requests.get')
    def test_book_detail_view_api_error(self, mock_get):
        """Test the book detail view handles a generic API error."""
        # Mock a request exception
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("Connection timed out")

        # Call the view
        url = reverse('books:detail', kwargs={'book_id': 'anybook'})
        response = self.client.get(url)

        # Assertions
        self.assertEqual(response.status_code, 302) # Should redirect
        self.assertRedirects(response, reverse('books:catalog'), fetch_redirect_response=False)
        mock_get.assert_called_once()

    @patch('apps.books.views.requests.get')
    def test_book_detail_view_fallback_to_google(self, mock_get):
        """If DB detail returns 404, fallback to Google endpoint and render details with Add button."""
        # First call: /api/books/{id} -> 404
        resp_404 = MagicMock()
        resp_404.status_code = 404
        # Second call: /api/books/google/{id} -> 200 with parsed item
        google_item = {
            'googleBooksId': 'gb123',
            'title': 'Google Parsed Title',
            'author': 'Author G',
            'description': 'From Google',
            'coverImage': 'http://img/g.jpg',
            'publishedDate': '2017-01-01',
            'pageCount': 123,
            'genres': ['Tech']
        }
        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.json.return_value = google_item
        mock_get.side_effect = [resp_404, resp_200]

        url = reverse('books:detail', kwargs={'book_id': 'gb123'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/detail.html')
        self.assertIn('book', response.context)
        self.assertEqual(response.context['book'].get('title'), 'Google Parsed Title')
        # Should expose in_catalog flag false for google fallback
        self.assertIn('in_catalog', response.context)
        self.assertFalse(response.context['in_catalog'])
        # Page should show an Add to Catalog button
        self.assertContains(response, 'Add to Catalog')
        self.assertContains(response, reverse('books:add', kwargs={'google_book_id': 'gb123'}))
        # Ensure two calls were made (DB then Google)
        self.assertEqual(mock_get.call_count, 2)

    @patch('apps.books.views.requests.get')
    def test_search_renders_links_to_detail(self, mock_get):
        """Search results should include links to the detail page for each book."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'id': 'vol1',
                    'volumeInfo': {
                        'title': 'Clickable One',
                        'authors': ['Author A']
                    }
                },
                {
                    'id': 'vol2',
                    'volumeInfo': {
                        'title': 'Clickable Two',
                        'authors': ['Author B']
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        response = self.client.get(reverse('books:search'), {'q': 'click'})
        self.assertEqual(response.status_code, 200)
        # Expect links to detail
        self.assertContains(response, reverse('books:detail', kwargs={'book_id': 'vol1'}))
        self.assertContains(response, reverse('books:detail', kwargs={'book_id': 'vol2'}))

    @patch('apps.books.views.requests.get')
    def test_catalog_uses_my_catalog_endpoint(self, mock_get):
        """Catalog view should fetch from /my-catalog endpoint with reading progress."""
        mock_books = [
            {
                'id': 'book1',
                'title': 'User Book One',
                'author': 'Test Author',
                'coverImage': 'http://example.com/cover1.jpg',
                'pageCount': 300,
                'status': 'reading',
                'currentPage': 150,
                'progressPercentage': 50.0,
            },
            {
                'id': 'book2',
                'title': 'User Book Two',
                'author': 'Another Author',
                'status': 'not_started',
                'currentPage': 0,
                'progressPercentage': 0.0,
            }
        ]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_books
        mock_get.return_value = mock_response

        response = self.client.get(reverse('books:catalog'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/catalog.html')
        
        # Verify API call to my-catalog
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('/my-catalog', call_args[0][0])
        
        # Verify context has books and stats
        self.assertIn('books', response.context)
        self.assertEqual(len(response.context['books']), 2)
        self.assertIn('reading_count', response.context)
        self.assertIn('not_started_count', response.context)
        self.assertIn('completed_count', response.context)
        
        # Verify stats calculated correctly
        self.assertEqual(response.context['reading_count'], 1)
        self.assertEqual(response.context['not_started_count'], 1)
        self.assertEqual(response.context['completed_count'], 0)

    @patch('apps.books.views.requests.get')
    def test_catalog_displays_reading_status(self, mock_get):
        """Catalog page should display reading status badges for each book."""
        mock_books = [
            {
                'id': 'book_reading',
                'title': 'Currently Reading',
                'author': 'Test Author',
                'status': 'reading',
                'progressPercentage': 75.5,
            },
            {
                'id': 'book_completed',
                'title': 'Finished Book',
                'author': 'Another Author',
                'status': 'completed',
            }
        ]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_books
        mock_get.return_value = mock_response

        response = self.client.get(reverse('books:catalog'))
        
        # Check for status badges in rendered HTML
        self.assertContains(response, 'Reading')
        self.assertContains(response, 'Completed')
        self.assertContains(response, '76%')  # Progress percentage (75.5 rounded)
