from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .serializers import *

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from selenium.common.exceptions import TimeoutException
from InstagramDjangoApp.models import Profile, InstagramAccount
from .bot import Bot 

class InstagramBotTaskView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name='profile_id', description='ID of the Profile', required=True, type=int)
        ],
        responses={200: None, 404: None, 500: None},
        description='Run Instagram bot task for a specific profile'
    )
    def get(self, request, profile_id):
        try:
            profile = get_object_or_404(Profile, id=profile_id)
            account = InstagramAccount.objects.get(profile=profile)
            
            print(f"{account.username}  {account.password}")
            bot = Bot(username=account.username, password=account.password, headless=False)
            print("Initialized bot")

            print("Trying to like stories")
            bot.like_stories()         
            print("liked stories")

            print("Trying to like posts from profile ......")
            bot.like_posts_from_profile()
            print("Liked posts from profile done")
            
            return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)
        
        except InstagramAccount.DoesNotExist:
            return Response({"error": "Instagram account not found for the given profile"}, status=status.HTTP_404_NOT_FOUND)
        
        except TimeoutException:
            return Response({"error": "Operation timed out"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([AllowAny])
def list_referred_users(request):
    user = request.user
    referrals = user.referrals.all()
    total_referrals = referrals.count()
    referrals_data = [
        {
            'email': referral.email, 
            'first_name': referral.first_name, 
            'last_name': referral.last_name,
            'referral_link': referral.referral_link
        } 
        for referral in referrals
    ]
    response_data = {
        'total_referrals': total_referrals,
        'referrals': referrals_data
    }
    
    return Response(response_data)


class ProfileCreateAPIView(generics.CreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProfileListAPIView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Profile.objects.all()


class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
    


class AdminProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Profile.objects.all()
    lookup_field = 'user__id'

    @action(detail=True, methods=['post'])
    def update_subscription(self, request, user__id=None):
        profile = self.get_object()
        plan = request.data.get('subscription_plan')
        end_date = request.data.get('subscription_end_date')

        if plan:
            profile.subscription_plan = plan
        if end_date:
            profile.subscription_end_date = end_date

        profile.save()
        return Response(self.get_serializer(profile).data)