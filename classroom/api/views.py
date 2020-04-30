from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from accounts.models import User
from classroom.models import Classroom
from .permissions import IsTeacher
from .serializers import (
            CreateClassroomSerializer, 
            ClassroomSerializer, 
            ClassroomListSerializer,
            ClassroomRetriveSerializer
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
class ClassListAPIView(generics.ListAPIView):
    model = Classroom
    permissions = [permissions.IsAuthenticated]
    serializer_class = ClassroomListSerializer

    def get_queryset(self):
        if self.request.user.is_student:
            return self.request.user.student.attending_classes
        else:
            return self.request.user.teacher.taking_classes

'''
---------
'''
class ClassRetriveAPIView(generics.RetrieveAPIView):
    model = Classroom
    permissions = [permissions.IsAuthenticated, IsTeacher]
    serializer_class = ClassroomRetriveSerializer
    lookup_field = 'classroom_id'
    lookup_url_kwarg = 'pk'
    
    def get_queryset(self):
        return Classroom.objects.all()