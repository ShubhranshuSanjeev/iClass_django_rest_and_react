from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken

from .serializers import RegisterUserSerializer, LoginUserSerializer, UserSerializer
from accounts.models import User

'''
RegistrationAPIView takes POST request with fields mentioned
in RegisterUserSerializer in serializer.py file. On successfull
user creation it returns user details and auth tokens in response 
'''
class RegistrationAPIView(generics.GenericAPIView):
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
        
        '''
        Using Knox AuthTokens to generate authentication tokens
        and send back to the user.
        '''
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

'''
LoginAPIView allows POST request with email and 
password passed in the body. After successfull validation
an auth token is returned as a response along with user details(username, email)  
'''
class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

'''
UserRetriveAPIView takes POST requests with empty body
and return user details associated with the authorization tokens
only on successfull authentication 
'''
class UserRetriveAPIView(generics.RetrieveAPIView):
    permission_classes      = [ permissions.IsAuthenticated, ]
    serializer_class        = UserSerializer

    def get_object(self):
        return self.request.user