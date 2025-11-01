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
        # Multiple API calls are now made (book, progress, clubs, related)
        self.assertGreaterEqual(mock_get.call_count, 1)

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
        
        # Third call: /api/clubs/my-clubs -> 200 with clubs
        resp_clubs = MagicMock()
        resp_clubs.status_code = 200
        resp_clubs.json.return_value = []
        
        # Fourth call: /api/books/gb123/related -> 200 with related books
        resp_related = MagicMock()
        resp_related.status_code = 200
        resp_related.json.return_value = {'results': []}
        
        mock_get.side_effect = [resp_404, resp_200, resp_clubs, resp_related]

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
        # Verify at least 2 calls were made (DB then Google)
        self.assertGreaterEqual(mock_get.call_count, 2)

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

    @patch('apps.books.views.requests.get')
    def test_book_detail_fetches_all_data(self, mock_get):
        """Test book_detail view fetches book, progress, clubs, and related books."""
        # Setup multiple mock responses for different API calls
        mock_book = MagicMock()
        mock_book.status_code = 200
        mock_book.json.return_value = {
            'id': 'testbook123',
            'title': 'Test Book',
            'author': 'Test Author',
            'pageCount': 300,
            'coverImage': 'http://example.com/cover.jpg'
        }
        
        mock_progress = MagicMock()
        mock_progress.status_code = 200
        mock_progress.json.return_value = {
            'status': 'reading',
            'currentPage': 150,
            'progressPercentage': 50.0,
            'startedAt': '2024-01-01T00:00:00Z'
        }
        
        mock_clubs = MagicMock()
        mock_clubs.status_code = 200
        mock_clubs.json.return_value = [
            {'id': 1, 'name': 'Test Club', 'description': 'A test club'}
        ]
        
        mock_related = MagicMock()
        mock_related.status_code = 200
        mock_related.json.return_value = {
            'results': [
                {'googleBooksId': 'related1', 'title': 'Related Book', 'author': 'Author'}
            ]
        }
        
        # Mock get to return different responses for different URLs
        def side_effect(url, *args, **kwargs):
            if '/api/books/testbook123' in url and '/related' not in url:
                return mock_book
            elif '/api/progress/' in url:
                return mock_progress
            elif '/api/clubs/my-clubs' in url:
                return mock_clubs
            elif '/related' in url:
                return mock_related
            return mock_book
        
        mock_get.side_effect = side_effect
        
        url = reverse('books:detail', kwargs={'book_id': 'testbook123'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/detail.html')
        
        # Verify context has all expected data
        context = response.context
        self.assertIn('book', context)
        self.assertIn('reading_progress', context)
        self.assertIn('user_clubs', context)
        self.assertIn('related_books', context)
        self.assertIn('reading_stats', context)
        
        # Verify reading stats were calculated
        self.assertIsNotNone(context['reading_stats'])
        # Verify multiple API calls were made
        self.assertGreaterEqual(mock_get.call_count, 4)

    @patch('apps.books.views.requests.put')
    def test_update_progress_success(self, mock_put):
        """Test updating reading progress successfully."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        
        url = reverse('books:update_progress', kwargs={'book_id': 'test123'})
        response = self.client.post(url, {
            'current_page': '200',
            'status': 'reading'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirects to detail
        mock_put.assert_called_once()
        call_args = mock_put.call_args
        self.assertIn('/api/progress/test123', call_args[0][0])
        self.assertEqual(call_args[1]['json']['currentPage'], 200)
        self.assertEqual(call_args[1]['json']['status'], 'reading')

    @patch('apps.books.views.requests.delete')
    def test_remove_book_success(self, mock_delete):
        """Test removing book from catalog successfully."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        url = reverse('books:remove', kwargs={'book_id': 'test123'})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)  # Redirects to catalog
        mock_delete.assert_called_once()
        call_args = mock_delete.call_args
        self.assertIn('/api/progress/test123', call_args[0][0])
