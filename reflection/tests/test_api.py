# -*- coding: utf-8 -*-

import json

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory


class ApiAuthTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

    # def test_details(self):
    #     # Create an instance of a GET request.
    #     request = self.factory.get('/customer/details')

    #     # Recall that middleware are not supported. You can simulate a
    #     # logged-in user by setting request.user manually.
    #     request.user = self.user

    #     # Or you can simulate an anonymous user by setting request.user to
    #     # an AnonymousUser instance.
    #     request.user = AnonymousUser()

    #     # Test my_view() as if it were deployed at /customer/details
    #     response = my_view(request)
    #     self.assertEqual(response.status_code, 200)

    def test_create_user(self):

        response = self.client.post(
            '/api/register',
            content_type='application/json',
            data=json.dumps({'username': 'test_user', 'email': 'test@test.com', 'password': 'supersecret'})
        )

        user = User.objects.get(email='test@test.com')
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(response.status_code, 200)

    def test_use_token(self):

        response = self.client.post(
            '/api/register',
            content_type='application/json',
            data=json.dumps({'username': 'test_user', 'email': 'test@test.com', 'password': 'supersecret'})
        )

        data = json.loads(response.content)

        response = self.client.post(
            '/api/event',
            content_type='application/json',
            data=json.dumps({'token': data['token']})
        )

    def test_login_user(self):

        user = User.objects.create_user('tester', 'this@test.com', 'thepassword')

        response = self.client.post(
            '/api/login',
            content_type='application/json',
            data=json.dumps({'username': user.username, 'password': 'thepassword'})
        )
        self.assertIsNotNone(json.loads(response.content)['token'])
