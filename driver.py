# Keeps a Firefox window open with YouTube studio bookmarked
# Cookies are available, so login isn't needed
# RedditIO depends on this to push videos to YouTube
# This process has to be manually started
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import constants as C

class DriverHelper:
    def __init__(self):
        self.driver = None
        self.options = Options()
        self.options.binary_location = C.FIREFOX_BINARY_PATH

    def start_session(self):
        # Only needs to be done once. Browser is kept alive until needed
        self.driver = webdriver.Firefox(options=self.options)

        print('Now, go to YouTube Studio and login')
        input('Type "Y" when done: ')

        driver = self.driver
        driver.get('https://www.google.com') # A page so that the browser is open

        self.driver = driver

    def get_driver(self):
        return self.driver
