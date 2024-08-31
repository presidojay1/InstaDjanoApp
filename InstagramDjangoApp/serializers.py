# serializers.py
from rest_framework import serializers
from .models import Profile


# serializers.py

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    subscription_is_valid = serializers.BooleanField(read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user_id', 'username', 'email', 'age', 'has_confirmed_otp', 'number_of_ig_accounts', 
                  'height', 'subscription_plan', 'subscription_end_date', 'subscription_is_valid']
        read_only_fields = ['stripe_customer_id', 'subscription_plan']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data.pop('subscription_plan')
        # Check if profile already exists
        if hasattr(user, 'profile'):
            raise serializers.ValidationError("Profile already exists for this user.")
        return Profile.objects.create(user=user, subscription_plan="unsubscribed", **validated_data)

    def update(self, instance, validated_data):
        # Prevent updating subscription details directly
        validated_data.pop('subscription_plan', None)
        validated_data.pop('subscription_end_date', None)
        return super().update(instance, validated_data)