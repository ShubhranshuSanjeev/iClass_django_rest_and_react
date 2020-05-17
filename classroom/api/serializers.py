import uuid
# import os
from rest_framework import serializers
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib import auth

from classroom.models import (
  Classroom,
  ClassroomStudents,
  JoinRequests,
  Assignment,
  ReferenceMaterial,
  AssignmentSubmission
)
from accounts.api.serializers import UserSerializer

User = auth.get_user_model()

class ClassroomSerializer(serializers.ModelSerializer):
  teacher = serializers.SerializerMethodField()
  class Meta:
    model = Classroom
    fields = (
      'id', 'room_number',
      'course_name', 'joining_permission',
      'teacher',
    )

  def get_teacher(self, obj):
    teacher = obj.teacher_id 
    teacher = UserSerializer(teacher).data
    return teacher

  def validate(self, data):
    if not data.get('course_name'):
      raise serializers.ValidationError( _('Course name should be provided.'))
    return data

  def create(self, validated_data):
    room_number = validated_data.get('room_number')
    course_name = validated_data.get('course_name')
    joining_permission = validated_data.get('joining_permission')
    teacher_id = validated_data.get('user')

    classroom_id = uuid.uuid4()
    class_instance = Classroom(
      id=classroom_id,
      room_number=room_number,
      course_name=course_name,
      teacher_id=teacher_id,
      joining_permission=joining_permission
    )
    class_instance.save()
    return class_instance

  def update(self, instance, validated_data):
    instance.room_number = validated_data.get('room_number')
    instance.course_name = validated_data.get('course_name')
    instance.joining_permission = validated_data.get('joining_permission')
    instance.save()
    return instance

class JoinRequestSerializer(serializers.ModelSerializer):

  class Meta:
    model = JoinRequests
    fields = ('id', 'classroom_id', 'student_id')

  def validate_classroom_id(self, value):
    if not value:
      raise serializers.ValidationError(_('Please enter classroom id'))
    return value

  def create(self, validated_data):
    print("Yaha pe aagaye")
    instance = JoinRequests(
      classroom_id=validated_data.get('classroom_id'),
      student_id=validated_data.get('student_id')
    )
    instance.save()

    return instance

class ClassroomStudentsSerializer(serializers.ModelSerializer):
  student = serializers.SerializerMethodField()
  class Meta:
    model = ClassroomStudents
    fields = ('student', )
  
  def get_student(self, obj):
    student = UserSerializer(obj.student_id).data
    return student

class AssignmentSerializer(serializers.ModelSerializer):
  class Meta:
    model = Assignment
    fields = (
      'id',
      'description',
      'max_marks',
      'deadline',
      'file',
    )

  def create(self, validated_data):
    assignment = Assignment(
      classroom_id=validated_data.get('classroom_id'),
      description=validated_data.get('description'),
      file=validated_data.get('file'),
      max_marks=validated_data.get('max_marks'),
      deadline=validated_data.get('deadline'), 
      teacher=validated_data.get('teacher')
    )
    assignment.save()
    return assignment

  def update(self, instance, validated_data):
      instance.description = validated_data.get('description'),
      instance.file = validated_data.get('file'),
      instance.max_marks = validated_data.get('marks')
      instance.save()
      return instance

class ReferenceMaterialSerializer(serializers.ModelSerializer):
  class Meta:
    model = ReferenceMaterial
    fields = (
      'id',
      'description',
      'file',
    )

  def create(self, validated_data):
    instance = ReferenceMaterial(
      classroom_id=validated_data.get('classroom_id'),
      description=validated_data.get('description'),
      file=validated_data.get('file'),
      teacher_id=validated_data.get('teacher')
    )
    instance.save()
    return instance

  def update(self, instance, validated_data):
    instance.description = validated_data.get('description')
    instance.file = validated_data.get('file')
    instance.save()
    return instance
