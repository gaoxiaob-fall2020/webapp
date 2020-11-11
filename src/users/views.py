import logging

from django.contrib.auth import get_user_model
from django.http import Http404
from django_statsd.clients import statsd
# from django.shortcuts import render
from rest_framework import status
# from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer

User = get_user_model()

# logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(f'django.{__name__}')


class UserList(APIView):

    # Create a new user
    def post(self, request):
        statsd.incr('view_users_views_UserList_POST')
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # <created()> is being called
            logger.info(serializer.data.get('username') +
                        ' was successfully created.')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    # authentication_classes = [BasicAuthentication]
    permission_classes = (IsAuthenticated, )

    # Get user object with username as lookup
    def get_object(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404

    # Get user information
    def get(self, request):
        statsd.incr('view_users_views_UserDetail_GET')
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    # Update user information
    def put(self, request):
        statsd.incr('view_users_views_UserDetail_PUT')
        serializer = UserSerializer(request.user, data=request.data)
        if request.data:
            errs = {}
            if request.data.get('username') != request.user.username:
                errs['username'] = 'Incorrect username.'
            for k in request.data:
                if k in ('id', 'account_created', 'account_updated'):
                    errs[k] = 'Unchangeable field.'
                elif k not in ('first_name', 'last_name', 'username', 'password'):
                    errs[k] = 'Unknown field.'
            if errs:
                return Response(errs, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()  # <update()> is being called
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
