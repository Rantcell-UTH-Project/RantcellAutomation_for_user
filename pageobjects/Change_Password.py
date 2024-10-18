from pageobjects.Dashboard import *
from pageobjects.account_settings import *
from utils.library import *
from module_controllers.module_controllers import *
def main_func_account_setting_change_password(driver,currentPassword,oldpassword,excelpath,url,emailId,reset_password_flag=False):
    Title = "Change password(account settings)"
    main_func_account_setting_change_password = account_setting_change_password_module_controllers()
    if "Yes".lower() == main_func_account_setting_change_password[-1].strip().lower():
        with allure.step("Account setting change password"):
            try:
                if reset_password_flag == False:
                    random_length = random.randint(3, 4)
                    random_alphabet = generate_random_alphabet(random_length)
                    newpassword = oldpassword + random_alphabet
                    currentPassword = oldpassword
                    dashboard_flag = launchbrowser_login_and_verify_the_dashboard_loaded(driver,url,emailId, currentPassword)
                    i = 2
                elif reset_password_flag == True:
                    newpassword = oldpassword
                    i = 1
                update_password_flag = False
                for j in range(i):
                    if j == 1:
                        time.sleep(5)
                        try:
                            driver.refresh()
                            logout(driver)
                        except Exception as e:
                            pass
                        time.sleep(60)
                        dashboard_flag = launchbrowser_login_and_verify_the_dashboard_loaded(driver,url,emailId, newpassword)
                        time.sleep(5)
                        currentPassword = newpassword
                        newpassword = oldpassword
                    click_on_account_icon_dropdown_btn(driver)
                    click_on_account_setting_btn(driver)
                    click_on_change_password_link_btn(driver)
                    try:
                        WebDriverWait(driver,10).until(EC.visibility_of_element_located(change_password_account_settings.current_password_text_field[:2]))
                    except Exception as e:
                        pass
                    allure.attach(driver.get_screenshot_as_png(), name="change password",attachment_type=allure.attachment_type.PNG)
                    update_password_flag = change_password(driver, currentPassword, newpassword, confirmpassword=newpassword)
                dashboard_flag = launchbrowser_login_and_verify_the_dashboard_loaded(driver,url,emailId, newpassword)
                if dashboard_flag:
                    updatecomponentstatus(Title, "Change Password -> {oldpassword}", "PASSED", "Successfully updated the password",excelpath)
                    updatehighmodulestatus(Title, "PASSED", "Successfully updated the password", excelpath)
                    allure.attach(driver.get_screenshot_as_png(), name="Successfully updated the password",attachment_type=allure.attachment_type.PNG)
                else:
                    updatecomponentstatus(Title, "Change Password -> {oldpassword}", "FAILED", "Unable to update the password",excelpath)
                    updatehighmodulestatus(Title, "FAILED", "Unable to update the password", excelpath)
                    allure.attach(driver.get_screenshot_as_png(), name="Unable to update the password",attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                pass
            finally:
                allure.attach(driver.get_screenshot_as_png(),name="account setting change password ",attachment_type=allure.attachment_type.PNG)
    elif "Yes".lower() != main_func_account_setting_change_password[-1].strip().lower():
        updatecomponentstatus(Title, "Change Password -> {oldpassword}", "SKIPPED", f"You have selected No for execute",excelpath)
        updatehighmodulestatus(Title, status="SKIPPED", comments=f"You have selected No for execute", path=excelpath)

def change_password(driver,currentPassword,newpassword,confirmpassword):
    with allure.step("change_password"):
        try:
            time.sleep(2)
            enter_Current_Password_to_text_box(driver, currentPassword)
            enter_New_Password_to_text_box(driver, newpassword)
            enter_Confirm_New_Password_to_text_box(driver, confirmpassword)
            time.sleep(3)
            allure.attach(driver.get_screenshot_as_png(), name="change password",attachment_type=allure.attachment_type.PNG)
            update_password_flag = click_on_update_password_btn(driver)
            allure.attach(driver.get_screenshot_as_png(), name="change password",attachment_type=allure.attachment_type.PNG)
            return update_password_flag
        except Exception as e:
            pass

def enter_Current_Password_to_text_box(driver,currentPassword):
   inputtext(driver ,change_password_account_settings.current_password_text_field ,currentPassword)

def enter_New_Password_to_text_box(driver ,newpassword):
   inputtext(driver,change_password_account_settings.new_password_txt_field,newpassword)

def enter_Confirm_New_Password_to_text_box(driver,confirmpassword):
    inputtext(driver,change_password_account_settings.confirm_new_password_txt_field,confirmpassword)

def click_on_update_password_btn(driver):
    update_btn_is_enabled_flag = verify_update_btn_is_enabled(driver)
    if update_btn_is_enabled_flag == True:
        clickec(driver,change_password_account_settings.update_password_btn)
        return True
    elif update_btn_is_enabled_flag == False:
         return False

def verify_update_btn_is_enabled(driver):
    try:
        update_btn_element = driver.find_element(*change_password_account_settings.update_password_btn[:2])
        if update_btn_element.is_enabled():
            return True
        else:
            return False
    except Exception as e:
        return False
        pass

