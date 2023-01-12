from django.test import TestCase
from users.models import User
from stops.models import Stop, Payment


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
        self.client.login(username='test', password='12345678Test')
        response = self.client.post('/park_1/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        assert(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'park_1.html')
        #check the context
        self.assertIn('plate', response.context)
        self.assertIn('start', response.context)
        self.assertIn('end', response.context)
        self.assertIn('amount', response.context)
        self.assertIn('free_spaces', response.context)

        #test the non logged behaviour
        self.client.logout()
        response = self.client.post('/park_1/', follow=True)
        self.assertEqual(response.status_code, 200)
        assert(not response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')

    #test the pay function
    def test_pay(self):
        self.client.login(username='test', password='12345678Test')
        response = self.client.post('/park_1/pay', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        assert(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'park_1.html')
        #check the if exists a payment
        payment = Payment.objects.filter(stop_id=Stop.objects.filter(plate=self.credentials['plate']).last().stop_id)
        self.assertTrue(payment)

        #test the non logged behaviour
        self.client.logout()
        response = self.client.post('/park_1/pay', follow=True)
        self.assertEqual(response.status_code, 200)
        assert(not response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')