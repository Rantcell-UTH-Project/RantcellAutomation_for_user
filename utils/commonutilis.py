import allure
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Setup WebDriver
def setup_driver(browser='chrome'):
    if browser.lower() == 'chrome':
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    elif browser.lower() == 'firefox':
        return webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    elif browser.lower() == 'safari':
        return webdriver.Safari()
    elif browser.lower() == 'edge':
        return webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
    else:
        raise ValueError("Unsupported browser! Supported browsers: 'chrome', 'firefox', 'safari', 'edge'.")

# Close Browser
def close_browser(driver):
    return driver.quit()

# Get Title
def get_title(driver):
    return driver.title

# Get Current URL
def get_current_url(driver):
    return driver.current_url

# Open URL
def open_url(driver, url):
    return driver.get(url)
def driver_maximize_window(driver):
    return driver.maximize_window()

def allure_get_screenshot_as_png(driver):
    return driver.get_screenshot_as_png()

def element_screenshot_as_png(element):
    return element.screenshot_as_png

def allure_attach_element_screenshot_as_png(element, name,attachment_type=allure.attachment_type.PNG):
    return allure.attach(element_screenshot_as_png(element), name=name,attachment_type=attachment_type)
def allure_attach_driver_screenshot_as_png(driver, name,attachment_type=allure.attachment_type.PNG):
    return allure.attach(allure_get_screenshot_as_png(driver), name=name,attachment_type=attachment_type)

def allure_step(title):
    return allure.step(title)

# Find Element
def find_element(driver, locators):
    return driver.find_element(*locators)

def WebDriver_Wait(driver, timeout):
    return WebDriverWait(driver, timeout)

# Wait Functions
def wait_for_element_presence(driver,locators,timeout):
    return WebDriver_Wait(driver, timeout).until(EC.presence_of_element_located(locators))

def wait_for_element_visibility(driver,locators, timeout):
    return WebDriver_Wait(driver, timeout).until(EC.visibility_of_element_located(locators))

def wait_for_element_clickable(driver,locators, timeout):
    return WebDriver_Wait(driver, timeout).until(EC.element_to_be_clickable(locators))

def wait_for_element_invisibility(driver,locators, timeout):
    return WebDriver_Wait(driver, timeout).until(EC.invisibility_of_element_located(locators))

def wait_for_all_elements_presence(driver,locators, timeout):
    return WebDriver_Wait(driver, timeout).until(EC.presence_of_all_elements_located(locators))

def wait_for_all_elements_visibility(driver,locators, timeout):
    return WebDriver_Wait(driver, timeout).until(EC.visibility_of_all_elements_located(locators))

def wait_for_element_selection_state(driver, locators, timeout,is_selected=True):
    return WebDriver_Wait(driver, timeout).until(EC.element_selection_state_to_be(locators, is_selected))

def wait_for_text_in_element(driver,locators, text, timeout):
    return WebDriver_Wait(driver, timeout).until(EC.text_to_be_present_in_element(locators, text))

def wait_for_text_in_element_value(driver,locators, text, timeout):
    return WebDriver_Wait(driver, timeout).until(EC.text_to_be_present_in_element_value(locators, text))

def wait_for_frame_and_switch(driver, frame_reference, timeout):
    return WebDriver_Wait(driver, timeout).until(EC.frame_to_be_available_and_switch_to_it(frame_reference))

def Action_Chains(driver):
    return ActionChains(driver)


class CommonFuncSelenium:
    def __init__(self,driver):
        self.driver = driver

    def _setup_driver(self, browser):
        if browser.lower() == 'chrome':
            return webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        elif browser.lower() == 'firefox':
            return webdriver.Firefox(service=Service(GeckoDriverManager().install()))
        elif browser.lower() == 'safari':
            return webdriver.Safari()
        elif browser.lower() == 'edge':
            return webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
        else:
            raise ValueError("Unsupported browser! Supported browsers: 'chrome', 'firefox', 'safari', 'edge'.")

    def open_url(self, url):
        return self.driver.get(url)

    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def close_browser(self):
        return self.driver.quit()

    def get_title(self):
        return self.driver.title

    def get_current_url(self):
        return self.driver.current_url

    def take_screenshot(self, file_path):
        return self.driver.save_screenshot(file_path)

    def execute_script(self, script, *args):
        return self.driver.execute_script(script, *args)

    # Wait Functions
    def wait_for_element_presence(self, by, value, timeout):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))

    def wait_for_element_visibility(self, by, value, timeout):
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((by, value)))

    def wait_for_element_clickable(self, by, value, timeout):
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, value)))

    def wait_for_element_invisibility(self, by, value, timeout):
        return WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located((by, value)))

    def wait_for_all_elements_presence(self, by, value, timeout):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located((by, value)))

    def wait_for_all_elements_visibility(self, by, value, timeout):
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_all_elements_located((by, value)))

    def wait_for_element_selection_state(self, by, value,timeout,is_selected=True):
        return WebDriverWait(self.driver, timeout).until(EC.element_selection_state_to_be((by, value), is_selected))

    def wait_for_text_in_element(self, by, value, text, timeout):
        return WebDriverWait(self.driver, timeout).until(EC.text_to_be_present_in_element((by, value), text))

    def wait_for_text_in_element_value(self, by, value, text, timeout):
        return WebDriverWait(self.driver, timeout).until(EC.text_to_be_present_in_element_value((by, value), text))

    def wait_for_frame_and_switch(self, frame_reference, timeout):
        return WebDriverWait(self.driver, timeout).until(EC.frame_to_be_available_and_switch_to_it(frame_reference))