from celery import shared_task
from django.utils import timezone
from .models import Profile, InstagramAccount
from InstagramDjangoApp.bot import Bot
import datetime

@shared_task
def perform_instagram_tasks():
    # Get the current time
    current_time = timezone.now()

    # Delay execution by 30 minutes from the start time
    eta_time = current_time + datetime.timedelta(minutes=30)
    
    # Schedule the task to start 30 minutes later
    perform_instagram_tasks.apply_async(eta=eta_time)

    # Get all profiles with active subscriptions
    profiles = Profile.objects.filter(subscription_is_valid=True)
    
    for profile in profiles:
        # Check subscription plan and perform actions accordingly
        if profile.subscription_plan == 'basic':
            # Perform bot actions for basic plan
            perform_bot_actions_for_profile(profile)
        elif profile.subscription_plan in ['medium', 'premium']:
            # Perform bot actions for medium and premium plans (e.g., more frequent tasks)
            perform_bot_actions_for_profile(profile)
        else:
            # Handle other cases, if needed
            pass

def perform_bot_actions_for_profile(profile):
    # Ensure the profile has Instagram accounts
    accounts = InstagramAccount.objects.filter(profile=profile)
    if accounts.exists():
        for account in accounts:
            # Initialize the bot with account credentials
            print(username=account.username, password=account.password)
            bot = Bot(username=account.username, password=account.password)
            
            try:
                # Perform bot actions
                bot.like_stories()
                bot.like_posts_from_feed()
                bot.follow_users_from_feed()
                bot.send_direct_message("Hello! This is an automated message.", ["user1", "user2"])
                bot.comment_on_posts(["Nice post!", "Great content!"])
                
                # Add more actions as needed
                # e.g., bot.unfollow_users()
                # e.g., bot.scrape_hashtags('#examplehashtag')
                
            except Exception as e:
                print(f"An error occurred while performing actions for account {account.username}: {e}")
            
            finally:
                # Close browser after operations
                bot.browser.quit()
    else:
        print(f"No Instagram accounts found for profile {profile.username}.")
