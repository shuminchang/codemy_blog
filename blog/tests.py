from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import requests
from .models import Post, Category, Comment
from django.utils.text import slugify
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from django.test import LiveServerTestCase
import io
import warnings
import os

warnings.filterwarnings("ignore")

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.update_category = Category.objects.create(name='Updated Category')
        self.post = Post.objects.create(
            title='Test Post', 
            body='Test Body', 
            author=self.user, 
            category=self.category.name,
            snippet='Test snippet'
        )
        self.test_image_path = './blog/tests/media/test_horizontal.jpg'
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

        with open(self.test_image_path, 'rb') as img:
            image = SimpleUploadedFile(img.name, img.read(), content_type='image/jpeg')

            response = self.client.post(url, {
                'title': 'Updated Post',
                'body': 'Updated body text',
                'snippet': 'Updated Snippet',
                'category': self.update_category.name,
                'author': self.user.id,
                'slug': self.post.slug,
                'header_image': image
            })

        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Post')
        self.assertEqual(self.post.body, 'Updated body text')
        self.assertEqual(self.post.snippet, 'Updated Snippet')
        self.assertEqual(self.post.category, self.update_category.name)
        self.assertEqual(self.post.author.id, self.user.id)
        self.assertTrue(self.post.header_image)

        # Check if the uploaded file name starts with the base name of the test image file
        uploaded_base_name = os.path.splitext(os.path.basename(self.post.header_image.name))[0]
        expected_base_name = os.path.splitext(os.path.basename(self.test_image_path))[0]
        
        self.assertTrue(uploaded_base_name.startswith(expected_base_name))

        # Clean up the uploaded file
        self.post.header_image.delete()

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
        # print(response.content.decode())
        # self.assertContains(response, 'No results found.')
        self.assertContains(response, f'You Searched For... "{long_query}"')

class TestImageUpload(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_valid_image_upload(self):
        with open('blog/tests/media/test_horizontal.jpg', 'rb') as img:
            image = SimpleUploadedFile(img.name, img.read(), content_type='image/jpeg')
            response = self.client.post(reverse('ckeditor_upload'), {'upload': image})
        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.json())

    def test_large_image_upload(self):
        with open('blog/tests/media/test_large.jpg', 'rb') as img:
            image = SimpleUploadedFile(img.name, img.read(), content_type='image/jpeg')
            response = self.client.post(reverse('ckeditor_upload'), {'upload': image})
        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.json())

    def test_invalid_file_upload(self):
        file = SimpleUploadedFile("file.txt", b"file_content", content_type="text/plain")
        response = self.client.post(reverse('ckeditor_upload'), {'upload': file})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

# class TestCSRFHandling(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.client.login(username='testuser', password='12345')

#     def test_missing_csrf_token(self):
#         response = self.client.post(reverse('add_post'), {'title': 'Test Post'}, follow=True)
#         self.assertEqual(response.status_code, 403)

#     def test_invalid_csrf_token(self):
#         response = self.client.post(reverse('add_post'), {'title': 'Test Post', 'csrfmiddlewaretoken': 'invalid'})
#         self.assertEqual(response.status_code, 403)
        
class TestDragAndDropUpload(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_valid_image_drag_and_drop(self):
        with open('blog/tests/media/test_horizontal.jpg', 'rb') as img:
            response = self.client.post(reverse('ckeditor_upload'), {'upload': img})
        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.json())

    def test_invalid_file_drag_and_drop(self):
        file = SimpleUploadedFile("file.txt", b"file_content", content_type="text/plain")
        response = self.client.post(reverse('ckeditor_upload'), {'upload': file})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        

class TestImageOrientationHandling(LiveServerTestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_horizontal_image_resize(self):
        with open('blog/tests/media/test_horizontal.jpg', 'rb') as img:
            original_image = Image.open(img)
            original_aspect_ratio = original_image.width / original_image.height

            img.seek(0)  # Reset file pointer to the beginning
            image = SimpleUploadedFile(img.name, img.read(), content_type='image/jpeg')
            response = self.client.post(reverse('ckeditor_upload'), {'upload': image})

        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.json())

        # Construct the full URL from the relative URL
        relative_url = response.json()['url']
        full_url = self.live_server_url + relative_url

        response = requests.get(full_url)
        self.assertEqual(response.status_code, 200)

        uploaded_image = Image.open(io.BytesIO(response.content))
        uploaded_aspect_ratio = uploaded_image.width / uploaded_image.height

        # Assert that the aspect ratio is maintained
        self.assertAlmostEqual(original_aspect_ratio, uploaded_aspect_ratio, places=2)
    
    def test_vertical_image_resize(self):
        with open('blog/tests/media/test_large.jpg', 'rb') as img:
            original_image = Image.open(img)
            original_aspect_ratio = original_image.width / original_image.height

            img.seek(0)  # Reset file pointer to the beginning
            image = SimpleUploadedFile(img.name, img.read(), content_type='image/jpeg')
            response = self.client.post(reverse('ckeditor_upload'), {'upload': image})

        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.json())

        # Construct the full URL from the relative URL
        relative_url = response.json()['url']
        full_url = self.live_server_url + relative_url

        response = requests.get(full_url)
        self.assertEqual(response.status_code, 200)

        uploaded_image = Image.open(io.BytesIO(response.content))
        uploaded_aspect_ratio = uploaded_image.width / uploaded_image.height

        # Assert that the aspect ratio is maintained
        self.assertAlmostEqual(original_aspect_ratio, uploaded_aspect_ratio, places=2)

class TestAuthorization(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='54321')
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post', 
            body='Test Body', 
            author=self.user, 
            category=self.category.name,
            snippet='Test snippet'
        )

    def test_unauthenticated_user_access(self):
        response = self.client.get(reverse('add_post'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are not allowed here (and you know it...)") # assertContains will decode the content of the response, and check if it include the text

    def test_authenticated_user_access(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('add_post'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_post.html')

    def test_edit_post_by_non_author(self):
        self.client.login(username='otheruser', password='54321')
        response = self.client.get(reverse('update_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)  # Assuming you return 403 Forbidden for unauthorized access
        self.assertContains(response, "You are not allowed here! (and you know it...)") # assertContains will decode the content of the response, and check if it include the text

    def test_delete_post_by_non_author(self):
        self.client.login(username='otheruser', password='54321')
        response = self.client.get(reverse('delete_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)  # Assuming you return 403 Forbidden for unauthorized access
        self.assertContains(response, "Your are not allow here (and you know it...)") # assertContains will decode the content of the response, and check if it include the text

class TestFormSubmission(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')

    def test_post_creation_with_valid_data(self):
        response = self.client.post(reverse('add_post'), {
            'title': 'Valid Post',
            'title_tag': 'Valid Tag',
            'body': 'This is a valid post.',
            'snippet': 'Snippet',
            'category': self.category.id,
            'author': self.user.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='Valid Post').exists())

    def test_post_creation_missing_required_fields(self):
        response = self.client.post(reverse('add_post'), {
            'title': '',
            'body': 'This post is missing the title.',
            'snippet': 'Snippet',
            'category': self.category.id,
            'author': self.user.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'This field is required.')

    def test_post_creation_with_long_title(self):
        long_title = 'A' * 256  # Assuming the max length is 255
        response = self.client.post(reverse('add_post'), {
            'title': long_title,
            'title_tag': 'Title Tag',
            'body': 'This post has a long title.',
            'snippet': 'Snippet',
            'category': self.category.id,
            'author': self.user.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Ensure this value has at most 255 characters (it has 256).')

    def test_post_creation_invalid_data(self):
        response = self.client.post(reverse('add_post'), {
            'title': 'Invalid Category',
            'title_tag': 'Invalid Tag',
            'body': 'This post has an invalid category ID.',
            'snippet': 'Snippet',
            'category': 999,
            'author': self.user.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'category', 'Select a valid choice. That choice is not one of the available choices.')

    def test_post_creation_with_empty_body(self):
        response = self.client.post(reverse('add_post'), {
            'title': 'Title Only',
            'title_tag': 'Title Tag',
            'body': '',
            'snippet': 'Snippet',
            'category': self.category.id,
            'author': self.user.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='Title Only').exists())

    def test_post_creation_with_special_characters_in_title(self):
        special_title = 'Title with special characters !@#$%^&*()'
        response = self.client.post(reverse('add_post'), {
            'title': special_title,
            'title_tag': 'Title Tag',
            'body': 'This post has a title with special characters.',
            'snippet': 'Snippet',
            'category': self.category.id,
            'author': self.user.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title=special_title).exists())

class TestPagination(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        for i in range(20):
            Post.objects.create(
                title=f'Post {i}', 
                body='Test Content', 
                author=self.user, 
                category=self.category.name
            )

    def test_category_view_pagination(self):
        response = self.client.get(reverse('category', kwargs={'cats': self.category.name}), {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories.html')
        self.assertEqual(len(response.context['category_posts']), 10)  # Assuming you paginate 10 posts per page
