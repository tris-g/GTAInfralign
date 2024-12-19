from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .forms import UserRegisterForm, AuthenticationForm

from secrets import token_urlsafe

class TestForms(TestCase):

    def setUp(self):
        self.test_username, self.test_password = ('test_user', token_urlsafe(16))
        self.test_user = User.objects.create_user(username=self.test_username, password=self.test_password)

    def test_user_register_form_succeeds(self):
        form = UserRegisterForm(data={'email': 'test@example.com', 'username': 'test_user_2', 'password1': 'test_user_password', 'password2': 'test_user_password'})
        self.assertTrue(form.is_valid())

    def test_authentication_form_succeeds(self):
        form = AuthenticationForm(self.client.request(), data={'username': self.test_username, 'password': self.test_password})
        self.assertTrue(form.is_valid())
        self.assertTrue(self.client.login(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password')))
    
    def test_login(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_post(self):
        response = self.client.post(reverse('login'), {'username': self.test_username, 'password': self.test_password})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))