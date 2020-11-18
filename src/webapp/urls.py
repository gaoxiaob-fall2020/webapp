from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', obtain_auth_token),
    path('v1/user/', include('users.urls')),
    path('v1/', include('question_n_answer.urls')),
    path('', HomeView.as_view())
]
