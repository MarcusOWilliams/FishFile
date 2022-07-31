import profile
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

class MainEndToEnd(unittest.TestCase):
    def setUp(self):
        self.account_pswd = input("Input password:")
        self.driver = webdriver.Chrome("tests\end_to_end\chromedriver\chromedriver.exe")
        self.url = "https://fishfilebath.herokuapp.com/"
        self.delay = 4

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
        stock.send_keys("S0001")
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
        driver.execute_script('arguments[0].click()', submit_button)

        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "fishInformation")))
        auto_fish_url = driver.current_url
        
        """UPDATE FISH"""
        update_link = driver.find_element("id", "updateFishLink")
        driver.execute_script('arguments[0].click()', update_link)
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "updateFishTable")))

        print(driver.title)

        fish_id = driver.find_element("id", "fish_id")
        fish_id.send_keys("Updated")
        tank_id = driver.find_element("id", "tank_id")
        tank_id.send_keys("Updated")
        males = driver.find_element("id", "males")
        males.send_keys(1)
        females = driver.find_element("id", "females")
        females.send_keys(1)
        unsexed = driver.find_element("id", "unsexed")
        unsexed.send_keys(1)
        carriers = driver.find_element("id", "carriers")
        carriers.send_keys(1)
        total = driver.find_element("id", "total")
        total.send_keys(1)
        father_tank = driver.find_element("id", "father_tank_id")
        father_tank.send_keys("AA101")
        father_stock = driver.find_element("id", "father_stock")
        father_stock.send_keys("S0001")
        mother_tank = driver.find_element("id", "mother_tank_id")
        mother_tank.send_keys("AA102")
        mother_stock = driver.find_element("id", "mother_stock")
        mother_stock.send_keys("S0002")
        allele = Select(driver.find_element("id", "allele"))
        allele.select_by_index(2)
        allele_name = allele.first_selected_option.text

        submit_button = driver.find_element("id", "submit")
        driver.execute_script('arguments[0].click()', submit_button)

        """CHECK ADDITIONAL LINKS"""
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "fishInformation")))
        histroy_link = driver.find_element("id", "historyFishLink")
        driver.execute_script('arguments[0].click()', histroy_link)
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "familyTree")))
        driver.back()

        changes_link = driver.find_element("id", "changesFishLink")
        driver.execute_script('arguments[0].click()', changes_link)
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "filterChangeForm")))

        filter_id = driver.find_element("id", "fish_id")
        driver.execute_script('arguments[0].click()', filter_id)

        filter_button = driver.find_element("id", "tank_id")
        driver.execute_script('arguments[0].click()', filter_button)

        filter_button = driver.find_element("id", "stock")
        driver.execute_script('arguments[0].click()', filter_button)

        filter_button = driver.find_element("id", "protocol")
        driver.execute_script('arguments[0].click()', filter_button)

        submit_button = driver.find_element("id", "submit")
        driver.execute_script('arguments[0].click()', submit_button)

        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "filterChangeForm")))

        """UPDATE ALLELE"""
        driver.get(auto_fish_url)
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "fishInformation")))
        
        allele_link = driver.find_element("id", "updateAllelesLink")
        driver.execute_script('arguments[0].click()', allele_link)
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "alleleTable")))
        unidentified = driver.find_element("name", f"{allele_name.replace(' ','')}Unidentified")
        identified = driver.find_element("name", f"{allele_name.replace(' ','')}Identified")
        homozygous = driver.find_element("name", f"{allele_name.replace(' ','')}Homozygous")
        heterozygous = driver.find_element("name", f"{allele_name.replace(' ','')}Heterozygous")
        hemizygous = driver.find_element("name", f"{allele_name.replace(' ','')}Hemizygous")
        submit_button = driver.find_element("id", "submit")

        driver.execute_script('arguments[0].click()', unidentified )
        driver.execute_script('arguments[0].click()', identified)
        driver.execute_script('arguments[0].click()', homozygous)
        driver.execute_script('arguments[0].click()', heterozygous)
        driver.execute_script('arguments[0].click()', hemizygous)
        driver.execute_script('arguments[0].click()', submit_button)






        driver.get(auto_fish_url)
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "fishInformation")))






        """DELETE FISH"""
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "fishInformation")))
        
        delete_button = driver.find_element("id", "deleteFishButton")
        driver.execute_script('arguments[0].click()', delete_button)

        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "mainSearchForm")))
        self.assertEqual("Home Page - FishFile", driver.title)


        """CHECK SEARCH FUNCTIONALITY"""

        submit_button = driver.find_element("id", "submit")
        driver.execute_script('arguments[0].click()', submit_button)
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "fishList")))

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        next_page = driver.find_element("id", "nextPageLink")
        driver.execute_script('arguments[0].click()', next_page)

        """CHECK USER PAGE AND SETTINGS"""

        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "profileDropdown")))
        profile_link = driver.find_element("id", "myProfileLink")
        driver.execute_script('arguments[0].click()', profile_link)

        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "profileNameHeader")))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        driver.get(f"{base_url}/settings")
        WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.ID, "notificationsSettingsCheckboxes")))
        add_notifications = driver.find_element("id", "add_notifications")
        driver.execute_script('arguments[0].click()', add_notifications)
        pl_add_notifications = driver.find_element("id", "pl_add_notifications")
        driver.execute_script('arguments[0].click()', pl_add_notifications)
        pl_custom_reminders = driver.find_element("id", "pl_custom_reminders")
        driver.execute_script('arguments[0].click()', pl_custom_reminders)
        emails = driver.find_element("id", "emails")
        driver.execute_script('arguments[0].click()', emails)
     
        
        driver.execute_script('arguments[0].click()', add_notifications)
        driver.execute_script('arguments[0].click()', pl_add_notifications)
        driver.execute_script('arguments[0].click()', pl_custom_reminders)
        driver.execute_script('arguments[0].click()', emails)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        submit  = driver.find_element("id", "submit")
        driver.execute_script('arguments[0].click()', submit)



        """LOGOUT"""


        logout_link = driver.find_element("id", "logoutLink")
        driver.execute_script('arguments[0].click()', logout_link)

        self.assertEquals(driver.title, "FishFile")


        
        


    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
