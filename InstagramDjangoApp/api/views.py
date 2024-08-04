from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegisterSerializer
from .validations import custom_validation
from django.contrib.auth import get_user_model
from django.contrib.auth import logout

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models import Profile
from .serializers import ProfileSerializer

UserModel = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.username
        # ...

        return token
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer






@api_view(['POST'])
def create_profile(request):
    user = request.user
    profile_data = request.data
    profile_data['user'] = user.id  # Link the profile to the user
    profile_serializer = ProfileSerializer(data=profile_data)
    if profile_serializer.is_valid():
        profile_serializer.save()
        return Response(profile_serializer.data, status=status.HTTP_201_CREATED)
    return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_profile(request, identifier=None):
    if identifier:
        if identifier.isdigit():
            try:
                user = UserModel.objects.get(id=int(identifier))
            except UserModel.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                user = UserModel.objects.get(username=identifier)
            except UserModel.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        profile = user.profile
    else:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return Response({'error': 'Profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    profile_serializer = ProfileSerializer(profile, data=request.data, partial=True)
    if profile_serializer.is_valid():
        profile_serializer.save()
        return Response(profile_serializer.data)
    return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_profile(request, identifier=None):
    if identifier:
        # Check if identifier is an integer (user ID) or a string (username)
        if identifier.isdigit():
            try:
                user = UserModel.objects.get(id=int(identifier))
            except UserModel.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                user = UserModel.objects.get(username=identifier)
            except UserModel.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        profile = user.profile
    else:
        # Fetch the profile for the currently authenticated user
        profile = request.user.profile

    profile_serializer = ProfileSerializer(profile)
    return Response(profile_serializer.data)

@api_view(['DELETE'])
def delete_profile(request, identifier=None):
    if identifier:
        if identifier.isdigit():
            try:
                user = UserModel.objects.get(id=int(identifier))
            except UserModel.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                user = UserModel.objects.get(username=identifier)
            except UserModel.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        profile = user.profile
    else:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return Response({'error': 'Profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    profile.delete()
    user.delete()  # This will delete the associated user
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_register(request):
    clean_data = custom_validation(request.data)
    serializer = UserRegisterSerializer(data=clean_data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.create(clean_data)
        # Create a profile for the newly registered user
        Profile.objects.create(user=user)
        response_data = {
            'user_id': user.id,
            'email': user.email,
            'username': user.username
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_logout(request):
    logout(request)
    return Response(status=status.HTTP_200_OK)
    
@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token',
        './api/token/refresh'
    ]
    return Response(routes)