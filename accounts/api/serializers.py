from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib import auth

from rest_framework import serializers

User = auth.get_user_model()


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email',
            'first_name', 'last_name',
            'is_student', 'is_teacher',
            'password'
        )

    def validate_username(self, value):
        """ Checking for pre-existing user with same username. """

        qs = User.objects.filter(username__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(_('User with this email already exists.'))
        return value

    def validate_email(self, value):
        """ Checking for pre-existing user with same email. """

        qs = User.objects.filter(email__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(_('User with this username already exists'))
        return value

    # def validate(self, data):
    #     pw = data.get('password', None)
    #     pw2 = data.get('password2', None)
    #     student = data.get('is_student', False)
    #     teacher = data.get('is_teacher', False)

    #     ''' Checking for equality of both the passwords. '''
    #     if pw != pw2:
    #         raise serializers.ValidationError(_('Both password and password should match'))

    #     ''' At least one of the two either student or teacher should be true. '''
    #     if not (student or teacher):
    #         raise serializers.ValidationError(_('Choose one of the roles'))
    #     if student and teacher:
    #         raise serializers.ValidationError(_('You can choose only one of the roles.'))

    #     return data

    def create(self, validated_data):
        """ Creating and saving a new user instance. """
        user_instance = User(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            is_teacher=validated_data.get('is_teacher'),
            is_student=validated_data.get('is_student'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
        )
        user_instance.set_password(validated_data.get('password'))
        user_instance.save()

        return user_instance

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username',
            'email', 'first_name',
            'last_name', 'avatar',
            'is_student', 'is_teacher'
        )

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username',
            'email', 'first_name',
            'last_name', 'is_student',
            'is_teacher'
        )


class LoginUserSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            '''
            Checking whether the credentials provided are correct or not
            '''
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            '''
      If either of the fields(email, password) is missing,
      then raise a validation error 
      '''
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name',
            'email'
        )

    def validate(self, data):
        email = data.get('email')
        qs = User.objects.filter(email__iexact=email).exclude(username__iexact=self.instance.username)
        if qs.exists():
            raise serializers.ValidationError(_('This email address is already being used by another user.'))
        return data

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.email = validated_data.get('email')
        instance.save()
        return instance
