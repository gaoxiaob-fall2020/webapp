# from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.http import Http404
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Answer, Question
from .serializers import AnswerSerializer, QuestionSerializer


class QuestionList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Get all questions
    def get(self, request):
        if request.path_info == reverse('post_a_question'):
            raise Http404
        qs = Question.objects.all()
        serializer = QuestionSerializer(qs, many=True)
        return Response(serializer.data)

    # Post a new question
    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.user.pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_q(self, question_id):
        try:
            q = Question.objects.get(pk=question_id)
        except (Question.DoesNotExist, ValidationError):
            raise Http404
        return q

    # Get a question
    def get(self, request, question_id):
        q = self.get_q(question_id)
        serializer = QuestionSerializer(q)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Update a question
    def put(self, request, question_id):
        q = self.get_q(question_id)
        serializer = QuestionSerializer(q, data=request.data)
        if q.user_id != request.user.id:
            return Response(
                {
                    'Unauthorized': 'You are not allowed to update a question posted by others.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if not request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a question
    def delete(self, request, question_id):
        q = self.get_q(question_id)
        if q.user_id != request.user.id:
            return Response(
                {
                    'Unauthorized': 'You\'re not allowed to delete a question posted by others.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if q.answers.all():
            return Response(
                {
                    'Unsupported': 'You\'re not allowed to delete a question that has already been answered.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        q.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnswerList(APIView):
    permission_classes = [IsAuthenticated]

    # Answer a question
    def post(self, request, question_id):
        try:
            q = Question.objects.get(pk=question_id)
        except (Question.DoesNotExist, ValidationError):
            raise Http404

        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(question_id=q.pk, user_id=request.user.pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnswerDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_q_n_a(self, question_id, answer_id):
        try:
            q = Question.objects.get(pk=question_id)
            a = Answer.objects.get(pk=answer_id)
        except (Question.DoesNotExist, Answer.DoesNotExist, ValidationError):
            raise Http404
        return q, a

    # Get a question's answer
    def get(self, request, question_id, answer_id):
        _, a = self.get_q_n_a(question_id, answer_id)
        serializer = AnswerSerializer(a)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Update a question's answer
    def put(self, request, question_id, answer_id):
        _, a = self.get_q_n_a(question_id, answer_id)
        if a.user_id != request.user.id:
            return Response(
                {
                    'Unauthorized': 'You\'re not allowed to update an answer that was posted by others.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = AnswerSerializer(a, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a question's answer
    def delete(self, request, question_id, answer_id):
        _, a = self.get_q_n_a(question_id, answer_id)
        if a.user_id != request.user.id:
            return Response(
                {
                    'Unauthorized': 'You\'re not allowed to delete an answer that was posted by others.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        a.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
