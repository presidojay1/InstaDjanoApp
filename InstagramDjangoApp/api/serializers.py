from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from ..models import *
UserModel = get_user_model()

# class UserRegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserModel
#         fields = '__all__'

#     def create(self, validated_data):
#         user_obj = UserModel.objects.create_user(
#             email=validated_data['email'],
#             username=validated_data['username'],
#             password=validated_data['password']
#         )
#         return user_obj

# class UserLoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField()

#     def check_user(self, clean_data):
#         user = authenticate(username=clean_data['email'], password=clean_data['password'])
#         if not user:
#             raise ValidationError('User not found')
#         return user

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserModel
#         fields = ('email', 'username')

class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = '__all__'

class InstagramAccountListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramAccount
        fields = '__all__'


class InstagramAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    followers = serializers.ListField(read_only=True)
    total_followers = serializers.IntegerField(read_only=True)
    following = serializers.ListField(read_only=True)
    total_following = serializers.IntegerField(read_only=True)
    last_updated = serializers.DateTimeField(read_only=True)

    class Meta:
        model = InstagramAccount
        fields = ['id', 'username', 'password', 'followers', 'is_business_account', 'total_followers', 'following', 'total_following', 'last_updated', 'reach_count', 'impression_count', 'profile_views', 'website_clicks','media_reach_count', 'media_like_count', 'media_comment_count','media_save_count', 'media_share_count', 'media_impression_count']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['is_business_account','reach_count', 'impression_count', 'profile_views', 'website_clicks','media_reach_count', 'media_like_count', 'media_comment_count','media_save_count', 'media_share_count', 'media_impression_count']

    def create(self, validated_data):
        password = validated_data.pop('password')
        instagram_account = InstagramAccount.objects.create(**validated_data)
        instagram_account.password = password  # This will use the property setter to encrypt
        instagram_account.save()
        return instagram_account

    def update(self, instance, validated_data):
        for field in ['followers', 'total_followers', 'following', 'total_following', 'last_updated']:
            validated_data.pop(field, None)

        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.password = password  # This will use the property setter to encrypt
        return super().update(instance, validated_data)



class InstagramAccountListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramAccount
        fields = ['id', 'username'] 

# class InstagramAccountSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = InstagramAccount
#         fields = ['id', 'username']

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    payment_history = PaymentHistorySerializer(many=True, read_only=True)
    instagram_accounts = InstagramAccountSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            'username',
            'user_id',
            'age',
            'has_confirmed_otp',
            'number_of_ig_accounts',
            'height',
            'stripe_customer_id',
            'subscription_plan',
            'subscription_end_date',
            'subscription_is_valid',
            'payment_history', 'instagram_accounts'
        ]