import datetime

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.http import HttpResponse, Http404

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from quiz.models import (
    Quiz,
    QuizStudentPermission,
    Question,
    Answer,
    Sitting,
    StudentAnswer
)

from .serializers import (
    QuizSerializer,
    QuizListSerializer,
    QuizStudentPermissionSerializer
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
        user = request.user
        classroom = Classroom.objects.get(id__exact=self.kwargs.get('classroom'))

        if not hasClassroomPermission(user, classroom):
            return unauthorizedRequest()

        quizzes = classroom.quizzes.all()

        return Response({
            'message': _('List of Quizzes.'),
            'quizzes': QuizSerializer(quizzes, many=True).data
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        classroom = Classroom.objects.get(id__exact=self.kwargs.get('classroom'))

        if not hasClassroomPermission(user, classroom) or user.is_student:
            return unauthorizedRequest()

        data = {
            'classroom': classroom.id,
            'name': request.data.get('name'),
            'max_attempts': request.data.get('max_attempts'),
        }

        duration = request.data.get('duration')
        [d, h, m, s] = [int(inp) for inp in duration.split()]
        duration = datetime.timedelta(days = d, hours=h, minutes=m, seconds=s)

        start_time = request.data.get('start_time')
        [d, m, y, h, mi] = [int(inp) for inp in start_time.split()]
        start_time = datetime.datetime(y, m, d, h, mi)

        end_time = request.data.get('end_time')
        [d, m , y, h, mi] = [int(inp) for inp in end_time.split()]
        end_time = datetime.datetime(y, m, d, h, mi)

        data['duration'] = duration
        data['start_time'] = start_time
        data['end_time'] = end_time

        serializer = QuizSerializer(data=data)
        serializer.is_valid(raise_exception = True)
        serializer.validated_data['owner'] = user
        quiz_instance = serializer.create(serializer.validated_data)

        classroom_students = classroom.students.all()
        for student in classroom_students:
            instance = QuizStudentPermission(
                quiz = quiz_instance,
                student_id = student.student_id.id
            )
            instance.save()

        return Response({
            'message' : _('Quiz successfully created'),
            'quiz': QuizSerializer(quiz_instance, context=self.get_serializer_context()).data
        }, status=status.HTTP_201_CREATED)

class QuizUpdateRetriveAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        user = request.user
        classroom = Classroom.objects.get(id__exact = kwargs.get('classroom'))
        quiz = Quiz.objects.get(id__exact = kwargs.get('pk'))
        print(quiz.classroom)
        if not hasClassroomPermission(user, classroom):
            return unauthorizedRequest()

        data = {
            'id' : quiz.id,
            'classroom': quiz.classroom,
            'name': quiz.name,
            'duration': quiz.duration,
            'start_time': quiz.start_time,
            'end_time': quiz.end_time,
            'max_attempts': quiz.max_attempts
        }

        if user.is_teacher:
            data['publish_results'] = quiz.publish_results
            data['enable_quiz_for_all'] = quiz.enable_quiz_for_all

        serialized_data = QuizSerializer(data)

        return Response({
            'quiz': serialized_data.data,
        }, status = status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = request.user
        classroom = Classroom.objects.get(id_exact=kwargs.get('classroom'))
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

class QuizStudentPermissionAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        user = request.user
        classroom = Classroom.objects.get(id__iexact=self.kwargs.get('classroom'))
        quiz = Quiz.objects.get(id__iexact=self.kwargs.get('pk'))

        if not hasClassroomPermission(user, classroom) and ownsQuiz(user, quiz):
            return unauthorizedRequest()

        data = quiz.permissions.all()
        serialized_data = QuizStudentPermissionSerializer(data, many=True)

        return Response({
            'message': _('List of Student Permissions'),
            'permissions': serialized_data.data
        }, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = request.user
        classroom = Classroom.objects.get(id__iexact=self.kwargs.get('classroom'))
        quiz = Quiz.objects.get(id__iexact=self.kwargs.get('pk'))

        if not hasClassroomPermission(user, classroom) and ownsQuiz(user, quiz):
            return unauthorizedRequest()

        for record in request.data:
            instance = QuizStudentPermission.objects.get(id__iexact=record.get('id'))
            if instance.allowed_to_attempt ^ (record.get('allowed_to_attempt') is 'True'):
                instance.allowed_to_attempt = not instance.allowed_to_attempt
                instance.save()

        return Response({
            'message': _('Updated Quiz Permissions'),
        }, status=status.HTTP_200_OK)