from django.urls import path, include, re_path
from rest_framework.authtoken import views
from knox.views import LogoutView
from .views import *

urlpatterns = [
    re_path(r'^auth/register/$', RegistrationAPIView.as_view()),
    re_path(r"^auth/login/$", LoginAPIView.as_view()),
    re_path(r'^auth/logout/$', LogoutView.as_view()),
    re_path(r'^auth/user/$', UserRetrieveUpdateAPIView.as_view()),
    re_path(r'^auth/user/update/$', UserRetrieveUpdateAPIView.as_view()),
]
