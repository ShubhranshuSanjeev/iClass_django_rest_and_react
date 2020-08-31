from rest_framework import serializers
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from quiz.models import (
    Quiz,
    QuizStudentPermission,
    Question,
    Answer,
    Sitting,
    StudentAnswer
)
from accounts.api.serializers import UserSerializer

from django.contrib import auth
User = auth.get_user_model()

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        exclude = ( 'owner', )

    def create(self, validated_data):
        name            = validated_data.get('name')
        duration        = validated_data.get('duration')
        start_time      = validated_data.get('start_time')
        end_time        = validated_data.get('end_time')
        max_attempts    = validated_data.get('max_attempts')
        classroom       = validated_data.get('classroom')
        owner           = validated_data.get('owner')

        instance = Quiz(
            classroom = classroom,
            owner = owner,
            name = name,
            duration = duration,
            start_time = start_time,
            end_time = end_time,
            max_attempts = max_attempts,
        )
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.name           = validated_data.get('name')
        instance.duration       = validated_data.get('duration')
        instance.start_time     = validated_data.get('startTime')
        instance.max_attempts   = validated_data.get('maxAttempts')

        instance.save()

        return instance

class QuizListSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    class Meta:
        model = Quiz
        fields = ('id', 'name', 'classroom', 'owner_name', )

    def get_owner_name(self, obj):
        return obj.owner.get_fullname()

class QuizStudentPermissionSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    class Meta:
        model = QuizStudentPermission
        fields = ('id', 'student', 'allowed_to_attempt')

    def get_student(self, obj):
        return obj.student.get_fullname()