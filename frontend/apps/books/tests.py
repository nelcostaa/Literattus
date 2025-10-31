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
        # Mock the 404 API response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Call the view
        url = reverse('books:detail', kwargs={'book_id': 'nonexistent'})
        response = self.client.get(url)

        # Assertions
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('books:catalog'), fetch_redirect_response=False)
        mock_get.assert_called_once()

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
