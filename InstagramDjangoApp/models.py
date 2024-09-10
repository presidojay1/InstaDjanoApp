from django.db import models
from django.contrib.auth import get_user_model
import datetime
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
from instagrapi import Client

UserModel = get_user_model()



class ProfileManager(models.Manager):
    def valid_subscriptions(self):
        return self.filter(subscription_end_date__gte=timezone.now())
    


class Profile(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    has_confirmed_otp = models.BooleanField(default=False)
    number_of_ig_accounts = models.PositiveIntegerField(default=0)
    height = models.FloatField(null=True, blank=True) 
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_plan = models.CharField(max_length=50, choices=[('free_trial', 'Free Trial'), ('basic', 'Basic'), ('medium', 'Medium'), ('premium', 'Premium'), ('unsubscribed', 'Unsubscribed')], null=True, blank=True, default='unsubscribed')
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    trial_start_date = models.DateTimeField(null=True, blank=True)
    

    objects = ProfileManager()

    @property
    def username(self):
        return self.user.username

    @property
    def user_id(self):
        return self.user.id

    @property
    def subscription_is_valid(self):
        if self.subscription_end_date:
            return timezone.now() <= self.subscription_end_date
        return False
    

    @property
    def is_trial(self):
        return self.subscription_plan == 'free_trial'


    @property
    def trial_is_valid(self):
        if self.trial_start_date:
            return timezone.now() <= self.trial_start_date + timezone.timedelta(days=5)
        return False

    def start_free_trial(self):
        self.subscription_plan = 'free_trial'
        self.trial_start_date = timezone.now()
        self.subscription_end_date = self.trial_start_date + timezone.timedelta(days=5)
        self.save()


    def __str__(self):
        return f'{self.user.username} Profile'
    
class PaymentHistory(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='payment_history')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    def __str__(self):
        return f'Payment of {self.amount} by {self.profile.user.username}'
    

    
class InstagramAccount(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='instagram_accounts')
    username = models.CharField(max_length=255)
    encrypted_password = models.BinaryField()
    followers = models.JSONField(default=list)  # List of follower usernames
    total_followers = models.IntegerField(default=0)
    following = models.JSONField(default=list)  # List of following usernames
    total_following = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def password(self):
        f = Fernet(settings.ENCRYPTION_KEY)
        encrypted_password_bytes = bytes(self.encrypted_password)
        return f.decrypt(encrypted_password_bytes).decode()
        # return f.decrypt(self.encrypted_password).decode()

    @password.setter
    def password(self, raw_password):
        f = Fernet(settings.ENCRYPTION_KEY)
        self.encrypted_password = f.encrypt(raw_password.encode())

    def __str__(self):
        return f'{self.username} (Profile: {self.profile.user.username})'

    def update_account_data(self):
        bot = Client()
        bot.login(self.username, self.password)

        # Update followers
        followers = bot.user_followers(bot.user_id)
        self.followers = [user.username for user in followers.values()]
        self.total_followers = len(self.followers)

        # Update following
        following = bot.user_following(bot.user_id)
        self.following = [user.username for user in following.values()]
        self.total_following = len(self.following)

        self.last_updated = timezone.now()
        self.save()
    