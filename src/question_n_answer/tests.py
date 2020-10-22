import base64

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Answer, Question

User = get_user_model()

test_user = {
    'first_name': 'Test',
    'last_name': 'One',
    'username': 'Test1@webapp.com',
    'password': 'P@ssword1!'
}

test_user2 = {
    'first_name': 'Test',
    'last_name': 'Two',
    'username': 'Test3@webapp.com',
    'password': 'P@ssword2+'
}

test_question = {
    'question_text': 'Do I look like a test question?',
    'categories': [
        {'category': 'cat1'},
        {'category': 'cat2'}
    ],
    'answers': [
        {'answer_text': 'ans1'},
        {'answer_text': 'ans2'}
    ]
}

test_question2 = {
    'question_text': 'Do I look like a test question2?',
    'categories': [
        {'category': 'cat21'},
        {'category': 'cat22'}
    ],
    'answers': [
        {'answer_text': 'ans21'},
        {'answer_text': 'ans22'}
    ]
}

test_answer = {
    'answer_text': 'I am the answer.'
}

test_answer2 = {
    'answer_text': 'I am some next answer.'
}


def auth_user_setup(self, user1=None):
    user = User.objects.create(
        **test_user) if not user1 else User.objects.create(**user1)
    # auth_token = Token.objects.create(user=user)
    # self.client.credentials(HTTP_AUTHORIZATION=f'Token {auth_token.key}')
    if not user1:
        auth_basic = f'{test_user["username"]}:{test_user["password"]}'
    else:
        auth_basic = f'{test_user2["username"]}:{test_user2["password"]}'
    self.client.credentials(HTTP_AUTHORIZATION=f'Basic {base64.b64encode(auth_basic.encode()).decode()}')
    return user


def unauth_user_setup(self):
    self.client.force_authenticate(user=None)
    return User.objects.create(**test_user)


def create_a_question(user_id=None):
    test_question_cp = dict(test_question)
    del test_question_cp['categories']
    del test_question_cp['answers']
    q = Question.objects.create(**test_question_cp, user_id=user_id)
    return q


class AuthenticationTestCase(APITestCase):
    def test_get_all_questions(self):
        unauth_user_setup(self)
        response = self.client.get(reverse('get_all_questions'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_a_question(self):
        user = unauth_user_setup(self)
        q = Question.objects.create(
            question_text=test_question['question_text'], user=user)
        response = self.client.get(
            reverse('get_put_del_a_question', kwargs={'question_id': q.question_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_an_answer(self):
        user = auth_user_setup(self, test_user2)
        q = create_a_question()
        a = Answer.objects.create(
            user_id=user.id, question_id=q.question_id, **test_answer)
        unauth_user_setup(self)
        response = self.client.get(reverse('get_put_del_an_answer', kwargs={
                                   'question_id': q.question_id, 'answer_id': a.answer_id}))
        # resp_payload = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_calls(self):
        user = unauth_user_setup(self)
        q = create_a_question()
        a = Answer.objects.create(
            user_id=user.id, question_id=q.question_id, **test_answer)
        response = self.client.post(
            reverse('post_a_question'), data=test_question)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(reverse('post_an_answer', kwargs={
                                    'question_id': q.question_id}), data=test_answer)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.put(reverse('get_put_del_an_answer', kwargs={
                                   'question_id': q.question_id, 'answer_id': a.answer_id}), data=test_answer2)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.delete(reverse('get_put_del_an_answer', kwargs={
                                      'question_id': q.question_id, 'answer_id': a.answer_id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.delete(
            reverse('get_put_del_a_question', kwargs={'question_id': q.question_id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.put(reverse('get_put_del_a_question', kwargs={
                                   'question_id': q.question_id}), data=test_question2)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ResponseContentTestCase(APITestCase):
    def test_post_a_question(self):
        auth_user_setup(self)
        test_question_cp = dict(test_question)
        del test_question_cp['answers']
        response = self.client.post(
            reverse('post_a_question'), data=test_question_cp)
        resp_payload = response.json()
        self.assertEqual(len(resp_payload), 8)
        for arg in (
            'question_id', 'created_timestamp', 'updated_timestamp', 'user_id', 'question_text', 'categories', 'answers'
        ):
            self.assertTrue(arg in resp_payload)

    def test_answer_a_question(self):
        auth_user_setup(self)
        q = create_a_question()
        response = self.client.post(reverse('post_an_answer', kwargs={
                                    'question_id': q.question_id}), data=test_answer)
        resp_payload = response.json()
        self.assertEqual(len(resp_payload), 7)
        for arg in (
            'answer_id', 'question_id', 'created_timestamp', 'updated_timestamp', 'user_id', 'answer_text'
        ):
            self.assertTrue(arg in resp_payload)

    def test_update_an_answer(self):
        user = auth_user_setup(self)
        q = create_a_question()
        a = Answer.objects.create(
            user_id=user.id, question_id=q.question_id, **test_answer)
        response = self.client.put(reverse('get_put_del_an_answer', kwargs={
                                   'question_id': q.question_id, 'answer_id': a.answer_id}), data=test_answer2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_an_answer(self):
        user = auth_user_setup(self)
        q = create_a_question()
        a = Answer.objects.create(
            user_id=user.id, question_id=q.question_id, **test_answer)
        response = self.client.delete(reverse('get_put_del_an_answer', kwargs={
                                      'question_id': q.question_id, 'answer_id': a.answer_id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_a_question(self):
        user = auth_user_setup(self)
        q = create_a_question(user.id)
        response = self.client.delete(
            reverse('get_put_del_a_question', kwargs={'question_id': q.question_id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_a_question(self):
        user = auth_user_setup(self)
        q = create_a_question(user.id)
        response = self.client.put(reverse('get_put_del_a_question', kwargs={
                                   'question_id': q.question_id}), data=test_question2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_an_answer(self):
        user = auth_user_setup(self)
        q = create_a_question()
        a = Answer.objects.create(
            user_id=user.id, question_id=q.question_id, **test_answer)
        response = self.client.get(reverse('get_put_del_an_answer', kwargs={
                                   'question_id': q.question_id, 'answer_id': a.answer_id}))
        resp_payload = response.json()
        self.assertEqual(len(resp_payload), 7)
        for arg in ('answer_id', 'question_id', 'created_timestamp', 'updated_timestamp', 'user_id', 'answer_text'):
            self.assertTrue(arg in resp_payload)

    def test_get_question(self):
        q = create_a_question()
        response = self.client.get(reverse('get_all_questions'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            reverse('get_put_del_a_question', kwargs={'question_id': q.question_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BadRequestHandlingTestCase(APITestCase):
    def test_update_and_delete_others_answer(self):
        other_user = auth_user_setup(self)
        q = create_a_question()
        a = Answer.objects.create(
            user_id=other_user.id, question_id=q.question_id, **test_answer)
        auth_user_setup(self, test_user2)
        response = self.client.put(reverse('get_put_del_an_answer', kwargs={
                                   'question_id': q.question_id, 'answer_id': a.answer_id}), data=test_answer2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.delete(reverse('get_put_del_an_answer', kwargs={
                                      'question_id': q.question_id, 'answer_id': a.answer_id}), data=test_answer2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_and_delete_others_question(self):
        other_user = auth_user_setup(self)
        q = create_a_question(other_user.id)
        auth_user_setup(self, test_user2)
        response = self.client.put(reverse('get_put_del_a_question', kwargs={
                                   'question_id': q.question_id}), data=test_question2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.delete(
            reverse('get_put_del_a_question', kwargs={'question_id': q.question_id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_a_question_with_ans(self):
        user = auth_user_setup(self)
        q = create_a_question()
        a = Answer.objects.create(
            user_id=user.id, question_id=q.question_id, **test_answer)
        q.answers.add(a)
        q.save()
        response = self.client.delete(
            reverse('get_put_del_a_question', kwargs={'question_id': q.question_id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
