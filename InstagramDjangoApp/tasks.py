from celery import shared_task
from django.utils import timezone
from .models import Profile, InstagramAccount
from InstagramDjangoApp.bot import Bot
import datetime
from datetime import timedelta


@shared_task
def perform_instagram_tasks():
    current_time = timezone.now()
    eta_time = current_time + datetime.timedelta(minutes=30)
    perform_instagram_tasks.apply_async(eta=eta_time)

    one_month_from_now = timezone.now() + timedelta(days=30)

    # Filter profiles with a subscription end date less than a month from now
    profiles = Profile.objects.filter(subscription_end_date__lt=one_month_from_now)

    # Check if any profiles were retrieved
    if profiles.exists():
        print(f"Found {profiles.count()} profiles with active subscriptions.")
    else:
        print("No profiles with active subscriptions found.")

    for profile in profiles:
        # Get Instagram accounts associated with the profile
        accounts = InstagramAccount.objects.filter(profile=profile)

        # Check if any Instagram accounts were retrieved
        if accounts.exists():
            print(f"Found {accounts.count()} Instagram accounts for profile {profile.username}.")
        else:
            print(f"No Instagram accounts found for profile {profile.username}.")

        for account in accounts:
            bot = Bot(username=account.username, password=account.password)
            try:
                bot.like_stories()
                bot.like_posts_from_feed()
            except Exception as e:
                print(f"An error occurred while performing actions for account {account.username}: {e}")
            finally:
                bot.browser.quit()
