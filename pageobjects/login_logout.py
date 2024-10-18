from module_controllers.module_controllers import login_module_controllers, logout_module_controllers
from utils.library import *
from locators.locators import Login_Logout
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def Navigate_to_loginPage(driver, url):
    try:
        assert launchbrowser(driver, url)
    except:
        pass
    try:
        WebDriverWait(driver, 90).until(EC.presence_of_element_located(Login_Logout.link_login1))
    except:
        pass
    try:
        assert clickec(driver,Login_Logout.link_login)
    except:
        pass

def login_user(driver, userid, password,excelpath):
    Title = "Login"
    # runvalue = Testrun_mode(value="Login")
    login_runvalue = login_module_controllers()
    if "Yes".lower() == login_runvalue[-1].strip().lower():
        try:
            try:
                WebDriverWait(driver, 90).until(EC.presence_of_element_located(Login_Logout.email))
            except:
                pass
            assert inputtext(driver, Login_Logout.textbox_username, userid)
            assert inputtext(driver, Login_Logout.textbox_password, password)
            assert click(driver, Login_Logout.button_login)
            dashboard_loading(driver)
            assert verifyelementispresent(driver, Login_Logout.dashboard)
            assert True
            updatehighmodulestatus(Title, "PASSED", "Successfully login to the application", excelpath)
            with allure.step("Login"):
                allure.attach(driver.get_screenshot_as_png(), name="Successfully login to the application",attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            updatehighmodulestatus(Title, "FAILED",  "Failed to  login to the application due to", excelpath)
            with allure.step("Login"):
                allure.attach(driver.get_screenshot_as_png(), name="Failed to  login to the application",attachment_type=allure.attachment_type.PNG)
            assert False
    elif "No".lower() == login_runvalue[-1].strip().lower():
        statement = "You have selected Not to execute"
        with allure.step(statement):
            updatehighmodulestatus(Title, "SKIPPED", "You have selected No for execute", excelpath)
            pass
def dashboard_loading(driver):
    try:
        dashboard_elemnt = driver.find_elements(Login_Logout.dashboard[0], Login_Logout.dashboard[1])
        start_time = time.time()
        # Maximum time in seconds the loop should run (1 minute = 60 seconds)
        max_run_time = 120
        if len(dashboard_elemnt) == 0:
            with allure.step("Waiting for Dashboard to load"):
                allure.attach(driver.get_screenshot_as_png(), name=f"Waiting for Dashboard to load",attachment_type=allure.attachment_type.PNG)
                while time.time() - start_time < max_run_time:
                    dashboard_elemnt = driver.find_elements(Login_Logout.dashboard[0], Login_Logout.dashboard[1])
                    # Check if the condition is met
                    if len(dashboard_elemnt) != 0:
                        break
    except:
        pass
def logout_user(driver,excelpath):
    Title = "Logout"
    # runvalue = Testrun_mode(value="Logout")
    logout_runvalue = logout_module_controllers()
    if "Yes".lower() == logout_runvalue[-1].strip().lower():
        try:
            assert click(driver, Login_Logout.dropdown_dropdown_toggle)
            time.sleep(1.2)
            assert click(driver, Login_Logout.link_logout)
            assert True
            updatehighmodulestatus(Title, "PASSED",  "Successfully Logged out from the application", excelpath)
            with allure.step("Logout"):
                allure.attach(driver.get_screenshot_as_png(), name="successfully Logged out from the application",attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            updatehighmodulestatus(Title, "FAILED", "Failed to  Logout from  the application", excelpath)
            with allure.step("Logout"):
                allure.attach(driver.get_screenshot_as_png(), name="Failed to  Logout from  the application",attachment_type=allure.attachment_type.PNG)
            assert False

    elif "No".lower() == logout_runvalue[-1].strip().lower():
        statement = "You have selected Not to execute"
        with allure.step(statement):
            updatehighmodulestatus(Title, "SKIPPED", "You have selected No for execute", excelpath)
            pass
def login(driver, userid, password):
    try:
        try:
            WebDriverWait(driver, 90).until(EC.presence_of_element_located(Login_Logout.email))
        except:
            pass
        assert inputtext(driver, Login_Logout.textbox_username, userid)
        assert inputtext(driver, Login_Logout.textbox_password, password)
        assert click(driver, Login_Logout.button_login)
        dashboard_loading(driver)
        assert verifyelementispresent(driver, Login_Logout.dashboard)
        assert True

    except Exception as e:
        assert False

def logout(driver):
    try:
        assert click(driver, Login_Logout.dropdown_dropdown_toggle)
        time.sleep(1.2)
        assert click(driver, Login_Logout.link_logout)
        assert True

    except Exception as e:
        assert False

def click_on_forgot_password(driver):
    click(driver,Login_Logout.forgot_password_xpath)

def launchbrowser_login_and_verify_the_dashboard_loaded(driver,url,emailId, password):
    launchbrowser(driver, url)
    try:
        clickec(driver, Login_Logout.link_login)
    except:
        pass
    login(driver, emailId, password)
    dashboard_flag = verifyelementispresent(driver, Login_Logout.dashboard)
    return dashboard_flag
