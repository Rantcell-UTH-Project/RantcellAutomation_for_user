import time

from locators.locators import reset_password
from module_controllers.module_controllers import forgot_password_module_controllers
from pageobjects.login_logout import *
from utils.Mail_reciever import mail_reader_and_extract_specfic_word, delete_specfic_mail_using_subject
from utils.library import *

def main_func_reset_password(driver,emailId,url,oldpassword,excelpath):
    Title = "Forgot Password"
    forgot_password_ = forgot_password_module_controllers()
    if "Yes".lower() == forgot_password_[-1].strip().lower():
        random_length = random.randint(3, 4)
        random_alphabet = generate_random_alphabet(random_length)
        newpassword = oldpassword + random_alphabet
        codevalue = None
        re_new_password = newpassword
        try:
            df_MegronMail_account_details = return_df_of_encrypted_excel_file(config.MegronMail_account_details_excel_path, "Mail_account_details", password="Megron@1")
            app_password = df_MegronMail_account_details.loc[df_MegronMail_account_details['Mail ID'] == emailId, 'App password'].values
            if app_password.size > 0:
                try:
                    with allure.step("Reset Password"):
                        while True:
                            delete_specfic_mail_using_subject(emailId, app_password[-1],Search_for_emails_with_specific_criteria="Request")
                            launchbrowser(driver, url)
                            clickec(driver, Login_Logout.link_login)
                            click_on_forgot_password(driver)
                            enter_emailid_and_click_on_reset_btn_form(driver, emailId)
                            try:
                                time.sleep(10)
                                WebDriverWait(driver, 20).until(EC.visibility_of_element_located(reset_password.Code_here_text_box[:2]))
                            except Exception as e:
                                pass
                            code_list = mail_reader_and_extract_specfic_word(emailId, app_password[-1],Search_for_emails_with_specific_criteria="Request",logic_for_extract=lambda content: re.findall(r'RantCell account is (\d+)',content))
                            for code in code_list:
                                codevalue = code
                                break
                            enter_code_and_new_password(driver, codevalue, newpassword, re_new_password)
                            time.sleep(10)
                            if WebDriverWait(driver,15).until(EC.invisibility_of_element((By.XPATH,'//div[@class="alert alert-danger"]//b[contains(text(),"Incorrect Code or Code has been expired.")]'))):
                                break
                except Exception as e:
                    pass
                finally:
                    dashboard_flag = launchbrowser_login_and_verify_the_dashboard_loaded(driver, url, emailId, newpassword)
                    if dashboard_flag:
                        updatecomponentstatus(Title, componentname=f"Old + {random_alphabet}", status="PASSED",comments="Password is reseted using 'Forgot Password'", path=excelpath)
                        updatehighmodulestatus(Title, status="PASSED",comments="Password is reseted using 'Forgot Password'", path=excelpath)
                        return newpassword , True
                    else:
                        dashboard_flag = launchbrowser_login_and_verify_the_dashboard_loaded(driver,url,emailId, oldpassword)
                        if dashboard_flag:
                            updatecomponentstatus(Title, componentname=f"Old password", status="FAILED",comments="Password is not reseted using 'Forgot Password'", path=excelpath)
                            updatehighmodulestatus(Title, status="FAILED",comments="Password is not reseted using 'Forgot Password'", path=excelpath)
                            return oldpassword , False
            else:
                updatecomponentstatus(Title, componentname=f"Old password", status="FAILED",comments=f"Password is not reseted using 'Forgot Password' because app password of that emailid is not present in {config.MegronMail_account_details_excel_path}.", path=excelpath)
                updatehighmodulestatus(Title, status="FAILED", comments="Password is not reseted using 'Forgot Password'",path=excelpath)
                return oldpassword, False
        except Exception as e:
            updatecomponentstatus(Title, componentname=f"Old password", status="FAILED",comments=f"Password is not reseted using 'Forgot Password' because of error {e}",path=excelpath)
            updatehighmodulestatus(Title, status="FAILED", comments="Password is not reseted using 'Forgot Password'",path=excelpath)
            return oldpassword, False
    elif "Yes".lower() != forgot_password_[-1].strip().lower():
        updatehighmodulestatus(Title, status="SKIPPED", comments=f"You have selected No for execute", path=excelpath)
        return oldpassword, False

def enter_code_and_new_password(driver,codevalue,new_password,re_new_password):
    with allure.step("Enter code and new password form"):
        enter_Code_here_in_text_box(driver, codevalue)
        enter_new_password_in_text_box(driver, new_password)
        enter_re_new_password_in_text_box(driver, re_new_password)
        click_on_done_btn(driver)
        allure.attach(driver.get_screenshot_as_png(), name=f"Enter code and new password form",attachment_type=allure.attachment_type.PNG)

def enter_emailid_and_click_on_reset_btn_form(driver,emailId):
    with allure.step("Enter emailid and click on reset btn form"):
        enter_emailInput_in_text_box(driver, emailId)
        click_on_reset_password_btn(driver)
        allure.attach(driver.get_screenshot_as_png(), name=f"Enter emailid and click on reset btn form",attachment_type=allure.attachment_type.PNG)

def enter_emailInput_in_text_box(driver,value):
    inputtext(driver,reset_password.emailInput_xpath,value)

def click_on_reset_password_btn(driver):
    clickec(driver,reset_password.reset_password_btn)

def enter_Code_here_in_text_box(driver,value):
    inputtext(driver,reset_password.Code_here_text_box,value)

def enter_new_password_in_text_box(driver,value):
    inputtext(driver,reset_password.new_password_text_box,value)

def enter_re_new_password_in_text_box(driver,value):
    inputtext(driver,reset_password.Re_new_password_text_box,value)

def click_on_done_btn(driver):
    clickec(driver,reset_password.Done_btn)
