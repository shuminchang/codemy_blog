from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Post, Category, Comment
from django.core.files.uploadedfile import SimpleUploadedFile
import os

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
        self.assertEqual(response.status_code, 302)

    def test_home_view_GET(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertTrue('cat_menu' in response.context)

    def test_category_view_GET(self):
        url = reverse('category', kwargs={'cats': 'Django'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories.html')
        self.assertEqual(len(response.context['category_posts']), 3)
        self.assertEqual(response.context['cats'], 'Django')

    def test_category_list_view_GET(self):
        response = self.client.get(reverse('category-list'))
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
            'title_tag': 'New Tag',
            'body': 'New body text',
            'snippet': 'Snippet',
            'category': self.category.id,
            'author': self.user.id
        })
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
        update_category = Category.objects.create(name='Updated Category')
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
                'category': update_category.name,
                'author': self.user.id,
                'slug': self.post.slug,
                'header_image': image
            })

        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Post')
        self.assertEqual(self.post.body, 'Updated body text')
        self.assertEqual(self.post.snippet, 'Updated Snippet')
        self.assertEqual(self.post.category, update_category.name)
        self.assertEqual(self.post.author.id, self.user.id)
        self.assertTrue(self.post.header_image)

        uploaded_base_name = os.path.splitext(os.path.basename(self.post.header_image.name))[0]
        expected_base_name = os.path.splitext(os.path.basename(self.test_image_path))[0]
        self.assertTrue(uploaded_base_name.startswith(expected_base_name))

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
