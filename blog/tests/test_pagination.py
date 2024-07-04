from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Post, Category

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
        self.assertEqual(len(response.context['category_posts']), 10)
