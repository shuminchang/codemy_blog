from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Post, Category

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
        long_title = 'A' * 256
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
