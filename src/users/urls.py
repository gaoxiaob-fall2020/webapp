from django.urls import path
from .views import UserList, UserDetail

urlpatterns = [
    path('', UserList.as_view()),
    path('<email>/', UserDetail.as_view()),
]