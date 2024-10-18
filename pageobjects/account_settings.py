from utils.library import *
from locators.locators import *



def click_on_change_password_link_btn(driver):
    allure.attach(driver.get_screenshot_as_png(), name="click_on_change_password_link_btn",attachment_type=allure.attachment_type.PNG)
    clickec(driver, change_password_account_settings.change_password_link_btn)


