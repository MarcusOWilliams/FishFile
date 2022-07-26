import sys
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest
from selenium.webdriver.support.ui import Select



# class SystemTest(unittest.TestCase):
#     def setUp(self):
#         self.driver = webdriver.Chrome("tests\end_to_end\chromedriver\chromedriver.exe")
#         self.url = "http://127.0.0.1:5000"
#         self.delay = 3

#     def test_landing_page(self):

#         # Set the driver and the base URL for the specidifc page
#         # In this case the url is just the main url with no extensions
#         driver = self.driver
#         base_url = self.url

#         # visit the URL
#         driver.get(base_url)

#         # check the Title is correct
#         self.assertEqual("FishFile", driver.title)

#         # Check for the register Link
#         register_link = driver.find_element("id", "registerLink")
#         self.assertEqual("Register", register_link.text)

#         # Click the register link
#         register_link.click()

#         # Wait for page to load using EC (Expected conditions)
#         WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "registrationContainer")))

#         # Check the URL is what is expected
#         self.assertEqual(f"{base_url}/register", driver.current_url)
#         # return back to the base page
#         driver.get(base_url)

#         # make sure the page has loaded
#         WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "loginLink")))

#         # repeat process but for login link
#         login_link = driver.find_element("id", "loginLink")
#         self.assertEqual("here", login_link.text)

#         login_link.click()
#         WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "signInForm")))


#         self.assertEqual(f"{base_url}/login", driver.current_url)


#     def tearDown(self):
#         self.driver.close()

class MainSystemTest(unittest.TestCase):
    def setUp(self):
        self.account_pswd = input("Input password:")
        self.driver = webdriver.Chrome("tests\end_to_end\chromedriver\chromedriver.exe")
        self.url = "http://127.0.0.1:5000"
        self.delay = 3

    def test_main_run_through(self):

        
        #setup driver
        driver = self.driver

        #get home page
        base_url = self.url
        driver.get(base_url)


        """LOGIN"""
        #visit the login page
        login_link = driver.find_element("id", "loginLink")
        login_link.click()
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "signInForm")))

        #input email and password and press sign in
        email_input = driver.find_element("id", "email")
        password_input = driver.find_element("id", "password")
        submit_button = driver.find_element("id", "submit")

        email_input.send_keys("mw2056@bath.ac.uk")
        password_input.send_keys(self.account_pswd)
        submit_button.click()

        #check you have made it to the home page
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "mainSearchForm")))
        self.assertEqual("Home Page - FishFile", driver.title)



        """ADD A FISH TO THE DATABASE"""
        new_fish_link = driver.find_element("id", "newFishLink")
        new_fish_link.click()
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "addFishTable")))

        fish_id = driver.find_element("id", "fish_id")
        fish_id.send_keys("Auto Test")
        tank_id = driver.find_element("id", "tank_id")
        tank_id.send_keys("Auto Test")
        stock = driver.find_element("id", "stock")
        stock.send_keys("Auto Test")
        license = Select(driver.find_element("id", "project_license"))
        license.select_by_visible_text('ABC123456')
        code = Select(driver.find_element("id", "user_code"))
        code.select_by_visible_text('MW (mw2056)')
        birthday = driver.find_element("id", "birthday")
        birthday.send_keys("01/01/2020")
        mutant_gene = driver.find_element("id", "mutant_gene")
        mutant_gene.send_keys("Auto Test")
        cross = driver.find_element("id", "cross_type")
        cross.send_keys("Auto Test")

        males = driver.find_element("id", "males")
        males.send_keys(0)
        females = driver.find_element("id", "females")
        females.send_keys(0)
        unsexed = driver.find_element("id", "unsexed")
        unsexed.send_keys(0)
        carriers = driver.find_element("id", "carriers")
        carriers.send_keys(0)
        total = driver.find_element("id", "total")
        total.send_keys(0)

        submit_button = driver.find_element("id", "submit")
        submit_button.click()


        """DELETE FISH"""
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "fishInformation")))
        print(driver.title)
        
        
        
        delete_button = driver.find_element("id", "deleteFishButton")
        driver.execute_script('arguments[0].click()', delete_button)

        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "mainSearchForm")))
        self.assertEqual("Home Page - FishFile", driver.title)
        print(driver.title)


    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
