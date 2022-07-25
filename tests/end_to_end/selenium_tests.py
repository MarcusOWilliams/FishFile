import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest


class SystemTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome("tests\end_to_end\chromedriver\chromedriver.exe")
        self.url = "http://127.0.0.1:5000"

    def test_landing_page(self):

        # Set the driver and the base URL for the specidifc page
        # In this case the url is just the main url with no extensions
        driver = self.driver
        base_url = self.url

        # visit the URL
        driver.get(base_url)

        # check the Title is correct
        self.assertEqual("FishFile", driver.title)

        # Check for the register Link
        register_link = driver.find_element("id", "registerLink")
        self.assertEqual("Register", register_link.text)

        # Click the register link
        register_link.click()

        # Wait for page to load using EC (Expected conditions)
        EC.title_contains("Register")

        # Check the URL is what is expected
        self.assertEqual(f"{base_url}/register", driver.current_url)

        # return back to the base page
        driver.get(base_url)

        # make sure the page has loaded
        EC.presence_of_element_located((By.ID, "loginLink"))

        # repeat process but for login link
        login_link = driver.find_element("id", "loginLink")
        self.assertEqual("here", login_link.text)

        login_link.click()
        EC.title_contains("Sign In")
        self.assertEqual(f"{base_url}/login", driver.current_url)

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":

    unittest.main()
