from django.test import TestCase
from users.models import User

# Create your tests here.
class UrlTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'fogli',
            'password': '12345678'}
        User.objects.create_user(**self.credentials)

    def test_admin(self):
        response = self.client.post('/admin/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_administration(self):
        response = self.client.post('/administration/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_override(self):
        response = self.client.post('/administration/override/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)