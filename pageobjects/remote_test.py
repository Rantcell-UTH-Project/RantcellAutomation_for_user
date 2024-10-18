import concurrent.futures
import queue
import re
import sys
import time
import allure
import pytest
from selenium.webdriver.common.by import By
from module_controllers.module_controllers import remote_module_controllers, module_controllers_for_testing_min
from pageobjects.Dashboard import *
from utils.library import *
from utils.readexcel import *
from locators.locators import *
import random
import string
def remote_test_(driver,campaigns_datas,campaigns_created,excelpath):
    device = None
    Title = "REMOTE TEST"
    remote_test_status = []
    remotetest_runvalue = remote_module_controllers()
    time_differnce = {}
    # runtest_runvalue = Testrun_mode(value="Remote Test")
    try:
        driver.execute_script(f"window.scrollTo({0}, {0});")
    except:
        pass
    remaining_test_minute_1st = remaining_test_minute_extraction(driver,statement="Pre Remote Test Remaining Test Minutes")
    if "Yes".lower() == remotetest_runvalue[-1].strip().lower():
        i = 0
        for campaigns_data in campaigns_datas:
            i +=1
            if i != 1:
                time.sleep(60)
            device, campaign, usercampaignsname, testgroup = campaigns_data
            timestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
            usercampaignsname = usercampaignsname +"_"+str(timestamp)
            remote_test_point, map_start_point, graph_start_point, export_start_point, load_start_point, PDF_Export_index_start_point, END_index = fetch_input_points()
            tests = fetch_components(campaign, remote_test_point, map_start_point)
            device , time_difference_value = remote_test_for_run_test(driver, device, campaign, campaigns_created, usercampaignsname, testgroup, tests,remote_test_status, excelpath,i)
            if time_difference_value != None:
                time_differnce[usercampaignsname] = time_difference_value
        if remote_test_status != []:
            updatehighmodulestatus(Title, "FAILED", "Remote test failed", excelpath)
        elif remote_test_status == []:
            updatehighmodulestatus(Title, "PASSED", "Remote test Succesfully executed", excelpath)
    elif "No".lower() == remotetest_runvalue[-1].strip().lower():
        statement = "You have selected Not to execute"
        with allure.step(statement):
            updatecomponentstatus(Title, "Not to execute", "SKIPPED", "You have selected No for execute",excelpath)
            updatehighmodulestatus(Title, "SKIPPED", "You have selected No for execute", excelpath)
            pass
    try:
        driver.execute_script(f"window.scrollTo({0}, {0});")
    except:
        pass
    remaining_test_minute_2nd = remaining_test_minute_extraction(driver,statement="Post Remote Test Remaining Test Minutes")
    check_the_remaining_test_minute_is_reduced(time1=remaining_test_minute_1st, time2=remaining_test_minute_2nd,time_differnce=time_differnce,excelpath=excelpath)
    return device

def check_the_remaining_test_minute_is_reduced(time1,time2,time_differnce,excelpath):
    Title = "TESTING MIN"
    # testing_min_runvalue = Testrun_mode(value="Testing min")
    testing_min_runvalue = module_controllers_for_testing_min()
    if "Yes".lower() == testing_min_runvalue[-1].strip().lower():
        time1 = convert_to_float(time1)
        time2 = convert_to_float(time2)
        minutes = 0
        remaining_seconds = 0
        total_seconds = 0
        for usercampaignsname , timeseconds in time_differnce.items():
            try:
                if isinstance(int(timeseconds),int):
                    total_seconds += timeseconds
            except Exception as e:
                continue
        minutes = int(total_seconds) // 60
        remaining_seconds = int(total_seconds) % 60
        # Round up if remaining seconds are 30 or more
        minutes1 = minutes
        if remaining_seconds >= 30:
            minutes1 += 1

        if isinstance(time1,float) and isinstance(time2,float):
            if int(time1) > int(time2):
                updatecomponentstatus(Title, f"{int(time1)} > {int(time2)}", "PASSED", f"Testing minute is reduced - {int(time1)} > {int(time2)}", excelpath)
            elif int(time1) >= int(time2):
                updatehighmodulestatus(Title, "FAILED", f"Testing minute is not reduced", excelpath)
                updatecomponentstatus(Title, f"{int(time1)} >= {int(time2)}", "FAILED", f"Testing minute is not reduced - {int(time1)} >= {int(time2)}", excelpath)
            else:
                updatehighmodulestatus(Title, "WARING", f"Testing minute condition is not satified", excelpath)
                updatecomponentstatus(Title, f"{int(time1) } and { int(time2)}", "WARING", f"Testing minute condition is not satified, i.e., {int(time1)} > {int(time2)} and {int(time1)} >= {int(time2)}", excelpath)

            differnce_in_remain_testing_time = int(time1) - int(time2)

            if int(differnce_in_remain_testing_time) == int(minutes) or int(differnce_in_remain_testing_time) == int(minutes1):
                updatehighmodulestatus(Title, "PASSED", f"Testing minute is reduced", excelpath)
                updatecomponentstatus(Title,f"{int(differnce_in_remain_testing_time)} == {int(minutes)} or {int(minutes1)}","PASSED",f"Testing minute is reduced - {int(differnce_in_remain_testing_time)} == {int(minutes)} or {int(minutes1)}",excelpath)
            elif int(differnce_in_remain_testing_time) != int(minutes) and int(differnce_in_remain_testing_time) != int( minutes1):
                updatehighmodulestatus(Title, "FAILED", f"Testing minute is not reduced", excelpath)
                updatecomponentstatus(Title,f"{int(differnce_in_remain_testing_time)} != {int(minutes)} and {int(minutes1)}","FAILED",f"Testing minute is not reduced - {int(differnce_in_remain_testing_time)} != {int(minutes)} and {int(minutes1)}",excelpath)

    elif "No".lower() == testing_min_runvalue[-1].strip().lower():
        statement = "You have selected Not to execute"
        with allure.step(statement):
            updatecomponentstatus(Title, "Not to execute", "SKIPPED", "You have selected No for execute",excelpath)
            updatehighmodulestatus(Title, "SKIPPED", "You have selected No for execute", excelpath)

def remote_test_for_run_test(driver,device,campaign,campaigns_created,usercampaignsname,testgroup,tests,remote_test_status,excelpath,i):
    Title = "REMOTE TEST"
    result_status = queue.Queue()
    test_complete = []
    test_Selected = []
    run_test_status_value = []
    test_Execution_status =[]
    campaigns_status = []
    device, time_difference_value = common(driver, device, campaign, campaigns_created, usercampaignsname, testgroup, tests, excelpath,Title,test_complete, test_Selected, result_status, run_test_status_value, test_Execution_status,campaigns_status,remote_test_status,"remote",i)
    return device ,time_difference_value

def common(driver,device,campaign,campaigns_created,usercampaignsname,testgroup,tests,excelpath,Title,test_complete,test_Selected,result_status,run_test_status_value,test_Execution_status,campaigns_status,remote_test_status,run,i):
    time_difference_value = None
    try:
        try:
            clickec(driver=driver,locators=remote_test.remotetest)
            time.sleep(3)
            if run == "remote":
                device = remotetest_for_android_pro(driver,Title,device,campaign,usercampaignsname,testgroup,tests,result_status,test_complete,test_Selected,run_test_status_value,excelpath,i)
            if test_complete == [True] and test_Selected == [True]:
                click(driver=driver, locators=Login_Logout.dashboard_id)
                test_name_in_table_view = (By.XPATH, f"//td[@id='loaderCamp']/following-sibling::td[normalize-space()='{usercampaignsname}']")
                if run == "remote":
                    verifying_of_test_execution_for_runtest(driver,Title,device,campaign,usercampaignsname,test_name_in_table_view,run_test_status_value,result_status,test_Execution_status,campaigns_status)
                    time_difference_value = extract_start_and_end_time_of_campaigns_generated(driver, usercampaignsname)
        except Exception as e:
            pass
        try:
            update_remote_test_result(result_status, excelpath)
        except Exception as e:
            pass
    finally:
        try:
            if ((test_complete == [] or test_complete == [False]) or (test_Selected == [] or test_Selected == [False])):
                # statement = "Test failed"
                # pytest.fail(statement)
                remote_test_status.append(False)
            if (test_Execution_status == [] or test_Execution_status == [False] or test_Execution_status == [None]) or (campaigns_status == [] or campaigns_status == [False]):
                # statement = "Test failed"
                # pytest.fail(statement)
                remote_test_status.append(False)
            campaigns_created.append(usercampaignsname)
        except Exception as e:
            pass
        return device , time_difference_value

def stop_pytest():
    sys.exit("Stopping pytest")

def extract_start_and_end_time_of_campaigns_generated(driver,usercampaignsname):
    test_execution = (By.XPATH,f"//td[@id='loaderCamp']/following-sibling::td[normalize-space()='{usercampaignsname}']/following-sibling::td[contains(.,'COMPLETED') or contains(.,'ABORTED')]")
    start_time_of_campaigns_generated_xpath = (By.XPATH,f"//td[@id='loaderCamp']/following-sibling::td[normalize-space()='{usercampaignsname}']/following-sibling::td[3]")
    end_time_of_campaigns_generated_xpath = (By.XPATH,f"//td[@id='loaderCamp']/following-sibling::td[normalize-space()='{usercampaignsname}']/following-sibling::td[4]")
    start_time = None
    end_time = None
    time_difference_value = None
    try:
        if WebDriverWait(driver,10).until(EC.presence_of_element_located(test_execution)):
           try:
               start_time_element = driver.find_element(*start_time_of_campaigns_generated_xpath)
               start_time = start_time_element.text
           except Exception as e:
                pass
           try:
               end_time_element = driver.find_element(*end_time_of_campaigns_generated_xpath)
               end_time = end_time_element.text
           except Exception as e:
                pass
    except Exception as e:
        pass
    try:
        if re.search(r"\d{2}:\d{2}:\d{2}", start_time) and re.search(r"\d{2}:\d{2}:\d{2}",end_time):
            time_a = re.search(r"\d{2}:\d{2}:\d{2}", start_time)
            time_b = re.search(r"\d{2}:\d{2}:\d{2}",end_time)
            time_difference_value = time_difference_in_seconds(start_time=time_a.group(), end_time=time_b.group())
    except Exception as e:
        pass
    finally:
        return time_difference_value

def verifying_of_test_execution_for_runtest(driver,Title,device,campaign,usercampaignsname,test_name_in_table_view,run_test_status_value,result_status,test_Execution_status,campaigns_status):
    try:
        with allure.step("Verification of the success or failed status from the application after clicking on start button in run test of remote test"):
            action = ActionChains(driver)
            try:
                table_view_refresh_element = driver.find_element(*remote_test.table_view_refresh[:2])
                action.move_to_element(table_view_refresh_element).perform()
            except Exception as e:
                pass
            execution_time = 0
            total_time = 331 #in min
            for i in range(0,total_time):
                try:
                    clickec(driver=driver,locators=remote_test.table_view_refresh)
                    WebDriverWait(driver,10).until(EC.visibility_of_element_located(test_name_in_table_view))
                    execution_time = total_time - i
                    break
                except Exception as e:
                    continue
            allure.attach(driver.get_screenshot_as_png(), name=f"verifying_of_test_execution",attachment_type=allure.attachment_type.PNG)
            try:
                Page_Down(driver=driver)
                test_name_siblings = WebDriverWait(driver,10).until(EC.visibility_of_element_located(test_name_in_table_view))
                campaigns_status.append(True)
                if run_test_status_value == [True]:
                    status_df = status(Title=Title,component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}",status="PASSED", comments=f"Success")
                    result_status.put(status_df)
                    waiting_for_complete_or_Aborted_status_for_runtest(Title,device,campaign,usercampaignsname,result_status,execution_time,driver=driver,test_Execution_status=test_Execution_status)
                elif run_test_status_value == [False]:
                    status_df = status(Title=Title,component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}",status="WARNING", comments=f"Remote Test config failed but campaign available")
                    result_status.put(status_df)
                    waiting_for_complete_or_Aborted_status_for_runtest(Title,device,campaign,usercampaignsname,result_status,execution_time,driver=driver,test_Execution_status=test_Execution_status)
            except Exception as e:
                campaigns_status.append(False)
                test_Execution_status.append(None)
                if run_test_status_value == [True]:
                    status_df = status(Title=Title,component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}",status="FAILED", comments=f"Remote Test config successful but campaign not available")
                    result_status.put(status_df)
                elif run_test_status_value == [False]:
                    status_df = status(Title=Title,component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}",status="FAILED", comments=f"	Remote Test config failed to run")
                    result_status.put(status_df)
                pass
    except Exception as e:
        pass

def waiting_for_complete_or_Aborted_status_for_runtest(Title,device,campaign,usercampaignsname,result_status,execution_time,driver,test_Execution_status):
    with allure.step("waiting for complete or Aborted status"):
        try:
            action = ActionChains(driver)
            for i in range(0, execution_time):
                try:
                    clickec(driver=driver, locators=remote_test.table_view_refresh)
                    test_execution = (By.XPATH,f"//td[@id='loaderCamp']/following-sibling::td[normalize-space()='{usercampaignsname}']/following-sibling::td[contains(.,'COMPLETED') or contains(.,'ABORTED')]")
                    WebDriverWait(driver,10).until(EC.visibility_of_element_located(test_execution))
                    break
                except Exception as e:
                    continue
            for i in range(0, 1):
                try:
                    clickec(driver=driver, locators=remote_test.table_view_refresh)
                    test_execution = (By.XPATH,f"//td[@id='loaderCamp']/following-sibling::td[normalize-space()='{usercampaignsname}']/following-sibling::td[contains(.,'COMPLETED') or contains(.,'ABORTED')]")
                    WebDriverWait(driver,10).until(EC.visibility_of_element_located(test_execution))
                    try:
                        test_execution_element = driver.find_element(*test_execution)
                        action.move_to_element(test_execution_element).perform()
                    except Exception as e:
                        pass
                    test_Execution_status.append(True)
                    status_df = status(Title=Title,component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}",status="PASSED", comments=f"Test Campaigns execution status is Completed/Aborted/Uploaded")
                    result_status.put(status_df)
                    break
                except Exception as e:
                    test_Execution_status.append(False)
                    status_df = status(Title=Title,component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}",status="FAILED", comments=f"Test Campaigns execution status is Executing")
                    result_status.put(status_df)
                    try:
                        test_executing = (By.XPATH,f"//td[@id='loaderCamp']/following-sibling::td[normalize-space()='{usercampaignsname}']/following-sibling::td[contains(.,'EXECUTING')]")
                        try:
                            test_executing_element = driver.find_element(*test_executing)
                            action.move_to_element(test_executing_element).perform()
                        except Exception as e:
                            pass
                        WebDriverWait(driver, 0.1).until(EC.invisibility_of_element_located(test_executing))
                    except Exception as e:
                        pass
            allure.attach(driver.get_screenshot_as_png(), name=f"waiting for complete or Aborted status",attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            pass

def Updating_automation_data_to_excel(worksheet,dataframe):
    try:
        # Find the last used row in the sheet
        last_row = worksheet.max_row
        # Append DataFrame data to the worksheet
        for index, row in dataframe.iterrows():
            worksheet.append(row.tolist())
    except Exception as e:
        pass

def update_automation_data(automation_data_dict,automation_data_execel_path,Sheet):
    try:
        dataframe_automation_data = []
        automation_data_df = "None"
        df_automation_data = pd.DataFrame(automation_data_dict)
        dataframe_automation_data.append(df_automation_data)
        if len(dataframe_automation_data) != 0:
            automation_data_df = pd.concat(dataframe_automation_data, ignore_index=True)
        workbook = openpyxl.load_workbook(automation_data_execel_path)
        worksheet_componentstatus = workbook[Sheet]
        if len(dataframe_automation_data) != 0:
            Updating_automation_data_to_excel(worksheet=worksheet_componentstatus, dataframe=automation_data_df)
        workbook.save(automation_data_execel_path)
        workbook.close()
    except Exception as e:
        pass

def update_remote_test_result(result_status,excelpath):
    try:
        dataframe_status = []
        combined_status_df = "None"
        while not result_status.empty():
            updatecomponentstatus2 = result_status.get()
            df_status = pd.DataFrame(updatecomponentstatus2)
            dataframe_status.append(df_status)
        if len(dataframe_status) != 0:
            combined_status_df = pd.concat(dataframe_status, ignore_index=True)
        workbook = openpyxl.load_workbook(excelpath)
        worksheet_componentstatus = workbook["COMPONENTSTATUS"]
        if len(dataframe_status) != 0:
            update_component_status_openpyxl(worksheet=worksheet_componentstatus, dataframe=combined_status_df)
        workbook.save(excelpath)
        workbook.close()
    except Exception as e:
        pass

def remotetest_for_android_pro(driver,Title,device,campaign,usercampaignsname,testgroup,tests,result_status,test_complete,test_Selected,run_test_status_value,excelpath,i):
    try:
        with allure.step(f"remotetest for android pro - {campaign}"):
            flag_test_group = []
            alert_text = None
            check_android_pro_is_active_in_remotetest(driver)
            verify_test_group_is_present(driver,Title,device,campaign,usercampaignsname,result_status,testgroup,flag_test_group)
            if flag_test_group == [True]:
                ##the below for loop line is temporary for testing###
                for j in range(1,5):
                    alert_text = None
                    if i == 1:
                        device_button_dropdown = click_on_test_group_button_to_open_dropdown(driver, testgroup)
                        click_on_the_check_devices(driver=driver,driver1=device_button_dropdown)
                        time.sleep(10)
                        try:
                            alert_text = alert_accept(driver=driver)

                        except Exception as e:
                            pass
                        if alert_text == None:
                            break

                        device_button_dropdown = click_on_test_group_button_to_open_dropdown(driver, testgroup)
                        time.sleep(5)


                # if i == 1:
                #     device_button_dropdown = click_on_test_group_button_to_open_dropdown(driver, testgroup)
                #     click_on_the_check_devices(driver=driver,driver1=device_button_dropdown)

                try:
                    alert_text = alert_accept(driver=driver)
                except Exception as e:
                    pass
                if alert_text !=None:
                    with allure.step(f"{alert_text}"):
                        status_df = status(Title=Title,component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}",status="FAILED",comments=f"{alert_text}")
                        result_status.put(status_df)
                elif alert_text == None:
                    with allure.step(f"no alert found, device is registered"):
                        status_df = status(Title=Title, component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}", status="PASSED", comments=f"no alert found, device is registered")
                        result_status.put(status_df)
                    if i == 1:
                        flag_status_value = []
                        device = check_device_status(driver,Title,device,campaign,usercampaignsname,flag_status_value,result_status)
                    device_button_dropdown = click_on_test_group_button_to_open_dropdown(driver, testgroup)
                    click_on_the_run_test(driver=driver,driver1=device_button_dropdown)
                    waiting_for_run_test_tab_for_loading(driver)
                    run_test_form(driver,Title,usercampaignsname,tests,test_complete,test_Selected,result_status,excelpath)
                    if test_complete == [True] and test_Selected == [True]:
                        statement = "Successfully entered test data for a particular type of test and clicked on the start button."
                        with allure.step(statement):
                            allure.attach(driver.get_screenshot_as_png(), name=f"{statement}",attachment_type=allure.attachment_type.PNG)
                            click_on_start_button_of_run_test(driver=driver)
                            status_df = status(Title=Title, component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}",status="PASSED", comments=statement)
                            result_status.put(status_df)
                            check_status_of_test(driver, Title, device, campaign, usercampaignsname,run_test_status_value,result_status)
                    elif (test_complete == [] or test_complete == [False]) and (test_Selected == [False] or test_Selected == []):
                        statement = "Test data was not entered successfully for a particular type of test,so clicked on the close button."
                        with allure.step(statement):
                            allure.attach(driver.get_screenshot_as_png(), name=f"{statement}",attachment_type=allure.attachment_type.PNG)
                            status_df = status(Title=Title, component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}",status="FAILED", comments=statement)
                            result_status.put(status_df)
                            click_on_close_button_of_run_test(driver)
                        time.sleep(0.1)
    except Exception as e:
        pass
    finally:
        return device

def update_device_name_for_test_data(driver,device):
    try:
        devices_element = driver.find_element(*remote_test.device_name)
        device = devices_element.get_attribute("innerText")
        return str(device).strip()
    except Exception as e:
        pass

def check_android_pro_is_active_in_remotetest(driver):
    try:
        with allure.step("checking android pro button is selected and is active in remotetest"):
            # Find the active and inactive elements based on the class
            inactive_element = driver.find_element(*remote_test.android_pro_is_inactive)
            # Check if the element is not active
            if inactive_element:
                # Click on the inactive element to make it active
                inactive_element.click()
            allure.attach(driver.get_screenshot_as_png(), name=f"android pro tab open",attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        pass

def verify_test_group_is_present(driver,Title,device,campaign,usercampaignsname,result_status,testgroup,flag_test_group):
    with allure.step("verifying test group is present"):
        try:
            WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH,f"//p[normalize-space()='{testgroup}']/ancestor::div[@class='deviceCtldiv']/following-sibling::div//div//button")))
            flag_test_group.append(True)
        except Exception as e:
            flag_test_group.append(False)
            with allure.step(f"Check the test group name is present in remote test as user input from test data"):
                status_df = status(Title=Title,component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}",status="FAILED", comments=f"Check the test group name is present in remote test as user input from test data")
                result_status.put(status_df)
            pass
        allure.attach(driver.get_screenshot_as_png(), name=f"verifying test group is present",attachment_type=allure.attachment_type.PNG)

def click_on_test_group_button_to_open_dropdown(driver,testgroup):
    try:
        with allure.step("click on the test group device button to open the dropdown"):
            device_button_dropdown_path =(By.XPATH,f"//p[normalize-space()='{testgroup}']/ancestor::div[@class='deviceCtldiv']/following-sibling::div//div//button","device_button_dropdown")
            device_button_dropdown = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,f"//p[normalize-space()='{testgroup}']/ancestor::div[@class='deviceCtldiv']/following-sibling::div//div//button")))
            element = driver.find_element(By.XPATH,f"//p[normalize-space()='{testgroup}']/ancestor::div[@class='deviceCtldiv']/following-sibling::div//div//button")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            clickec(driver=driver,locators=device_button_dropdown_path)
            allure.attach(driver.get_screenshot_as_png(), name=f"click on the test group device button to open the dropdown",attachment_type=allure.attachment_type.PNG)
            return device_button_dropdown
    except Exception as e:
        pass
def click_on_the_check_devices(driver,driver1):
    try:
        with allure.step("click on the check devices"):
            check_devices_element = driver1.find_element(*remote_test.check_devices)
            check_devices_element.click()
            with allure.step("Waiting for loading check device"):
                try:
                    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(remote_test.check_device_tab))
                except Exception as e:
                    pass
            allure.attach(driver.get_screenshot_as_png(), name=f"click on the check devices.",attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        pass
def wait_for_timer_to_reach_zero_in_check_device_popup(driver):
    try:
        with allure.step("waiting for the timer to reach zero in check device popup"):
            timer_element = driver.find_element(*remote_test.timer_xpath)
            # Extract the countdown attribute value
            countdown_value = timer_element.get_attribute("countdown")
            WebDriverWait(driver, int(countdown_value)+2).until(EC.visibility_of_element_located(remote_test.online_or_offline_status))
            allure.attach(driver.get_screenshot_as_png(), name=f"Timer reached 0 seconds.",attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        pass
def wait_for_status_of_run_test_popup(driver):
    try:
        with allure.step("waiting for the status of run test popup"):
            countdown_value = 60
            WebDriverWait(driver, int(countdown_value)+2).until(EC.visibility_of_element_located((remote_test.run_test_start_status[:2])))
            allure.attach(driver.get_screenshot_as_png(), name=f"waiting for the status of run test popup.",attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        print(f"Timer did not reach 0 within the specified time. {e}")
def check_status_of_test(driver,Title,device,campaign,usercampaignsname,run_test_status_value,result_status):
    try:
        with allure.step("checking the status of test"):
            try:
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located(remote_test.run_test_start_status_popup))
            except Exception as e:
                pass
            wait_for_status_of_run_test_popup(driver)
            status_of_runtests = driver.find_elements(*remote_test.run_test_start_status[:2])
            for status_of_runtest in status_of_runtests:
                status_value = status_of_runtest.text
                if status_value.lower().replace(" ", "") == "Failed".lower():
                    with allure.step("Test execution didnt started may be due to device is offline"):
                        run_test_status_value.append(False)
                        allure.attach(driver.get_screenshot_as_png(), name=f"offline",attachment_type=allure.attachment_type.PNG)
                        status_df = status(Title=Title, component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}",status="WARING", comments="Test execution didnt started may be due to device is offline")
                        result_status.put(status_df)
                elif status_value.lower().replace(" ", "") == "Success".lower():
                    with allure.step("Test execution didnt started may be due to device is offline"):
                        run_test_status_value.append(True)
                        allure.attach(driver.get_screenshot_as_png(), name=f"offline",attachment_type=allure.attachment_type.PNG)
                        status_df = status(Title=Title, component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}",status="PASSED",comments="Test execution started and device is online")
                        result_status.put(status_df)
            clickec(driver=driver,locators=remote_test.run_test_start_statusclose_btn)
    except Exception as e:
        pass
def check_device_status(driver,Title,device,campaign,usercampaignsname,flag_status_value,result_status):
    try:
        with allure.step("check whether the device is online/offline "):
            wait_for_timer_to_reach_zero_in_check_device_popup(driver)
            device = update_device_name_for_test_data(driver, device)
            status_of_devices = driver.find_elements(*remote_test.status_of_devices_Offline)
            offline_flag = False
            for status_of_device in status_of_devices:
                offline_flag = True
                status_value = status_of_device.text
                if status_value.lower().replace(" ", "") == "Offline".lower():
                    with allure.step("device is offline"):
                        a = "device is offline"
                        flag_status_value.append(False)
                        allure.attach(driver.get_screenshot_as_png(), name=f"offline",attachment_type=allure.attachment_type.PNG)
                        status_df = status(Title=Title, component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}", status="FAILED", comments="device is offline")
                        result_status.put(status_df)
            if offline_flag == False:
                status_of_devices = driver.find_elements(*remote_test.status_of_devices_Online)
                for status_of_device in status_of_devices:
                    status_value = status_of_device.text
                    if status_value.lower().replace(" ","") == 'Online'.lower():
                        with allure.step("device is Online"):
                            flag_status_value.append(True)
                            status_df = status(Title=Title, component=f"device:- {device},campaign:- {campaign},usercampaignsname:-{usercampaignsname}", status="PASSED", comments=f"device is Online")
                            result_status.put(status_df)
                            allure.attach(driver.get_screenshot_as_png(), name=f"online",attachment_type=allure.attachment_type.PNG)
                            break
        click_on_close_button_of_check_device(driver)
    except Exception as e:
        try:
            click_on_close_button_of_check_device(driver)
        except Exception as e:
            pass
        pass
    finally:
        return device
def click_on_the_run_test(driver,driver1):
    try:
        with allure.step("click on run test option from the dropdown"):
            Run_Test_element = driver1.find_element(*remote_test.Run_Test)
            Run_Test_element.click()
            allure.attach(driver.get_screenshot_as_png(), name=f"click on  run test option from the dropdown.",attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        pass
def click_on_close_button_of_check_device(driver):
    try:
        with allure.step("click on close button of check device"):
            clickec(driver=driver,locators=remote_test.closebtn_ofcheckdevice)
            allure.attach(driver.get_screenshot_as_png(), name=f"click on close button of check device.",attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        pass
def click_on_close_button_of_run_test(driver):
    try:
        with allure.step("click on the close button of run test"):
            click(driver=driver,locators=remote_test.closebtn_ofrun_test)
            time.sleep(0.1)
            allure.attach(driver.get_screenshot_as_png(), name=f"click on the close button of run test.",attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        pass

def click_on_start_button_of_run_test(driver):
    try:
        with allure.step("click on start button of run test"):
            start_button = driver.find_element(*remote_test.startbtn_ofrun_test[:2])
            if start_button.is_enabled():
                click(driver=driver,locators=remote_test.startbtn_ofrun_test)
                time.sleep(0.1)
            allure.attach(driver.get_screenshot_as_png(), name=f"click on start button of run test.",attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        pass

def waiting_for_run_test_tab_for_loading(driver):
    try:
        with allure.step("waiting for run test tab for loading"):
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(remote_test.run_test_tab))
            allure.attach(driver.get_screenshot_as_png(), name=f"waiting for run test tab for loading.",attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        pass

def run_test_form(driver,Title,usercampaignsname,tests,test_complete,test_Selected,result_status,excelpath):
    try:
        with allure.step("run test form"):
            inputtext(driver=driver,locators=remote_test.test_name,value=f"{usercampaignsname}")
            inputtext(driver=driver,locators=remote_test.iteration_textbox,value="1")
            inputtext(driver=driver, locators=remote_test.delays_bw_tests, value="5")
            allure.attach(driver.get_screenshot_as_png(), name=f"run_test_form.",attachment_type=allure.attachment_type.PNG)
            try:
                df_remote_test = pd.read_excel(config.test_data_path,sheet_name="Remote_Test")
            except Exception as e:
                with allure.step(f"Check {config.test_data_path}"):
                    print(f"Check {config.test_data_path}")
                    assert False
            txt = []
            if tests.__len__() == 0:
                statement = f"{Title}  --  Nothing is marked 'Yes' in {str(config.test_data_path)}"
                with allure.step(f"Nothing is marked 'Yes' in {str(config.test_data_path)} for '{Title}'"):
                    status_df = status(Title=Title, component="[]", status="FAILED",comments=f"Nothing marked in {str(config.test_data_path)}")
                    result_status.put(status_df)
                    e = Exception
                    raise e
            else:
                test_complete.append(True)
                for test in tests:
                    try:
                        if test.lower().replace(" ", "") == "tcp-iperftest".lower().replace(" ", "") or test.lower().replace(" ", "") == "udp-iperftest".lower().replace(" ", ""):
                             testmodified = test.replace("TCP-", "").replace("UDP-", "")
                             # remote_test_datas = df_remote_test[df_remote_test['Test_Type'].str.contains(testmodified,case=False, na=False)].groupby('Test_Type').apply(lambda x: x[['Parameter', 'Value']].to_dict(orient='records')).tolist()
                             remote_test_datas = df_remote_test[df_remote_test['Test_Type'].str.contains(testmodified, case=False, na=False)].groupby('Test_Type').apply(lambda x: x[['Parameter', 'Value']].to_dict(orient='records')).tolist()
                        else:
                            remote_test_datas = df_remote_test[df_remote_test['Test_Type'].str.contains(test, case=False, na=False)].groupby('Test_Type').apply(lambda x: x[['Parameter', 'Value']].to_dict(orient='records')).tolist()
                        remote_test_dict = {str(record['Parameter']).strip(): record['Value'] for record in remote_test_datas[0]}
                        print(remote_test_dict)
                        test = test.strip().lower().replace(" ", "")
                        test_functions = {
                            "pingtest": ping_test,
                            "calltest": call_test,
                            "smstest": sms_test,
                            "speed_test": speed_test,
                            "httpspeedtest": http_speed_test,
                            "webtest": web_test,
                            "streamtest": stream_test,
                            "tcp-iperftest": iperf_test,
                            "udp-iperftest": iperf_test
                        }
                        test_name = test.lower().replace(" ", "")
                        for name, func in test_functions.items():
                            if re.fullmatch(name, test_name):
                                if name in ["webtest", "streamtest"]:
                                    func(driver=driver, test_data=remote_test_dict, type_of_test="runtest")
                                elif name in ["tcp-iperftest", "udp-iperftest"]:
                                    func(driver=driver, Title=Title, test_data=remote_test_dict,result_status=result_status, type_of_test="runtest",test_name=test_name)
                                else:
                                    func(driver=driver, Title=Title, test_data=remote_test_dict,result_status=result_status, type_of_test="runtest")
                                break
                    except Exception as e:
                        try:
                            test_complete.remove(True)
                        except Exception as e:
                            pass
                        test_complete.append(False)
                        test_complete = list(set(test_complete))
                        continue
                test_Selected.append(True)
                for test in tests:
                    try:
                        test = test.strip().lower().replace(" ", "")
                        test_checkboxes = {
                            "pingtest": remote_test.ping_test_checkbox,
                            "calltest": remote_test.call_test_checkbox,
                            "smstest": remote_test.sms_test_checkbox,
                            "speed_test": remote_test.speed_test_checkbox,
                            "httpspeedtest": remote_test.http_speed_test_checkbox,
                            "webtest": remote_test.webtest_checkbox,
                            "streamtest": remote_test.stream_checkbox,
                            "tcp-iperftest": remote_test.iperf_testcheckbox,
                            "udp-iperftest": remote_test.iperf_testcheckbox
                        }
                        test_name = test.lower().replace(" ", "")
                        for name, checkbox in test_checkboxes.items():
                            if re.fullmatch(name, test_name):
                                typeoftest_is_selected(driver, checkbox)
                                break
                    except Exception as e:
                        try:
                            test_Selected.remove(True)
                        except Exception as e:
                            pass
                        test_Selected.append(False)
                        test_Selected = list(set(test_complete))
                        continue
    except Exception as e:
        pass

def typeoftest_is_selected(driver,locator):
    checkbox_input = driver.find_element(*locator[:2])
    try:
        if checkbox_input.is_selected():
            pass
        elif not checkbox_input.is_selected():
            raise
    except Exception as e:
        if not checkbox_input.is_selected():
            raise e

def ping_test(driver,Title,test_data,result_status,type_of_test):
    try:
        with allure.step("Ping test"):
            if type_of_test == "runtest":
                clickec(driver=driver, locators=remote_test.ping_test_checkbox)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(remote_test.ping_test_form))
            Ping_test = None
            ping_test_form_fields_names = driver.find_elements(*remote_test.ping_test_form)
            Ping_test = True
            for ping_test_form_fields_name in ping_test_form_fields_names:
                try:
                    field_name = str(ping_test_form_fields_name.text).lower().replace(" ","")
                    if re.search("Host".lower(),field_name,re.IGNORECASE):
                        try:
                            ping_data = test_data["Host"]
                        except Exception as e:
                            statement = f"Check parameter is present in remote test sheet test data excel"
                            with allure.step(statement):
                                status_df = status(Title=Title, component=f"Ping_test:-'Host'", status="FAILED", comments=statement)
                                result_status.put(status_df)
                                raise e
                        inputtext(driver=ping_test_form_fields_name,locators=remote_test.host_textbox,value=ping_data)
                    elif re.search("Packet Size".lower().replace(" ",""),field_name,re.IGNORECASE):
                        try:
                            ping_data = test_data["Packet Size"]
                        except Exception as e:
                            statement = f"Check parameter is present in remote_test sheet test data excel"
                            with allure.step(statement):
                                status_df = status(Title=Title, component=f"Ping_test:-'Packet Size'", status="FAILED",comments=statement)
                                result_status.put(status_df)
                                raise e
                        if is_numeric(ping_data):
                            if 32 <= int(ping_data) <= 65500:
                                inputtext(driver=ping_test_form_fields_name,locators=remote_test.packetsize_textbox,value=ping_data)
                            else:
                                statement = f"Check the value given within the range"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Ping_test:-'Packet Size'", status="FAILED",comments=statement)
                                    result_status.put(status_df)
                                    e = Exception
                                    raise e
                        else:
                            statement = f"Check the entered value is numeric"
                            with allure.step(statement):
                                status_df = status(Title=Title, component=f"Ping_test:-'Packet Size'", status="FAILED",comments=statement)
                                result_status.put(status_df)
                                e = Exception
                                raise e
                except Exception as e:
                    Ping_test = False
                    continue
            allure.attach(driver.get_screenshot_as_png(), name=f"Ping_test.",attachment_type=allure.attachment_type.PNG)
            if Ping_test == True:
                okbtn = driver.find_element(*remote_test.pingtest_okbtn[:2])
                if okbtn.is_enabled():
                    clickec(driver=driver,locators=remote_test.pingtest_okbtn)
                elif not okbtn.is_enabled():
                    clickec(driver=driver, locators=remote_test.pingtest_closebtn)
                    e = Exception
                    raise e
            elif Ping_test == False or Ping_test == None:
                clickec(driver=driver, locators=remote_test.pingtest_closebtn)
                e = Exception
                raise e
    except Exception as e:
        raise e

def call_test(driver,Title,test_data,result_status,type_of_test):
    try:
        with allure.step("Call test"):
            if type_of_test == "runtest":
                clickec(driver=driver, locators=remote_test.call_test_checkbox)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(remote_test.call_test_form))
            Call_test = None
            call_test_form_fields_names = driver.find_elements(*remote_test.call_test_form)
            Call_test = True
            for call_test_form_fields_name in call_test_form_fields_names:
                try:
                    field_name = str(call_test_form_fields_name.text).lower().replace(" ","")
                    if re.search("B Party Phone Number".lower().replace(" ",""),field_name,re.IGNORECASE):
                        try:
                            call_data = test_data["B Party Phone Number"]
                        except Exception as e:
                            statement = f"Check parameter is present in remote test sheet test data excel"
                            with allure.step(statement):
                                status_df = status(Title=Title, component=f"Call_test:-'B Party Phone Number'", status="FAILED",comments=statement)
                                result_status.put(status_df)
                                raise e
                        inputtext(driver=call_test_form_fields_name,locators=remote_test.Call_B_Party_Phone_Number_textbox,value=call_data)
                    elif re.search("Call Duration".lower().replace(" ",""),field_name,re.IGNORECASE):
                        try:
                            call_data = test_data["Call Duration"]
                        except Exception as e:
                            statement = f"Check parameter is present in remote_test sheet test data excel"
                            with allure.step(statement):
                                status_df = status(Title=Title, component=f"Call_test:-'Call Duration'", status="FAILED",comments=statement)
                                result_status.put(status_df)
                                raise e
                        if is_numeric(call_data):
                            if 1 <= int(call_data) <= 5400:
                                inputtext(driver=call_test_form_fields_name, locators=remote_test.Call_Duration_textbox,value=call_data)
                            else:
                                statement = f"Check the value given within the range"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Call_test:-'Call Duration'", status="FAILED",comments=statement)
                                    result_status.put(status_df)
                                    e = Exception
                                    raise e
                        else:
                            statement = f"Check the entered value is numeric"
                            with allure.step(statement):
                                status_df = status(Title=Title, component=f"Call_test:-'Call Duration'", status="FAILED",comments=statement)
                                result_status.put(status_df)
                                e = Exception
                                raise e
                except Exception as e:
                    Call_test = False
                    continue
            allure.attach(driver.get_screenshot_as_png(), name=f"Call_test.",attachment_type=allure.attachment_type.PNG)
            if Call_test == True:
                okbtn = driver.find_element(*remote_test.calltest_okbtn[:2])
                if okbtn.is_enabled():
                    clickec(driver=driver,locators=remote_test.calltest_okbtn)
                elif not okbtn.is_enabled():
                    clickec(driver=driver, locators=remote_test.calltest_closebtn)
                    e = Exception
                    raise e
            elif Call_test == False or Call_test == None:
                clickec(driver=driver, locators=remote_test.calltest_closebtn)
                e = Exception
                raise e
    except Exception as e:
        raise e
def sms_test(driver,Title,test_data,result_status,type_of_test):
    try:
        with allure.step("Sms test"):
            if type_of_test == "runtest":
                clickec(driver=driver, locators=remote_test.sms_test_checkbox)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(remote_test.sms_test_form))
            Sms_test = None
            sms_test_form_fields_names = driver.find_elements(*remote_test.sms_test_form)
            Sms_test = True
            for sms_test_form_fields_name in sms_test_form_fields_names:
                try:
                    field_name = str(sms_test_form_fields_name.text).lower().replace(" ","")
                    if re.search("B Party Phone Number".lower().replace(" ",""),field_name,re.IGNORECASE):
                        try:
                            sms_data = test_data["B Party Phone Number"]
                        except Exception as e:
                            statement = f"Check parameter is present in remote test sheet test data excel"
                            with allure.step(statement):
                                status_df = status(Title=Title, component=f"Sms_test:-'B Party Phone Number'", status="FAILED",comments=statement)
                                result_status.put(status_df)
                                raise e
                        inputtext(driver=sms_test_form_fields_name,locators=remote_test.sms_B_Party_Phone_Number_textbox,value=sms_data)
                    elif re.search("Wait Duration".lower().replace(" ",""),field_name,re.IGNORECASE):
                        try:
                            sms_data = test_data["Wait Duration"]
                        except Exception as e:
                            statement = f"Check parameter is present in remote test sheet test data excel"
                            with allure.step(statement):
                                status_df = status(Title=Title, component=f"Sms_test:-'Wait Duration'", status="FAILED",comments=statement)
                                result_status.put(status_df)
                                raise e
                        if is_numeric(sms_data):
                            if 30 <= int(sms_data) <= 180:
                                inputtext(driver=sms_test_form_fields_name,locators=remote_test.sms_Wait_Duration_textbox,value=sms_data)
                            else:
                                statement = f"Check the value given within the range"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Sms_test:-'Wait Duration'", status="FAILED",comments=statement)
                                    result_status.put(status_df)
                                    e = Exception
                                    raise e
                        else:
                            statement = f"Check the entered value is numeric"
                            with allure.step(statement):
                                status_df = status(Title=Title, component=f"Sms_test:-'Wait Duration'", status="FAILED",comments=statement)
                                result_status.put(status_df)
                                e = Exception
                                raise e
                except Exception as e:
                    Sms_test = False
                    continue
            allure.attach(driver.get_screenshot_as_png(), name=f"Sms_test.",attachment_type=allure.attachment_type.PNG)
            if Sms_test == True:
                okbtn = driver.find_element(*remote_test.smstest_okbtn[:2])
                if okbtn.is_enabled():
                    clickec(driver=driver,locators=remote_test.smstest_okbtn)
                elif not okbtn.is_enabled():
                    clickec(driver=driver, locators=remote_test.smstest_closebtn)
                    e = Exception
                    raise e
            elif Sms_test == False or Sms_test == None:
                clickec(driver=driver, locators=remote_test.smstest_closebtn)
                e = Exception
                raise e
    except Exception as e:
        raise e
def speed_test(driver,Title,test_data,result_status,type_of_test):
    try:
        with allure.step("speed test"):
            if type_of_test == "runtest":
                clickec(driver=driver, locators=remote_test.speed_test_checkbox)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(remote_test.speed_test_form))
            Speed_test = None
            speed_test_form_fields_names = driver.find_elements(*remote_test.speed_test_form)
            Speed_test = True
            try:
                Use_Default_Server_speed_data = test_data["Use Default Server"]
            except Exception as e:
                statement = f"Check parameter is present in remote test sheet test data excel"
                with allure.step(statement):
                    status_df = status(Title=Title, component=f"Speed_test:-'Use Default Server'", status="FAILED", comments=statement)
                    result_status.put(status_df)
            try:
                Enable_Upload_Test_speed_data = test_data["Enable Upload Test"]
            except Exception as e:
                statement = f"Check parameter is present in remote test sheet test data excel"
                with allure.step(statement):
                    status_df = status(Title=Title, component=f"Speed_test:-'Enable Upload Test'", status="FAILED",comments=statement)
                    result_status.put(status_df)
            try:
                Enable_FTP_Stop_Timer_speed_data = test_data["Enable FTP Stop Timer"]
            except Exception as e:
                statement = f"Check parameter is present in remote test sheet test data excel"
                with allure.step(statement):
                    status_df = status(Title=Title, component=f"Speed_test:-'Enable FTP Stop Timer'", status="FAILED",comments=statement)
                    result_status.put(status_df)
            for speed_test_form_fields_name in speed_test_form_fields_names:
                try:
                    field_name = str(speed_test_form_fields_name.text).lower().replace(" ","")
                    if re.search("Parallel Connections".lower().replace(" ",""),field_name,re.IGNORECASE):
                        pass
                    elif re.search("Use Default Server".lower().replace(" ",""),field_name,re.IGNORECASE):
                        checkbox_input = speed_test_form_fields_name.find_element(*remote_test.speed_Use_Default_Server_checkbox[:2])
                        if (Use_Default_Server_speed_data == "No" and checkbox_input.is_selected()) or (Use_Default_Server_speed_data == "Yes" and not checkbox_input.is_selected()):
                            clickec(driver=speed_test_form_fields_name,locators=remote_test.speed_Use_Default_Server_checkbox)

                    elif re.search("Select Download Test File Size".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Use_Default_Server_speed_data == "Yes" and Enable_FTP_Stop_Timer_speed_data == "No":
                            try:
                                speed_data = test_data["Select Download Test File Size"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote_test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Speed_test:-'Select Download Test File Size'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    raise e
                            Select_Download_Test_File_Size_option = (By.XPATH,f"//select[@id='downloadfilesize']//option[normalize-space()={speed_data}]","Select_Download_Test_File_Size_option")
                            clickec(driver=driver,locators=remote_test.Select_Download_Test_File_Size_dropdown)
                            clickec(driver=driver,locators=Select_Download_Test_File_Size_option)
                    elif re.search("FTP Server".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Use_Default_Server_speed_data == "No":
                            try:
                                speed_data = test_data["FTP Server"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote_test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Speed_test:-'FTP Server'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    raise e
                            inputtext(driver=speed_test_form_fields_name,locators=remote_test.FTP_Server_textbox,value=speed_data)
                    elif re.search("UserName".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Use_Default_Server_speed_data == "No":
                            try:
                                speed_data = test_data["UserName"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Speed_test:-'UserName'", status="FAILED",comments=statement)
                                    result_status.put(status_df)
                                    raise e
                            inputtext(driver=speed_test_form_fields_name,locators=remote_test.UserName_textbox,value=speed_data)
                    elif re.search("Password".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Use_Default_Server_speed_data == "No":
                            try:
                                speed_data = test_data["Select Download Test File Size"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote_test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Speed_test:-'Password'", status="FAILED",comments=statement)
                                    result_status.put(status_df)
                                    raise e
                            inputtext(driver=speed_test_form_fields_name,locators=remote_test.Password_textbox,value=speed_data)
                    elif re.search("Download File Name".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Use_Default_Server_speed_data == "No":
                            try:
                                speed_data = test_data["Download File Name"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Speed_test:-'Download File Name'", status="FAILED",comments=statement)
                                    result_status.put(status_df)
                                    raise e
                        inputtext(driver=speed_test_form_fields_name,locators=remote_test.Download_File_Name_textbox,value=speed_data)
                    elif re.search("Enable Upload Test".lower().replace(" ",""),field_name,re.IGNORECASE):
                        checkbox_input = speed_test_form_fields_name.find_element(*remote_test.Enable_Upload_Test_checkbox[:2])
                        if (Enable_Upload_Test_speed_data == "Yes" and not checkbox_input.is_selected()) or (Enable_Upload_Test_speed_data == "No" and checkbox_input.is_selected()):
                            clickec(driver=speed_test_form_fields_name, locators=remote_test.Enable_Upload_Test_checkbox)

                    elif re.search("File Size".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Enable_Upload_Test_speed_data == "Yes" and Enable_FTP_Stop_Timer_speed_data == "No":
                            try:
                                speed_data = test_data["File Size"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Speed_test:-'File Size'", status="FAILED",comments=statement)
                                    result_status.put(status_df)
                                    raise e
                            # input_field = speed_test_form_fields_name.find_element(*remote_test.speed_File_Size_textbox[:2])
                            # min_value = input_field.get_attribute("min")
                            # max_value = input_field.get_attribute("max")
                            if is_numeric(speed_data):
                                if 10 <= int(speed_data) <= 9999:
                                    inputtext(driver=speed_test_form_fields_name,locators=remote_test.speed_File_Size_textbox,value=speed_data)
                                else:
                                    statement = f"Check the value given within the range"
                                    with allure.step(statement):
                                        status_df = status(Title=Title, component=f"Speed_test:-'File Size'", status="FAILED",comments=statement)
                                        result_status.put(status_df)
                                        e = Exception
                                        raise e
                            else:
                                statement = f"Check the entered value is numeric"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Speed_test:-'File Size'", status="FAILED",comments=statement)
                                    result_status.put(status_df)
                                    e = Exception
                                    raise e
                                # speed_data = max(int(min_value), min(int(max_value), int(speed_data)))
                    elif re.search("Enable FTP Stop Timer".lower().replace(" ",""),field_name,re.IGNORECASE):
                        checkbox_input = speed_test_form_fields_name.find_element(*remote_test.Enable_FTP_Stop_Timer_checkbox[:2])
                        if (Enable_FTP_Stop_Timer_speed_data == "Yes" and not checkbox_input.is_selected()) or (Enable_FTP_Stop_Timer_speed_data == "No" and checkbox_input.is_selected()):
                            clickec(driver=speed_test_form_fields_name, locators=remote_test.Enable_FTP_Stop_Timer_checkbox)

                    elif re.search("Set Timeout".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Enable_FTP_Stop_Timer_speed_data == "Yes":
                            try:
                                speed_data = test_data["Set Timeout"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Speed_test:-'Set Timeout'", status="FAILED",comments=statement)
                                    result_status.put(status_df)
                                    raise e
                            if is_numeric(speed_data):
                                if 60 <= int(speed_data) <= 250:
                                    inputtext(driver=speed_test_form_fields_name,locators=remote_test.speed_Wait_Duration_textbox,value=speed_data)
                                else:
                                    statement = f"Check the value given within the range"
                                    with allure.step(statement):
                                        status_df = status(Title=Title, component=f"Speed_test:-'Set Timeout'", status="FAILED",comments=statement)
                                        result_status.put(status_df)
                                        e = Exception
                                        raise e
                            else:
                                statement = f"Check the entered value is numeric"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Speed_test:-'Set Timeout'", status="FAILED",comments=statement)
                                    result_status.put(status_df)
                                    e = Exception
                                    raise e
                except Exception as e:
                    Speed_test = False
                    continue
                            # speed_data = max(int(min_value), min(int(max_value), int(speed_data)))
            allure.attach(driver.get_screenshot_as_png(), name=f"Speed_test.",attachment_type=allure.attachment_type.PNG)
            if Speed_test == True:
                okbtn = driver.find_element(*remote_test.speedtest_okbtn[:2])
                if okbtn.is_enabled():
                    clickec(driver=driver,locators=remote_test.speedtest_okbtn)
                elif not okbtn.is_enabled():
                    clickec(driver=driver, locators=remote_test.speedtest_closebtn)
                    e = Exception
                    raise e
            elif Speed_test == False or Speed_test == None:
                clickec(driver=driver, locators=remote_test.speedtest_closebtn)
                e = Exception
                raise e
    except Exception as e:
        raise e

def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def http_speed_test(driver,Title,test_data,result_status,type_of_test):
    try:
        with allure.step("http speed test"):
            if type_of_test == "runtest":
                clickec(driver=driver, locators=remote_test.http_speed_test_checkbox)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(remote_test.http_speed_test_form))
            Http_speed_test = None
            http_speed_test_form_fields_names = driver.find_elements(*remote_test.http_speed_test_form)
            Http_speed_test = True
            try:
                Enter_custom_URL_http_speed_data = test_data["Enter custom URL"]
            except Exception as e:
                statement = f"Check parameter is present in remote test sheet test data excel"
                with allure.step(statement):
                    status_df = status(Title=Title, component=f"Http_speed_test:-'Enter custom URL'", status="FAILED",comments=statement)
                    result_status.put(status_df)
            try:
                Enable_HTTP_Speed_Test_Upload_Test_http_speed_data = test_data["Enable HTTP Speed Test Upload Test"]
            except Exception as e:
                statement = f"Check parameter is present in remote test sheet test data excel"
                with allure.step(statement):
                    status_df = status(Title=Title, component=f"Http_speed_test:-'Enable HTTP Speed Test Upload Test'", status="FAILED",comments=statement)
                    result_status.put(status_df)
            try:
                Enable_HTTP_Speed_Test_stop_timer_http_speed_data = test_data["Enable HTTP Speed Test stop timer"]
            except Exception as e:
                statement = f"Check parameter is present in remote test sheet test data excel"
                with allure.step(statement):
                    status_df = status(Title=Title, component=f"Http_speed_test:-'Enable HTTP Speed Test stop timer'",status="FAILED", comments=statement)
                    result_status.put(status_df)
            try:
                Enter_Custom_Upload_URL_http_speed_data = test_data["Enter Custom Upload URL"]
            except Exception as e:
                statement = f"Check parameter is present in remote test sheet test data excel"
                with allure.step(statement):
                    status_df = status(Title=Title, component=f"Http_speed_test:-'Enter Custom Upload URL'",status="FAILED", comments=statement)
                    result_status.put(status_df)
            for http_speed_test_form_fields_name in http_speed_test_form_fields_names:
                try:
                    field_name = str(http_speed_test_form_fields_name.text).lower().replace(" ","")
                    if re.search("Parallel Connections".lower().replace(" ",""),field_name,re.IGNORECASE):
                        pass
                    elif re.search("Enter custom URL".lower().replace(" ",""),field_name,re.IGNORECASE):
                        checkbox_input = driver.find_element(*remote_test.Enter_custom_URL_checkbox[:2])
                        if (Enter_custom_URL_http_speed_data == "Yes" and not checkbox_input.is_selected()) or (Enter_custom_URL_http_speed_data == "No" and checkbox_input.is_selected()):
                            clickec(driver=driver, locators=remote_test.Enter_custom_URL_checkbox)

                    elif re.search("Enter URL".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Enter_custom_URL_http_speed_data == "Yes":
                            try:
                                http_speed_data = test_data["Enter URL"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Http_speed_test:-'Enter Custom Upload URL'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    raise e
                            inputtext(driver=driver,locators=remote_test.Enter_URL_textbox,value=http_speed_data)
                    elif re.search("HTTP Speed Download Test File Size".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Enter_custom_URL_http_speed_data == "No" and Enable_HTTP_Speed_Test_stop_timer_http_speed_data == "No":
                            try:
                                http_speed_data = test_data["HTTP Speed Download Test File Size"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote_test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Http_speed_test:-'HTTP Speed Download Test File Size'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    raise e
                            HTTP_Speed_Download_Test_File_Size_dropdown_option = (By.XPATH,f"//div[@id='httpspeedtest']//option[normalize-space()='{http_speed_data}']","HTTP_Speed_Download_Test_File_Size_dropdown_option")
                            clickec(driver=driver,locators=remote_test.HTTP_Speed_Download_Test_File_Size_dropdown)
                            clickec(driver=driver,locators=HTTP_Speed_Download_Test_File_Size_dropdown_option)
                    elif re.search("Enable HTTP Speed Test Upload Test".lower().replace(" ",""),field_name,re.IGNORECASE):
                        checkbox_input = driver.find_element(*remote_test.Enable_HTTP_Speed_Test_Upload_Test_checkbox[:2])
                        if (Enable_HTTP_Speed_Test_Upload_Test_http_speed_data == "Yes" and not checkbox_input.is_selected()) or (Enable_HTTP_Speed_Test_Upload_Test_http_speed_data == "No" and checkbox_input.is_selected()):
                            clickec(driver=driver, locators=remote_test.Enable_HTTP_Speed_Test_Upload_Test_checkbox)

                    elif re.search("File Size".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Enable_HTTP_Speed_Test_Upload_Test_http_speed_data == "Yes" and Enable_HTTP_Speed_Test_stop_timer_http_speed_data == "No":
                            try:
                                http_speed_data = test_data["File Size"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title,component=f"Http_speed_test:-'File Size'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    raise e

                            if is_numeric(http_speed_data):
                                if 10 <= int(http_speed_data) <= 9999:
                                    inputtext(driver=driver,locators=remote_test.http_speed_File_Size_textbox,value=http_speed_data)
                                else:
                                    statement = f"Check the value given within the range"
                                    with allure.step(statement):
                                        status_df = status(Title=Title, component=f"Http_speed_test:-'File Size'", status="FAILED",comments=statement)
                                        result_status.put(status_df)
                                        e = Exception
                                        raise e
                            else:
                                statement = f"Check the entered value is numeric"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Http_speed_test:-'File Size'", status="FAILED",comments=statement)
                                    result_status.put(status_df)
                                    e = Exception
                                    raise e

                    elif re.search("Enable HTTP Speed Test stop timer".lower().replace(" ",""),field_name,re.IGNORECASE):
                        checkbox_input = driver.find_element(*remote_test.Enable_HTTP_Speed_Test_stop_timer_checkbox[:2])
                        if (Enable_HTTP_Speed_Test_stop_timer_http_speed_data == "Yes" and not checkbox_input.is_selected()) or (Enable_HTTP_Speed_Test_stop_timer_http_speed_data == "No" and checkbox_input.is_selected()):
                            clickec(driver=driver, locators=remote_test.Enable_HTTP_Speed_Test_stop_timer_checkbox)

                    elif re.search("Set Timeout".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Enable_HTTP_Speed_Test_stop_timer_http_speed_data == "Yes":
                            try:
                                http_speed_data = test_data["Set Timeout"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Http_speed_test:-'Set Timeout'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    raise e

                            if is_numeric(http_speed_data):
                                if 60 <= int(http_speed_data) <= 200:
                                    inputtext(driver=driver, locators=remote_test.HTTP_Speed_Set_Timeout_textbox,value=http_speed_data)
                                else:
                                    statement = f"Check the value given within the range"
                                    with allure.step(statement):
                                        status_df = status(Title=Title, component=f"Http_speed_test:-'Set Timeout'",status="FAILED", comments=statement)
                                        result_status.put(status_df)
                                        e = Exception
                                        raise e
                            else:
                                statement = f"Check the entered value is numeric"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Http_speed_test:-'Set Timeout'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    e = Exception
                                    raise e
                    elif re.search("Enter Custom Upload URL".lower().replace(" ",""),field_name,re.IGNORECASE):
                        checkbox_input = driver.find_element(*remote_test.Enter_Custom_Upload_URL_checkbox[:2])
                        if (Enter_Custom_Upload_URL_http_speed_data == "Yes" and not checkbox_input.is_selected()) or (Enter_Custom_Upload_URL_http_speed_data == "No" and checkbox_input.is_selected()):
                            clickec(driver=driver, locators=remote_test.Enter_Custom_Upload_URL_checkbox)
                    elif re.search("Upload URL".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Enter_Custom_Upload_URL_http_speed_data == "Yes":
                            try:
                                http_speed_data = test_data["Upload URL"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Http_speed_test:-'Upload URL'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    raise e
                            inputtext(driver=driver,locators=remote_test.Upload_URL_textbox,value=http_speed_data)
                except Exception as e:
                    Http_speed_test = False
                    continue
            allure.attach(driver.get_screenshot_as_png(), name=f"Speed_test.",attachment_type=allure.attachment_type.PNG)
            if Http_speed_test == True:
                okbtn = driver.find_element(*remote_test.http_speedtest_okbtn[:2])
                if okbtn.is_enabled():
                    clickec(driver=driver,locators=remote_test.http_speedtest_okbtn)
                elif not okbtn.is_enabled():
                    clickec(driver=driver, locators=remote_test.http_speedtest_closebtn)
                    e = Exception
                    raise e
            elif Http_speed_test == False or Http_speed_test == None:
                clickec(driver=driver, locators=remote_test.http_speedtest_closebtn)
                e = Exception
                raise e
    except Exception as e:
        raise e
def iperf_test(driver,Title,test_data,result_status,type_of_test,test_name):
    try:
        with allure.step("iperf test"):
            if type_of_test == "runtest":
                clickec(driver=driver, locators=remote_test.iperf_testcheckbox)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(remote_test.iperf_test_form))
            Iperf_test = None
            iperf_test_form_fields_names = driver.find_elements(*remote_test.iperf_test_form)
            Iperf_test = True
            try:
                Use_Default_Server_iperf_data = test_data["Use Default Server"]
            except Exception as e:
                statement = f"Check parameter is present in remote test sheet test data excel"
                with allure.step(statement):
                    status_df = status(Title=Title, component=f"Iperf_test:-'Use Default Server'", status="FAILED",comments=statement)
                    result_status.put(status_df)
            try:
                Enable_Iperf_Upload_Test_iperf_data = test_data["Enable Iperf Upload Test"]
            except Exception as e:
                statement = f"Check parameter is present in remote test sheet test data excel"
                with allure.step(statement):
                    status_df = status(Title=Title, component=f"Iperf_test:-'Enable Iperf Upload Test'", status="FAILED",comments=statement)
                    result_status.put(status_df)
            try:
                Enable_Iperf_Upload_Test_iperf_data = test_data["Enable Iperf Upload Test"]
            except Exception as e:
                statement = f"Check parameter is present in remote test sheet test data excel"
                with allure.step(statement):
                    status_df = status(Title=Title, component=f"Iperf_test:-'Enable Iperf Upload Test'", status="FAILED",comments=statement)
                    result_status.put(status_df)
            try:
                TCP_Mode_iperf_data = test_data["TCP Mode"]
            except Exception as e:
                statement = f"Check parameter is present in remote test sheet test data excel"
                with allure.step(statement):
                    status_df = status(Title=Title, component=f"Iperf_test:-'TCP Mode'", status="FAILED",comments=statement)
                    result_status.put(status_df)
            try:
                UDP_Mode_iperf_data = test_data["UDP Mode"]
            except Exception as e:
                statement = f"Check parameter is present in remote test sheet test data excel"
                with allure.step(statement):
                    status_df = status(Title=Title, component=f"Iperf_test:-'UDP Mode'", status="FAILED",comments=statement)
                    result_status.put(status_df)
            for iperf_test_form_fields_name in iperf_test_form_fields_names:
                try:
                    field_name = str(iperf_test_form_fields_name.text).lower().replace(" ","")
                    if re.search("Use Default Server".lower().replace(" ",""),field_name,re.IGNORECASE):
                        checkbox_input = driver.find_element(*remote_test.Iperf_Use_Default_Server_checkbox[:2])
                        if (Use_Default_Server_iperf_data == "Yes" and not checkbox_input.is_selected()) or (Use_Default_Server_iperf_data == "No" and checkbox_input.is_selected()):
                            clickec(driver=driver, locators=remote_test.Iperf_Use_Default_Server_checkbox)
                    elif re.search("Host Name".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if Use_Default_Server_iperf_data == "No":
                            try:
                                iperf_data = test_data["Host Name"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Iperf_test:-'Host Name'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    raise  e
                            inputtext(driver=driver,locators=remote_test.Host_Name_textbox,value=iperf_data)
                    elif re.search("Test Duration".lower().replace(" ",""),field_name,re.IGNORECASE):
                            try:
                                iperf_data = test_data["Test Duration(sec)"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Iperf_test:-'Test Duration(sec)'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    raise e
                            if is_numeric(iperf_data):
                                if 10 <= int(iperf_data) <= 120:
                                    inputtext(driver=driver,locators=remote_test.Test_Duration_textbox,value=iperf_data)
                                else:
                                    statement = f"Check the value given within the range"
                                    with allure.step(statement):
                                        status_df = status(Title=Title, component=f"Iperf_test:-'Test Duration'",status="FAILED", comments=statement)
                                        result_status.put(status_df)
                                        e = Exception
                                        raise e
                            else:
                                statement = f"Check the entered value is numeric"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Iperf_test:-'Test Duration'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    e = Exception
                                    raise e
                    elif re.search("Enable Iperf Upload Test".lower().replace(" ",""),field_name,re.IGNORECASE):
                        checkbox_input = driver.find_element(*remote_test.Enable_Iperf_Upload_Test_checkbox[:2])
                        if (Enable_Iperf_Upload_Test_iperf_data == "Yes" and not checkbox_input.is_selected()) or (Enable_Iperf_Upload_Test_iperf_data == "No" and checkbox_input.is_selected()):
                            clickec(driver=driver, locators=remote_test.Enable_Iperf_Upload_Test_checkbox)
                    elif re.search("TCP Mode".lower().replace(" ",""),field_name,re.IGNORECASE) and test_name.lower().replace(" ", "") == "TCP-Iperf Test".lower().replace(" ", ""):
                        checkbox_input = driver.find_element(*remote_test.TCP_Mode_checkbox[:2])
                        checkbox_input1 = driver.find_element(*remote_test.UDP_Mode_checkbox[:2])
                        if (TCP_Mode_iperf_data == "Yes" and not checkbox_input.is_selected()) or (TCP_Mode_iperf_data == "No" and checkbox_input.is_selected()):
                            if checkbox_input1.is_selected():
                                clickec(driver=driver, locators=remote_test.UDP_Mode_checkbox)
                            clickec(driver=driver, locators=remote_test.TCP_Mode_checkbox)
                    elif re.search("UDP Mode".lower().replace(" ",""),field_name,re.IGNORECASE) and test_name.lower().replace(" ", "") == "UDP-Iperf Test".lower().replace(" ", ""):
                        checkbox_input = driver.find_element(*remote_test.UDP_Mode_checkbox[:2])
                        checkbox_input1 = driver.find_element(*remote_test.TCP_Mode_checkbox[:2])
                        if (UDP_Mode_iperf_data == "Yes" and not checkbox_input.is_selected()) or (UDP_Mode_iperf_data == "No" and checkbox_input.is_selected()):
                            if checkbox_input1.is_selected():
                                clickec(driver=driver, locators=remote_test.TCP_Mode_checkbox)
                            clickec(driver=driver, locators=remote_test.UDP_Mode_checkbox)
                    elif re.search("Enter the Bandwidth".lower().replace(" ",""),field_name,re.IGNORECASE):
                        if UDP_Mode_iperf_data == "Yes":
                            try:
                                iperf_data = test_data["Enter the Bandwidth"]
                            except Exception as e:
                                statement = f"Check parameter is present in remote_test sheet test data excel"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Iperf_test:-'Enter the Bandwidth'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    raise e
                            if is_numeric(iperf_data):
                                if 1 <= int(iperf_data) <= 9999:
                                    inputtext(driver=driver,locators=remote_test.Enter_the_Bandwidth_textbox,value=iperf_data)
                                else:
                                    statement = f"Check the value given within the range"
                                    with allure.step(statement):
                                        status_df = status(Title=Title, component=f"Iperf_test:-'Test Duration'",status="FAILED", comments=statement)
                                        result_status.put(status_df)
                                        e = Exception
                                        raise e
                            else:
                                statement = f"Check the entered value is numeric"
                                with allure.step(statement):
                                    status_df = status(Title=Title, component=f"Iperf_test:-'Enter the Bandwidth'",status="FAILED", comments=statement)
                                    result_status.put(status_df)
                                    e = Exception
                                    raise e
                except Exception as e:
                    Iperf_test = False
                    continue
            allure.attach(driver.get_screenshot_as_png(), name=f"Speed_test.",attachment_type=allure.attachment_type.PNG)
            if Iperf_test == True:
                okbtn = driver.find_element(*remote_test.iperf_test_okbtn[:2])
                if okbtn.is_enabled():
                    clickec(driver=driver,locators=remote_test.iperf_test_okbtn)
                elif not okbtn.is_enabled():
                    clickec(driver=driver, locators=remote_test.iperf_test_closebtn)
                    e = Exception
                    raise e
            elif Iperf_test == False or Iperf_test == None:
                clickec(driver=driver, locators=remote_test.iperf_test_closebtn)
                e = Exception
                raise e
    except Exception as e:
        raise e
def web_test(driver,test_data,type_of_test):
    try:
        with allure.step("Web test"):
            if type_of_test == "runtest":
                clickec(driver=driver, locators=remote_test.webtest_checkbox)
            web_data = None
            try:
                web_data = test_data["URL"]
            except Exception as e:
                raise
            # Interaction with URL input field and "OK" button
            clickec(driver=driver, locators=remote_test.web_url)
            inputtext(driver=driver, locators=remote_test.web_url, value=web_data)
            allure.attach(driver.get_screenshot_as_png(), name=f"Web Test.", attachment_type=allure.attachment_type.PNG)
            clickec(driver=driver, locators=remote_test.web_test_okbtn)
    except Exception as e:
        print(e)
        raise e
def stream_test(driver,test_data,type_of_test):
    try:
        with allure.step("stream test"):
            if type_of_test == "runtest":
                clickec(driver=driver, locators=remote_test.stream_checkbox)
            stream_data = None
            try:
                stream_data = test_data["Enter_Video_URL"]
            except Exception as e:
                raise
            clickec(driver,remote_test.enter_url_checkbox)
            inputtext(driver,locators=remote_test.txt_box_url,value=stream_data)
            allure.attach(driver.get_screenshot_as_png(), name=f"Enter video URL value", attachment_type=allure.attachment_type.PNG)
            clickec(driver,remote_test.submit_ok_btn)
    except Exception as e:
        raise e