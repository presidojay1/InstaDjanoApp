from celery import shared_task
from django.utils import timezone
from .models import Profile, InstagramAccount
from .bot import Bot
import time
import random
from celery.exceptions import MaxRetriesExceededError
from django.core.exceptions import ObjectDoesNotExist



@shared_task
def schedule_instagram_tasks():
    profiles = Profile.objects.valid_subscriptions()
    for profile in profiles:
        perform_instagram_tasks_for_profile.delay(profile.id)



@shared_task(bind=True, max_retries=3, rate_limit='1/m')
def perform_instagram_tasks_for_profile(self, profile_id):
    try:
        profile = Profile.objects.get(id=profile_id)
    except ObjectDoesNotExist:
        print(f"Profile with id {profile_id} not found.")
        return

    if not profile.subscription_is_valid:
        print(f"Profile {profile.username} does not have a valid subscription.")
        return

    accounts = InstagramAccount.objects.filter(profile=profile)
    
    if not accounts.exists():
        print(f"No Instagram accounts found for profile {profile.username}.")
        return

    for account in accounts:
        perform_bot_actions_for_account.delay(account.id, profile.subscription_plan)



@shared_task(bind=True, max_retries=3, rate_limit='1/m')
def perform_bot_actions_for_account(self, account_id, subscription_plan):
    try:
        account = InstagramAccount.objects.get(id=account_id)
    except ObjectDoesNotExist:
        print(f"Instagram account with id {account_id} not found.")
        return

    bot = Bot(username=account.username, password=account.password)
    
    try:
        # bot.login()
        time.sleep(random.uniform(5, 15))  # Random delay

        # Perform actions based on subscription plan
        if subscription_plan == 'basic':
            perform_basic_actions(bot)
        elif subscription_plan == 'medium':
            perform_medium_actions(bot)
        elif subscription_plan == 'premium':
            perform_premium_actions(bot)
        
    except Exception as e:
        print(f"An error occurred while performing actions for account {account.username}: {e}")
        try:
            self.retry(countdown=60 * 5)  # Retry after 5 minutes
        except MaxRetriesExceededError:
            print(f"Max retries exceeded for account {account.username}")
    
    finally:
        bot.browser.quit()



def perform_basic_actions(bot):
    bot.like_stories()
    time.sleep(random.uniform(5, 15))
    bot.like_posts_from_feed(limit=10)

def perform_medium_actions(bot):
    perform_basic_actions(bot)
    time.sleep(random.uniform(5, 15))
    bot.follow_users_from_feed(limit=5)
    time.sleep(random.uniform(5, 15))
    bot.like_posts_from_profile(limit=15)

def perform_premium_actions(bot):
    perform_medium_actions(bot)
    time.sleep(random.uniform(5, 15))
    bot.send_direct_message("Hello! This is an automated message.", ["user1", "user2"])
    time.sleep(random.uniform(5, 15))
    bot.comment_on_posts(["Nice post!", "Great content!"], limit=5)
    time.sleep(random.uniform(5, 15))
    bot.unfollow_users(limit=3)
    time.sleep(random.uniform(5, 15))
    bot.scrape_hashtags('#examplehashtag', limit=20)