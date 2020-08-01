from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.http import HttpResponse, Http404

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from quiz.models import (
    Quiz,
    Question,
    Answer,
    Sitting,
    StudentAnswer
)

from .serializers import (
    QuizSerializer,
    QuizListSerializer
)

from accounts.models import User
from classroom.models import Classroom

def hasClassroomPermission(user, classroom):
    if user.is_student:
        return classroom.students.filter(student_id=user).exists()
    return classroom.teacher_id.id == user.id

def ownsQuiz(user, quiz):
    return user.id == quiz.owner.id

def unauthorizedRequest():
    return Response({
        'message': _('You are not authorized to perform this action')
    }, status=status.HTTP_401_UNAUTHORIZED)


class QuizListCreateAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        classroom = Classroom.objects.get(id__exact=self.kwargs.get('pk'))

        if not hasClassroomPermission(user, classroom):
            return unauthorizedRequest()

        quizzes = classroom.quizzes.all()
        return Response({
            'message': _('List of Quizzes.'),
            'quizzes': QuizListSerializer(quizzes, many=True).data
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        classroom = Classroom.objects.get(id__exact=self.kwargs.get('pk'))

        if not hasClassroomPermission(user, classroom) or user.is_student:
            return unauthorizedRequest()

        serializer = QuizSerializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        serializer.validated_data['owner'] = user
        serializer.validated_data['classroom'] = classroom
        quiz_instance = serializer.create(serializer.validated_data)

        return Response({
            'message' : _('Quiz successfully created'),
            'quiz': QuizSerializer(quiz_instance, context=self.get_serializer_context()).data
        }, status=status.HTTP_201_CREATED)


class QuizUpdateRetriveAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        user = request.user
        classroom = Classroom.objects.get(id__exact = kwargs.get('classroom_id'))
        quiz = Quiz.objects.get(id__exact = kwargs.get('pk'))

        if not hasClassroomPermission(user, classroom):
            return unauthorizedRequest()

        data = {
            'classroom': quiz.get('classroom'),
            'name': quiz.get('name'),
            'duration': quiz.get('duration'),
            'start_time': quiz.get('start_time'),
            'max_attempts': quiz.get('max_attempts')
        }

        if user.is_teacher:
            data['publish_results'] = quiz.get('publish_results')
            data['enable_quiz_for_all'] = quiz.get('enable_quiz_for_all')

        serialized_data = QuizSerializer(data)

        return Response({
            'quiz': serialized_data.data,
        }, status = status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = request.user
        classroom = Classroom.objects.get(id_exact=kwargs.get('classroom_id'))
        quiz = Quiz.objects.get(id_exact=kwargs.get('pk'))

        if not hasClassroomPermission(user, classroom) or not ownsQuiz(user, quiz):
            return unauthorizedRequest()

        serializer = QuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.update(serializer.validated_data)

        return Response({
            'message' : _('Quiz deatils have been successfully updated.'),
            'quiz': QuizSerializer(instance).data
        }, status=status.HTTP_200_OK)




