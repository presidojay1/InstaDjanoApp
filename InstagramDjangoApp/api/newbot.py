from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import os


class Bot:

    def __init__(self, code, password, headless=False):
        self.user_code = code
        self.password = password
        self.login_url = "https://accounts.centris.ca/Account/Login"
        current_directory = os.path.dirname(os.path.abspath(__file__))
        chromedriver_path = os.path.join(current_directory, 'chromedriver.exe') 
        service = Service(executable_path=chromedriver_path)

        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--log-level=3')

        self.browser = webdriver.Chrome(options=chrome_options, service=service)
        self.browser.maximize_window()


        self.login()

    def login(self):
        self.browser.get(self.login_url)

        self.browser.find_element(By.NAME, 'UserCode').send_keys(self.user_code)
        self.browser.find_element(By.NAME, 'Password').send_keys(self.password)

        WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()

        try:
            button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            )
            button.click()
            print("Button clicked successfully!")
        except Exception as e:
            print("Error clicking the button:", e)

    def get_next_page_number(self):
        try:
            # Attempt to find the "next" button
            next_button = self.browser.find_element(By.CSS_SELECTOR, '.pagination .btn-nav.page-link:not(.disabled) i.fal.fa-chevron-right')
            
            if next_button:
                # Find the parent anchor tag and extract the page number from it
                parent_anchor = next_button.find_element(By.XPATH, '..')  # Go to the parent <a> element
                page_number_text = parent_anchor.text.strip()  # Extract text from the <a> tag
                
                # Check if the text is a number or infer the next page number
                if page_number_text.isdigit():
                    return int(page_number_text)
                else:
                    # Fallback to infer the next page number if not directly found
                    current_page_number = self.get_current_page_number()
                    return current_page_number + 1
            else:
                # Handle the case where the "next" button is not found
                print("No next page button found. This may be the last page.")
                return None
        except Exception as e:
            print("No next page button found. This may be the last page.")

    def get_current_page_number(self):
        try:
            # Find the active page number
            active_page = self.browser.find_element(By.CSS_SELECTOR, '.pagination .page-item.active')
            return int(active_page.text.strip())
        except Exception as e:
            print("Error retrieving current page number:", e)
            return 1

    def navigate_to_page(self, page_number):
        url = f"https://zone.centris.ca/Dashboard?ml-page={page_number}&ml-showAllListings=false&tab=list"
        self.browser.get(url)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
        time.sleep(20)  # Wait for the page to load

    def get_listings(self):
        all_data = []  # Initialize a list to store data from all pages
        page_number = 1
        while True:
            print(f"Scraping page {page_number}...")

            # Get the listings from the current page
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
            

            js_script = """
                var rows = document.querySelectorAll('tbody tr');
                return Array.from(rows).map(row => {
                    var photoElement = row.querySelector('td .listing-photo img');
                    var addressElement = row.querySelector('.listing-address a');
                    var priceElement = row.querySelector('.listing-price span');
                    var typeElement = row.querySelector('.listing-properties > div:first-child'); // Adjusted selector
                    var roomsElement = row.querySelector('.listing-properties > div:last-child'); // Adjusted selector
                    var datesElement = row.querySelector('.listing-info-container');
                    var numberElement = row.querySelector('.listing-number');
                    var statusElement = row.querySelector('.status-container span:last-child');
                    
                    return {
                        imageUrl: photoElement ? photoElement.src : 'N/A',
                        address: addressElement ? addressElement.textContent.trim() : 'N/A',
                        price: priceElement ? priceElement.innerHTML
                                            .replace(/&nbsp;/g, ' ')
                                            .replace(/[^0-9\s]/g, '') // Remove any non-numeric characters except spaces
                                            .trim() : 'N/A',
                        type: typeElement ? typeElement.textContent.trim() : 'N/A',
                        roomsAndToilets: roomsElement ? roomsElement.textContent.trim() : 'N/A', // Changed to roomsAndToilets
                        dates: datesElement ? datesElement.textContent.trim() : 'N/A',
                        number: numberElement ? numberElement.textContent.trim() : 'N/A',
                        status: statusElement ? statusElement.textContent.trim() : 'N/A'
                    };
                });
            """

            data = self.browser.execute_script(js_script)
            all_data.extend(data)

            # Get the next page number and navigate to it
            next_page_number = self.get_next_page_number()
            if next_page_number:
                page_number = next_page_number
                self.navigate_to_page(page_number)
            else:
                break

        # printing just to see result
        print(all_data)

        return all_data
# Example usage
# bot = Bot("132186", "Andywebsite21!", headless=True)
# bot.get_listings()
