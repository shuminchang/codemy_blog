from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Profile
from .forms import SignUpForm, EditProfileForm, ProfilePageForm, PasswordChangingForm

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = Profile.objects.create(user=self.user, bio='Test Bio')

    def test_create_profile_page_view_GET(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('create_profile_page')) # Replace with your url name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/create_user_profile_page.html')

    def test_edit_profile_page_view_GET(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('edit_profile_page', args=[self.profile.id])) # Replace with your url name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/edit_profile_page.html')

    def test_show_profile_page_view_GET(self):
        response = self.client.get(reverse('show_profile_page', args=[self.profile.id])) # Replace with your url name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/user_profile.html')

    def test_passwords_change_view_GET(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('change_password')) # Replace with your url name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/change-password.html') # Replace with the actual template

    def test_password_success_view_GET(self):
        response = self.client.get(reverse('password_success')) # Replace with your url name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_success.html')

    def test_user_register_view_GET(self):
        response = self.client.get(reverse('register')) # Replace with your url name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_user_edit_view_GET(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('edit_profile')) # Replace with your url name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/edit_profile.html')

