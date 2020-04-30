from django.urls import path, include, re_path
from .views import ClassCreateAPIView, ClassListAPIView, ClassRetriveAPIView

urlpatterns = [
    re_path(r'^create/classroom/$', ClassCreateAPIView.as_view()),
    re_path(r'^classroom_list/', ClassListAPIView.as_view()),
    re_path(r'^classroom/(?P<pk>[0-9A-Za-z_\-]+)/$', ClassRetriveAPIView.as_view())
]