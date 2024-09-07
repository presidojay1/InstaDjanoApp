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
    permission_classes = [IsAuthenticated]
    @extend_schema(
        # parameters=[
        #     OpenApiParameter(name='user_id', description='ID of the User', required=True, type=int)
        # ],
        responses={200: None, 404: None, 500: None},
        description='Run Instagram bot task for a specific User'
    )
    def get(self, request, user_id):
        try:
            profile = get_object_or_404(Profile, user__id=user_id)
            accounts = InstagramAccount.objects.filter(profile=profile)
            
            if not accounts.exists():
                return Response({"error": "No Instagram accounts found for the given profile"}, status=status.HTTP_404_NOT_FOUND)
            
            for account in accounts:
                print(f"Running tasks for account: {account.username}")
                
                # Initialize the bot for each account
                bot = Bot(username=account.username, password=account.password, headless=True)
                print("Initialized bot")

                print("Trying to like stories")
                bot.like_stories()         
                print("liked stories")

                print("Trying to like posts from profile ......")
                bot.like_posts_from_profile()
                print("Liked posts from profile done")
                
            print(f"Completed tasks for all accounts of user: {user_id}")
            return Response({"message": "Tasks completed successfully for all Instagram accounts"}, status=status.HTTP_200_OK)
            
        except InstagramAccount.DoesNotExist:
            return Response({"error": "Instagram account not found for the given profile"}, status=status.HTTP_404_NOT_FOUND)
        
        except TimeoutException:
            return Response({"error": "Operation timed out"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InstagramBotTaskView1(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        # parameters=[
        #     OpenApiParameter(name='user_id', description='ID of the User', required=True, type=int)
        # ],
        responses={200: None, 404: None, 500: None},
        description='Run Instagram bot task based on the user’s subscription plan'
    )
    def get(self, request, user_id):
        try:
            # Fetch the profile using user_id
            profile = get_object_or_404(Profile, user__id=user_id)
            accounts = InstagramAccount.objects.filter(profile=profile)
            
            if not accounts.exists():
                return Response({"error": "No Instagram accounts found for the given profile"}, status=status.HTTP_404_NOT_FOUND)
            
            for account in accounts:
                print(f"Running tasks for account: {account.username}")
                
                # Initialize the bot for each account
                bot = Bot(username=account.username, password=account.password, headless=True)
                print("Initialized bot")
                
                # Perform actions based on the user's subscription plan
                self.perform_actions_based_on_plan(profile, bot)

            print(f"Completed tasks for all accounts of user: {user_id}")
            return Response({"message": "Tasks completed successfully for all Instagram accounts"}, status=status.HTTP_200_OK)
            

        except Profile.DoesNotExist:
            return Response({"error": "Profile not found for the given user ID"}, status=status.HTTP_404_NOT_FOUND)

        except InstagramAccount.DoesNotExist:
            return Response({"error": "Instagram accounts not found for the given profile"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def perform_actions_based_on_plan(self, profile, bot):
        """
        Perform Instagram bot actions based on the user's subscription plan.
        """
        plan = profile.subscription_plan

        if plan == 'basic':
            perform_basic_actions(bot)
        elif plan == 'medium':
            perform_medium_actions(bot)
        elif plan == 'premium':
            perform_premium_actions(bot)
        else:
            raise ValueError("Invalid subscription plan. Cannot perform actions.")
        

class InstagramBotTaskView2(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        parameters=[
            # OpenApiParameter(name='user_id', description='ID of the User', required=True, type=int),
            OpenApiParameter(name='task', description='Task to run based on subscription (basic, medium, premium)', required=True, type=str)
        ],
        responses={200: None, 404: None, 500: None},
        description='Run Instagram bot task for a specific user based on their subscription plan'
    )
    def get(self, request, user_id):
        try:
            # Fetch the profile using user_id
            task = request.query_params.get('task')
            valid_tasks = ['basic', 'medium', 'premium']
            if not task:
                return Response({"error": "Task parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            if task not in valid_tasks:
                return Response({"error": f"Invalid task specified. Choose from {', '.join(valid_tasks)}."}, status=status.HTTP_400_BAD_REQUEST)
            profile = get_object_or_404(Profile, user__id=user_id)
            accounts = InstagramAccount.objects.filter(profile=profile)
            
            if not accounts.exists():
                return Response({"error": "No Instagram accounts found for the given profile"}, status=status.HTTP_404_NOT_FOUND)
            
            for account in accounts:
                print(f"Running tasks for account: {account.username}")
                
                # Initialize the bot for each account
                bot = Bot(username=account.username, password=account.password, headless=True)
                print("Initialized bot")

                # Determine which actions to perform based on the task
                if task == 'basic':
                    perform_basic_actions(bot)
                elif task == 'medium':
                    perform_medium_actions(bot)
                elif task == 'premium':
                    perform_premium_actions(bot)
                else:
                    return Response({"error": "Invalid task specified. Choose from 'basic', 'medium', 'premium'."}, status=status.HTTP_400_BAD_REQUEST)
                
            print(f"Completed tasks for all accounts of user: {user_id}")
            return Response({"message": "Tasks completed successfully for all Instagram accounts"}, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({"error": "Profile not found for the given user ID"}, status=status.HTTP_404_NOT_FOUND)

        except InstagramAccount.DoesNotExist:
            return Response({"error": "Instagram account not found for the given profile"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Define the functions to perform actions based on the subscription plan

def perform_basic_actions(bot):
    bot.like_stories()
    # bot.like_posts_from_feed()

def perform_medium_actions(bot):
    perform_basic_actions(bot)
    # bot.follow_users_from_feed()
    bot.like_posts_from_profile()

def perform_premium_actions(bot):
    perform_medium_actions(bot)
    bot.send_direct_message("Hello! This is an automated message.", ["user1", "user2"])
    bot.comment_on_posts(["Nice post!", "Great content!"])
    bot.unfollow_users()
    bot.scrape_hashtags('#examplehashtag')

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