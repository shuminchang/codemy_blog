from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Post, Comment, Category
from django.utils.text import slugify

class TestModels(TestCase):
    def setUp(self):
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
