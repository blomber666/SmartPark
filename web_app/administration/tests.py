from django.test import TestCase
from users.models import User
from parkings.models import Price
from thingsboard_api_tools import TbApi
import datetime, time
from administration.views import price_control
#Create your tests here.
class UrlTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'fogli',
            'password': '12345678'}
        User.objects.create_superuser(**self.credentials)
        #ThingsBoard REST API URL
        url = "http://192.168.1.197:8080"
        #Default Tenant Administrator credentials
        username = "tenant@thingsboard.org"
        password = "tenant"
        self.tbapi = TbApi(url, username, password)

    def test_admin(self):
        response = self.client.post('/admin/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_administration(self):
        #logged behaviour
        self.client.logout()
        self.client.login(**self.credentials)
        response = self.client.get('/administration/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'administration.html')
        #check the context
        self.assertIn('active_stops', response.context)
        self.assertIn('completed_stops', response.context)
        self.assertIn('stats', response.context)
        self.assertIn('prices', response.context)

        #with post
        response = self.client.post('/administration/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'administration.html')
        #check the context
        self.assertIn('active_stops', response.context)
        self.assertIn('completed_stops', response.context)
        self.assertIn('stats', response.context)
        self.assertIn('prices', response.context)

        #non logged behaviour
        self.client.logout()
        self.client.login(username='wrong', password='wrong')
        response = self.client.get('/administration/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')

    def test_override(self):
        #logged behaviour
        self.client.logout()
        self.client.login(**self.credentials)
        response = self.client.post('/administration/override/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'administration.html')

        #simulate the form with the button entry_open
        response = self.client.post('/administration/override/', {'entry_open': 'entry_open'}, follow=True)
        #get the telemetry of the device named 'override_1_1'
        entry_door = self.tbapi.get_device_by_name(name='override_1_1')
        entry_door_telemetry = self.tbapi.get_latest_telemetry(entry_door['id'], telemetry_keys=["value"])
        last_tel = entry_door_telemetry['value'][0]
        self.assertEqual(last_tel['value'], 'open')
        #check that timestamp is less than 10 seconds from now
        self.assertLess(time.time() - last_tel['ts'], 10)

        #simulate the form with the button entry_close
        response = self.client.post('/administration/override/', {'entry_close': 'entry_close'}, follow=True)
        #get the telemetry of the device named 'override_1_1'
        entry_door = self.tbapi.get_device_by_name(name='override_1_1')
        entry_door_telemetry = self.tbapi.get_latest_telemetry(entry_door['id'], telemetry_keys=["value"])
        last_tel = entry_door_telemetry['value'][0]
        self.assertEqual(last_tel['value'], 'close')
        #check that timestamp is less than 10 seconds from now
        self.assertLess(time.time() - last_tel['ts'], 10)

        #simulate the form with the button entry_default
        response = self.client.post('/administration/override/', {'entry_default': 'entry_default'}, follow=True)
        #get the telemetry of the device named 'override_1_1'
        entry_door = self.tbapi.get_device_by_name(name='override_1_1')
        entry_door_telemetry = self.tbapi.get_latest_telemetry(entry_door['id'], telemetry_keys=["value"])
        last_tel = entry_door_telemetry['value'][0]
        self.assertEqual(last_tel['value'], 'null')
        #check that timestamp is less than 10 seconds from now
        self.assertLess(time.time() - last_tel['ts'], 10)

        #simulate the form with the button exit_open
        response = self.client.post('/administration/override/', {'exit_open': 'exit_open'}, follow=True)
        #get the telemetry of the device named 'override_1_2'
        exit_door = self.tbapi.get_device_by_name(name='override_1_2')
        exit_door_telemetry = self.tbapi.get_latest_telemetry(exit_door['id'], telemetry_keys=["value"])
        last_tel = exit_door_telemetry['value'][0]
        self.assertEqual(last_tel['value'], 'open')
        #check that timestamp is less than 10 seconds from now
        self.assertLess(time.time() - last_tel['ts'], 10)

        #simulate the form with the button exit_close
        response = self.client.post('/administration/override/', {'exit_close': 'exit_close'}, follow=True)
        #get the telemetry of the device named 'override_1_2'
        exit_door = self.tbapi.get_device_by_name(name='override_1_2')
        exit_door_telemetry = self.tbapi.get_latest_telemetry(exit_door['id'], telemetry_keys=["value"])
        last_tel = exit_door_telemetry['value'][0]
        self.assertEqual(last_tel['value'], 'close')
        #check that timestamp is less than 10 seconds from now
        self.assertLess(time.time() - last_tel['ts'], 10)

        #simulate the form with the button exit_default
        response = self.client.post('/administration/override/', {'exit_default': 'exit_default'}, follow=True)
        #get the telemetry of the device named 'override_1_2'
        exit_door = self.tbapi.get_device_by_name(name='override_1_2')
        exit_door_telemetry = self.tbapi.get_latest_telemetry(exit_door['id'], telemetry_keys=["value"])
        last_tel = exit_door_telemetry['value'][0]
        self.assertEqual(last_tel['value'], 'null')
        #check that timestamp is less than 10 seconds from now
        self.assertLess(time.time() - last_tel['ts'], 10)
        
        #non logged behaviour
        self.client.logout()
        self.client.login(username='wrong', password='wrong')
        response = self.client.post('/administration/override/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')

class PriceTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'fogli',
            'password': '12345678'}
        User.objects.create_superuser(**self.credentials)
        #ThingsBoard REST API URL
        url = "http://192.168.1.197:8080"
        #Default Tenant Administrator credentials
        username = "tenant@thingsboard.org"
        password = "tenant"
        self.tbapi = TbApi(url, username, password)

    def test_price_date(self):
        self.client.logout()
        self.client.login(**self.credentials)

        #simulate the form with all fields
        Price.objects.all().delete()
        tomorrow1 = datetime.date.today() + datetime.timedelta(days=1) 
        # conert tomorrow in dd/mm/yyyy format
        tomorrow = tomorrow1.strftime('%d/%m/%Y')
        #add
        response = self.client.post('/administration/price/', {'add':'', 'price_date': tomorrow, 'price_price': '1.0', \
            'price_start_time': '00:00:00', 'price_end_time': '23:59:59'}, follow=True)
        #check that new row is in the database
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        #edit
        #get the id of the row to edit
        price = Price.objects.get(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_date': tomorrow, 'price_price': '2.0', \
            'price_start_time': '00:00:00', 'price_end_time': '23:59:59'}, follow=True)
        #check that the row is updated
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=2.0, start_time='00:00:00', end_time='23:59:59').exists())
        #delete
        #get the id of the row to delete
        price = Price.objects.get(date=tomorrow1, price=2.0, start_time='00:00:00', end_time='23:59:59')
        print('price.id: ' + str(price.id))
        response = self.client.post('/administration/price/', {'delete': '', 'price_id': price.id}, follow=True)
        #check that the row is deleted
        self.assertFalse(Price.objects.filter(date=tomorrow1, price=2.0, start_time='00:00:00', end_time='23:59:59').exists())

        #simulate the form with only date
        #but no price is given, so the row is not added   
        #add
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_date': tomorrow, \
            'price_start_time': '00:00:00', 'price_end_time': '23:59:59'}, follow=True)
        #check that new row is not in the database
        self.assertFalse(Price.objects.filter(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        #edit
        #add a row to edit
        Price.objects.all().delete()
        Price.objects.create(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59')
        #get the id of the row to edit
        price = Price.objects.get(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_price': '', \
            'price_start_time': '00:00:00', 'price_end_time': '23:59:59'}, follow=True)
        #check that the row is not updated
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        #delete the row
        price = Price.objects.get(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'delete': '', 'price_id': price.id}, follow=True)
        #check if no row exists
        self.assertFalse(Price.objects.all().exists())

        #simulate the form with only date
        #but price is negative, so the row isnt added
        #add
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_date': tomorrow, 'price_price': '-1.0', \
            'price_start_time': '00:00:00', 'price_end_time': '23:59:59'}, follow=True)
        #check that new row is not in the database
        self.assertFalse(Price.objects.filter(date=tomorrow1, price=-1.0, start_time='00:00:00', end_time='23:59:59').exists())
        #edit
        #add a row to edit
        Price.objects.all().delete()
        Price.objects.create(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59')
        #get the id of the row to edit
        price = Price.objects.get(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_price': '-1.0', \
            'price_start_time': '00:00:00', 'price_end_time': '23:59:59'}, follow=True)
        #check that the row is not updated
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        self.assertFalse(Price.objects.filter(date=tomorrow1, price=-1.0, start_time='00:00:00', end_time='23:59:59').exists())

        #simulate the form with date and price
        #but no start time is given, so the start time must be 00:00:00
        #add
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_date': tomorrow, 'price_price': '1.0', \
            'price_end_time': '23:59:59'}, follow=True)
        #check that new row is in the database
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        #edit
        #get the id of the row to edit
        price = Price.objects.get(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_date': tomorrow, 'price_price': '2.0', \
            'price_end_time': '23:59:59'}, follow=True)
        #check that the row is updated
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=2.0, start_time='00:00:00', end_time='23:59:59').exists())
        #delete
        #get the id of the row to delete
        price = Price.objects.get(date=tomorrow1, price=2.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'delete': '', 'price_id': price.id}, follow=True)
        #check that the row is deleted
        self.assertFalse(Price.objects.filter(date=tomorrow1, price=2.0, start_time='00:00:00', end_time='23:59:59').exists())

        #simulate the form with date and price
        #but no end time is given, so the end time must be 23:59:59
        #add
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_date': tomorrow, 'price_price': '1.0', \
            'price_start_time': '00:00:00'}, follow=True)
        #check that new row is in the database
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        #edit
        #get the id of the row to edit
        price = Price.objects.get(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_date': tomorrow, 'price_price': '2.0', \
            'price_start_time': '00:00:00'}, follow=True)
        #check that the row is updated
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=2.0, start_time='00:00:00', end_time='23:59:59').exists())
        #delete
        #get the id of the row to delete
        price = Price.objects.get(date=tomorrow1, price=2.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'delete': '', 'price_id': price.id}, follow=True)
        #check that the row is deleted
        self.assertFalse(Price.objects.filter(date=tomorrow1, price=2.0, start_time='00:00:00', end_time='23:59:59').exists())

        #simulate the form with start time after end time
        #add
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_date': tomorrow, 'price_price': '1.0', \
            'price_start_time': '12:00:00', 'price_end_time': '11:00:00'}, follow=True)
        #check that no row is in the database
        self.assertFalse(Price.objects.filter(date=tomorrow1, price=1.0, start_time='12:00:00', end_time='11:00:00').exists())
        #edit
        #create a row to edit
        Price.objects.all().delete()
        Price.objects.create(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59')
        #get the id of the row to edit
        price = Price.objects.get(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_date': tomorrow, 'price_price': '2.0', \
            'price_start_time': '12:00:00', 'price_end_time': '11:00:00'}, follow=True)
        #check that the row is not updated
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        self.assertFalse(Price.objects.filter(date=tomorrow1, price=2.0, start_time='12:00:00', end_time='11:00:00').exists())
        
        
        #simulate the form with date and price
        #add 2 rows with conflicting times
        #delete all prices
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_date': tomorrow, 'price_price': '1.0', \
            'price_start_time': '00:00:00', 'price_end_time': '12:00:00'}, follow=True)
        response = self.client.post('/administration/price/', {'add':'', 'price_date': tomorrow, 'price_price': '1.0', \
            'price_start_time': '11:00:00', 'price_end_time': '23:59:59'}, follow=True)
        #check that only the first row is in the database
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='12:00:00').exists())
        self.assertFalse(Price.objects.filter(date=tomorrow1, price=1.0, start_time='11:00:00', end_time='23:59:59').exists())
        #edit the first row to have no conflicts
        price = Price.objects.get(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='12:00:00')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_date': tomorrow, 'price_price': '2.0', \
            'price_start_time': '00:00:00', 'price_end_time': '10:00:00'}, follow=True)
        #check that the row is updated
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=2.0, start_time='00:00:00', end_time='10:00:00').exists())

        
        #test conflicts with edit
        #add 2 rows with no conflicts
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_date': tomorrow, 'price_price': '1.0', \
            'price_start_time': '00:00:00', 'price_end_time': '12:00:00'}, follow=True)
        response = self.client.post('/administration/price/', {'add':'', 'price_date': tomorrow, 'price_price': '1.0', \
            'price_start_time': '12:00:01', 'price_end_time': '23:59:59'}, follow=True)
        #edit the first row to have a conflict
        price = Price.objects.get(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='12:00:00')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_date': tomorrow, 'price_price': '1.0', \
            'price_start_time': '11:00:00', 'price_end_time': '23:59:59'}, follow=True)
        #check that the row is not updated
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=1.0, start_time='00:00:00', end_time='12:00:00').exists())
        self.assertTrue(Price.objects.filter(date=tomorrow1, price=1.0, start_time='12:00:01', end_time='23:59:59').exists())
        self.assertFalse(Price.objects.filter(date=tomorrow1, price=1.0, start_time='11:00:00', end_time='23:59:59').exists())

    def test_price_day(self):
        ##------------DAY TESTS-------------------## (same as date but with day instead of date)
        self.client.logout()
        self.client.login(**self.credentials)
        
        #simulate the form with all fields
        #add
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_day': 'Everyday', 'price_price': '1.0', \
            'price_start_time': '00:00:00', 'price_end_time': '23:59:59'}, follow=True)
        #check that new row is in the database
        self.assertTrue(Price.objects.filter(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        #edit
        #get the id of the row to edit
        price = Price.objects.get(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_day': 'Everyday', 'price_price': '2.0', \
            'price_start_time': '00:00:00', 'price_end_time': '23:59:59'}, follow=True)
        #check that the row is updated
        self.assertTrue(Price.objects.filter(day='Everyday', price=2.0, start_time='00:00:00', end_time='23:59:59').exists())
        #delete
        #get the id of the row to delete
        price = Price.objects.get(day='Everyday', price=2.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'delete': '', 'price_id': price.id}, follow=True)
        #check that the row is deleted
        self.assertFalse(Price.objects.filter(day='Everyday', price=2.0, start_time='00:00:00', end_time='23:59:59').exists())

        #simulate the form with only day
        #but no price is given, so the row is not added
        #add
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_day': 'Everyday'}, follow=True)
        #check that new row is not in the database
        self.assertFalse(Price.objects.filter(day='Everyday').exists())
        #edit
        #create a row to edit
        Price.objects.all().delete()
        Price.objects.create(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59')
        #get the id of the row to edit
        price = Price.objects.get(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_price': ''}, follow=True)
        #check that the row is not updated
        self.assertTrue(Price.objects.filter(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        #delete the row
        price = Price.objects.get(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59')
        price.delete()
        #check if no row exists
        self.assertFalse(Price.objects.all().exists())


        #simulate the form with only day
        #but price is negative, so the row is not added
        #add
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_day': 'Everyday', 'price_price': '-1.0'}, follow=True)
        #check that new row is not in the database
        self.assertFalse(Price.objects.filter(day='Everyday', price=-1.0).exists())
        #edit
        #create a row to edit
        Price.objects.all().delete()
        Price.objects.create(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59')
        #get the id of the row to edit
        price = Price.objects.get(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_price': '-1.0'}, follow=True)
        #check that the row is not updated
        self.assertTrue(Price.objects.filter(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        self.assertFalse(Price.objects.filter(day='Everyday', price=-1.0, start_time='00:00:00', end_time='23:59:59').exists())

        #simulate the form with day and price
        #but no start time is given, so the start time must be 00:00:00
        #add
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_day': 'Everyday', 'price_price': '1.0', 'price_end_time': '23:59:59'}, follow=True)
        #check that new row is in the database
        self.assertTrue(Price.objects.filter(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        #edit
        #get the id of the row to edit
        price = Price.objects.get(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_day': 'Everyday', 'price_price': '2.0', \
            'price_start_time': '00:00:00', 'price_end_time': '12:59:59'}, follow=True)
        #check that the row is updated
        self.assertTrue(Price.objects.filter(day='Everyday', price=2.0, start_time='00:00:00', end_time='12:59:59').exists())
        #delete
        #get the id of the row to delete
        price = Price.objects.get(day='Everyday', price=2.0, start_time='00:00:00', end_time='12:59:59')
        response = self.client.post('/administration/price/', {'delete': '', 'price_id': price.id}, follow=True)
        #check that the row is deleted
        self.assertFalse(Price.objects.filter(day='Everyday', price=2.0, start_time='00:00:00', end_time='12:59:59').exists())

        #simulate the form with day and price
        #but no end time is given, so the end time must be 23:59:59
        #add
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_day': 'Everyday', 'price_price': '1.0', 'price_start_time': '00:00:00'}, follow=True)
        #check that new row is in the database
        self.assertTrue(Price.objects.filter(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        #edit
        #get the id of the row to edit
        price = Price.objects.get(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_day': 'Everyday', 'price_price': '2.0', \
            'price_start_time': '00:00:00', 'price_end_time': '12:59:59'}, follow=True)
        #check that the row is updated
        self.assertTrue(Price.objects.filter(day='Everyday', price=2.0, start_time='00:00:00', end_time='12:59:59').exists())
        #delete
        #get the id of the row to delete
        price = Price.objects.get(day='Everyday', price=2.0, start_time='00:00:00', end_time='12:59:59')
        response = self.client.post('/administration/price/', {'delete': '', 'price_id': price.id}, follow=True)
        #check that the row is deleted
        self.assertFalse(Price.objects.filter(day='Everyday', price=2.0, start_time='00:00:00', end_time='12:59:59').exists())

        #simulate the form with start time after end time
        #add
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_day': 'Everyday', 'price_price': '1.0', 'price_start_time': '12:00:00', 'price_end_time': '11:00:00'}, follow=True)
        #check that no row is in the database
        self.assertFalse(Price.objects.filter(day='Everyday', price=1.0, start_time='12:00:00', end_time='11:00:00').exists())
        #edit
        #create a row to edit
        Price.objects.create(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59')
        #get the id of the row to edit
        price = Price.objects.get(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_day': 'Everyday', 'price_price': '2.0', \
            'price_start_time': '12:00:00', 'price_end_time': '11:00:00'}, follow=True)
        #check that the row is not updated
        self.assertTrue(Price.objects.filter(day='Everyday', price=1.0, start_time='00:00:00', end_time='23:59:59').exists())
        self.assertFalse(Price.objects.filter(day='Everyday', price=2.0, start_time='12:00:00', end_time='11:00:00').exists())

        #simulate the form with day and price
        #add 2 rows with conflicting times
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_day': 'Everyday', 'price_price': '1.0', 'price_start_time': '00:00:00', 'price_end_time': '12:00:00'}, follow=True)
        response = self.client.post('/administration/price/', {'add':'', 'price_day': 'Everyday', 'price_price': '1.0', 'price_start_time': '11:00:00', 'price_end_time': '23:59:59'}, follow=True)
        #check that only the first row is in the database
        self.assertTrue(Price.objects.filter(day='Everyday', price=1.0, start_time='00:00:00', end_time='12:00:00').exists())
        self.assertFalse(Price.objects.filter(day='Everyday', price=1.0, start_time='11:00:00', end_time='23:59:59').exists())
        #edit the first row to have no conflicts
        #get the id of the row to edit
        price = Price.objects.get(day='Everyday', price=1.0, start_time='00:00:00', end_time='12:00:00')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_day': 'Everyday', 'price_price': '2.0', \
            'price_start_time': '00:00:00', 'price_end_time': '10:00:00'}, follow=True)
        #check that the row is updated
        self.assertTrue(Price.objects.filter(day='Everyday', price=2.0, start_time='00:00:00', end_time='10:00:00').exists())

        #test conflict with edit
        #add 2 rows with no conflicts
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_day': 'Everyday', 'price_price': '1.0', 'price_start_time': '00:00:00', 'price_end_time': '12:00:00'}, follow=True)
        response = self.client.post('/administration/price/', {'add':'', 'price_day': 'Everyday', 'price_price': '1.0', 'price_start_time': '13:00:00', 'price_end_time': '23:59:59'}, follow=True)
        #check that both rows are in the database
        self.assertTrue(Price.objects.filter(day='Everyday', price=1.0, start_time='00:00:00', end_time='12:00:00').exists())
        self.assertTrue(Price.objects.filter(day='Everyday', price=1.0, start_time='13:00:00', end_time='23:59:59').exists())
        #edit the first row to have conflicts
        #get the id of the row to edit
        price = Price.objects.get(day='Everyday', price=1.0, start_time='00:00:00', end_time='12:00:00')
        response = self.client.post('/administration/price/', {'edit': '', 'price_id': price.id, 'price_day': 'Everyday', 'price_price': '2.0', \
            'price_start_time': '00:00:00', 'price_end_time': '14:00:00'}, follow=True)
        #check that the row is not updated
        self.assertTrue(Price.objects.filter(day='Everyday', price=1.0, start_time='00:00:00', end_time='12:00:00').exists())
        self.assertTrue(Price.objects.filter(day='Everyday', price=1.0, start_time='13:00:00', end_time='23:59:59').exists())
        self.assertFalse(Price.objects.filter(day='Everyday', price=2.0, start_time='00:00:00', end_time='14:00:00').exists())

    def test_price_general(self):
        #logged behaviour
        self.client.logout()
        self.client.login(**self.credentials)
        response = self.client.post('/administration/price/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'administration.html')

        #------------------GENERAL TESTS------------------
        #test add with no date and no day
        Price.objects.all().delete()
        response = self.client.post('/administration/price/', {'add':'', 'price_price': '1.0', 'price_start_time': '00:00:00', 'price_end_time': '12:00:00'}, follow=True)
        #check all messages.error for 'Date or day must be filled'
        self.assertTrue(any('Date or day must be filled' in str(message) for message in response.context['messages']))
        
        #check that no rows are in the database
        self.assertFalse(Price.objects.all().exists())

        #test with both date and day
        Price.objects.all().delete()
        tomorrow1 = datetime.date.today() + datetime.timedelta(days=1) 
        # conert tomorrow in dd/mm/yyyy format
        tomorrow = tomorrow1.strftime('%d/%m/%Y')

        response = self.client.post('/administration/price/', {'add':'', 'price_day': 'Everyday', 'price_price': '1.0', 'price_start_time': '00:00:00', 'price_end_time': '12:00:00', 'price_date': tomorrow}, follow=True)
        #check all messages.error for 'Date and day cannot be filled at the same time'
        self.assertTrue(any('Date and day cannot be filled at the same time' in str(message) for message in response.context['messages']))
        #check that no rows are in the database
        self.assertFalse(Price.objects.all().exists())

        #non logged behaviour
        self.client.logout()
        self.client.login(username='wrong', password='wrong')
        response = self.client.post('/administration/price/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')