from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Category, Comment
from django.utils.text import slugify
import warnings

warnings.filterwarnings("ignore")

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post', 
            body='Test Body', 
            author=self.user, 
            category=self.category.name,
            snippet='Test snippet'
        )
        self.comment = Comment.objects.create(
            post=self.post, 
            name='testuser', 
            body='Test Comment'
        )
        self.url = reverse('article-detail', kwargs={'slug': self.post.slug})
        self.category1 = Category.objects.create(name='Django')
        self.category2 = Category.objects.create(name='Flask')
        for i in range(5):
            Post.objects.create(
                title=f'Test Post {i}', 
                body='Test Content', 
                author=self.user, 
                category=self.category1 if i % 2 == 0 else self.category2
            )

    def test_like_view_POST(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('like_post', args=[self.post.slug]), {
            'post_slug': self.post.slug
        })
        self.assertEqual(response.status_code, 302) # Redirect to article-detail

    def test_home_view_GET(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertTrue('cat_menu' in response.context)

    # def test_article_detail_view_GET(self):
    #     response = self.client.get(reverse('article-detail', args=[self.post.id]))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'article_details.html')
    
    def test_category_view_GET(self):
        url = reverse('category', kwargs={'cats': 'Django'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories.html')
        self.assertEqual(len(response.context['category_posts']), 3) # Testing pagination
        self.assertEqual(response.context['cats'], 'Django')

    def test_category_list_view_GET(self):
        response = self.client.get(reverse('category-list')) # Replace with your url name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category_list.html')
        self.assertTrue('cat_menu_list' in response.context)
        self.assertEqual(len(response.context['cat_menu_list']), 3)

    def test_article_detail_view_GET(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('article-detail', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'article_details.html')
        self.assertTrue('total_likes' in response.context)
        self.assertTrue('liked' in response.context)
        self.assertTrue('comment_form' in response.context)

    def test_article_detail_view_POST_add_comment(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('article-detail', args=[self.post.slug]), {
            'name': 'testuser',
            'body': 'Test Comment'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(body='Test Comment').exists())

    def test_add_post_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('add_post'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_post.html')

        response = self.client.post(reverse('add_post'), {
            'title': 'New Post',
            'title_tag': 'New Tag',  # required
            'body': 'New body text',
            'snippet': 'Snippet',    # required
            'category': self.category.id,
            'author': self.user.id
        })

        # Debugging
        # if response.status_code != 302:
        #     print(response.context['form'].errors)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New Post').exists())

    def test_add_comment_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('add_comment', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_comment.html')

        response = self.client.post(reverse('add_comment', args=[self.post.id]), {
            'name': self.user,
            'body': 'New Comment',
            'post': self.post.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(body='New Comment').exists())

    def test_add_category_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('add_category'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('add_category'), {
            'name': 'New Category'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='New Category').exists())

    def test_update_post_view(self):
        self.client.login(username='testuser', password='password')
        url = reverse('update_post', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_post.html')

        response = self.client.post(url, {
            'title': 'Updated Post',
            'title_tag': 'Updated Tag',  # required
            'body': 'Updated body text',
            'snippet': 'Updated Snippet',    # required
            'category': self.category.id,
            'author': self.user.id
        })
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Post')

    def test_delete_post_view(self):
        self.client.login(username='testuser', password='password')
        url = reverse('delete_post', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_post.html')

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    """
    models.py test
    """

    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.body, 'Test Body')
        self.assertEqual(self.post.author.username, 'testuser')
        self.assertEqual(self.post.category, 'Test Category')
        self.assertEqual(self.post.snippet, 'Test snippet')
        self.assertTrue(isinstance(self.post, Post))

    def test_slug_generation(self):
        self.post.save()
        self.assertEqual(self.post.slug, slugify(self.post.title))

    def test_total_likes(self):
        self.post.likes.add(self.user)
        self.assertEqual(self.post.total_like(), 1)
        self.post.likes.remove(self.user)
        self.assertEqual(self.post.total_like(), 0)

    def test_comment_creation(self):
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.name, 'testuser')
        self.assertEqual(self.comment.body, 'Test Comment')

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

        # Check if posts with title or body containing 'Test' are found
        found_titles = [post.title for post in response.context['posts']]
        self.assertIn('Test Post', found_titles)
        self.assertIn('Another Post', found_titles)

        # Ensure 'Case Insensitive' post is not included in this search result
        self.assertNotIn('Case Insensitive', found_titles)

    def test_search_case_insensitivity(self):
        response = self.client.post(reverse('search-articles'), {'searched': 'case'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')

        # Check if the post with title 'Case Insensitive' is found
        found_titles = [post.title for post in response.context['posts']]
        self.assertIn('Case Insensitive', found_titles)

    def test_search_no_results(self):
        response = self.client.post(reverse('search-articles'), {'searched': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')

        # Check that no posts are found
        self.assertEqual(len(response.context['posts']), 0)
        self.assertContains(response, 'You Searched For... "NonExistent"')

    def test_search_empty_string(self):
        response = self.client.post(reverse('search-articles'), {'searched': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')

        # Check that no posts are found
        self.assertEqual(len(response.context['posts']), 0)
        self.assertContains(response, 'You Forgot To Search For a Venue')

    def test_search_partial_matches(self):
        response = self.client.post(reverse('search-articles'), {'searched': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')

        # Check if posts with partial match 'test' are found
        found_titles = [post.title for post in response.context['posts']]
        self.assertIn('Test Post', found_titles)
        self.assertIn('Another Post', found_titles)

    def test_search_highlighted_html(self):
        response = self.client.post(reverse('search-articles'), {'searched': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_articles.html')

        # Check if the search term is highlighted in the response
        self.assertContains(response, '<mark>Test</mark>', html=True)



