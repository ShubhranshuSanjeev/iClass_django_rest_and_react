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
from .serializers import *

def hasClassroomPermission(user, classroom):
  if user.is_student:
    return classroom.students.filter(student_id=user).exists()
  return classroom.teacher_id.id == user.id

def hasCreatedAssignment(user, assignment):
  return user.id == assignment.teacher.id

def hasCreatedReferenceMaterial(user, reference_material):
  return user.id == reference_material.teacher_id.id

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
      'message': _('Classroom was successfully created'),
      'class': ClassroomSerializer(class_instance, context=self.get_serializer_context()).data,
    }, status=status.HTTP_201_CREATED)

class JoinClassAPIView(generics.GenericAPIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request, *args, **kwargs):
    try:
      classroom = Classroom.objects.get(id__iexact=self.request.data.get('classroom_id'))
    except:
      return Response({
        'message': _('Enter valid Clasroom Id')
      },status=status.HTTP_404_NOT_FOUND)

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

      instance = JoinRequests(classroom_id=classroom, student_id=user)
      instance.save()

      return Response({
          'message': _('Your join request has been queued. Wait till the course admin accepts the request.')
      }, status=status.HTTP_202_ACCEPTED)

    instance = ClassroomStudents( classroom_id = classroom, student_id = user )
    instance.save()
    return Response({
      'message': _('You have been successfully enrolled to the classroom.')
    }, status.HTTP_202_ACCEPTED)

class ClassRetriveUpdateDeleteAPIView(generics.GenericAPIView):
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
      'message': _('Classroom details successfully updated'),
      'class_details': ClassroomSerializer(instance).data
    }, status=status.HTTP_200_OK)

  def delete(self, request, *args, **kwargs):
    classroom = self.get_object()
    user = request.user
    if user.is_student or not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()
    classroom.delete()
    return Response({
      'message' : 'Classroom successfully deleted.',
    },status=status.HTTP_200_OK)

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


class JoinRequestAcceptRejectAPIView(generics.GenericAPIView):
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

  def delete(self, request, *args, **kwargs):
    join_request = self.get_object()
    classroom = join_request.classroom_id
    student = join_request.student_id
    user = request.user

    if user.is_student or not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()

    join_request.delete()

    return Response({}, status=status.HTTP_200_OK)

class ClassroomStudentsListAPIView(generics.GenericAPIView):
  permission_classes = (permissions.IsAuthenticated, )

  def get_object(self):
    return Classroom.objects.get(id__iexact=self.kwargs.get('classroom'))

  def get(self, request, *args, **kwargs):
    classroom = self.get_object()
    user = request.user

    if not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()

    queryset = classroom.students.all()
    students = ClassroomStudentsSerializer(queryset, many=True).data
    return Response({
      'students' : students
    }, status=status.HTTP_200_OK)

class ClassroomStudentsRemoveAPIView(generics.GenericAPIView):
  permission_classes = (permissions.IsAuthenticated, )

  def delete(self, request, *args, **kwargs):
    user = request.user
    classroom = Classroom.objects.get(id__iexact=kwargs.get('classroom'))
    if user.is_student or not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()

    instance = ClassroomStudents.objects.get(id__exact=kwargs.get('pk'))
    instance.delete()

    return Response({
      'message' : 'Student has been removed.'
    }, status=status.HTTP_200_OK)

class AssignmentCreateListAPIView(generics.GenericAPIView):
  permission_classes = (permissions.IsAuthenticated,)
  parser_class = (FileUploadParser,)

  def get_object(self):
    return Classroom.objects.get(id__iexact = self.kwargs.get('classroom'))

  def get(self, request, *args, **kwargs):
    classroom = self.get_object()
    user = request.user
    if not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()
    queryset = classroom.assignments
    serializer = AssignmentSerializer(queryset, many=True)
    print(serializer.data)
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

class AssignmentRetriveUpdateDeleteAPIView(generics.GenericAPIView):
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
    user = request.user

    if user.is_student or not hasCreatedAssignment(user, assignment):
      return unauthorizedRequest()

    data = {key:value for key,value in request.data.items()}
    data['publish_grades'] = True if data['publish_grades'] == 'true' else False
    data['file_updated'] = True if data['file_updated'] == 'true' else False
    data['max_marks'] = int(data['max_marks'])
    serializer = AssignmentUpdateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.update(assignment, serializer.validated_data)

    if data.get('file_updated'):
      file_serializer = AssignmentFileSerializer(data=data)
      file_serializer.is_valid(raise_exception=True)
      instance = file_serializer.update(instance, file_serializer.validated_data)

    return Response({
      'message': _('Assignment has been successfully updated.'),
      'assignment': AssignmentSerializer(instance).data
    },status=status.HTTP_200_OK)

  def delete(self, request, *args, **kwargs):
    assignment = self.get_object()
    user = request.user
    if user.is_student or not hasCreatedAssignment(user, assignment):
      return unauthorizedRequest()
    assignment.delete()
    return Response({
      'message' : _('Assignment successfully deleted'),
    }, status=status.HTTP_200_OK)

class ReferenceMaterialCreateListAPIView(generics.GenericAPIView):
  permission_classes = (permissions.IsAuthenticated, )

  def get_object(self):
    return Classroom.objects.get(id__iexact=self.kwargs.get('classroom'))

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
      'reference_material': ReferenceMaterialSerializer(reference_material).data
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

    if user.is_student or not hasCreatedReferenceMaterial(user, reference_material) or not hasClassroomPermission(user, classroom):
      return unauthorizedRequest()

    serializer = ReferenceMaterialSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.update(reference_material, serializer.validated_data)

    return Response({
      'assignment': ReferenceMaterialSerializer(instance).data
    },status=status.HTTP_200_OK)

class AssignmentSubmissionCreateListAPIView(generics.GenericAPIView):
  permission_classes = (permissions.IsAuthenticated, )

  def get(self, request, *args, **kwargs):
    user = request.user

    try:
      classroom  = Classroom.objects.get(id__exact=kwargs.get('classroom'))
      assignment = Assignment.objects.get(id__exact=kwargs.get('assignment'))
    except:
      return Response({
        'error' : _('No such assignment exists')
      }, status=status.HTTP_404_NOT_FOUND)

    if user.is_student or not hasClassroomPermission(user, classroom):
      return Response({
        'error': _('Not authorized to do this action')
      })

    queryset = assignment.assignment_submissions.all()
    print(queryset)
    serializer = AssignmentSubmissionDetailListSerializer(queryset, many=True)
    return Response({
      'submissions' : serializer.data
    })

  def post(self, request, *args, **kwargs):
    user = request.user
    try:
      classroom  = Classroom.objects.get(id__exact=kwargs.get('classroom'))
      assignment = Assignment.objects.get(id__exact=kwargs.get('assignment'))
    except:
      return Response({
        'error' : _('No such assignment exists')
      }, status=status.HTTP_404_NOT_FOUND)

    if user.is_teacher or not hasClassroomPermission(user, classroom):
      return Response({
        'error': _('Not authorized to do this action')
      })

    try:
      instance = AssignmentSubmission.objects.get(Q(student_id=user) & Q(assignment_id=assignment))
      serializer = AssignmentSubmissionStudentUpdateSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      instance = serializer.update(instance, serializer.validated_data)
    except:
      serializer = AssignmentSubmissionCreateSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      serializer.validated_data['student_id']=user
      serializer.validated_data['assignment_id']=assignment
      instance = serializer.create(serializer.validated_data)

    return Response({
      'message': 'Your file has been submitted'
    },status=status.HTTP_202_ACCEPTED)

class AssignmentSubmissionUpdateAPIView(generics.GenericAPIView):
  permission_classes = (permissions.IsAuthenticated, )

  def patch(self, request, *args, **kwargs):
    instance = AssignmentSubmission.objects.get(id__iexact=kwargs.get('pk'))
    serializer = AssignmentSubmissionTeacherUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.update(instance, serializer.validated_data)
    return Response({
      'message' : 'Marks updated successfully.',
      'submission' : AssignmentSubmissionDetailListSerializer(instance).data
    },status=status.HTTP_200_OK)