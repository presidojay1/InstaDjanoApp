from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .validations import custom_validation
from django.contrib.auth import get_user_model
from django.contrib.auth import logout

from .newbot import Bot
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models import Profile
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from paystackapi.transaction import Transaction
from paystackapi.paystack import Paystack
from django.conf import settings
import uuid
import json
import datetime
import requests
from decimal import Decimal, InvalidOperation


import stripe
from instagrapi import Client

import requests





stripe.api_key = settings.STRIPE_SECRET_KEY

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
@permission_classes([AllowAny])
def user_register(request):
    clean_data = custom_validation(request.data)
    serializer = UserRegisterSerializer(data=clean_data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.create(clean_data)
        # Create a profile with a default "unsubscribed" plan
        Profile.objects.create(user=user, subscription_plan="unsubscribed")
        response_data = {
            'user_id': user.id,
            'email': user.email,
            'username': user.username
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def create_profile(request):
    clean_data = custom_validation(request.data)
    serializer = UserRegisterSerializer(data=clean_data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.create(clean_data)
        # Create a profile with a default "unsubscribed" plan
        Profile.objects.create(user=user, subscription_plan="unsubscribed")
        response_data = {
            'user_id': user.id,
            'email': user.email,
            'username': user.username
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


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
def user_logout(request):
    logout(request)
    return Response(status=status.HTTP_200_OK)
    

def get_plan_details(plan_id):
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }
    response = requests.get(f'https://api.paystack.co/plan/{plan_id}', headers=headers)
    return response.json()


@api_view(['POST'])
def subscribe_to_plan(request):
    user = UserModel.objects.get(id=request.data.get('user_id'))
    plan = request.data.get('plan')
    payment_method_id = request.data.get('payment_method_id')
    profile = user.profile

    try:
        # Retrieve Stripe plan details
        stripe_plan = stripe.Plan.retrieve(settings.STRIPE_PLAN_IDS[plan])
        amount = Decimal(stripe_plan['amount']) / 100  # Convert from cents to dollars

        # Create a Stripe customer if not already created
        if not profile.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.username,
            )
            profile.stripe_customer_id = customer.id
            profile.save()
        else:
            customer = stripe.Customer.retrieve(profile.stripe_customer_id)

        # Use a test token to create a PaymentMethod
        # payment_method = stripe.PaymentMethod.create(
        #     type="card",
        #     card={
        #         "token": "tok_visa",  # Use a Stripe-provided test token for Visa
        #     },
        # )
        stripe.PaymentMethod.attach(payment_method_id, customer=customer.id)

        # Set the default payment method for the customer
        stripe.Customer.modify(
            customer.id,
            invoice_settings={
                'default_payment_method': payment_method_id,
            },
        )

        # Create a subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'plan': settings.STRIPE_PLAN_IDS[plan]}],
            default_payment_method=payment_method_id  # Set the test payment method as default
        )

        # Update the user's subscription plan and end date
        profile.subscription_plan = plan
        profile.subscription_end_date = datetime.date.today() + datetime.timedelta(days=30)
        profile.save()

        PaymentHistory.objects.create(
            profile=profile,
            amount=amount,
            description=f'{plan.capitalize()} Plan Subscription',
            reference=subscription['id'],  # Save the subscription ID as a reference
        )

        return Response({'status': 'Subscription successful', 'subscription_id': subscription['id']}, status=201)

    except stripe.error.StripeError as e:
        return Response({'status': 'Subscription failed', 'message': str(e)}, status=400)

@api_view(['POST'])
def add_instagram_account(request):
    user = UserModel.objects.get(id=request.data.get('user_id'))
    profile = user.profile
    if profile.subscription_plan == 'unsubscribed':
        return Response({'error': 'You must subscribe to a plan before adding Instagram accounts'}, status=status.HTTP_403_FORBIDDEN)

    # Plan restrictions for adding Instagram accounts
    if profile.subscription_plan == 'basic' and profile.instagram_accounts.count() >= 2:
        return Response({'error': 'Basic plan allows only 2 Instagram accounts'}, status=status.HTTP_403_FORBIDDEN)
    elif profile.subscription_plan == 'medium' and profile.instagram_accounts.count() >= 5:
        return Response({'error': 'Medium plan allows only 5 Instagram accounts'}, status=status.HTTP_403_FORBIDDEN)
    elif profile.subscription_plan == 'premium' and profile.instagram_accounts.count() >= 10:
        return Response({'error': 'Premium plan allows only 10 Instagram accounts'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    instagram_serializer = InstagramAccountSerializer(data=data)
    if instagram_serializer.is_valid():
        instagram_serializer.save(profile=profile)
        profile.number_of_ig_accounts += 1
        profile.save()
        return Response(instagram_serializer.data, status=status.HTTP_201_CREATED)
    return Response(instagram_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def payments_history(request, identifier=None):
    try:
        # Check if identifier is provided, if not, use the authenticated user
        if identifier:
            if identifier.isdigit():
                user = UserModel.objects.get(id=int(identifier))
            else:
                user = UserModel.objects.get(username=identifier)
        else:
            user = request.user

        profile = user.profile
        payments = profile.payment_history.all()
        serializer = PaymentHistorySerializer(payments, many=True)
        return Response(serializer.data)

    except UserModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def payment_history_by_reference(request,reference):
    user = UserModel.objects.get(id=request.data.get('user_id'))
    profile = user.profile
    try:
        payment = PaymentHistory.objects.get(reference=reference)
    except PaymentHistory.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PaymentHistorySerializer(payment)
    return Response(serializer.data)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        customer_id = invoice['customer']
        subscription_id = invoice['subscription']
        amount_paid = Decimal(invoice['amount_paid']) / 100  # Convert from cents to dollars

        profile = Profile.objects.get(stripe_customer_id=customer_id)

        # Update the user's profile
        profile.subscription_plan = 'subscribed'  # You might want to handle specific plan names
        profile.save()

        PaymentHistory.objects.create(
            profile=profile,
            amount=amount_paid,
            description=f'{profile.subscription_plan.capitalize()} Plan Subscription',
            reference=subscription_id,
        )

    return JsonResponse({'status': 'success'})


@api_view(['POST'])
def manage_instagram_accounts(request):
    user = UserModel.objects.get(id=request.data.get('user_id'))
    profile = user.profile
    instagram_accounts = InstagramAccount.objects.filter(profile=profile)
    
    response = {"success": [], "failed": []}

    for account in instagram_accounts:
        cl = Client()
        try:
            cl.login(account.username, account.password)
            
            # Get account info
            account_info = cl.account_info()
            bio = account_info.biography

            # Define the link to be added
            link_to_add = "http://127.0.0.1:8000/api/profile/1/"
            
            # Check if the bio contains a link
            if link_to_add in bio:
                # Remove the existing link
                new_bio = bio.replace(link_to_add, "")
                if cl.account_edit(biography=new_bio):
                    response["success"].append(f"{account.username} removed link from bio")
                else:
                    response["failed"].append(f"{account.username} could not remove link from bio")
            else:
                # Add the new link to the bio
                new_bio = f"{bio} {link_to_add}"
                if cl.account_edit(biography=new_bio):
                    response["success"].append(f"{account.username} added link to bio")
                else:
                    response["failed"].append(f"{account.username} could not add link to bio")
            
            cl.logout()
        except Exception as e:
            response["failed"].append(f"{account.username} failed with error: {str(e)}")
    
    return JsonResponse(response)


@api_view(['POST'])
def get_centrish_listings(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Initialize Bot with the provided credentials
        bot = Bot(username, password, headless=True)
        new_listings_data = bot.get_listings()  # This returns a list of dictionaries

        # Fetch the main listing or create it if it doesn't exist
        main_listing, created = Listing.objects.get_or_create(id=1)

        # Update the main listing with new data
        main_listing.listings = new_listings_data
        main_listing.save()

        return Response({
            "message": "Main Listing updated successfully",
            "listings": main_listing.listings
        })

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def get_main_listing(request):
    try:
        main_listing = Listing.objects.first()
        if not main_listing:
            return Response({"error": "No listings found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(main_listing.listings)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)