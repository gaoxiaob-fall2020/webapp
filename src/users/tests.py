from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json

User = get_user_model()

test_user1 = {
    'first_name': 'Test',
    'last_name': 'One',
    'email_address': 'Test1@webapp.com',
    'password': 'P@ssword!'
}

test_user2 = {
    'first_name': 'Test',
    'last_name': 'Two',
    'email_address': 'Test2@webapp.com',
    'password': 'P@ssword+'
}

def auth_user_setup(self, user1=True):
    user = User.objects.create(**test_user1) if user1 else User.objects.create(**test_user2)
    auth_token = Token.objects.create(user=user)
    self.client.credentials(HTTP_AUTHORIZATION=f'Token {auth_token.key}')
    return user

def unauth_user_setup(self):
    user = User.objects.create(**test_user1)
    self.client.force_authenticate(user=None)
    return user

def create_user_unauth(self, req_data):
    # user = User.objects.filter(email_address=test_user1['email_address'])
    # if user:
    #     user.delete()
    payload = json.dumps(req_data)
    response = self.client.post(
        reverse('user_create'),
        data=payload,
        content_type='application/json'
    )
    return response

def get_user_auth(self):
    pass

def update_user_auth(self, user, req_data):
    payload = json.dumps(req_data)
    response = self.client.put(
        reverse('user_info', args=[user.email_address]),
        data=payload,
        content_type='application/json'
    )
    return response


# Authentication for API calls testing
class AuthenticationTestCase(APITestCase):  
    def test_unauth_create_user(self):
        response = create_user_unauth(self, test_user1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auth_get_user(self):
        user = auth_user_setup(self)
        response = self.client.get(reverse('user_info', args=[user.email_address]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauth_get_user(self):
        user = unauth_user_setup(self)
        response = self.client.get(reverse('user_info', args=[user.email_address]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_update_user(self):
        user = auth_user_setup(self)
        response = update_user_auth(self, user, test_user1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauth_update_user(self):
        user = unauth_user_setup(self)
        payload = json.dumps(test_user1)
        response = self.client.put(
            reverse('user_info', args=[user.email_address]),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# Response content testing
class RespContentTestCase(APITestCase):
    def test_create_user(self):
        response = create_user_unauth(self, test_user1)
        resp_payload = response.json()
        self.assertEqual(len(resp_payload), 6)
        for arg in ('id', 'first_name', 'last_name', 'email_address', 'account_created', 'account_updated'):
            self.assertTrue(arg in resp_payload)
        # self.assertFalse('password' in resp_payload)

    def test_get_user(self):
        user = auth_user_setup(self)
        response = self.client.get(reverse('user_info', args=[user.email_address]))
        resp_payload = response.json()
        self.assertEqual(len(resp_payload), 6)
        for arg in ('id', 'first_name', 'last_name', 'email_address', 'account_created', 'account_updated'):
            self.assertTrue(arg in resp_payload)


# Bad requests handing testing
class BadReqHandingTestCase(APITestCase):
    def test_create_user(self):
        # User already exists
        user = User.objects.create(**test_user1)
        response = create_user_unauth(self, test_user1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.delete()

        # Request paramenters miss
        test_user1_cp = dict(test_user1)
        for k in test_user1:
            del test_user1_cp[k]
            response = create_user_unauth(self, test_user1_cp)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            test_user1_cp[k] = test_user1[k]
        self.assertEqual(create_user_unauth(self, None).status_code, status.HTTP_400_BAD_REQUEST)

        # Request paramenters overload
        test_user1_cp['dummy_arg'] = 'some_dummy_value'
        self.assertEqual(create_user_unauth(self, test_user1_cp).status_code, status.HTTP_201_CREATED)

    def test_update_user(self):
        user = auth_user_setup(self)

        # Request paramenters miss
        test_user1_cp = dict(test_user1)
        for k in test_user1:
            del test_user1_cp[k]
            response = update_user_auth(self, user, test_user1_cp)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            test_user1_cp[k] = test_user1[k]
        self.assertEqual(update_user_auth(self, user, None).status_code, status.HTTP_400_BAD_REQUEST)

        # Request paramenters overload
        test_user1_cp['dummy_arg'] = 'some_dummy_value'
        self.assertEqual(update_user_auth(self, user, test_user1_cp).status_code, status.HTTP_204_NO_CONTENT)

        # Email is already taken by other user
        user2 = auth_user_setup(self, False)
        self.assertEqual(update_user_auth(self, user, test_user2).status_code, status.HTTP_400_BAD_REQUEST)

        
