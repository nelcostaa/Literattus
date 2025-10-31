from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock


class BookSearchViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['access_token'] = 'test_token'
        session.save()

    @patch('apps.books.views.requests.get')
    def test_search_calls_backend_with_correct_params(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        query = 'harry potter'
        response = self.client.get(reverse('books:search'), {'q': query})

        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn('/api/books/search', args[0])
        # Validate params and headers
        self.assertIn('params', kwargs)
        self.assertEqual(kwargs['params']['q'], query)
        self.assertEqual(kwargs['params']['max_results'], 20)
        self.assertIn('headers', kwargs)
        self.assertEqual(kwargs['headers'].get('Authorization'), 'Bearer test_token')
        self.assertEqual(kwargs.get('timeout'), 10)

    @patch('apps.books.views.requests.get')
    def test_search_success_renders_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'id': 'vol1',
                    'volumeInfo': {
                        'title': 'Result One',
                        'authors': ['Author A'],
                        'publishedDate': '2020-01-01',
                        'imageLinks': {'thumbnail': 'http://img/1.jpg'},
                        'description': 'First book'
                    }
                },
                {
                    'id': 'vol2',
                    'volumeInfo': {
                        'title': 'Result Two',
                        'authors': ['Author B'],
                        'publishedDate': '2019-01-01',
                        'imageLinks': {'thumbnail': 'http://img/2.jpg'},
                        'description': 'Second book'
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        response = self.client.get(reverse('books:search'), {'q': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Result One')
        self.assertContains(response, 'Result Two')

    @patch('apps.books.views.requests.get')
    def test_search_filters_out_missing_ids(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'id': 'valid123',
                    'volumeInfo': { 'title': 'Valid Book', 'authors': ['Author One'] }
                },
                {
                    # missing id
                    'volumeInfo': { 'title': 'Invalid Book Without ID', 'authors': ['Author Two'] }
                }
            ]
        }
        mock_get.return_value = mock_response

        response = self.client.get(reverse('books:search'), {'q': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Valid Book')
        self.assertNotContains(response, 'Invalid Book Without ID')

    @patch('apps.books.views.requests.get')
    def test_search_backend_failure_shows_empty_state(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_get.return_value = mock_response

        response = self.client.get(reverse('books:search'), {'q': 'nothing'})
        self.assertEqual(response.status_code, 200)
        # When query present and no books, the template shows no results message
        self.assertContains(response, 'No results found for')

    @patch('apps.books.views.requests.get')
    def test_search_handles_backend_parsed_schema(self, mock_get):
        """
        Backend returns parsed schema (googleBooksId, title, author, coverImage, etc.).
        The view should normalize and render items.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'googleBooksId': 'gb1',
                    'title': 'Parsed One',
                    'author': 'Author P',
                    'coverImage': 'http://img/p1.jpg',
                    'publishedDate': '2018-01-01',
                    'pageCount': 111,
                    'averageRating': 4.0
                },
                {
                    'googleBooksId': 'gb2',
                    'title': 'Parsed Two',
                    'author': 'Author Q',
                    'coverImage': 'http://img/p2.jpg',
                    'publishedDate': '2017-01-01',
                    'pageCount': 222,
                    'averageRating': 3.5
                }
            ]
        }
        mock_get.return_value = mock_response

        response = self.client.get(reverse('books:search'), {'q': 'parsed'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Parsed One')
        self.assertContains(response, 'Parsed Two')
