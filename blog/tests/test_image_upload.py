from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
import requests
import os
from django.test import LiveServerTestCase

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

            img.seek(0)
            image = SimpleUploadedFile(img.name, img.read(), content_type='image/jpeg')
            response = self.client.post(reverse('ckeditor_upload'), {'upload': image})

        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.json())

        relative_url = response.json()['url']
        full_url = self.live_server_url + relative_url

        response = requests.get(full_url)
        self.assertEqual(response.status_code, 200)

        uploaded_image = Image.open(io.BytesIO(response.content))
        uploaded_aspect_ratio = uploaded_image.width / uploaded_image.height
        self.assertAlmostEqual(original_aspect_ratio, uploaded_aspect_ratio, places=2)
    
    def test_vertical_image_resize(self):
        with open('blog/tests/media/test_large.jpg', 'rb') as img:
            original_image = Image.open(img)
            original_aspect_ratio = original_image.width / original_image.height

            img.seek(0)
            image = SimpleUploadedFile(img.name, img.read(), content_type='image/jpeg')
            response = self.client.post(reverse('ckeditor_upload'), {'upload': image})

        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.json())

        relative_url = response.json()['url']
        full_url = self.live_server_url + relative_url

        response = requests.get(full_url)
        self.assertEqual(response.status_code, 200)

        uploaded_image = Image.open(io.BytesIO(response.content))
        uploaded_aspect_ratio = uploaded_image.width / uploaded_image.height
        self.assertAlmostEqual(original_aspect_ratio, uploaded_aspect_ratio, places=2)
