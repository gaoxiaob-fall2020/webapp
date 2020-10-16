import base64
import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()

test_user1 = {
    'first_name': 'Test',
    'last_name': 'One',
    'username': 'Test1@webapp.com',
    'password': 'P@ssword1!'
}

test_user2 = {
    'first_name': 'Test',
    'last_name': 'Two',
    'username': 'Test2@webapp.com',
    'password': 'P@ssword2+'
}


def auth_user_setup(self, user1=True):
    user = User.objects.create(**test_user1) if user1 else User.objects.create(**test_user2)
    # auth_token = Token.objects.create(user=user)
    # self.client.credentials(HTTP_AUTHORIZATION=f'Token {auth_token.key}')
    if user1:
        auth_basic = f'{test_user1["username"]}:{test_user1["password"]}'
    else:
        auth_basic = f'{test_user2["username"]}:{test_user2["password"]}'
    self.client.credentials(HTTP_AUTHORIZATION=f'Basic {base64.b64encode(auth_basic.encode()).decode()}')
    return user


def unauth_user_setup(self):
    user = User.objects.create(**test_user1)
    self.client.force_authenticate(user=None)
    return user


def create_user_unauth(self, req_data):
    payload = json.dumps(req_data)
    response = self.client.post(
        reverse('user_create'),
        data=payload,
        content_type='application/json'
    )
    return response


def update_user_auth(self, user, req_data):
    payload = json.dumps(req_data)
    response = self.client.put(
        reverse('user_info'),
        data=payload,
        content_type='application/json'
    )
    return response


# Authentication for API calls testing
class AuthenticationTestCase(APITestCase):
    def test_unauth_create_user(self):
        response = create_user_unauth(self, test_user1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auth_create_user(self):
        auth_user_setup(self, test_user1)
        payload = json.dumps(test_user2)
        response = self.client.post(
            reverse('user_create'),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auth_get_user(self):
        auth_user_setup(self)
        response = self.client.get(reverse('user_info'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauth_get_user(self):
        unauth_user_setup(self)
        response = self.client.get(reverse('user_info'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_update_user(self):
        user = auth_user_setup(self)
        response = update_user_auth(self, user, test_user1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauth_update_user(self):
        unauth_user_setup(self)
        payload = json.dumps(test_user1)
        response = self.client.put(
            reverse('user_info'),
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
        for arg in ('id', 'first_name', 'last_name', 'username', 'account_created', 'account_updated'):
            self.assertTrue(arg in resp_payload)
        # self.assertFalse('password' in resp_payload)

    def test_get_user(self):
        auth_user_setup(self)
        response = self.client.get(reverse('user_info'))
        resp_payload = response.json()
        self.assertEqual(len(resp_payload), 6)
        for arg in ('id', 'first_name', 'last_name', 'username', 'account_created', 'account_updated'):
            self.assertTrue(arg in resp_payload)


# Bad requests handing testing
class BadReqHandingTestCase(APITestCase):
    def test_create_user(self):

        # User with that email already exists
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

        test_user1_cp['username'] = 'This_is_not_a_email'
        self.assertEqual(create_user_unauth(self, test_user1_cp).status_code, status.HTTP_400_BAD_REQUEST)
        test_user1_cp['username'] = test_user1['username']

        # Request paramenters overload
        test_user1_cp['dummy_arg'] = 'some_dummy_value'
        self.assertEqual(create_user_unauth(self, test_user1_cp).status_code, status.HTTP_201_CREATED)

    def test_update_user(self):
        User.objects.create(**test_user2)
        user = auth_user_setup(self)

        # Request paramenters miss
        test_user1_cp = dict(test_user1)
        for k in test_user1:
            del test_user1_cp[k]
            response = update_user_auth(self, user, test_user1_cp)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            test_user1_cp[k] = test_user1[k]
        self.assertEqual(update_user_auth(self, user, None).status_code, status.HTTP_400_BAD_REQUEST)

        # Current authenticated user tries to update other's account
        self.assertEqual(update_user_auth(self, user, test_user2).status_code, status.HTTP_400_BAD_REQUEST)

        # Request paramenters are unknown
        test_user1_cp['dummy_arg'] = 'some_dummy_value'
        self.assertEqual(update_user_auth(self, user, test_user1_cp).status_code, status.HTTP_400_BAD_REQUEST)

        # # Email is already taken by other user
        # user2 = auth_user_setup(self, False)
        # self.assertEqual(update_user_auth(self, user, test_user2).status_code, status.HTTP_400_BAD_REQUEST)


class OtherTestCase(APITestCase):

    # Test if account_updated automatically updates when user update is successful
    def test_account_updated(self):
        user = auth_user_setup(self)
        old_acc_updated = user.account_updated
        update_user_auth(self, user, test_user1)
        self.assertGreater(User.objects.get(username=user.username).account_updated, old_acc_updated)

    # Test password complexity
    def test_pwd(self):
        user_cp = dict(test_user1)
        for pwd in ('short6', 'This_is_all_chars', '123456789'):
            user_cp['password'] = pwd
            self.assertEqual(create_user_unauth(self, user_cp).status_code, status.HTTP_400_BAD_REQUEST)
        user_cp['password'] = 'GoodPWD1!'
        self.assertEqual(create_user_unauth(self, user_cp).status_code, status.HTTP_201_CREATED)
