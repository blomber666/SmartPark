from django.test import TestCase
from users.models import User
from parkings.models import Stop, Payment, Statistic, Price
import os
from django.conf import settings
from django.utils import timezone
from django.test import Client
from datetime import datetime, timedelta, time as dtime
from dateutil import tz
from parkings.views import calculate_amount, get_stops
import time

class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    END = '\033[0m' #RESET COLOR
    CYAN = '\033[36m'
    GREEN = '\033[32m' # Dark Green
    YELLOW = '\033[33m' # Dark Yellow
    RED = '\033[31m' # Dark Red
    BLUE = '\033[34m' # Dark Blue
    MAGENTA = '\033[35m' # Dark Magenta
    WHITE = '\033[37m' # Dark White
    BLACK = '\033[30m' # Dark Black
    UNDERLINE = '\033[4m'
    BOLD = '\033[1m'
    INVISIBLE = '\033[08m'
    REVERSE = '\033[07m'


def printc(*args):
    color = args[0]
    strings = args[1::]
    c = getattr(bcolors,color)
    string=' '.join(map(str, strings))
    print(c + string + bcolors.END)
# Create your tests here.

class UrlsTest(TestCase):
    def setUp(self):

        self.credentials = {
            'username': 'test',
            'password': '12345678Test',
        }
        self.user = User.objects.create_user(**self.credentials)
        stop = Stop.objects.create(user=self.user, start_time=timezone.now(), park='1')

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

        #non logged behaviour
        self.client.logout()
        self.client.login(username='wrong', password='wrong')
        response = self.client.post('/park_1/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')

        # #check that media/park_1.png was created less than 30 secs ago
        # file_path = os.path.join(settings.MEDIA_ROOT, 'park_1.png')
        # self.assertTrue(os.path.exists(file_path))
        # if not(time.time() - os.path.getmtime(file_path) < 30):
        #     printc('ERROR', 'park_1.png was created more than 30 secs ago, check if the cronjob is working correctly')
        # self.assertTrue(time.time() - os.path.getmtime(file_path) < 30)

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

        #non logged behaviour
        self.client.logout()
        self.client.login(username='wrong', password='wrong')
        response = self.client.post('/park_1/pay', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')

    def test_get_parkings(self):
        #logged behaviour
        self.client.login(**self.credentials)
        json_context = self.client.get('/update_parkings/')
        #get the context
        json_context = json_context.json()
        self.assertIn('park_status', json_context)
        self.assertIn('park_percent', json_context)

        #non logged behaviour
        self.client.logout()
        self.client.login(username='wrong', password='wrong')
        json_context = self.client.get('/update_parkings/')
        #get the context
        json_context = json_context.json()
        self.assertEqual(json_context, {})

        


        
class CalculateAmontTest(TestCase):
    def test_calculate_amount(self):
        #price is for every minute
        # Test case 0
        default_price = 10
        Price.objects.all().delete()
        Price(price=20, day='Every Day', start_time=dtime(9), end_time=dtime(12)).save()

        start1 = datetime(2022, 1, 1, 0, 0)
        end1 = datetime(2022, 1, 2, 0, 0)

        start2 = datetime(2022, 1, 5, 0, 0)
        end2 = datetime(2022, 1, 6, 0, 0)

        start3 = datetime(2022, 1, 10, 23, 59, 59)
        end3 = datetime(2022, 1, 11, 23, 59, 59)

        start4 = datetime(2022, 1, 15, 23 ,59, 59)
        end4 = datetime(2022, 1, 17, 0, 0, 1)

        
        amount1 = calculate_amount(start1, end1, default_price)['amount']
        amount2 = calculate_amount(start2, end2, default_price)['amount']
        amount3 = calculate_amount(start3, end3, default_price)['amount']
        amount4 = calculate_amount(start4, end4, default_price)['amount']

        #check if all amonts are approximately the same (with a tolerance of 1%) 
        self.assertTrue(abs(amount1 - amount2) < 0.01*amount1)
        self.assertTrue(abs(amount1 - amount3) < 0.01*amount1)
        self.assertTrue(abs(amount1 - amount4) < 0.01*amount1)
        self.assertTrue(abs(amount2 - amount3) < 0.01*amount2)
        self.assertTrue(abs(amount2 - amount4) < 0.01*amount2)
        self.assertTrue(abs(amount3 - amount4) < 0.01*amount3)


        # Test case 1
        default_price = 10
        Price.objects.all().delete()
        Price(price=15, day='Every Wednesday', start_time=dtime(hour=12), end_time=dtime(hour=17)).save()
        Price(price=20, day='Every Day', start_time=dtime(9), end_time=dtime(12)).save()
        Price(price=25, date=datetime.strptime('2022-01-01', '%Y-%m-%d').date(), start_time=dtime(hour=9), end_time=dtime(hour=12)).save()

        start = datetime(2023, 2, 14, 8, 0)
        end = datetime(2023, 2, 16, 0, 0)
        #calculate the expected amount using the values of the test case
        expected_amount = (default_price + 3* 20 + 12*default_price) +(9*default_price + 3* 20 + 5* 15 + 7*default_price) 
        amount = calculate_amount(start, end, default_price=default_price)['amount']
        print('amount', amount)
        print('expected_amount', expected_amount)
        self.assertTrue(abs(amount - expected_amount) < expected_amount/10)


        #test case 2
        default_price = 10
        Price.objects.all().delete()
        Price(price=15, day='Every Wednesday', start_time=dtime(hour=12), end_time=dtime(hour=17)).save()
        Price(price=20, day='Every Day', start_time=dtime(9), end_time=dtime(12)).save()
        Price(price=25, date=datetime.strptime('2023-03-25', '%Y-%m-%d').date(), start_time=dtime(hour=9), end_time=dtime(hour=12)).save()

        start = datetime(2023, 3, 25, 8, 0)
        end = datetime(2023, 3, 26, 10, 0)
        remaining_times = [[start, end]]

        #calculate the expected amount using the values of the test case
        expected_amount = (default_price + 3*25+ 12*default_price) + (9*default_price + 20) 
        amount = calculate_amount(start, end, default_price=default_price)['amount']
        self.assertTrue(abs(amount - expected_amount) < expected_amount/10)


        #Test case 3
        default_price = 10
        Price.objects.all().delete()
        Price(price=15, day='Every Wednesday', start_time=dtime(hour=12), end_time=dtime(hour=17)).save()
        Price(price=20, day='Every Day', start_time=dtime(9), end_time=dtime(12)).save()
        Price(price=25, date=datetime.strptime('2023-05-01', '%Y-%m-%d').date(), start_time=dtime(hour=9), end_time=dtime(hour=12)).save()

        start = datetime(2023, 4, 30, 18, 0)
        end = datetime(2023, 5, 2, 10, 0)
        remaining_times = [[start, end]]

        #calculate the expected amount using the values of the test case
        expected_amount = (6*default_price) + (9*default_price + 3*25 + 12*default_price) + (9*default_price + 20)
        amount = calculate_amount(start, end, default_price=default_price)['amount']
        self.assertTrue(abs(amount - expected_amount) < expected_amount/10)


        #Test case 4
        default_price = 10
        #delete all the prices
        Price.objects.all().delete()
        Price(price=15, day='Every Monday', start_time=dtime(hour=8), end_time=dtime(hour=20)).save()
        Price(price=30, day='Every Tuesday', start_time=dtime(8), end_time=dtime(20)).save()
        Price(price=20, day='Every Day', start_time=dtime(8), end_time=dtime(20)).save()
        Price(price=25, date=datetime.strptime('2023-05-01', '%Y-%m-%d').date(), start_time=dtime(hour=8), end_time=dtime(hour=20)).save()

        start = datetime(2023, 2, 12, 6, 0)
        end = datetime(2023, 2, 16, 8, 0)
        #end = datetime(2023, 2, 16, 8, 0)
        remaining_times = [[start, end]]

        #calculate the expected amount using the values of the test case
        expected_amount = (2*default_price + 12*20 + 4*default_price) + (8*default_price + 12*15 + 4*default_price) + (8*default_price + 12*30 + 4*default_price) + (8*default_price + 12*20 + 4*default_price) + (8*default_price)
        amount = calculate_amount(start, end, default_price=default_price)['amount']
        self.assertTrue(abs(amount - expected_amount) < expected_amount/10)

class GetStopsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='AA111AA')

        self.stop1 = Stop.objects.create(user=self.user, start_time=(timezone.now() - timedelta(days=1)), end_time=timezone.now()) #from yesterday to today
        self.stop2 = Stop.objects.create(user=self.user, start_time=timezone.now(), end_time=timezone.now() + timedelta(days=1)) #from today to tomorrow
        self.stop3 = Stop.objects.create(user=self.user, start_time=timezone.now() - timedelta(days=3), end_time=timezone.now() - timedelta(days=2)) #from 3 days ago to 2 day ago
        self.payment1 = Payment.objects.create(stop=self.stop1, amount=10)
        self.payment2 = Payment.objects.create(stop=self.stop2, amount=20)

    def test_get_stops_with_dates(self):
        start_date = timezone.now() - timedelta(days=1) #yesterday
        end_date = timezone.now() + timedelta(days=1) #tomorrow
        park_num = None
        stops = get_stops(self.user, start_date, end_date, park_num)
        self.assertCountEqual(stops, [self.stop1, self.stop2])
        self.assertEqual(float(stops[0].amount.split('€')[0]), 10)
        self.assertEqual(float(stops[1].amount.split('€')[0]), 20)

    def test_get_stops_with_park_num(self):
        start_date = None
        end_date = None
        park_num = 1
        stops = get_stops(self.user, start_date, end_date, park_num)
        self.assertCountEqual(stops, [])

    def test_get_stops_with_no_dates(self):
        start_date = None
        end_date = None
        park_num = None
        stops = get_stops(self.user, start_date, end_date, park_num)
        self.assertCountEqual(stops, [self.stop1, self.stop2, self.stop3])
        self.assertEqual(float(stops[0].amount.split('€')[0]), 10)
        self.assertEqual(float(stops[1].amount.split('€')[0]), 20)
        self.assertEqual(stops[2].amount, f'{ calculate_amount(self.stop3.start_time)["amount"] }€ (not payed)')

    def test_get_stops_with_no_user(self):
        start_date = timezone.now() - timedelta(days=1)
        end_date = timezone.now() + timedelta(days=1)
        park_num = None
        with self.assertRaises(AssertionError):
            stops = get_stops(None, start_date, end_date, park_num)   









        