import os

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.http import HttpResponse, Http404

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin
from rest_framework.parsers import FileUploadParser

from accounts.models import User
from classroom.models import (
  Classroom,
  ClassroomStudents,
  JoinRequests,
  Assignment,
  ReferenceMaterial,
  AssignmentSubmission
)
from .serializers import (
  ClassroomSerializer,
  JoinRequestSerializer,
  AssignmentSerializer,
  ReferenceMaterial
)

'''
ClassCreateAPIView takes POST request with Course Name and
Room Number values in the body. On successfull creation of new class 
it returns classroom id and success message.

This endpoint can only be accessed by a teacher(user having role set as teacher)
'''

def hasClassroomPermission(user, classroom):
  if user.is_student:
    return classroom.students.filter(student_id=user).exists()
  return classroom.teacher_id.id == user.id

def hasCreatedAssignment(user, assignment):
  return user.id == assignment.teacher_id.id

def hasSubmittedSolution(user, submission):
  return user.id == submission.student_id.id

def unauthorizedRequest():
  return Response({
    'message': _('You are not authorized to perform this action')
  }, status=status.HTTP_401_UNAUTHORIZED)

class ClassCreateListAPIView(generics.GenericAPIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request, *args, **kwargs):
    user = request.user
    data = user.get_classrooms()

    class_list = ClassroomSerializer(data, many=True)
    return Response({
      'classrooms': class_list.data
    }, status=status.HTTP_200_OK)

  def post(self, request, *args, **kwargs):
    user = request.user
    if user.is_student:
      return unauthorizedRequest()

    serializer = ClassroomSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.validated_data['user'] = User.objects.get(id=user.id)
    class_instance = serializer.create(serializer.validated_data)

    return Response({
      'message': _('Classroom created'),
      'class': ClassroomSerializer(class_instance, context=self.get_serializer_context()).data,
    }, status=status.HTTP_201_CREATED)

class JoinClassAPIView(generics.GenericAPIView):
  permission_classes = [permissions.IsAuthenticated]

  def get_object(self):
    return Classroom.objects.get(id__iexact=self.request.data.get('classroom_id'))

  def post(self, request, *args, **kwargs):
    classroom = self.get_object()
    user = request.user

    if user.is_teacher:
      return unauthorizedRequest()

    if classroom.students.filter(student_id=user).exists():
      return Response({
        'message': _('You are already enrolled in the course')
      }, status=status.HTTP_403_FORBIDDEN)

    if classroom.joining_permission:
      if user.join_requests.filter(classroom_id=classroom).exists():
        return Response({
          'message': _('Your previous request is already there in the waiting queue.\
            Wait for the course admin to accept the request')
        }, status=status.HTTP_403_FORBIDDEN)

        serializer = JoinRequestSerializer(data={
          'classroom_id': classroom,
          'student_id': user
        })
        serializer.is_valid(raise_exception=True)
        serializer.create(validated_data=serializer.validated_data)
        return Response({
            'message': _('Your join request has been queued. Wait till the course admin accepts the request.')
        }, status=status.HTTP_202_ACCEPTED)

    instance = ClassroomStudents( classroom_id = classroom, student_id = user )
    instance.save()

    return Response({
      'message': _('You have been successfully enrolled to the classroom.')
    }, status.HTTP_202_ACCEPTED)

class ClassRetriveUpdateAPIView(generics.GenericAPIView):
  permissions = [permissions.IsAuthenticated]

  def get_object(self):
    return Classroom.objects.get(id__iexact=self.kwargs.get('pk'))

  def get(self, request, *args, **kwargs):
    classroom = self.get_object()
    user = request.user

    if not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()

    return Response({
      'class_details': ClassroomSerializer(classroom).data
    }, status=status.HTTP_200_OK)

  def patch(self, request, *args, **kwargs):
    classroom = self.get_object()
    user = request.user

    if user.is_student or not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()

    serializer = ClassroomSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.update(classroom, serializer.validated_data)

    return Response({
      'class_details': ClassroomSerializer(instance).data
    }, status=status.HTTP_200_OK)

class JoinRequestsListAPIView(generics.GenericAPIView):
  permission_classes = [permissions.IsAuthenticated]

  def get_object(self):
    return Classroom.objects.get(id__iexact=self.kwargs.get('classroom'))

  def get(self, request, *args, **kwargs):
    classroom = self.get_object()
    user = request.user
    if user.is_student or not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()

    join_requests = classroom.pending_requests.all()
    serializer = JoinRequestSerializer(join_requests, many=True)
    return Response({
      'join_requests': serializer.data,
    }, status=status.HTTP_200_OK)


class AcceptJoinRequestAPIView(generics.GenericAPIView):
  permission_classes = [permissions.IsAuthenticated,]

  def get_object(self):
    return JoinRequests.objects.get(id = self.kwargs.get('pk'))

  def post(self, request, *args, **kwargs):
    join_request = self.get_object()
    classroom = join_request.classroom_id
    student = join_request.student_id
    user = request.user 

    if user.is_student or not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()

    instance = ClassroomStudents(classroom_id = classroom, student_id = student)
    instance.save()
    join_request.delete()

    return Response({}, status=status.HTTP_202_ACCEPTED)

class AssignmentCreateListAPIView(generics.GenericAPIView):
  permission_classes = (permissions.IsAuthenticated,)
  parser_class = (FileUploadParser,)

  def get_object(self):
    return Classroom.objects.get(id__iexact = self.kwargs.get('pk'))

  def get(self, request, *args, **kwargs):
    classroom = self.get_object()
    user = request.user
    if not hasClassroomPermission(user, classroom): 
      return unauthorizedRequest()
    queryset = classroom.assignments
    serializer = AssignmentSerializer(queryset, many=True)
    return Response({
      'assignments' : serializer.data
    }, status=status.HTTP_200_OK)

  def post(self, request, *args, **kwargs):
    classroom = self.get_object()
    user = request.user

    if user.is_student or not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()

    serializer = AssignmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.validated_data['classroom_id'] = classroom
    serializer.validated_data['teacher'] = user
    assignment = serializer.create(validated_data=serializer.validated_data)

    return Response({
      'message':_('Assignment has been successfully added.'),
      'assignment': AssignmentSerializer(assignment).data
    }, status=status.HTTP_201_CREATED)

class AssignmentRetriveUpdateAPIView(generics.GenericAPIView):
  permission_classes = [permissions.IsAuthenticated, ]

  def get_object(self):
    return Assignment.objects.get(id__iexact = self.kwargs.get('pk'))

  def get(self, request, *args, **kwargs):
    assignment = self.get_object()
    classroom = assignment.classroom_id
    user = request.user

    if not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()

    return Response({
      'assignment' : AssignmentSerializer(assignment).data
    }, status=status.HTTP_200_OK)

  def patch(self, request, *args, **kwargs):
    assignment = self.get_object()
    classroom = assignment.classroom_id
    user = request.user

    if user.is_student or not hasCreatedAssignment(user, assignment):
      return unauthorizedRequest()

    serializer = AssignmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.update(assignment_instance,serializer.validated_data)

    return Response({
      'assignment': AssignmentSerializer(instance).data
    },status=status.HTTP_200_OK)

class DownloadAssignmentFileView(APIView):
    permission_class = (permissions.IsAuthenticated, )

    def get(self, request, *args, **kwargs):
      path = Assignment.objects.get(id=kwargs['id'])
      file_path = os.path.join(settings.MEDIA_ROOT, path)
      if os.path.exists(file_path):
          with open(file_path, 'rb') as fh:
              response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
              response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
              return response
      return Response({
          'message': _('File not found')
      }, status=status.HTTP_404_NOT_FOUND)

class ReferenceMaterialCreateListAPIView(generics.GenericAPIView):
  permission_classes = (permissions.IsAuthenticated, )

  def get_object(self):
    return Classroom.objects.get(id__iexact=self.kwargs.get('classroom_id'))

  def get(self, request, *args, **kwargs):
    classroom = self.get_object()
    user = request.user

    if not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()

    queryset = classroom.reference_materials
    serializer = ReferenceMaterialSerializer(queryset, many=True)
    return Response({
      'reference_materials' : serializer.data
    }, status=status.HTTP_200_OK)
  
  def post(self, request, *args, **kwrags):
    classroom = self.get_object()
    user = request.user

    if user.is_student or not hasClassroomPermission(user, classroom):
      return unauthorizedRequest
    
    serializer = ReferenceMaterialSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.validated_data['classroom_id'] = classroom
    serializer.validated_data['teacher'] = user
    reference_material = serializer.create(validated_data=serializer.validated_data)

    return Response({
      'message':_('Reference Material has been successfully added.'),
      'assignment': ReferenceMaterialSerializer(reference_material).data
    }, status=status.HTTP_201_CREATED)

class ReferenceMaterialRetriveUpdateAPIView(generics.GenericAPIView):
  permission_classes = [permissions.IsAuthenticated, ]

  def get_object(self):
    return ReferenceMaterial.objects.get(id__iexact = self.kwargs.get('pk'))

  def get(self, request, *args, **kwargs):
    reference_material = self.get_object()
    classroom = reference_material.classroom_id
    user = request.user

    if user.is_student or not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()

    return Response({
      'reference_material' : ReferenceMaterialSerializer(reference_material).data
    }, status=status.HTTP_200_OK)

  def patch(self, request, *args, **kwargs):
    reference_material = self.get_object()
    classroom = reference_material.classroom_id
    user = request.user

    if user.is_student or not hasCreatedAssignment(user, assignment):
      return unauthorizedRequest()

    serializer = ReferenceMaterialSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.update(reference_material, serializer.validated_data)

    return Response({
      'assignment': ReferenceMaterialSerializer(instance).data
    },status=status.HTTP_200_OK)

class DownloadReferenceMaterialFileView(APIView):
  permission_class = (permissions.IsAuthenticated, )

  def get(self, request, *args, **kwargs):
    path = ReferenceMaterial.objects.get(id=kwargs['id'])
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
      with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response
    return Response({
        'message': _('File not found')
    }, status=status.HTTP_404_NOT_FOUND)


    



# ## Assignmnet submission view
