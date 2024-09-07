from django.core.mail import send_mail
from .models import CustomUser
from InstagramDjango.settings import EMAIL_HOST_USER ,CLIENT_URL
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


def send_registration_email(email):
    subject = "Welcome to AstraLemon"
    message = "Thank you for registering on our website. We're glad to have you!"
    sender = EMAIL_HOST_USER
    recipients = [email]
    send_mail(subject=subject,message=message,from_email=sender,recipient_list=recipients,fail_silently=False)




def send_verification_email(email, token):
    try:
        user = CustomUser.objects.get(email=email)
        # print('got user')
    except CustomUser.DoesNotExist:
        user = None

    if user is not None:
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        verification_url = f"{CLIENT_URL}/accounts/verify/{uid}/{token}/"
        # print(verification_url)
        subject = "Welcome to AstraLemon"
        context = {
            'full_name' : user.first_name,
            'user_email': email,
            'verification_url': verification_url,
        }
        # print('before template')
        message = render_to_string('account-verify.html', context)
        html_message = render_to_string('account-verify.html',context)
        sender = EMAIL_HOST_USER 
        recipients = [email]
        # print(message)
        send_mail(subject=subject , message=message,from_email=sender,recipient_list=recipients,html_message=html_message)




def send_password_reset_email(email):

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        user = None

    if user is not None:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{CLIENT_URL}/reset-password?uid={uid}&token={token}"
        subject = 'Password Reset Request'
        context = {'reset_link': reset_link}
        message = render_to_string('password_reset_email.html', context)
        html_message = render_to_string('password_reset_email.html', context)
        send_mail(subject, message, EMAIL_HOST_USER, [user.email], html_message=html_message)