from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class MapViewTest(TestCase):

    def test_map_view_authenticated_user(self):
        # Test with authenticated user who is not a superuser
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)
        response = self.client.get(reverse('map_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'map.html')
        self.assertIn('park_status', response.context)
        self.assertIn('park_percent', response.context)
        # Test with authenticated superuser
        user.is_superuser = True
        user.save()
        response = self.client.get(reverse('map_view'))
        self.assertRedirects(response, '/administration')

    def test_map_view_unauthenticated_user(self):
        response = self.client.get(reverse('map_view'))
        self.assertRedirects(response, '/')
        self.assertContains(response, 'HTTP ERROR: 401 - Unauthorized')


class HomeViewTest(TestCase):

    def test_home_view_authenticated_user(self):
        # Test with authenticated user who is not a superuser
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/home')
        # Test with authenticated superuser
        user.is_superuser = True
        user.save()
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/administration')

    def test_home_view_unauthenticated_user(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIn('login_form', response.context)
        self.assertIn('signup_form', response.context)

    def test_home_view_login_post(self):
        response = self.client.post(reverse('home'), {'login': True, 'username': 'testuser', 'password': 'testpass'})
        self.assertRedirects(response, '/home')

    def test_home_view_signup_post(self):
        response = self.client.post(reverse('home'), {'signup': True, 'username': 'newuser', 'password1': 'newpass', 'password2': 'newpass'})
        self.assertRedirects(response, '/login')