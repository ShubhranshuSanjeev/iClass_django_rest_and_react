from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from classroom.models import Classroom,Assignment,Note
from accounts.models import Teacher, Student, User
from accounts.api.serializers import UserSerializer

import uuid

class CreateClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model       = Classroom
        fields      = (
            'room_number', 'course_name',
        )
    
    def validate(self, data):
        if not data.get('course_name'):
            raise serializers.ValidationError(_('Course name should be provided.'))
        return data

    def create(self, data):
        room_number = data.get('room_number')
        course_name = data.get('course_name')

        classroom_id = uuid.uuid4()
        print(data.get('user'))
        teacher_id   = Teacher.objects.get(user = data.get('user'))
        class_instance = Classroom(
                            classroom_id=classroom_id,
                            room_number=room_number,
                            course_name=course_name,
                            teacher_id=teacher_id
                        )
        class_instance.save()
        return class_instance

class ClassroomListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = (
            'classroom_id',
            'course_name',
        )

''' This serializer is just for testing purpose '''
class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = (
            'classroom_id',
            'room_number',
            'course_name',
            'teacher_id',
        )

class ClassroomRetriveSerializer(serializers.ModelSerializer):
    teacher        = serializers.SerializerMethodField()
    students       = serializers.SerializerMethodField()
    class Meta:
        model = Classroom
        fields = (
            'classroom_id',
            'room_number',
            'course_name',

            'teacher',
            'students',
        )
    
    def get_teacher(self, obj):
        teacher = obj.teacher_id.user.get_full_name()
        return teacher
    def get_students(self, obj):
        qs = obj.student_id.all()
        students = []
        for student in qs:
            students.append(UserSerializer(student.user).data)
        return students