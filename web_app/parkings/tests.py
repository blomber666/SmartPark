from django.test import TestCase
from users.models import User
from parkings.models import Stop, Payment
import os
import time
from django.conf import settings
from django.utils import timezone
from django.test import Client


# Create your tests here.

class UrlsTest(TestCase):
    def setUp(self):

        self.credentials = {
            'username': 'test',
            'password': '12345678Test',
        }
        self.user = User.objects.create_user(**self.credentials)
        stop = Stop.objects.create(user=self.user, park='1')



    def test_park_1(self):
        #logged behaviour
        self.client.login(username='test', password='12345678Test')
        response = self.client.post('/park_1/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'park_1.html')
        #check the context
        self.assertIn('start', response.context)
        self.assertIn('end', response.context)
        self.assertIn('amount', response.context)
        self.assertIn('free_spaces', response.context)

        #test the non logged behaviour
        self.client.logout()
        self.client.login(username='wrong', password='wrong')
        response = self.client.post('/park_1/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')

        #check that media/park_1.png was created less than 30 secs ago
        file_path = os.path.join(settings.MEDIA_ROOT, 'park_1.png')
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(time.time() - os.path.getmtime(file_path) < 30)

    #test the pay function
    def test_pay(self):
        self.client.login(**self.credentials)
        response = self.client.post('/park_1/pay', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'park_1.html')
        #get the last stop
        stop = Stop.objects.filter(user=self.user).last()
        #check the if exists a payment
        payment = Payment.objects.filter(stop=stop).last()
        self.assertTrue(payment)

        #test the non logged behaviour
        self.client.logout()
        self.client.login(username='wrong', password='wrong')
        response = self.client.post('/park_1/pay', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')