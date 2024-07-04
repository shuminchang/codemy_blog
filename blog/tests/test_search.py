from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import Post

class SearchArticlesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.post1 = Post.objects.create(title='Test Post', body='This is a test post body.', author=self.user)
        self.post2 = Post.objects.create(title='Another Post', body='Another test body with Test keyword.', author=self.user)
        self.post3 = Post.objects.create(title='Case Insensitive', body='case insensitive search', author=self.user)

    def test_search_articles(self):
        response = self.client.post(reverse('search-articles'), {'searched': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')

        found_titles = [post.title for post in response.context['posts']]
        self.assertIn('Test Post', found_titles)
        self.assertIn('Another Post', found_titles)
        self.assertNotIn('Case Insensitive', found_titles)

    def test_search_case_insensitivity(self):
        response = self.client.post(reverse('search-articles'), {'searched': 'case'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')

        found_titles = [post.title for post in response.context['posts']]
        self.assertIn('Case Insensitive', found_titles)

    def test_search_no_results(self):
        response = self.client.post(reverse('search-articles'), {'searched': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')
        self.assertEqual(len(response.context['posts']), 0)
        self.assertContains(response, 'You Searched For... "NonExistent"')

    def test_search_empty_string(self):
        response = self.client.post(reverse('search-articles'), {'searched': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')
        self.assertEqual(len(response.context['posts']), 0)
        self.assertContains(response, 'You Forgot To Search For a Venue')

    def test_search_partial_matches(self):
        response = self.client.post(reverse('search-articles'), {'searched': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')

        found_titles = [post.title for post in response.context['posts']]
        self.assertIn('Test Post', found_titles)
        self.assertIn('Another Post', found_titles)

    def test_search_highlighted_html(self):
        response = self.client.post(reverse('search-articles'), {'searched': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')
        self.assertContains(response, '<mark>Test</mark>', html=True)

    def test_search_with_special_characters(self):
        response = self.client.post(reverse('search-articles'), {'searched': '!@#$%^&*()'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')
        self.assertEqual(len(response.context['posts']), 0)

    def test_search_with_long_query(self):
        long_query = 'A' * 1000
        response = self.client.post(reverse('search-articles'), {'searched': long_query})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')
        self.assertEqual(len(response.context['posts']), 0)
        self.assertContains(response, f'You Searched For... "{long_query}"')
