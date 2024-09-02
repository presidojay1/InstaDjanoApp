from django.db import models
from django.contrib.auth import get_user_model
import datetime
from django.utils import timezone

UserModel = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    has_confirmed_otp = models.BooleanField(default=False)
    number_of_ig_accounts = models.PositiveIntegerField(default=0)
    height = models.FloatField(null=True, blank=True) 
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_plan = models.CharField(max_length=50, choices=[('basic', 'Basic'), ('medium', 'Medium'), ('premium', 'Premium'), ('unsubscribed', 'Unsubscribed')], null=True, blank=True, default='unsubscribed')
    subscription_end_date = models.DateField(null=True, blank=True)

    @property
    def username(self):
        return self.user.username

    @property
    def user_id(self):
        return self.user.id

    @property
    def subscription_is_valid(self):
        if self.subscription_end_date:
            return timezone.now().date() <= self.subscription_end_date
        return False

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
    

class Listing(models.Model):
    listings = models.JSONField(default=list)  # Stores the array of listings as JSON
    last_updated = models.DateTimeField(auto_now=True)  # Automatically updates the timestamp on save

    def save(self, *args, **kwargs):
        # Ensure that only one instance of Listing exists in the database
        if Listing.objects.exists() and not self.pk:
            # If there's already a Listing, delete it before saving the new one
            Listing.objects.all().delete()
        super(Listing, self).save(*args, **kwargs)

    def __str__(self):
        return f"Main Listing - Last Updated: {self.last_updated}"
    
class InstagramAccount(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='instagram_accounts')
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Ideally, this should be encrypted

    def __str__(self):
        return f'{self.username} (Profile: {self.profile.user.username})'
