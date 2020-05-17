from django.utils.translation import gettext_lazy as _
from django.contrib import auth
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from knox.models import AuthToken

from .serializers import *

User = auth.get_user_model()


class RegistrationAPIView(generics.GenericAPIView):
    serializer_class = RegisterUserSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
        print(self.get_serializer_context())
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        }, status=status.HTTP_200_OK)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        }, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data
        }, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = request.user

        if not user.check_password(request.data.get('password')):
            return Response({
                'error': 'Password doesn\'t match. Provide correct password.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserUpdateSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.update(user, serializer.validated_data)

        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data
        }, status=status.HTTP_200_OK)
