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
    is_business_account = models.BooleanField(default=False)
    followers = models.JSONField(default=list)  # List of follower usernames
    total_followers = models.IntegerField(default=0)
    following = models.JSONField(default=list)  # List of following usernames
    total_following = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    followers_1_day_ago = models.IntegerField(default=0)
    followers_2_days_ago = models.IntegerField(default=0)
    followers_3_days_ago = models.IntegerField(default=0)

    following_1_day_ago = models.IntegerField(default=0)
    following_2_days_ago = models.IntegerField(default=0)
    following_3_days_ago = models.IntegerField(default=0)

    # Account Insights
    reach_count = models.IntegerField(default=0)
    impression_count = models.IntegerField(default=0)
    profile_views = models.IntegerField(default=0)
    website_clicks = models.IntegerField(default=0)

    # Media Insights (aggregate data for the last week)
    media_reach_count = models.IntegerField(default=0)
    media_like_count = models.IntegerField(default=0)
    media_comment_count = models.IntegerField(default=0)
    media_save_count = models.IntegerField(default=0)
    media_share_count = models.IntegerField(default=0)
    media_impression_count = models.IntegerField(default=0)

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

        self.followers_3_days_ago = self.followers_2_days_ago
        self.followers_2_days_ago = self.followers_1_day_ago
        self.followers_1_day_ago = self.total_followers

        self.following_3_days_ago = self.following_2_days_ago
        self.following_2_days_ago = self.following_1_day_ago
        self.following_1_day_ago = self.total_following

        try:
            # Try to fetch business account insights
            account_insights = bot.insights_account()
            self.is_business_account = True

            metrics = account_insights.get('data', {}).get('user', {}).get('business_manager', {}).get('account_summary', {}).get('metric_graph', {}).get('nodes', [])
            
            for metric in metrics:
                metric_name = metric.get('metric')
                metric_value = metric.get('metric_value')
                
                if metric_name == 'reach':
                    self.reach_count = int(metric_value)
                elif metric_name == 'impressions':
                    self.impression_count = int(metric_value)
                elif metric_name == 'profile_views':
                    self.profile_views = int(metric_value)
                elif metric_name == 'website_clicks':
                    self.website_clicks = int(metric_value)

            # self.reach_count = account_insights.get('reach_count', 0)
            # self.impression_count = account_insights.get('impression_count', 0)
            # self.profile_views = account_insights.get('profile_view_count', 0)
            # self.website_clicks = account_insights.get('website_clicks', 0)

            # Update media insights (for the last week)
            media_insights = bot.insights_media_feed_all(
                post_type="ALL",
                time_frame="ONE_WEEK",
                data_ordering="REACH_COUNT"
            )

            self.media_reach_count = sum(media.get('reach_count', 0) for media in media_insights)
            self.media_like_count = sum(media.get('like_count', 0) for media in media_insights)
            self.media_comment_count = sum(media.get('comment_count', 0) for media in media_insights)
            self.media_save_count = sum(media.get('save_count', 0) for media in media_insights)
            self.media_share_count = sum(media.get('share_count', 0) for media in media_insights)
            self.media_impression_count = sum(media.get('impression_count', 0) for media in media_insights)

        except UserError as e:
            # If it's not a business account
            self.is_business_account = False
            self.reach_count = 0
            self.impression_count = 0
            self.profile_views = 0
            self.website_clicks = 0
            self.media_reach_count = 0
            self.media_like_count = 0
            self.media_comment_count = 0
            self.media_save_count = 0
            self.media_share_count = 0
            self.media_impression_count = 0


        self.last_updated = timezone.now()
        self.save()
    