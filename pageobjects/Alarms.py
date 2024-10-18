import pandas as pd
from locators.locators import alarms, Login_Logout
from module_controllers.module_controllers import alarms_module_controllers
from pageobjects.group_reporter import selecting_date_or_hours_for_group_reporter, \
    click_on_group_reporter_duration_selection_dropdown, navigate_to_date_grp, click_load_more_grp
from utils.library import *

def main_func_alarms(driver,excelpath,downloadpath):
    with allure.step("Main func Alarms"):
        Title = "Alarms"
        try:
            alarms_runvalue = alarms_module_controllers()
            if "Yes".lower() == alarms_runvalue[-1].strip().lower():
                click_on_side_bar_alarm_icon(driver)
                selecting_date_or_hours_for_alarms(driver, Title, excelpath)
                click_on_load_more_until_invisble(driver)
                verify_the_No_failed_alarms_found(driver, Title, excelpath, downloadpath)
            elif "Yes".lower() != alarms_runvalue[-1].strip().lower():
                updatecomponentstatus(Title, "Not to execute", "SKIPPED", "You have selected No for execute", excelpath)
                pass
        except Exception as e:
            pass
        finally:
            try:
                update_module_status_based_on_reading_component_status(modules={"Alarms":"FAILED"},excelpath=excelpath)
            except Exception as e:
                pass
            finally:
                click(driver=driver, locators=Login_Logout.dashboard_id)

def click_on_side_bar_alarm_icon(driver):
    clickec(driver,alarms.alarm_icon)

def selecting_date_or_hours_for_alarms(driver,Title,excelpath):
    with allure.step("Selecting date or hours for Alarms"):
        yes_flag = False
        selected_flag = False
        selected_value = None
        enable_of_element_untill_loaded(driver,alarms.custom_query_btn[:2],1,120)
        try:
            Page_up(driver)
            df = pd.read_excel(config.test_data_path, sheet_name='date_time')
            # Loop through each row in the DataFrame
            for index, row in df.iterrows():
                select_hours = row['Select_hours']
                execute_flag = row['Execute']
                if isinstance(execute_flag, str) and execute_flag.lower() == 'yes':
                    yes_flag = True
                    if select_hours.lower() == 'custom date':
                        # Handle custom date range
                        start_date = row['Start Date']
                        end_date = row['End Date']

                        # Click on the button to open the date picker
                        click(driver, alarms.custom_query_btn)

                        # code to select custom date range
                        navigate_to_date_grp(driver, start_date, end_date)
                        clickec(driver, alarms.datetime_apply_btn)
                        updatecomponentstatus(Title=Title, componentname=f"{select_hours}=={start_date}/{end_date}", status="PASSED",comments="Successfully Selected",path=excelpath)
                        selected_flag = True
                        selected_value = f"{select_hours}=={start_date}/{end_date}"
                    else:
                        click_on_alarms_duration_selection_dropdown(driver)
                        option_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((alarms.option_xpath_date_time[0],alarms.option_xpath_date_time[1].format(str(select_hours).lower()))))
                        option_element.click()
                        updatecomponentstatus(Title=Title, componentname=f"{select_hours}", status="PASSED",comments="Successfully Selected",path=excelpath)
                        selected_flag = True
                        selected_value = f"{select_hours}"
            if yes_flag == False:
                updatecomponentstatus(Title=Title, componentname=f"{selected_value}", status="FAILED",comments=f"Select the anyone option in date/time by giving the 'Yes' in '{config.test_data_path}' sheet:-'date_time'")
            elif yes_flag == True and selected_flag == False:
                updatecomponentstatus(Title=Title, componentname=f"{selected_value}", status="FAILED",comments=f"Failed to select",path=excelpath)
            allure.attach(driver.get_screenshot_as_png(), name=f"Selecting date or hours for group reporter screenshot",attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            if yes_flag == True and selected_flag == False:
                updatecomponentstatus(Title=Title, componentname=f"{selected_value}", status="FAILED", comments=f"Failed to select",path=excelpath)
            allure.attach(driver.get_screenshot_as_png(), name=f"Selecting date or hours for group reporter screenshot",attachment_type=allure.attachment_type.PNG)
            raise e

def click_on_alarms_duration_selection_dropdown(driver):
    clickec(driver,alarms.Alarms_Selection_drop_down_btn)

def click_on_Close_btn(driver):
    clickec(driver,alarms.Close_btn)

def click_on_Export_All_btn(driver):
    clickec(driver,alarms.Export_All_btn)

def verify_the_No_failed_alarms_found(driver,Title,excelpath,downloadpath):
    with allure.step("Verify the No failed alarms found"):
        allure.attach(driver.get_screenshot_as_png(), name=f"Verify the No failed alarms found.",attachment_type=allure.attachment_type.PNG)
        if not WebDriverWait(driver,20).until(EC.invisibility_of_element(alarms.No_failed_alarms_found_text[:2])):
            updatecomponentstatus(Title=Title, componentname=f"No failed alarms found.", status="PASSED", comments=f"No failed alarms found.",path=excelpath)
            allure.attach(driver.get_screenshot_as_png(), name=f"No failed alarms found.",attachment_type=allure.attachment_type.PNG)
        elif WebDriverWait(driver,20).until(EC.invisibility_of_element(alarms.No_failed_alarms_found_text[:2])):
            updatecomponentstatus(Title=Title, componentname=f"Failed alarms found.", status="FAILED",comments=f"Failed alarms found.", path=excelpath)
            allure.attach(driver.get_screenshot_as_png(), name=f"Failed alarms found.",attachment_type=allure.attachment_type.PNG)
            downloadpath_alarms = specifying_download_path(driver,downloadpath,"Alarms")
            click_on_Export_All_btn(driver)
            time.sleep(30)
            change_the_download_path(driver,downloadpath)
            not_empty_file_flag , empty_csv_files = check_dir_where_all_read_csv_file_contains_data(downloadpath_alarms)
            if not_empty_file_flag == True:
                updatecomponentstatus(Title=Title, componentname=f"Csv files", status="PASSED",comments=f"Failed alarms found and csv contains data.", path=excelpath)
            elif not_empty_file_flag == False:
                updatecomponentstatus(Title=Title, componentname=f"Csv files --> {empty_csv_files}", status="FAILED",comments=f"Failed alarms found and csv not contains data.", path=excelpath)
            elif not_empty_file_flag == None:
                updatecomponentstatus(Title=Title, componentname=f"Csv files --> {empty_csv_files}", status="FAILED",comments=f"Failed alarms found and csv is not downloaded in the path. Please check in the particular alarms download path.", path=excelpath)

def click_on_load_more_until_invisble(driver):
    with allure.step("Click on load more until invisble"):
        allure.attach(driver.get_screenshot_as_png(), name=f"Verify the No failed alarms found.",attachment_type=allure.attachment_type.PNG)
        while True:
            click_load_more_alarms(driver, alarms.load_more_button_xpath,5)
            try:
                WebDriverWait(driver,5).until(EC.invisibility_of_element_located(alarms.load_more_button_xpath[:2]))
                break
            except Exception as e:
                print(f"{e}")
                pass

def click_load_more_alarms(driver,load_more_button_xpath,time):
    for i in range(0,2):
        try:
            try:
                while WebDriverWait(driver,10).until(EC.visibility_of_element_located(load_more_button_xpath[:2])):
                    try:
                        enable_of_element_untill_loaded(driver,load_more_button_xpath[:2],1)
                        load_more_button = WebDriverWait(driver, time).until(EC.visibility_of_element_located(load_more_button_xpath[:2]))
                        load_more_button.click()
                    except Exception as e:
                        break
            except Exception as e:
                pass
            try:
                while WebDriverWait(driver, 10).until(EC.presence_of_element_located(load_more_button_xpath[:2])):
                    try:
                        enable_of_element_untill_loaded(driver, load_more_button_xpath[:2], 1)
                        load_more_button = WebDriverWait(driver, time).until(EC.presence_of_element_located(load_more_button_xpath[:2]))
                        load_more_button.click()
                    except Exception as e:
                        break
            except Exception as e:
                pass
        except Exception as e:
            continue