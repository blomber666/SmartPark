from django.test import TestCase
from users.models import User
from stops.models import Stop, Payment
import os
import time
from django.conf import settings


# Create your tests here.

class UrlsTest(TestCase):
    def setUp(self):
        # user, created = User.objects.get_or_create(username="test")
        # user.set_password('12345678Test')
        # user.save()
        self.credentials = {
            'username': 'test',
            'password': '12345678Test',
            'plate': 'AA123AA'
        }
        result = User.objects.create_user(**self.credentials)
        #create a sto
        Stop.objects.create(plate=self.credentials['plate'], start_time='2020-01-01 00:00:00', end_time='2020-01-01 00:00:00')

    def test_park_1(self):
        #logged behaviour
        self.client.login(**self.credentials)
        response = self.client.post('/park_1/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'park_1.html')
        #check the context
        self.assertIn('plate', response.context)
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
        #check the if exists a payment
        payment = Payment.objects.filter(stop_id=Stop.objects.filter(plate=self.credentials['plate']).last().stop_id)
        self.assertTrue(payment)

        #test the non logged behaviour
        self.client.logout()
        self.client.login(username='wrong', password='wrong')
        response = self.client.post('/park_1/pay', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')