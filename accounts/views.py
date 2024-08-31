from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, authenticate, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from .task import *
from django.core.mail import send_mail
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.db  import transaction
from rest_framework.exceptions import APIException
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_referred_users(request):
    user = request.user
    referrals = user.referrals.all()
    referrals_data = [
        {
            'email': referral.email, 
            'first_name': referral.first_name, 
            'last_name': referral.last_name
        } 
        for referral in referrals
    ]
    return Response(referrals_data)



class UserRegisteration(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def perform_create(self, serializer):
        referrer_id = self.request.query_params.get('ref')
        
        if referrer_id:
            serializer.validated_data['referred_by'] = referrer_id

        user = serializer.save()
        token = default_token_generator.make_token(user)
        # send_verification_email(user.email, token='ccfqeb-762f22538682d6dffd48bfb59e4e1354')
          
        try:
            send_verification_email(user.email, token)
        except Exception as e:
                # If an error occurs during email sending, rollback the transaction
            user.delete()
            message = "There was an error with sending the registration email. Please try registering again."
            raise APIException(detail=message, code=status.HTTP_400_BAD_REQUEST)
        
        if user.referred_by:
            pass  # Handle successful referral
        
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ref', 
                description='Referrer ID',
                required=False, 
                type=str
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    # def get_serializer(self):
    #     return self.serializer_class(data=self.request.data, context={'request': self.request})
    
    
    
            

class UserUpdateView(generics.UpdateAPIView):
    serializer_class = CustomUserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CurrentUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FullCustomUserSerializer

    def get(self, request):
        user = request.user  
        serializer = self.get_serializer(user) 
        return Response(serializer.data)



def verify_email(request, uid, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = CustomUser.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        return render(request, 'verify-success.html')
    else:
        return render(request, 'verify-fail.html')
    




class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                send_password_reset_email(user)
                return Response({"detail": "Password reset email sent."}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"detail": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     


class PasswordResetConfirmView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        
        try:
            custom_user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"message": "Invalid email and password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not custom_user.is_verified:
            return Response(
                {"message": "Account is not verified. Please verify your account to login."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response(
        {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "login successful",
            "email": user.email,
            "first_name": user.first_name,
            
        },
        status=status.HTTP_200_OK,
    )

        return Response(
            {"message": "Invalid email and password"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
        
        



class ChangePasswordView(GenericAPIView, UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer  # You need to define this serializer

    # def post(self, request, *args, **kwargs):
    #     return self.update(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data.get('old_password')
            new_password = serializer.validated_data.get('new_password')
            confirm_password = serializer.validated_data.get('confirm_password')

            # Ensure the old password is correct
            if not self.object.check_password(old_password):
                return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure new password and confirm password match
            if new_password != confirm_password:
                return Response({'error': 'New password and confirm password do not match.'}, status=status.HTTP_400_BAD_REQUEST)

            # Set the new password
            self.object.set_password(new_password)
            self.object.save()
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_referral_link(request):
    user = request.user
    referral_link = request.build_absolute_uri(reverse('register') + f'?ref={user.referrer_id}')
    return Response({'referral_link': referral_link})