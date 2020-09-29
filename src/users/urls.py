from django.urls import path
from .views import UserList, UserDetail

urlpatterns = [
    path('', UserList.as_view(), name='user_create'),
    path('<email>/', UserDetail.as_view(), name='user_info'),
]