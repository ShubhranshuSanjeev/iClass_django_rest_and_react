from django.urls import path, re_path
from .views import *

urlpatterns = [
    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/quizzes$', QuizListCreateAPIView.as_view()),
    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/quizzes/(?P<pk>[0-9]+)$', QuizUpdateRetriveAPIView.as_view()),
    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/quizzes/(?P<pk>[0-9]+)/permissions$', QuizStudentPermissionAPIView.as_view()),
]
