from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json

User = get_user_model()

test_user = {
    'first_name': 'Web',
    'last_name': 'App',
    'email_address': 'webapp@email.com',
    'password': 'some_strong_psw'
}


# Authentication for API calls testing
class AuthenticationTestCase(APITestCase):  
    def __auth_setup(self):
        user = User.objects.create(**test_user)
        auth_token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {auth_token.key}')
        return user

    def __unauth_setup(self):
        user = User.objects.create(**test_user)
        self.client.force_authenticate(user=None)
        return user

    def test_unauth_create_user(self):
        user = User.objects.filter(email_address=test_user['email_address'])
        # if user:
        #     user.delete()
        payload = json.dumps(test_user)
        response = self.client.post(
            reverse('user_create'),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auth_get_user(self):
        user = self.__auth_setup()
        response = self.client.get(reverse('user_info', args=[user.email_address]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauth_get_user(self):
        user = self.__unauth_setup()
        response = self.client.get(reverse('user_info', args=[user.email_address]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_update_user(self):
        user = self.__auth_setup()
        payload = json.dumps(test_user)
        response = self.client.put(
            reverse('user_info', args=[user.email_address]),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauth_update_user(self):
        user = self.__unauth_setup()
        payload = json.dumps(test_user)
        response = self.client.put(
            reverse('user_info', args=[user.email_address]),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
