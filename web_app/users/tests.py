from django.test import TestCase
from users.models import User
from thingsboard_api_tools import TbApi

class UrlTest(TestCase):
    def setUp(self):
        self.credentials_super = {
            'username': 'super',
            'password': '12345678'}
        User.objects.create_superuser(**self.credentials_super)
        self.credentials = {
            'username': 'fogli',
            'password': '12345678'}
        User.objects.create_user(**self.credentials)
        # ThingsBoard REST API URL
        url = "http://192.168.1.197:8080"
        # Default Tenant Administrator credentials
        username = "tenant@thingsboard.org"
        password = "tenant"
        self.tbapi = TbApi(url, username, password)

    def test_home(self):
        #normal user behaviour
        self.client.logout()
        self.client.login(**self.credentials)
        response = self.client.get('/home/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'map.html')
        #check the context
        self.assertIn('park_status', response.context)
        self.assertIn('park_percent', response.context)

        #super user behaviour
        self.client.logout()
        self.client.login(**self.credentials_super)
        response = self.client.get('/home/', self.credentials_super, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTrue(response.context['request'].user.is_superuser)
        self.assertTemplateUsed(response, 'administration.html')


        #non logged behaviour
        self.client.logout()
        self.client.login(username='wrong', password='wrong')
        response = self.client.get('/home/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')


    def test_auth(self):
        #normal user behaviour
        self.client.logout()
        self.client.login(**self.credentials)
        response = self.client.get('/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'map.html')

        #super user behaviour
        self.client.logout()
        self.client.login(**self.credentials_super)
        response = self.client.get('/', self.credentials_super, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'administration.html')

        #non logged post login behaviour
        self.client.logout()
        response = self.client.post('/', {'login': ''}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')
        #check the context
        self.assertIn('login_form', response.context)
        self.assertIn('signup_form', response.context)

        #non logged post signup behaviour
        self.client.logout()
        response = self.client.post('/', {'signup': ''}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')
        #check the context
        self.assertIn('login_form', response.context)
        self.assertIn('signup_form', response.context)
        

