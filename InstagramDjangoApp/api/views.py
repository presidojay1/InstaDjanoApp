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




paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)

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

    profile = user.profile

    plan_id = settings.PAYSTACK_PLAN_IDS[plan]
    response = create_paystack_subscription(user.email, plan_id)

    plan_details_response = get_plan_details(plan_id)
    plan_details = plan_details_response['data']
    try:
        amount = Decimal(plan_details['amount'])  # Convert to Decimal
    except (KeyError, InvalidOperation):
        return Response({'error': 'Invalid plan amount'}, status=400)

    # Convert amount to kobo if necessary (Paystack uses kobo)
    amount_in_kobo = int(amount * 100)

    if response['status']:  # Check if the transaction was initialized successfully
        # Update the user's subscription plan and end date
        profile.subscription_plan = plan
        profile.subscription_end_date = datetime.date.today() + datetime.timedelta(days=30)
        profile.save()

        PaymentHistory.objects.create(
            profile=profile,
            amount=amount,  # Convert amount back to naira
            description=f'{plan.capitalize()} Plan Subscription',
            reference=response['data']['reference'],  # Save the transaction reference
        )

        return Response({'status': 'Subscription successful', 'authorization_url': response['data']['authorization_url']}, status=201)
    else:
        return Response({'status': 'Subscription failed', 'message': response['message']}, status=400)


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
def paystack_webhook(request):
    event = json.loads(request.body.decode('utf-8'))
    
    if event['event'] == 'subscription.create':
        transaction = event['data']['transaction']
        email = transaction['customer']['email']
        profile = Profile.objects.get(user__email=email)
        
        # Update the user profile and payment history
        profile.subscription_plan = 'subscribed'
        profile.save()

        # Amount in kobo; convert to naira
        amount = transaction['amount'] / 100

        PaymentHistory.objects.create(
            profile=profile,
            amount=amount,  # Convert from kobo to naira
            description=f'{profile.subscription_plan.capitalize()} Plan Subscription',
            reference=transaction['reference']
        )

    return JsonResponse({'status': 'success'})


def create_paystack_subscription(email, plan_id):
    # Retrieve plan details from Paystack
    plan_details_response = get_plan_details(plan_id)
    if not plan_details_response['status']:
        raise Exception('Failed to retrieve plan details')
    
    plan_details = plan_details_response['data']
    try:
        amount = Decimal(plan_details['amount'])  # Convert to Decimal
    except (KeyError, InvalidOperation):
        return Response({'error': 'Invalid plan amount'}, status=400)

    # Convert amount to kobo if necessary (Paystack uses kobo)
    amount_in_kobo = int(amount * 100)

    response = paystack.transaction.initialize(
        reference=str(uuid.uuid4()),  # Unique transaction reference
        amount=amount_in_kobo,  # Amount in kobo
        email=email,
        plan=plan_id
    )
    return response