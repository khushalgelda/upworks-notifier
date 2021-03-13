
from bs4 import BeautifulSoup as soup
from time import sleep
from selenium import webdriver
import datetime
import time
from library import send_telegram

query_freq_in_mins = 9


def new_posts(old, new):
    # print("{:<100} {:<100}".format('==========', '=========='))
    # print("{:<100} {:<100} {:<100}".format('JOB', 'Link', 'Posted'))
    for key, value in new.items():
        if key not in old.keys():
            title = value['title']
            howold = value['howold']
            link = key
            msg = title + '\n' + howold + '\n' + link
            send_telegram(msg, -409087011)
            sleep(0.2)


class Driver:
    """
    path: Web driver path, eg: Chrome, Firefox
    options: list of web driver options
    This creates a webdriver object with options.
    """

    def __init__(self, path, options=()):
        self.path = path
        self.options = options
        self.driver_options = webdriver.ChromeOptions()
        for option in self.options:
            self.driver_options.add_argument(option)
        self.driver = webdriver.Chrome(path, options=self.driver_options)

    def click_button_xpath(self, tag_value):
        """Finds the element using xpath. If found, clicks it."""
        button = self.driver.find_elements_by_xpath(tag_value)
        if len(button) > 0:
            self.driver.execute_script("arguments[0].click();", button[0])

    def get_element_list(self, tag_value):
        """Get a list of elements from an xpath"""
        return self.driver.find_elements_by_xpath(tag_value)

    def execute_script(self, code, element):
        """Executes script"""
        return self.driver.execute_script(code, element)

    def current_url(self):
        """Gets current URL"""
        return self.driver.current_url

    def page_source(self):
        """Gets page source"""
        return self.driver.page_source

    def back(self):
        """Takes the driver 1 page back"""
        return self.driver.back()

    def close(self):
        """closes the driver"""
        return self.driver.close()


jobs_dict_new = {}
jobs_dict_old = {}

web_driver_path = '/Users/khugel01/Downloads/chromedriver'
driver_options = ('--ignore-certificate-errors',
                  '--incognito',
                  # '--headless'
                  )
driver = Driver(web_driver_path, driver_options)

upwork_username = 'geldabhojal'
upwork_password = 'Bgt56yhN_'

# Upwork Login
driver.driver.get("https://www.upwork.com/ab/account-security/login")

# Wait till Recaptcha is manually solved
# wait = driver.get_element_list("//h1[text()='Please verify you are a human']")
# while len(wait) > 0:
#     wait = driver.get_element_list("//h1[text()='Please verify you are a human']")
#     sleep(90)

driver.get_element_list("//input[@id='login_username']")[0].send_keys(upwork_username)
driver.click_button_xpath("//button[@id='login_password_continue']")
sleep(3)
driver.get_element_list("//input[@id='login_password']")[0].send_keys(upwork_password)
driver.click_button_xpath("//button[@id='login_control_continue']")
sleep(3)

# Go to advanced search
driver.driver.get("https://www.upwork.com/ab/jobs/search/")
driver.driver.maximize_window()
sleep(3)

# Change number of search result per page from 10 -> 50.
driver.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
driver.get_element_list("//data-eo-select[@id='jobs-per-page']")[0].click()
driver.get_element_list("//data-eo-select[@id='jobs-per-page']//div//ul/li[3]")[0].click()
sleep(3)

# for rerun_count in range(3):
#     try:
#         # Go to search Page in upworks
#         driver.driver.get("https://www.upwork.com/ab/jobs/search/")
#         driver.driver.maximize_window()
#         sleep(2)
counter = 0
while True:
    # Click on Search box
    driver.get_element_list("//input[@type='search' and @id='search-box-el']")[0].click()
    sleep(2)

    # Get number of saved searches
    saved_searches = driver.get_element_list("//span[contains(@class,'saved-search-suggestion-label')]")

    for x in range(len(saved_searches)):
        # Click on the Search box
        driver.click_button_xpath("//input[@type='search' and @id='search-box-el']")
        sleep(1)

        # Extract saved Searches
        saved_searches = driver.get_element_list("//span[contains(@class,'saved-search-suggestion-label')]")
        search = saved_searches[x].text
        jobs_dict_new[search] = {}
        sleep(1)

        # Click on the saved search
        driver.driver.execute_script("arguments[0].click();", saved_searches[x])
        sleep(4)

        # Click on the search button next to search box - Otherwise search results wont show 50 results.
        driver.click_button_xpath("//button[contains(@class,'qa-search-button')]")
        sleep(4)

        # Save page source
        page_source = driver.driver.page_source
        page_soup = soup(page_source, "html.parser")

        # Extract search results
        print('Searching for new jobs for {} at {} Hrs'.format(search, datetime.datetime.now().time()))
        all_jobs = page_soup.findAll("div", {"data-job-tile": "::job"})

        # Convert new postings into dictionary (with link as key)
        for job in all_jobs:
            jobs_dict_new[search][
                'https://www.upwork.com' + job.select("a[class*=job-title-link]")[0]['href']] = {}
            jobs_dict_new[search]['https://www.upwork.com' + job.select("a[class*=job-title-link]")[0]['href']][
                'title'] = job.select("a[class*=job-title-link]")[0].text
            jobs_dict_new[search]['https://www.upwork.com' + job.select("a[class*=job-title-link]")[0]['href']][
                'howold'] = job.findAll("time")[0].text

        if counter > 0:
            new_posts(jobs_dict_old[search], jobs_dict_new[search])
        jobs_dict_old[search] = jobs_dict_new[search].copy()
    counter = counter + 1
    print(counter)
    time.sleep(query_freq_in_mins*60)

# time.sleep(query_freq_in_mins * 60)
    # except Exception as e:
    #     if rerun_count == 2:
    #         sys.exit('Retry failed after an exception occurred')
    #         driver.driver.close()
    #     print('Re-trying')
    #     continue

driver.driver.close()

# Pop-up notification in MAC
# def notify(title, text):
#     os.system("""
#               osascript -e 'display notification "{}" with title "{}"'
#               """.format(text, title))
#
#
# notify("Title", "Heres an alert")
