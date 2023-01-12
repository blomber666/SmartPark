from django.test import TestCase
from users.models import User
from thingsboard_api_tools import TbApi
import time
# Create your tests here.
class UrlTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'fogli',
            'password': '12345678'}
        User.objects.create_superuser(**self.credentials)
        # ThingsBoard REST API URL
        url = "http://192.168.1.197:8080"
        # Default Tenant Administrator credentials
        username = "tenant@thingsboard.org"
        password = "tenant"
        self.tbapi = TbApi(url, username, password)

    def test_admin(self):
        response = self.client.post('/admin/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_administration(self):
        #logged behaviour
        self.client.login(**self.credentials)
        response = self.client.post('/administration/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'administration.html')
        #check the context
        self.assertIn('active_stops', response.context)
        self.assertIn('completed_stops', response.context)

        #test the non logged behaviour
        self.client.logout()
        self.client.login(username='wrong', password='wrong')
        response = self.client.post('/administration/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')


    def test_override(self):
        #logged behaviour
        self.client.login(**self.credentials)
        response = self.client.post('/administration/override/', self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'administration.html')

        #simulate the form with the button entry_open
        response = self.client.post('/administration/override/', {'entry_open': 'entry_open'}, follow=True)
        #get the telemetry of the device named 'override_1_1'
        entry_door = self.tbapi.get_tenant_device(name='override_1_1')
        entry_door_telemetry = self.tbapi.get_latest_telemetry(entry_door['id'], telemetry_keys=["value"])
        last_tel = entry_door_telemetry['value'][0]
        self.assertEqual(last_tel['value'], 'open')
        #check that timestamp is less than 10 seconds from now
        self.assertLess(time.time() - last_tel['ts'], 10)

        #simulate the form with the button entry_close
        response = self.client.post('/administration/override/', {'entry_close': 'entry_close'}, follow=True)
        #get the telemetry of the device named 'override_1_1'
        entry_door = self.tbapi.get_tenant_device(name='override_1_1')
        entry_door_telemetry = self.tbapi.get_latest_telemetry(entry_door['id'], telemetry_keys=["value"])
        last_tel = entry_door_telemetry['value'][0]
        self.assertEqual(last_tel['value'], 'close')
        #check that timestamp is less than 10 seconds from now
        self.assertLess(time.time() - last_tel['ts'], 10)

        #simulate the form with the button entry_normal
        response = self.client.post('/administration/override/', {'entry_normal': 'entry_normal'}, follow=True)
        #get the telemetry of the device named 'override_1_1'
        entry_door = self.tbapi.get_tenant_device(name='override_1_1')
        entry_door_telemetry = self.tbapi.get_latest_telemetry(entry_door['id'], telemetry_keys=["value"])
        last_tel = entry_door_telemetry['value'][0]
        self.assertEqual(last_tel['value'], 'null')
        #check that timestamp is less than 10 seconds from now
        self.assertLess(time.time() - last_tel['ts'], 10)

        #simulate the form with the button exit_open
        response = self.client.post('/administration/override/', {'exit_open': 'exit_open'}, follow=True)
        #get the telemetry of the device named 'override_1_2'
        exit_door = self.tbapi.get_tenant_device(name='override_1_2')
        exit_door_telemetry = self.tbapi.get_latest_telemetry(exit_door['id'], telemetry_keys=["value"])
        last_tel = exit_door_telemetry['value'][0]
        self.assertEqual(last_tel['value'], 'open')
        #check that timestamp is less than 10 seconds from now
        self.assertLess(time.time() - last_tel['ts'], 10)

        #simulate the form with the button exit_close
        response = self.client.post('/administration/override/', {'exit_close': 'exit_close'}, follow=True)
        #get the telemetry of the device named 'override_1_2'
        exit_door = self.tbapi.get_tenant_device(name='override_1_2')
        exit_door_telemetry = self.tbapi.get_latest_telemetry(exit_door['id'], telemetry_keys=["value"])
        last_tel = exit_door_telemetry['value'][0]
        self.assertEqual(last_tel['value'], 'close')
        #check that timestamp is less than 10 seconds from now
        self.assertLess(time.time() - last_tel['ts'], 10)

        #simulate the form with the button exit_normal
        response = self.client.post('/administration/override/', {'exit_normal': 'exit_normal'}, follow=True)
        #get the telemetry of the device named 'override_1_2'
        exit_door = self.tbapi.get_tenant_device(name='override_1_2')
        exit_door_telemetry = self.tbapi.get_latest_telemetry(exit_door['id'], telemetry_keys=["value"])
        last_tel = exit_door_telemetry['value'][0]
        self.assertEqual(last_tel['value'], 'null')
        #check that timestamp is less than 10 seconds from now
        self.assertLess(time.time() - last_tel['ts'], 10)

        #test the non logged behaviour
        self.client.logout()
        self.client.login(username='wrong', password='wrong')
        response = self.client.post('/administration/override/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertTemplateUsed(response, 'login.html')






        
