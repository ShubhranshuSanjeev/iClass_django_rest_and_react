from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin

from accounts.models import User
from classroom.models import Classroom, JoinQueue
from .permissions import IsTeacher, IsStudent, DoesTeachClass
from .serializers import (
            CreateClassroomSerializer, 
            ClassroomSerializer, 
            ClassroomListSerializer,
            ClassroomRetriveSerializer,
            QueuedCoursesSerializer,
            QueuedStudentsSerializer,
        )

'''
ClassCreateAPIView takes POST request with Course Name and
Room Number values in the body. On successfull creation of new class 
it returns classroom id and success message.

This endpoint can only be accessed by a teacher(user having role set as teacher)
'''
class ClassCreateAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacher]
    serializer_class = CreateClassroomSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['user'] = User.objects.get(email = self.request.user)
        class_instance = serializer.create(serializer.validated_data)

        return Response({
            'message' : _('Classroom created'),
            'class': ClassroomSerializer(class_instance, context=self.get_serializer_context()).data,
        }, status=status.HTTP_201_CREATED)

'''
Returns a list of classes which the user is teaching
or attending as a student

Both students and teacher can use this endpoint
'''
class ClassListAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if self.request.user.is_teacher:
            class_list = ClassroomListSerializer(self.request.user.teacher.taking_classes.all(), many=True)
            return Response({
                'class_list': class_list.data
            }, status=status.HTTP_200_OK)
        
        class_list = ClassroomListSerializer(self.request.user.student.attending_classes.all(), many=True)
        queued_classes = QueuedCoursesSerializer(self.request.user.student.join_request_queued.all(), many=True)
        return Response({
            'class_list' : class_list.data,
            'queued_classes': queued_classes.data
        }, status=status.HTTP_200_OK) 


class ClassRetriveAPIView(generics.GenericAPIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        classroom = Classroom.objects.get(classroom_id = kwargs.get('pk'))
        pending_requests = classroom.awaiting_join_requests.all()
        data = {
                'classroom_id': classroom.classroom_id,
                'room_number': classroom.room_number,
                'course_name': classroom.course_name
            }

        classroom = ClassroomRetriveSerializer(data=data, context=self.get_serializer_context())
        classroom.is_valid(raise_exception=True)
        if request.user.is_teacher:
            pending_requests = QueuedStudentsSerializer(pending_requests, many=True)
            return Response({
                "class_details": classroom.data,
                "pending_requests": pending_requests.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "class_details": classroom.data,
        }, status=status.HTTP_200_OK)

         
class ClassJoinAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def post(self, request, *args, **kwargs):
        classroom = Classroom.objects.get(classroom_id = self.request.data.get('classroom_id'))

        if classroom.student_id.filter(user=self.request.user):
            return Response({
                'message':_('You are already enrolled in the course')
            }, status=status.HTTP_403_FORBIDDEN)

        if classroom.joining_permission:
            if self.request.user.student.join_request_queued.filter(classroom_id=classroom):
                return Response({
                    'message': _('Your previous request is already there in the waiting queue.\
                        Wait for the course admin to accept the request')
                })

            queue_request = JoinQueue(
                classroom_id = classroom, 
                student_id = request.user.student
            )
            queue_request.save()
            return Response({
                'message': _('Your join request has been queued. Wait till the course admin accepts the request.')
            })
        
        student = request.user.student
        classroom.student_id.add(student)
        classroom.save()

        return Response({
            'message': _('You have been successfully enrolled to the classroom.')
        })

## Accepting requests to join class view
class AcceptJoinRequestAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacher, DoesTeachClass]

    def get_object(self):
        return Classroom.objects.get(classroom_id = self.request.data.get('classroom_id'))

    def post(self, request, *args, **kwargs):
        classroom = self.get_object()
        student = User.objects.get(
                    username = 
                    self.request.data.get('student_username')
                ).student

        try:
            queued_request = JoinQueue.objects.get(
                                Q(classroom_id = classroom)&
                                Q(student_id = student) 
                            )
            classroom.student_id.add(student)
            queued_request.delete()
        except:
            return Response({
                'message' : _('No such request found.')
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'classroom_id': self.request.data.get('classroom_id'),
            'student': self.request.data.get('student_username'),
            'message': _('Request has been accepted.')
        }, status=status.HTTP_202_ACCEPTED)
                    
## Creating new assignments view
## Creating new notes view
## Assignmnet submission view