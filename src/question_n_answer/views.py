# from django.shortcuts import render
import boto3
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import Http404, JsonResponse
from django.urls import reverse
from django_statsd.clients import statsd
from rest_framework import status
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Answer, File, Question
from .serializers import AnswerSerializer, FileSerializer, QuestionSerializer


def get_q(question_id):
    try:
        q = Question.objects.get(pk=question_id)
    except (Question.DoesNotExist, ValidationError):
        raise Http404
    return q


def get_a(answer_id):
    try:
        a = Answer.objects.get(pk=answer_id)
    except (Answer.DoesNotExist, ValidationError):
        raise Http404
    return a


def get_f(file_id):
    try:
        f = File.objects.get(pk=file_id)
    except (File.DoesNotExist, ValidationError):
        raise Http404
    return f


class QuestionList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Get all questions
    def get(self, request):
        statsd.incr('view_question_n_answer_views_QuestionList_GET')
        if request.path_info == reverse('post_a_question'):
            raise Http404
        qs = Question.objects.all()
        serializer = QuestionSerializer(qs, many=True)
        return Response(serializer.data)

    # Post a new question
    def post(self, request):
        statsd.incr('view_question_n_answer_views_QuestionList_POST')
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.user.pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # def get_q(self, question_id):
    #     try:
    #         q = Question.objects.get(pk=question_id)
    #     except (Question.DoesNotExist, ValidationError):
    #         raise Http404
    #     return q

    # Get a question
    def get(self, request, question_id):
        statsd.incr('view_question_n_answer_views_QuestionDetail_GET')
        q = get_q(question_id)
        serializer = QuestionSerializer(q)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Update a question
    def put(self, request, question_id):
        statsd.incr('view_question_n_answer_views_QuestionDetail_PUT')
        q = get_q(question_id)
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
        statsd.incr('view_question_n_answer_views_QuestionDetail_DELETE')
        q = get_q(question_id)
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
        statsd.incr('view_question_n_answer_views_AnswerList_POST')
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
        statsd.incr('view_question_n_answer_views_AnswerDetail_GET')
        _, a = self.get_q_n_a(question_id, answer_id)
        serializer = AnswerSerializer(a)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Update a question's answer
    def put(self, request, question_id, answer_id):
        statsd.incr('view_question_n_answer_views_AnswerDetail_PUT')
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
        statsd.incr('view_question_n_answer_views_AnswerDetail_DELETE')
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


class FileList(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id=None, answer_id=None):
        statsd.incr('view_question_n_answer_views_FileList_POST')
        if not request.data.get('file') or request.data.get('file').name.rsplit('.', 1)[-1] not in ('png', 'jpg', 'jpeg'):
            return Response(
                {'Detail': 'No image of .png, .jpg, or .jpeg found.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        q = get_q(question_id)
        a = get_a(answer_id) if answer_id else None
        f = request.data.get('file')
        s3 = boto3.resource('s3')

        if q.user.id != request.user.id:
            return Response(
                {'Detail': 'You\'re not the author of the question/answer.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not a:
            img = File(file_name=f.name, question=q)
            img.s3_object_name = f'{question_id}/{img.pk}/{f.name}'

            s3.Bucket(settings.AWS_S3_BUCKET).put_object(
                Key=img.s3_object_name, Body=f)
            img.save()
            return Response(FileSerializer(img).data, status=status.HTTP_201_CREATED)

        # Attach an image file to an answer
        if str(a.question.pk) != question_id:
            return Response(
                {'Detail': "The answer and the question don\'t match."},
                status=status.HTTP_400_BAD_REQUEST
            )
        img = File(file_name=f.name, question=q, answer=a)
        img.s3_object_name = f'{answer_id}/{img.pk}/{f.name}'
        s3.Bucket(settings.AWS_S3_BUCKET).put_object(
            Key=img.s3_object_name, Body=f)
        img.save()
        return Response(FileSerializer(img).data, status=status.HTTP_201_CREATED)

    def delete(self, request, file_id, question_id=None, answer_id=None):
        statsd.incr('view_question_n_answer_views_FileList_DELETE')
        q = get_q(question_id)
        a = get_a(answer_id) if answer_id else None
        f = get_f(file_id)
        s3 = boto3.resource('s3')

        if q.user.id != request.user.id:
            return Response(
                {'Detail': 'You\'re not the author of the question/answer.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete an image file from a question/an answer
        if a and (str(a.question.pk) != question_id or str(f.answer.pk) != answer_id):
            print(str(f.pk) != file_id)
            print(a.question.pk, f.pk, file_id)
            return Response(
                {'Detail': "The question, the answer, and the file don\'t match."},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj = s3.Object(settings.AWS_S3_BUCKET, f.s3_object_name)
        obj.delete()
        f.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
