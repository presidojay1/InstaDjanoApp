from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate 
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from InstagramDjangoApp.models import Profile


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    referred_by = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'username', 'last_name', 'email', 'password', 'phone_no', 'referred_by']
        read_only_fields = ['id'] 

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        referred_by_username = validated_data.pop('referred_by', None)
        user = CustomUser.objects.create_user(**validated_data)
        if referred_by_username:
            try:
                referrer = CustomUser.objects.get(username=referred_by_username)
                user.referred_by = referrer
                user.save()
            except CustomUser.DoesNotExist:
                pass  # If the referrer doesn't exist, we just ignore it
        
        # Create user profile
        Profile.objects.create(user=user)
        
        return user



class CustomUserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        exclude = [
            'email', 'password', 'is_staff', 'is_superuser', 'groups', 'user_permissions',
            'is_verified', 'is_active', 'last_login'
        ]
    
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New password and confirm password do not match.")
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Password fields didn't match."})
        return data

    def save(self):
        uid = self.validated_data['uid']
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']
        
        try:
            uid = urlsafe_base64_decode(uid).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise serializers.ValidationError({"uid": "Invalid value"})
        
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Invalid value"})

        user.set_password(new_password)
        user.save()
        return user


class FullCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
