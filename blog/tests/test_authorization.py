from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Post, Category

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
        self.assertContains(response, "You are not allowed here (and you know it...)")

    def test_authenticated_user_access(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('add_post'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_post.html')

    def test_edit_post_by_non_author(self):
        self.client.login(username='otheruser', password='54321')
        response = self.client.get(reverse('update_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are not allowed here! (and you know it...)")

    def test_delete_post_by_non_author(self):
        self.client.login(username='otheruser', password='54321')
        response = self.client.get(reverse('delete_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your are not allow here (and you know it...)")
