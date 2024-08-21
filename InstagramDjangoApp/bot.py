
# SELENIUM DEPENDENCIES
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import JavascriptException, NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# LOGGING, RANDOM & TIME
import logging
import random
import time

INSTAGRAM_LOGIN_URL = "https://www.instagram.com/"
INSTAGRAM_STORY_URL = "https://www.instagram.com/stories/"
SCROLL_PAUSE_TIME = 10 
HOURLY_STORY_LIKE =  100 # 30 stories per hour
HOURLY_POST_LIKE = 31
DAILY_POST_LIKE = 200
DAILY_STORY_LIKE = 1000
DAILY_FOLLOW = 150
DAILY_UNFOLLOW = 150
HOURLY_FOLLOW = 30
HOURLY_UNFOLLOW = 25
NUMBER_OF_PROFILES_TO_GET = 30
LIKE_POSTS_PER_ACCOUNT = 5



INSTAGRAM_LOGIN_URL = "https://www.instagram.com/"
LOGIN_BUTTON_XPATH = "//button[@type='submit']"
NOT_NOW_BUTTON_TEXT_LOGIN = "Not now"
NOT_NOW_BUTTON_TEXT_NOTIFICATION = "Not Now"
STORY_BUTTONS = '//button[contains(@aria-label, "Story by")]'
LIKE_BUTTON_1 = "//span//div[contains(@class, 'x1i10hfl') and contains(@class, 'x972fbf') and contains(@class, 'x16tdsg8') and contains(@class, 'x1hl2dhg') and contains(@class, 'x1a2a7pz') and @role='button']"
LIKE_BUTTON_2 = "//div/div/div[2]/div/div/div[1]/div[1]/section/div[1]/div/div/div[1]/div[2]/div[3]/div[1]/div[2]/span/div"
ROLE_BUTTON = "[role='button']"
STORY_BUTTON_NEXT = "//button[@aria-label='Next']"
VIEW_STORY_XPATH = "//div/div/div[2]/div/div/div[1]/div[1]/section/div[1]/div/div/div/div[2]/div/div[3]/div"
VIEW_STORY_AS_USER_BUTTON_XPATH = "//div[contains(@class, 'x1i10hfl') and @role='button' and text()='View story']"




class Bot:
    def __init__(self, username, password):
        # Saving user's username and password
        self.username = username
        self.password = password
        self.base_url = "https://www.instagram.com/"
        self.profile_links = None

        # Setting selenium browser instance
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--log-level=3')
        self.browser = webdriver.Chrome(options=chrome_options)
        
        self.login()

    def challenge(self):
        """
            Detect if the IG account has been rate limited.

            Usually, it redirects the account to the challenge URL.
        """
        # Detect challenge
        challenge = self.browser.execute_script("""return window.location.href.contains("/challenge/");""")

        # If it is a click button challenge
        if challenge:
            WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ROLE_BUTTON))
            ).click()
            # Wait time for DOM to reload or possible challenge
            time.sleep(4)

            # Detect if there is still a challenge
            challenge = self.browser.execute_script("""return window.location.href.contains("/challenge/");""")
            if challenge: return print(f"-> Automated behaviour has been detected by Instagram.\nLog into {self.username} and pass the challenge, then run the bot again.")

        if not challenge: print("-> No challenge detected")

    def login(self):
        # Log into an IG account
        self.browser.get(INSTAGRAM_LOGIN_URL)
        print("->oya print")
        # Finding and filling username and password fields
        self.browser.find_element(By.NAME, 'username').send_keys(self.username)
        self.browser.find_element(By.NAME, 'password').send_keys(self.password)

        # Click login button
        WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.XPATH, LOGIN_BUTTON_XPATH))).click()

        # Detect challenge
        self.challenge()

        # Click "Not Now" button on login
        try:
            not_now_button_login = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//div[text()='{NOT_NOW_BUTTON_TEXT_LOGIN}']"))
            )
            not_now_button_login.click()

        except Exception: print(f"[{self.username}][Login] -> Not Now not in DOM.")

        # Click "Not Now" button for notifications
        try:
            not_now_button_notification = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[text()='{NOT_NOW_BUTTON_TEXT_NOTIFICATION}']"))
            )
            not_now_button_notification.click()
        except Exception: print(f"[{self.username}][Notifications] -> Not Now not in DOM.")

    # Extract usernames of users who currently have a story up
    def __extract_usernames_from_story_list(self):
        usernames = []
        seen_story_elements = set()

        while len(usernames) < HOURLY_STORY_LIKE:
            new_story_buttons = self.browser.find_elements(By.XPATH, STORY_BUTTONS)
            for story_button in new_story_buttons:
                if story_button not in seen_story_elements:
                    seen_story_elements.add(story_button)
                    attempts = 0
                    while attempts < 3:  # Retry a few times
                        try:
                            username_div = story_button.find_element(By.XPATH, ".//div[contains(@class, 'x9f619') and contains(@class, 'x1lliihq')]")
                            username = username_div.text
                            usernames.append(username)
                            logging.info(f'Appended username "{username}"')
                            break
                        except NoSuchElementException: break

                        except StaleElementReferenceException:
                            # Increment the attempt counter and try again
                            attempts += 1
                            time.sleep(0.5)  # Wait a bit before retrying

                    if len(usernames) >= HOURLY_STORY_LIKE: break

            if len(usernames) < HOURLY_STORY_LIKE:
                try:
                    next_button = self.browser.find_element(By.XPATH, STORY_BUTTON_NEXT)
                    next_button.click()
                    time.sleep(SCROLL_PAUSE_TIME)  # Wait for the new stories to load

                except NoSuchElementException: break

        return usernames[1:HOURLY_STORY_LIKE]

    def like_stories(self):
        usernames = self.__extract_usernames_from_story_list()

        for user in usernames:
            story_url = f"{INSTAGRAM_STORY_URL}{user}"
            self.browser.get(story_url)
            time.sleep(2)

            view_story_button = self.browser.find_element(By.XPATH, VIEW_STORY_AS_USER_BUTTON_XPATH)

            try:
                view_story_button.click()
                print(f"[{self.username}] -> " + user + " has a story up.")
                time.sleep(4)

                try:
                    like_button = self.browser.find_element(By.XPATH, LIKE_BUTTON_1)
                   
                    # Click the like button using JavaScript
                    self.browser.execute_script("arguments[0].click();", like_button)
                    print(f"[{self.username}] -> Liked {user} story.")
                    time.sleep(3)

                except NoSuchElementException:
                    try:
                        like_button = self.browser.find_element(By.XPATH, LIKE_BUTTON_1)
                        like_button.click()
                        print("Liked the story successfully using the second path!")
                        time.sleep(2)

                    except NoSuchElementException: print("Like button not found.")

            except NoSuchElementException: print(f"[{self.username}] -> " + user + " has no story up.")

            except Exception as e: print("An unexpected error occurred:", str(e))

    # still under development
    def like_posts_from_feed(self):

        last_height = self.browser.execute_script("return document.body.scrollHeight")

        number_of_liked_posts = 0
        
        while number_of_liked_posts <= HOURLY_POST_LIKE:
            # Find all like buttons and click them using JavaScript
            like_buttons = self.browser.find_elements(By.XPATH, '//div[contains(@class, "x1i10hfl") and @role="button" and contains(@class, "x1y1aw1k") and contains(@class, "x1sxyh0") and contains(@class, "xwib8y2") and contains(@class, "xurb0ha") and contains(@class, "xcdnw81")]')

            print(f"Found {len(like_buttons)} like buttons")
            for button in like_buttons:
                try:
                    self.browser.execute_script("arguments[0].click();", button)
                    # Add a random delay between 1 and 3 seconds
                    time.sleep(random.uniform(1, 5))
                except Exception as e:
                    print(f"An error occurred when trying to like a post: {e}")

            # Scroll down to load more posts
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Wait for new posts to load, adjust as needed

            new_height = self.browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Break the loop if no new posts are loaded
            last_height = new_height

        print(f'Number of liked Posts: {number_of_liked_posts}')

    # private method to get followers of user
    def __get_user_followers(self, number_of_followers_to_get):

        # Go to profile page
        self.browser.get(f'{self.base_url}{self.username}')

        user_followers = WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.XPATH, f"//a[@href='/{self.username}/followers/']"))
        )
        user_followers.click()

        scroll_box = WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6')]"))
        )

        # Scroll the element
        last_ht, ht, number_of_scrolls = 0, 1, 0
        while last_ht != ht and number_of_scrolls <= 3:
            last_ht = ht
            time.sleep(2)
            # Scroll down and return the height of scroll (JS script)
            ht = self.browser.execute_script("""
                arguments[0].scrollTo(0, arguments[0].scrollHeight);
                return arguments[0].scrollHeight;
            """, scroll_box)

            number_of_scrolls += 1

        time.sleep(3)
        followers = self.browser.find_elements(By.XPATH, ".//a[contains(@href, '/') and contains(@class, 'notranslate _a6hd')]")

        number_of_requested_followers = followers[:number_of_followers_to_get]
        # store profile links 
        self.profile_links = [follower.get_attribute('href') for follower in number_of_requested_followers]

        return followers

    def like_posts_from_profile(self):

        number_of_liked = 0

        if not self.profile_links:
            # Get followers
            followers = self.__get_user_followers(NUMBER_OF_PROFILES_TO_GET)

        profile_links = self.profile_links

        print('-> Gotten followers')

        # Loop theough each profile link 
        for profile_link in profile_links:

            # Make sure to check for limit
            if number_of_liked >= LIKE_POSTS_PER_ACCOUNT:
                break

            # Open profile link
            self.browser.get(profile_link)
            time.sleep(5)
            
            last_height = self.browser.execute_script("return document.body.scrollHeight")
            post_available = True

            # Perform loop while limit has not been reached or if follower has posts 
            while number_of_liked < LIKE_POSTS_PER_ACCOUNT and post_available:

                # Scroll to load posts
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                
                new_height = self.browser.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

                try:
                    # Get div holding all posts
                    main_div = WebDriverWait(self.browser, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "x1iyjqo2 xdj266r xkrivgy x4n8cb0 x1gryazu x1fawyso x6tf39o xc73u3c x18d9i69 x5ib6vp x19sv2k2 x164vai7 x13ijfrp xhwgc15 xkvl2z1 x58vhm7")]'))
                    )
        
                    # Get rows containing posts within the viewable screen height
                    rows = main_div.find_elements(By.XPATH, './/div/div/div[contains(@class, "_ac7v xras4av xgc1b0m xat24cr xzboxd6")]')
                   
                   # Loop through each row 
                    for row in rows:
                        if number_of_liked >= LIKE_POSTS_PER_ACCOUNT:
                            break
                        
                        # Get all posts in a specific row
                        posts = row.find_elements(By.XPATH, './/div[contains(@class, "x1lliihq x1n2onr6 xh8yej3 x4gyw5p xfllauq xo2y696 x11i5rnm x2pgyrj")]')
                        
                        # Getting a single post from posts in row
                        for post in posts:
                            if number_of_liked >= LIKE_POSTS_PER_ACCOUNT:
                                break

                            
                            post.click()
                            print('-> clicked post')
                            time.sleep(5)

                            try:
                                heart_button = self.browser.find_element(By.XPATH, '//span[@class="x1rg5ohu xp7jhwk"]/div/div/span')

                                # Like button if button is not already liked
                                if heart_button.find_element(By.TAG_NAME, 'svg').get_attribute('aria-label') == 'Like':
                                    self.browser.execute_script("arguments[0].click();", heart_button)
                                    number_of_liked += 1

                                    print('-> Liked post')
                                else:
                                    print("Post is already liked.")
                                time.sleep(2)

                                # Close the displayed post
                                close_button = self.browser.find_element(By.XPATH, '//div[@class="x160vmok x10l6tqk x1eu8d0j x1vjfegm"]').click()
                                time.sleep(2)

                            except NoSuchElementException:
                                close_button = self.browser.find_element(By.XPATH, '//div[@class="x160vmok x10l6tqk x1eu8d0j x1vjfegm"]').click()
                                close_button.click()
                                print('-> No like button found')

                    post_available = False

                except TimeoutException:
                    print('-> No posts timeout')
                    post_available = False

                except NoSuchElementException:
                    print('-> No posts present')
                    post_available = False

    def follow_users(self):
        if not self.profile_links:
            # Get followers
            followers = self.__get_user_followers(NUMBER_OF_PROFILES_TO_GET)

        profile_links = self.profile_links

        number_of_followed = 0
        
        for profile_link in profile_links:

            # Make sure to check for limit
            if number_of_followed >= HOURLY_FOLLOW:
                print('-> Hourly Limit reached')
                break

            # Open profile link
            self.browser.get(profile_link)
            time.sleep(5)

            try:
                # Get followers count
                followers_element = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//a[@href='/{profile_link.rstrip('/').split('/')[-1]}/followers/']/span/span[@class='_ac2a _ac2b']"))
                )
            except TimeoutException:
                print('-> Private account')
                continue

            # Extract the followers count text
            followers_text = followers_element.get_attribute('title')

            # Remove commas and convert to integer
            followers_count = int(followers_text.replace(',', ''))

            print(f'followers: {followers_count}')

            # Wait for the following element to be present
            following_element = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/following/")]/span/span[@class="_ac2a _ac2b"]'))
            )

            # Extract the following count text
            following_text = following_element.text

            # Remove commas and convert to integer
            following_count = int(following_text.replace(',', ''))

            print(f'following: {following_count}')

            # only follow followers if followers are larger than following
            if followers_count > following_count:
                
                followers_element.click()

                scroll_box = WebDriverWait(self.browser, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6')]"))
                )

                # Scroll the element
                last_ht, ht, number_of_scrolls = 0, 1, 0
                while last_ht != ht and number_of_scrolls <= 3:
                    last_ht = ht
                    time.sleep(2)
                    # Scroll down and return the height of scroll (JS script)
                    ht = self.browser.execute_script("""
                        arguments[0].scrollTo(0, arguments[0].scrollHeight);
                        return arguments[0].scrollHeight;
                    """, scroll_box)

                    number_of_scrolls += 1

                time.sleep(5)

                follow_buttons = scroll_box.find_elements(By.XPATH, '//button')

                for button in follow_buttons:
                    # Find the inner div with the text
                    try:
                        inner_div = button.find_element(By.XPATH, './/div[@class="_ap3a _aaco _aacw _aad6 _aade"]')
                     
                        button_text = inner_div.text

                        if button_text == "Follow":
                            self.browser.execute_script("arguments[0].click();", button)
                            number_of_followed += 1
                            print(f"-> Followed user")
                        elif button_text == "Following":
                            print("-> Already following user")
                    except NoSuchElementException:
                        print('-> Follow status not found')

                    time.sleep(5)
            else:
                print('-> Following greater than follower. Skipping')
                continue
    
    def story_view(self, subscribers=None):
        """
            Mass view of stories
            
            The bot will see the stories of all the most engaged subscribers of your competitors.

            In the case of most engaged subscribers, subscribers to be extracted from the db and
            the usernames placed in the list.
        """
        # Return if there are no subscribers
        if subscribers == [] or subscribers is None: return print(f"-> {self.username} has no subscribers with story up.")

        for subscriber in subscribers:
            # Get the profile url of the subscriber
            self.browser.get(f"{INSTAGRAM_LOGIN_URL}{subscriber}")
            time.sleep(2)

            # Check if the user has a story
            story_exists = self.browser.execute_script("""
                if(document.querySelector("header section").querySelectorAll("[role='button'] canvas").length == 1) return true;
                else return false;
            """)

            if story_exists:
                # Get the story url of the subscriber
                self.browser.get(f"{INSTAGRAM_STORY_URL}{subscriber}")
                time.sleep(2)

                print(f"[{self.username}] -> {subscriber} has a story up.")
                
                view_story = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[text()='View story']"))
                )
                view_story.click()

                # Next story
                next_story = """document.querySelector("[aria-label='Next']").parentElement.parentElement.click()"""

                # View each story
                WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'x1ned7t2 x78zum5')]"))
                )
                number_of_stories = int(self.browser.execute_script("""return document.querySelector(".x1ned7t2.x78zum5").childElementCount;"""))
                viewed_stories = 0

                while viewed_stories < number_of_stories:
                    # View for a random number of seconds varying from 3 to 6 seconds then skip to the next story
                    print(f"[{self.username}] -> Viewed {viewed_stories + 1} out of {number_of_stories} {subscriber} stories.")
                    time.sleep(random.choice([3,4,5,6]))

                    # Make sure the next button is still clickable
                    try: self.browser.execute_script(next_story)
                    except JavascriptException: pass

                    # Increase count of viewed stories
                    viewed_stories += 1

                # Viewed all the stories
                print(f"-> Viewed all of {subscriber} stories.")

            else: print(f"[{self.username}] -> {subscriber} has no story up.")

    def story_view_from_feed(self):
        """
            Engage with the stories of users currently subscribed to.

            Retrieves the usernames and interacts with their stories
            if they any within 24 hours.
        """
        # Retrieve the usernames of users with stories
        usernames = self.__extract_usernames_from_story_list()

        # Mass view the stories of the users
        self.story_view(subscribers=usernames)
        
    def unfollow_users(self):
        # Navigate to the user's profile page
        self.browser.get(f'{self.base_url}{self.username}')

        # Wait for and click on the 'following' element to load the list of followed users
        following_element = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//a[@href='/{self.username}/following/']"))
        )
        following_element.click()

        # Wait for the scroll box element to be present, which contains the list of followed users
        scroll_box = WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6')]"))
        )

        number_of_scrolls = 0
        max_scrolls = 3
        number_of_unfollowed = 0

        last_ht, ht, number_of_scrolls = 0, 1, 0
        while last_ht != ht and number_of_scrolls <= max_scrolls:
            last_ht = ht
            time.sleep(2)
            # Scroll down and return the height of scroll (JS script)
            ht = self.browser.execute_script("""
                arguments[0].scrollTo(0, arguments[0].scrollHeight);
                return arguments[0].scrollHeight;
            """, scroll_box)

            number_of_scrolls += 1

        # Find all follow buttons within the scroll box
        follow_buttons = scroll_box.find_elements(By.XPATH, '//button')

        while number_of_unfollowed < HOURLY_UNFOLLOW:
            follow_buttons = scroll_box.find_elements(By.XPATH, '//button')

            if not follow_buttons:
                print("-> No more follows found")
                break

            for button in follow_buttons:
                if number_of_unfollowed >= HOURLY_UNFOLLOW:
                    break

                try:
                    # Check if the button's inner div text is "Following"
                    inner_div = button.find_element(By.XPATH, './/div[@class="_ap3a _aaco _aacw _aad6 _aade"]')
                    button_text = inner_div.text

                    if button_text == "Following":
                        # Scroll the button into view before clicking
                        self.browser.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)  # Allow some time for scrolling

                        # Click the "Following" button to unfollow
                        self.browser.execute_script("arguments[0].click();", button)
                        time.sleep(2)

                        # Wait for and click the "Unfollow" confirmation button
                        unfollow_button = WebDriverWait(self.browser, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, '_a9-- _ap36 _a9-_') and text()='Unfollow']"))
                        )
                        self.browser.execute_script("arguments[0].click();", unfollow_button)

                        number_of_unfollowed += 1
                        print(f"-> Unfollowed user")
                        time.sleep(7)  # To avoid action blocking

                except NoSuchElementException:
                    print('-> Follow status not found')

                except TimeoutException:
                    print('-> Follow status timeout')

        print(f"-> Total unfollowed users: {number_of_unfollowed}")

    def welcome_dm(self, username, message):
        """
            You can set up a welcome message for each of your new subscribers.

            This sends each new subscriber a Direct Message(DM).
            The message will be specfied and retrieved from the database.
        """
        # Go to messages
        self.browser.get(self.base_url + "direct/inbox")
        time.sleep(5)

        # Remove pop up if any
        self.browser.execute_script(
            """
            Array.from(document.querySelectorAll('button')).forEach(function(button){
                // Check if 'Not Now'
                if(button.innerText == 'Not Now'){
                    button.click();
                }
            });
        """
        )
        time.sleep(2)

        # Clicks on pencil icon
        self.browser.execute_script(
            """
            Array.from(document.querySelectorAll("[role='button']")).forEach(function(button){
                // Check for the pencil icon
                if(button.querySelector("[aria-label='New message']")){
                    button.click();
                }
            });
        """
        )
        time.sleep(7)

        # Set userFound
        userFound = False

        # Input the username
        self.browser.find_element(By.CSS_SELECTOR, '[role="dialog"]').find_element(
            By.TAG_NAME, "input"
        ).send_keys(username)
        time.sleep(3)

        # Select the username
        userFound = self.browser.execute_script(
            f"""
            var userFound = false;
            Array.from(document.querySelector("[role='dialog']").querySelectorAll("[role='button']")).forEach(function(button){{
                // Check for username
                Array.from(button.querySelectorAll("span[dir='auto']")).forEach(function(user){{
                    if(user.querySelector("span").innerHTML == '{username}'){{
                        userFound = true;
                        button.click();
                    }}
                }});
            }});
            return userFound;
        """
        )
        if userFound is False:
            # Input the username without the last letter
            self.browser.find_element(By.CSS_SELECTOR, '[role="dialog"]').find_element(
                By.TAG_NAME, "input"
            ).send_keys(Keys.CONTROL + "a")
            self.browser.find_element(By.CSS_SELECTOR, '[role="dialog"]').find_element(
                By.TAG_NAME, "input"
            ).send_keys(Keys.DELETE)
            self.browser.find_element(By.CSS_SELECTOR, '[role="dialog"]').find_element(
                By.TAG_NAME, "input"
            ).send_keys(username)
            time.sleep(3)

            userFound = self.browser.execute_script(
                f"""
                var userFound = false;
                Array.from(document.querySelector("[role='dialog']").querySelectorAll("[role='button']")).forEach(function(button){{
                    // Check for username
                    Array.from(button.querySelectorAll("span[dir='auto']")).forEach(function(user){{
                        if(user.querySelector("span").innerHTML == '{username}'){{
                            userFound = true;
                            button.click();
                        }}
                    }});
                }});
                return userFound;
            """
            )
        time.sleep(4)

        if userFound is True:
            # Chat Button
            self.browser.execute_script(
                """
                Array.from(document.querySelector("[role='dialog']").querySelectorAll("[role='button']")).forEach(function(button){
                    // Check if 'Chat'
                    if(button.innerText == "Chat"){
                        button.click();
                    }
                });
            """
            )
            time.sleep(4)

            # Input the message in the Lexical TextEditor
            safeToSend = True
            try:
                self.browser.execute_script(
                f"""
                    var lexicalEditor = document.querySelector("[role='textbox'");

                    var inputEvent = new InputEvent('input', {{
                    data: '{message}',
                    inputType: 'insertText',
                    dataTransfer: null,
                    isComposing: false,
                    bubbles: true,
                    }});
                    lexicalEditor.dispatchEvent(inputEvent);
                """
                )
            except JavascriptException:
                safeToSend = False

            # Send message
            if safeToSend is True:
                self.browser.execute_script(
                    """
                    Array.from(document.querySelector("[role='main']").querySelectorAll("[role='button']")).forEach(function(button){
                        // Check if 'Send'
                        if(button.innerText == 'Send'){
                            button.click();
                        }
                    });
                """
                )
                print(f"[{self.username}] -> Welcome DM sent to {username}.")
                time.sleep(2)

a = Bot("username", "password")
a.follow_users()
a.unfollow_users()