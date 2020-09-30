from django.shortcuts import render
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated

User = get_user_model()


class UserList(APIView):

    # Create a new user
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # <created()> is being called
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    permission_classes = (IsAuthenticated, )

    # Get user object with email address as lookup
    def get_object(self, email):
        try:
            return User.objects.get(email_address=email)
        except User.DoesNotExist:
            raise Http404

    # Get user information
    def get(self, request, email):
        user = self.get_object(email)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # Update user information
    def put(self, request, email):
        user = self.get_object(email)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()  # <update()> is being called
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# def test(request):
#     from django.http import HttpResponse
#     print(request.POST)
#     return HttpResponse('this is a test')
