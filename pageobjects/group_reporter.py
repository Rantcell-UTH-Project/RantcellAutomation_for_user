import re
import statistics
from collections import Counter
from math import nan
from typing import Optional, OrderedDict

from module_controllers.module_controllers import groupreporter_module_controllers
from pageobjects.remote_test import *
from pageobjects.Dashboard import *
from utils.library import *
from locators.locators import *

def main_func_group_reporter_for_daily_automation(driver, environment, userid, campaigns_datas,downloadpath, excelpath):
    groupreporter_runvalue = groupreporter_module_controllers()
    Title = "Group Reporter"
    try:
        if "Yes".lower() == groupreporter_runvalue[-1].strip().lower():
            testgroup_list = [campaigns_datas[i][3] for i in range(len(campaigns_datas))]
            testgroup_list = list(set(testgroup_list))
            for testgroup in testgroup_list[:1]:
                main_func_group_reporter(driver,Title,environment, userid, testgroup, downloadpath, excelpath)
        elif "No".lower() == groupreporter_runvalue[-1].strip().lower():
            updatecomponentstatus(Title, "Not to execute", "SKIPPED", "You have selected No for execute", excelpath)
            pass
    except Exception as e:
        pass
    finally:
        try:
            update_module_status_based_on_reading_component_status(modules={"Group Reporter":"FAILED"},excelpath=excelpath)
        except Exception as e:
            pass

def main_func_group_reporter(driver,Title,environment,userid,testgroup,downloadpath,excelpath):
    result_same = queue.Queue()
    result_status = queue.Queue()
    result_Difference = queue.Queue()
    try:
        group_reporter(driver, testgroup,downloadpath,Title,result_same,result_Difference,result_status,excelpath)
    except Exception as e:
        pass
    finally:
        try:
            update_gr_data_result_to_excel(result_status,result_Difference,result_same,excelpath)
        except Exception as e:
            pass
def update_gr_data_result_to_excel(result_status,data_difference,data_same,excelpath):
    dataframe_status = []
    dataframe_difference =[]
    dataframe_same = []
    combined_status_df = "None"
    combined_difference_df ="None"
    combined_same_df = "None"
    while not result_status.empty():
        updatecomponentstatus2 = result_status.get()
        df_status = pd.DataFrame(updatecomponentstatus2)
        dataframe_status.append(df_status)
    while not data_same.empty():
        same = data_same.get()
        df_same = pd.DataFrame(same)
        dataframe_same.append(df_same)
    while not data_difference.empty():
        difference = data_difference.get()
        df_difference = pd.DataFrame(difference)
        dataframe_difference.append(df_difference)
    if len(dataframe_status) != 0:
        combined_status_df = pd.concat(dataframe_status, ignore_index=True)
    if len(dataframe_difference) != 0:
        statement = "Values are difference"
        with allure.step(statement):
            combined_difference_df = pd.concat(dataframe_difference, ignore_index=True)
            html_table = combined_difference_df.to_html(index=False, escape=False)
            allure.attach(html_table, name="HTML Table", attachment_type=allure.attachment_type.HTML)
    if len(dataframe_same) !=0:
        statement = "Values are same"
        with allure.step(statement):
            combined_same_df = pd.concat(dataframe_same, ignore_index=True)
            html_table = combined_same_df.to_html(index=False, escape=False)
            allure.attach(html_table, name="HTML Table", attachment_type=allure.attachment_type.HTML)
    workbook = openpyxl.load_workbook(excelpath)
    worksheet_componentstatus = workbook["COMPONENTSTATUS"]
    data_matchsheet = workbook["Gr_DATA_MATCH"]
    data_not_matchsheet = workbook["Gr_DATA_NOT_MATCH"]
    if len(dataframe_status) != 0:
        update_component_status_openpyxl(worksheet=worksheet_componentstatus, dataframe=combined_status_df)
    if len(dataframe_difference) != 0:
        update_excel_datavalidation_gr_data_each_testcase_openpyxl(df=combined_difference_df, worksheet=data_not_matchsheet)
    if len(dataframe_same) != 0:
        update_excel_datavalidation_gr_data_each_testcase_openpyxl(df=combined_same_df, worksheet=data_matchsheet)
    workbook.save(excelpath)
    workbook.close()

def update_excel_datavalidation_gr_data_each_testcase_openpyxl(df,worksheet):
    """
        Update the high-level Excel report for data validation of individualpopup.
        Args:
            df (DataFrame): The DataFrame containing data to be added to the Excel sheet.
            sheet (Excel Sheet): The Excel sheet to update with the data and formatting.
        Returns:
            None
        """
    try:
        color_mapping = {
            'STARTHERE': PatternFill(start_color="D2B48C", end_color="D2B48C", fill_type="solid"),  # Light Brown
            'ENDHERE': PatternFill(start_color="D2B48C", end_color="D2B48C", fill_type="solid"),  # Light Brown
            "Same": PatternFill(start_color="C2FFAD", end_color="C2FFAD", fill_type="solid"),  # Green
            "Difference": PatternFill(start_color='FF9999', end_color='FF9999', fill_type="solid"),   #light Red
            "Key name can't find in csv": PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type="solid") , # Yellow
            "notcal": PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type="solid"),
            "Row Start": PatternFill(start_color='ADD8E8', end_color='ADD8E9', fill_type="solid"),
            "is equal": PatternFill(start_color="C2FFAD", end_color="C2FFAD", fill_type="solid"),  # light Green
            "is not equal": PatternFill(start_color='FF9999', end_color='FF9999', fill_type="solid"),  # Red
            # "Key name can't find in csv file": PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type="solid")  # Light Yellow
        }
        # Find the last used row in the sheet
        last_row = worksheet.max_row
        start_row = last_row + 1
        # Insert the DataFrame into the worksheet
        for index, row in df.iterrows():
            worksheet.append(row.tolist())
        # Apply color formatting to the entire range
        for i, row in enumerate(worksheet.iter_rows(min_row=start_row, max_row=start_row + len(df) - 1, min_col=2, max_col=2),start=start_row):
            validation_cell = row[0]
            data_validation = df.iloc[i - start_row]["Data validation"]
            for keyword, fill in color_mapping.items():
                if keyword in data_validation:
                    validation_cell.fill = fill
        for i, row in enumerate(worksheet.iter_rows(min_row=start_row, max_row=start_row + len(df) - 1, min_col=3, max_col=3),start=start_row):
            validation_cell = row[0]
            data_validation = df.iloc[i - start_row]["Data validation"]
            for keyword, fill in color_mapping.items():
                if keyword in data_validation:
                    validation_cell.fill = fill
        for i, row in enumerate(worksheet.iter_rows(min_row=start_row, max_row=start_row + len(df) - 1, min_col=4, max_col=4),start=start_row):
            validation_cell = row[0]
            data_validation = df.iloc[i - start_row]["Data validation"]
            for keyword, fill in color_mapping.items():
                if keyword in data_validation:
                    validation_cell.fill = fill
        for i, row in enumerate(worksheet.iter_rows(min_row=start_row, max_row=start_row + len(df) - 1, min_col=5, max_col=5),start=start_row):
            validation_cell = row[0]
            data_validation = df.iloc[i - start_row]["Data validation"]
            for keyword, fill in color_mapping.items():
                if keyword in data_validation:
                    validation_cell.fill = fill
        # Set colors for File columns
        for i in range(start_row, start_row + len(df)):
            worksheet.cell(row=i, column=1).fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
    except Exception as e:
        with allure.step(f"{str(e)}"):
            pass

def group_reporter(driver,testgroup,downloadpath,Title,result_same,result_Difference,result_status,excelpath):
    try:
        click_on_group_reporter_btn(driver)
        click_on_group_dropdown_btn(driver, testgroup)
        click_on_group_reporter_runquery(driver)
        selecting_date_or_hours_for_group_reporter(driver,Title,result_status)
        group_reporter_downloadpath = downloadpath +"\\GROUP_REPORTER"
        create_folder_for_downloads(group_reporter_downloadpath)
        change_the_download_path(driver,group_reporter_downloadpath)
        testtype_dict = {
            "StreamTest": ["StreamTest", []],
            "WebTest": ["WebTest", []],
            "TCPiPerfTest": ["TCPiPerfData", []],
            "Upload Test": ["UploadTest", []],
            "Ping Test": ["PingTest", []],
            "HTTP Speed Download Test": ["HttpDownloadTest", []],
            "Call Test": ["CallTest", []],
            "Download Test": ["DownloadTest", []],
            "HTTP Speed Upload Test": ["HTestUploadTest", []],
            "UDPiPerfTest": ["UDPiPerfData", []],
            "SMS Test": ["SmsTest", []]
        }
        function_map = {
            "avg_datavalidation_groupreporter": avg_datavalidation_groupreporter,
            "max_datavalidation_groupreporter": max_datavalidation_groupreporter,
            "min_datavalidation_groupreporter": min_datavalidation_groupreporter,
            "aboveOrbelow_data_validation_groupreporter_with_fliter_df_flag_True": aboveOrbelow_data_validation_groupreporter_with_fliter_df_flag_True,
            "aboveOrbelow_data_validation_groupreporter_with_fliter_df_flag_Flase":aboveOrbelow_data_validation_groupreporter_with_fliter_df_flag_Flase,
            "betweenOrto_data_validation_groupreporter_with_fliter_df_True": betweenOrto_data_validation_groupreporter_with_fliter_df_True,
            "betweenOrto_data_validation_groupreporter_with_fliter_df_Flase":betweenOrto_data_validation_groupreporter_with_fliter_df_Flase,
            "stringvaluesInlist_data_validation_groupreporter": stringvaluesInlist_data_validation_groupreporter,
            "count_data_validation_groupreporter": count_data_validation_groupreporter,
            "Total_Test_success_Count_data_validation_groupreporter": count_data_validation_groupreporter,
            "Total_Test_Failed_Count_data_validation_groupreporter": count_data_validation_groupreporter,
            "Total_Test_Conducted_data_validation_groupreporter": count_data_validation_groupreporter,
            "Number_of_Detected_Operators_data_validation_groupreporter": Number_of_Detected_Operators_data_validation_groupreporter,
            "Dropped_Packets_data_validation_groupreporter": Dropped_Packets_data_validation_groupreporter,
            "sum_data_validation_groupreporter": sum_data_validation_groupreporter,
            nan: " "
        }
        func_for_testtype_validation = {
            'Download Test': read_group_reporter_excel_for_validation(function_map,sheetname="Download Test"),
            'Upload Test': read_group_reporter_excel_for_validation(function_map,sheetname="Upload Test"),
            'HTTP Speed Download Test': read_group_reporter_excel_for_validation(function_map,sheetname="HTTP Speed Download Test"),
            'HTTP Speed Upload Test': read_group_reporter_excel_for_validation(function_map,sheetname="HTTP Speed Upload Test"),
            'Ping Test': read_group_reporter_excel_for_validation(function_map,sheetname="Ping Test"),
            "SMS Test": read_group_reporter_excel_for_validation(function_map,sheetname="SMS Test"),
            "StreamTest": read_group_reporter_excel_for_validation(function_map,sheetname="StreamTest"),
            "Call Test": read_group_reporter_excel_for_validation(function_map,sheetname="Call Test"),
            "WebTest": read_group_reporter_excel_for_validation(function_map,sheetname="WebTest"),
            'UDPiPerfTest': {"DL": read_group_reporter_excel_for_validation(function_map,sheetname="UDPiPerfTest_DL"),
                             "UL": read_group_reporter_excel_for_validation(function_map,sheetname="UDPiPerfTest_UL")},
            "TCPiPerfTest": {"DL": read_group_reporter_excel_for_validation(function_map,sheetname="TCPiPerfTest_DL"),
                             "UL": read_group_reporter_excel_for_validation(function_map,sheetname="TCPiPerfTest_UL")}
        }
        for select_Testtype,datalist in testtype_dict.items():
            extract_data_from_all_testtype(driver, groupreporter.Export_btn, select_Testtype, Title, excelpath,datalist[1])

        for select_Testtype,datalist in testtype_dict.items():
            group_reporter_csv_file1 = [file for file in glob.glob(group_reporter_downloadpath + "\\*.csv") if re.fullmatch(str(datalist[0]),re.sub(r'[^A-Za-z]', '', (file.split("\\")[-1]).split("_")[0]),re.IGNORECASE)]
            if len(group_reporter_csv_file1) != 0 and None not in datalist:
                df_gr = pd.read_csv(group_reporter_csv_file1[0])
                func_flag = False
                try:
                    func_for_testtype = func_for_testtype_validation[select_Testtype]
                    func_flag = True
                    group_reporter_data_validation(df_gr,datalist[1][0], select_Testtype,group_reporter_csv_file1[0], func_for_testtype, Title,result_same, result_Difference, result_status)
                except Exception as e:
                    if func_flag == False:
                        r_result = status(Title=Title, component=select_Testtype, status="FAILED",comments=f"Error in finding the func for testtype, please check the '{select_Testtype}' in func_for_testtype_validation dictionary")
                        print(r_result)
                        result_status.put(r_result)
                    print(e)
            elif (datalist[1][0] == None or len(datalist) != 2) and len(group_reporter_csv_file1) == 0:
                r_result = status(Title=Title, component=select_Testtype, status="WARNING",comments="No data found in application and No csv found in the download path")
                print(r_result)
                result_status.put(r_result)
            elif datalist[1][0] == None or len(datalist) != 2 :
                r_result = status(Title=Title, component=select_Testtype, status="FAILED",comments="No data found in application")
                print(r_result)
                result_status.put(r_result)
            elif len(group_reporter_csv_file1) == 0:
                r_result = status(Title=Title, component=select_Testtype, status="FAILED",comments="No csv found in the download path")
                print(r_result)
                result_status.put(r_result)
    except Exception as e:
        pass
    finally:
        click(driver=driver, locators=Login_Logout.dashboard_id)

def click_on_group_reporter_btn(driver):
    clickec(driver, groupreporter.groupreporter_btn)

def click_on_group_dropdown_btn(driver,testgroup):
    try:
        with allure.step("click on the group button to open the dropdown"):
            device_button_dropdown_path = (groupreporter.device_button_dropdown_path[0],groupreporter.device_button_dropdown_path[1].format(testgroup),groupreporter.device_button_dropdown_path[2])
            device_button_dropdown = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(device_button_dropdown_path[:2]))
            element = driver.find_element(*device_button_dropdown_path[:2])
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            clickec(driver=driver, locators=device_button_dropdown_path)
            allure.attach(driver.get_screenshot_as_png(),name=f"click on the group button to open the dropdown",attachment_type=allure.attachment_type.PNG)
            return device_button_dropdown
    except Exception as e:
        pass

def read_group_reporter_excel_for_validation(function_map,sheetname):
    # Read the Excel file
    df = pd.read_excel(config.group_reporter_path,sheet_name=sheetname)

    # Reconstruct the original data format
    reconstructed_data = {}

    for _, row in df.iterrows():
        header = row["Header"]
        function_str = row["Function/Method"]
        function = function_str
        try:
            function = function_map[function_str]
        except Exception as e:
            print(function_str)
            pass# Map string to actual function
        parameter = row["Parameter"]

        # Collect filter parameters
        filter_parameters = {}
        for col in df.columns:
            if col.startswith("Filter Parameters_"):
                if pd.notna(row[col]):
                    try:
                        key, value = row[col].split(":")
                        filter_parameters[key] = str(value).strip()
                    except Exception as e:
                        print(header)
                elif nan == row[col]:
                        filter_parameters = None
        if filter_parameters == {}:
            filter_parameters = None
        # Assign values to the reconstructed data
        if header not in reconstructed_data:
            reconstructed_data[header] = {}
        reconstructed_data[header][function] = [parameter, filter_parameters]
    return reconstructed_data

def click_on_group_reporter_runquery(driver):
    clickec(driver, groupreporter.runquery_btn)

def click_on_group_reporter_duration_selection_dropdown(driver):
    clickec(driver, groupreporter.showtimedropdown_btn)

def selecting_date_or_hours_for_group_reporter(driver,Title,result_status):
    with allure.step("Selecting date or hours for group reporter"):
        yes_flag = False
        selected_flag = False
        selected_value = None
        enable_of_element_untill_loaded(driver,groupreporter.custom_query_btn[:2],1,120)
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
                        click(driver, groupreporter.custom_query_btn)

                        # code to select custom date range
                        navigate_to_date_grp(driver, start_date, end_date)
                        clickec(driver, date_time.datetime_apply_btn)
                        r_result = status(Title=Title, component=f"{select_hours}=={start_date}/{end_date}", status="PASSED",comments="Successfully Selected")
                        result_status.put(r_result)
                        selected_flag = True
                        selected_value = f"{select_hours}=={start_date}/{end_date}"
                    else:
                        click_on_group_reporter_duration_selection_dropdown(driver)
                        option_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((groupreporter.option_xpath_date_time[0],groupreporter.option_xpath_date_time[1].format(str(select_hours).lower()))))
                        option_element.click()
                        r_result = status(Title=Title, component=f"{select_hours}", status="PASSED",comments="Successfully Selected")
                        result_status.put(r_result)
                        selected_flag = True
                        selected_value = f"{select_hours}"
            if yes_flag == False:
                r_result = status(Title=Title, component=f"{selected_value}", status="FAILED",comments=f"Select the anyone option in date/time by giving the 'Yes' in '{config.test_data_path}' sheet:-'date_time'")
                result_status.put(r_result)
            elif yes_flag == True and selected_flag == False:
                r_result = status(Title=Title, component=f"{selected_value}", status="FAILED",comments=f"Failed to select")
                result_status.put(r_result)
            allure.attach(driver.get_screenshot_as_png(), name=f"Selecting date or hours for group reporter screenshot",attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            if yes_flag == True and selected_flag == False:
                r_result = status(Title=Title, component=f"{selected_value}", status="FAILED", comments=f"Failed to select")
                result_status.put(r_result)
            allure.attach(driver.get_screenshot_as_png(), name=f"Selecting date or hours for group reporter screenshot",attachment_type=allure.attachment_type.PNG)
            raise e
def navigate_to_date_grp(driver, start_date, end_date):
    # Extract year, month, and day from start_date
    global current_year
    start_year = start_date.year
    start_month = start_date.month
    start_day = start_date.day
    # Assuming start_month is the month number, for example, 5 for May
    start_month_number = start_month
    # Convert the month number to its corresponding name
    start_month_name = calendar.month_name[start_month_number][:3]

    # Loop until the start month and year are visible
    while True:
            try:
                try:
                    # Get the currently displayed month and year
                     # Adjust this XPath as needed
                    current_month_year_element = driver.find_element(*groupreporter.current_month_year_xpath)

                    # Get the currently displayed month and year
                    current_month_year = current_month_year_element.text

                    # Parse the displayed month and year
                    start_month_name, current_year = current_month_year.split()
                except Exception as e:
                    print(Exception)
                    pass
                start_month_name = list(calendar.month_abbr).index(start_month_name)

                # Check if the start month and year are visible
                if start_month_name == start_month and int(current_year) == start_year:
                    break
            except Exception as e:
                pass
            # Find and click the navigation button to go to the previous or next month
            if int(current_year) > start_year or (int(current_year) == start_year and start_month_name > start_month):
                # Click on the "<" button to go to the previous month
                navigation_button_xpath = groupreporter.navigation_button_prevavailable_xpath
            else:
                # Click on the ">" button to go to the next month
                navigation_button_xpath = groupreporter.navigation_button_nextavailable_xpath
            navigation_button = driver.find_element(*navigation_button_xpath)
            navigation_button.click()

    # Find and click the element corresponding to the start day
    start_day_element = driver.find_element(groupreporter.start_day_element_xpath[0],groupreporter.start_day_element_xpath[1].format(start_day))
    start_day_element.click()

    # # Extract year, month, and day from end_date
    end_year = end_date.year
    end_month = end_date.month
    end_day = end_date.day
    end_month_number = end_month
    end_month_name = calendar.month_name[end_month_number][:3]
    # Loop until the end month and year are visible
    while True:
        try:
            try:
                # Get the currently displayed month and year
                current_month_year_element = driver.find_element(*groupreporter.current_month_year_xpath1)
                current_month_year = current_month_year_element.text

                # Parse the displayed month and year
                end_month_name, current_year = current_month_year.split()
            except Exception as e:
                pass
            end_month_name = list(calendar.month_abbr).index(end_month_name)

            # Check if the end month and year are visible
            if end_month_name == end_month and int(current_year) == end_year:
                break
        except Exception as e:
            pass

        # Find and click the navigation button to go to the previous or next month
        if int(current_year) > end_year or (int(current_year) == end_year and end_month_name > end_month):
            navigation_button_xpath1 = groupreporter.navigation_button_prevavailable_xpath1
        else:
            navigation_button_xpath1 = groupreporter.navigation_button_nextavailable_xpath1
        navigation_button = driver.find_element(*navigation_button_xpath1)
        navigation_button.click()

    # Find and click the element corresponding to the end day
    end_day_element = driver.find_element(groupreporter.end_day_element_xpath[0],groupreporter.end_day_element_xpath[1].format(end_day))
    end_day_element.click()

def selecting_testtype_from_dropdown_for_group_reporter(driver,select_Testtype,Title,excelpath):
    option_text_list = [select_Testtype]
    driver.execute_script(f"window.scrollTo({0}, {0});")
    enable_of_element_untill_loaded(driver,groupreporter.showTestTypedropdown_btn[:2],1)
    select_from_listbox_ECs(driver, groupreporter.showTestTypedropdown_btn[:2], groupreporter.option_xpath_drp_down,option_text_list, Title, excelpath)
    test_data_found = None
    try:
        test_data_found = WebDriverWait(driver,10).until(EC.invisibility_of_element(groupreporter.No_test_data_found_xpath))
    except Exception as e:
        print(select_Testtype, "_______", test_data_found)
        pass
    while True:
        click_load_more_grp(driver, groupreporter.load_more_button_xpath,5,test_data_found)
        try:
            WebDriverWait(driver,5).until(EC.invisibility_of_element_located(groupreporter.load_more_button_xpath[:2]))
            break
        except Exception as e:
            print(select_Testtype, "_______", test_data_found)
            pass
    try:
        test_data_found = WebDriverWait(driver,3).until(EC.invisibility_of_element(groupreporter.No_test_data_found_xpath))
    except Exception as e:
        print(select_Testtype, "_______", test_data_found)
        pass
    allure.attach(driver.get_screenshot_as_png(), name=f"{select_Testtype}_is_loaded",attachment_type=allure.attachment_type.PNG)
    return test_data_found
def click_load_more_grp(driver, load_more_button_xpath,time,test_data_found):
    for i in range(0,2):
        try:
            try:
                if test_data_found:
                    while WebDriverWait(driver,10).until(EC.visibility_of_element_located(load_more_button_xpath[:2])) or WebDriverWait(driver,10).until(EC.invisibility_of_element(groupreporter.No_test_data_found_xpath)):
                        try:
                            enable_of_element_untill_loaded(driver,load_more_button_xpath[:2],1)
                            load_more_button = WebDriverWait(driver, time).until(EC.visibility_of_element_located(load_more_button_xpath[:2]))
                            load_more_button.click()
                        except Exception as e:
                            break
                elif test_data_found == False:
                    while WebDriverWait(driver,10).until(EC.visibility_of_element_located(groupreporter.No_test_data_found_xpath)):
                        try:
                            enable_of_element_untill_loaded(driver, load_more_button_xpath[:2], 1)
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
def extract_data_from_all_testtype(driver,Export_btn,select_Testtype,Title,excelpath,datalist):
    try:
        with allure.step(f'{select_Testtype}'):
            test_data_found = selecting_testtype_from_dropdown_for_group_reporter(driver,select_Testtype, Title, excelpath)
            allure.attach(driver.get_screenshot_as_png(), name=f"{select_Testtype}_for_group_test",attachment_type=allure.attachment_type.PNG)
            if test_data_found:
                data = {}
                if "StreamTest" == select_Testtype or "WebTest" == select_Testtype:
                    data_list = []
                    canvasvalues = {}
                    canvas = driver.find_element(*groupreporter.barchartWebtest_xpath)
                    action_chains = ActionChains(driver)
                    action_chains.move_to_element(canvas).perform()
                    canvas_height = int(canvas.size['height']/1.5)
                    canvas_width_2 = int(canvas.size['width']/3)
                    for j in range(-(canvas_height), canvas_height,15):
                        for i in range(-(canvas_width_2), -50, 13):
                            try:
                                action_chains.move_to_element_with_offset(canvas,i,j).perform()
                                if driver.find_element(*groupreporter.barchartWebtest_tooltip_xpath).is_displayed():
                                    data_element = driver.find_element(*groupreporter.barchartWebtest_tooltip_xpath)
                                    datatext = data_element.text
                                    data_list.append(datatext)
                                    break
                            except:
                                pass
                    for data_i in list(set(data_list)):
                        data_j = str(data_i).split(":")
                        if len(data_j)== 2:
                            canvasvalues[data_j[0]] = data_j[1]
                    if len(canvasvalues) != 0:
                        data[0] = canvasvalues
                elif "StreamTest" != select_Testtype or "WebTest" != select_Testtype:
                    extract_data_of_ranges(driver, select_Testtype, range_data_dict=data)
                Page_Down(driver)
                table_summary_of_group_reporter(driver, select_Testtype, Title, excelpath,table_summary_data_dict=data)
                datalist.append(data)
                print(f"{select_Testtype} = ",data)
                clickec(driver,Export_btn)
            else:
                datalist.append(None)
                print("datalist.append(None)")
            allure.attach(driver.get_screenshot_as_png(), name=f"{select_Testtype}_for_group_test",attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        pass

def extract_data_of_ranges(driver,select_Testtype,range_data_dict):
    try:
        Range_value_data_elements = driver.find_elements(groupreporter.Range_value_xpath[0],groupreporter.Range_value_xpath[1].format(""))
        range_data = {}
        for i in range(1,len(Range_value_data_elements)+1):
            try:
                Range_value_data_element = driver.find_element(groupreporter.Range_value_xpath[0],groupreporter.Range_value_xpath[1].format(f"[{i}]"))
                Range_name_data_element = Range_value_data_element.find_element(groupreporter.Range_name_xpath[0],groupreporter.Range_name_xpath[1])
                Range_value_data = Range_value_data_element.text
                Range_name_data = Range_name_data_element.text
                range_data[Range_name_data] = Range_value_data
            except Exception as e:
                print(select_Testtype,"--------",str(e))
        if len(range_data) != 0:
            range_data_dict[0] = range_data
    except Exception as e:
        pass

def table_summary_of_group_reporter(driver,select_Testtype,Title,excelpath,table_summary_data_dict):
    try:
        test = str(select_Testtype).replace(" ", "").lower()
        if "HTTP Speed Download Test".replace(" ", "").lower() == test or "HTTP Speed Upload Test".replace(" ","").lower() == test:
            test = "http"
        table_summary_data_elements = driver.find_elements(groupreporter.table_summary_xpath[0],groupreporter.table_summary_xpath[1].format("",test))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", table_summary_data_elements[0])
        except Exception as e:
            pass
        for i in range(1,len(table_summary_data_elements)+1):
            table_summary = {}
            try:
                table_summary_data = extract_table_datas_content(driver,(groupreporter.table_summary_xpath[0],groupreporter.table_summary_xpath[1].format(f"[{i}]",test)),2,select_Testtype,Title,excelpath,extracttype='textContent',sub_tags=None)
                for item in table_summary_data[1:len(table_summary_data)]:
                    if select_Testtype == "WebTest" and str(item[0]).lower().replace(" ","") == "WebURL".lower():
                        table_summary[item[0]] = str(item[1]).lower().replace("...","").replace("more","").replace("less","").replace("\n",",").replace(" ","")
                    else:
                        table_summary[item[0]] = item[1]
                table_summary_data_dict[i] = table_summary
                print(table_summary)
            except Exception as e:
                print(select_Testtype,(groupreporter.table_summary_xpath[0],groupreporter.table_summary_xpath[1].format("",test)),"--------", str(e))
    except Exception as e:
        print(select_Testtype,"--------",str(e))

def comparsion_between_group_reporter_values_against_the_calculated_value(func,File, select_Testtype, parameter, key, value, Groupreportervalue,compared_data, flag_difference):
    if compare_values(value,func):
        comprasion_data = {"File": f'({File + "  " + select_Testtype}):- {parameter}', "Group reporter key": key,"Group reporter value": f"{Groupreportervalue}", "calculated csv value": f"{func}","Data validation": f"{key}:{Groupreportervalue} is equal to calculated {key}:{func}"}
        compared_data.append(comprasion_data)
    elif not compare_values(value, func):
        comprasion_data = {"File": f'({File + "  " +  select_Testtype}):- {parameter}', "Group reporter key": key,"Group reporter value": f"{Groupreportervalue}", "calculated csv value": f"{func}","Data validation": f"{key}:{Groupreportervalue} is not equal to calculated {key}:{func}"}
        compared_data.append(comprasion_data)
        flag_difference = True
    return flag_difference

def comparsionvaluesinlist_between_group_reporter_values_against_the_calculated_value(func,File, select_Testtype, parameter, key, value, Groupreportervalue,compared_data, flag_difference):
    if comparsion_values_in_bw_two_list(value,func):
        comprasion_data = {"File": f'({File + "  " + select_Testtype}):- {parameter}', "Group reporter key": key,"Group reporter value": f"{Groupreportervalue}", "calculated csv value": f"{func}","Data validation": f"{key}:{Groupreportervalue} is equal to calculated {key}:{func}"}
        compared_data.append(comprasion_data)
    elif not comparsion_values_in_bw_two_list(value, func):
        comprasion_data = {"File": f'({File + "  " +  select_Testtype}):- {parameter}', "Group reporter key": key,"Group reporter value": f"{Groupreportervalue}", "calculated csv value": f"{func}","Data validation": f"{key}:{Groupreportervalue} is not equal to calculated {key}:{func}"}
        compared_data.append(comprasion_data)
        flag_difference = True
    return flag_difference
def values_list_for_particular_header(df_gr,File, select_Testtype, parameter,key,Groupreportervalue,compared_data):
    try:
        df_data = df_to_values_list_for_particular_header(parameter, df_gr)
        df_data = [convert_to_float(value) for value in df_data]
        return df_data
    except Exception as e:
        comprasion_data = {"File": f'({File + "  " + select_Testtype}):- {parameter}', "Group reporter key": key,"Group reporter value": f"{Groupreportervalue}", "calculated csv value": f"Not calculated","Data validation": f'{key}:- parameter "{parameter}" name cant find in csv'}
        compared_data.append(comprasion_data)
        raise e

def avg_datavalidation_groupreporter(avg_parameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    try:
        value = re.sub(r'[A-Za-z]', '', testtypedata_value)
        ndecimalpoint = count_decimal_points(value)
        parameter = avg_parameter
        df = df_gr
        if df_gr_filtered_by is not None:
            for Columnheader, filtered_by in df_gr_filtered_by.items():
                df = filter_df(df, Columnheader, filtered_by)
        data_list = values_list_for_particular_header(df, csv_file, select_Testtype,parameter, testtypedata_data_key, testtypedata_value,compared_data)
        Avg_comparsion = comparsion_between_group_reporter_values_against_the_calculated_value
        flag_difference = Avg_comparsion(f"{avg(data_list):.{ndecimalpoint}f}", csv_file, select_Testtype, parameter, testtypedata_data_key,value, testtypedata_value, compared_data, flag_difference)
    except Exception as e:
        error_statment_for_group_reporter_for_data_validation(csv_file, select_Testtype, avg_parameter,testtypedata_data_key, testtypedata_value, compared_data,e,"def avg_datavalidation_groupreporter")
        pass
    finally:
        return flag_difference
def max_datavalidation_groupreporter(max_parameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    try:
        value = re.sub(r'[A-Za-z]', '', testtypedata_value)
        parameter = max_parameter
        ndecimalpoint = count_decimal_points(value)
        df = df_gr
        if df_gr_filtered_by != None:
            for Columnheader, filtered_by in df_gr_filtered_by.items():
                df = filter_df(df, Columnheader, filtered_by)
        data_list = values_list_for_particular_header(df,csv_file, select_Testtype,parameter, testtypedata_data_key, testtypedata_value,compared_data)
        max_comparsion = comparsion_between_group_reporter_values_against_the_calculated_value
        flag_difference = max_comparsion(f"{max(data_list):.{ndecimalpoint}f}", csv_file, select_Testtype, parameter, testtypedata_data_key,value, testtypedata_value, compared_data, flag_difference)
    except Exception as e:
        error_statment_for_group_reporter_for_data_validation(csv_file, select_Testtype, max_parameter,testtypedata_data_key, testtypedata_value, compared_data,e,"def max_datavalidation_groupreporter")
        pass
    finally:
        return flag_difference

def min_datavalidation_groupreporter(min_parameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    try:
        value = re.sub(r'[A-Za-z]', '', testtypedata_value)
        ndecimalpoint = count_decimal_points(value)
        parameter = min_parameter
        df = df_gr
        if df_gr_filtered_by is not None:
            for Columnheader, filtered_by in df_gr_filtered_by.items():
                df = filter_df(df, Columnheader, filtered_by)
        data_list = values_list_for_particular_header(df, csv_file, select_Testtype,parameter, testtypedata_data_key, testtypedata_value,compared_data)
        min_comparsion = comparsion_between_group_reporter_values_against_the_calculated_value
        flag_difference = min_comparsion(f"{min(data_list):.{ndecimalpoint}f}", csv_file, select_Testtype, parameter, testtypedata_data_key,value, testtypedata_value, compared_data, flag_difference)
    except Exception as e:
        error_statment_for_group_reporter_for_data_validation(csv_file, select_Testtype, min_parameter,testtypedata_data_key, testtypedata_value, compared_data,e,"def min_datavalidation_groupreporter")
        pass
    finally:
        return flag_difference
def aboveOrbelow_data_validation_groupreporter(aboveOrbelow_parameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,fliter_df_flag,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    try:
        parameter = aboveOrbelow_parameter
        start_range = extract_numeric_value(text=testtypedata_data_key)
        value = re.sub(r'[A-Za-z]', '', testtypedata_value)
        ndecimalpoint = count_decimal_points(str(value).replace("%",""))
        df = df_gr
        if df_gr_filtered_by is not None:
            for Columnheader, filtered_by in df_gr_filtered_by.items():
                df = filter_df(df, Columnheader, filtered_by)
        data_list = None
        data_list1 = None
        if fliter_df_flag == True:
            data_list1 = values_list_for_particular_header(df, csv_file, select_Testtype, parameter,testtypedata_data_key, testtypedata_value, compared_data)
            data_list = data_list1
        elif fliter_df_flag == False or fliter_df_flag == None:
            data_list1 = values_list_for_particular_header(df, csv_file, select_Testtype,parameter, testtypedata_data_key, testtypedata_value,compared_data)
            data_list = values_list_for_particular_header(df_gr, csv_file, select_Testtype, parameter, testtypedata_data_key,testtypedata_value, compared_data)
        if re.search('above', str(testtypedata_data_key).lower().replace(" ", ""), re.IGNORECASE):
            filtered_data_list = values_list_above(data_list1, start_range)
            percentage_for_above_comprasion = comparsion_between_group_reporter_values_against_the_calculated_value
            flag_difference = percentage_for_above_comprasion(f"{percentage(df_data=data_list, filtered_data_list=filtered_data_list):.{ndecimalpoint}f}", csv_file, select_Testtype,parameter, testtypedata_data_key, value, testtypedata_value, compared_data, flag_difference)
        elif re.search('below', str(testtypedata_data_key).lower().replace(" ", ""), re.IGNORECASE) or re.search('less', str(testtypedata_data_key).lower().replace(" ", ""), re.IGNORECASE):
            filtered_data_list = values_list_below(data_list1, start_range)
            percentage_for_below_comprasion = comparsion_between_group_reporter_values_against_the_calculated_value
            flag_difference = percentage_for_below_comprasion(f"{percentage(df_data=data_list, filtered_data_list=filtered_data_list):.{ndecimalpoint}f}", csv_file, select_Testtype,parameter, testtypedata_data_key, value, testtypedata_value, compared_data, flag_difference)
    except Exception as e:
        error_statment_for_group_reporter_for_data_validation(csv_file, select_Testtype, aboveOrbelow_parameter,testtypedata_data_key, testtypedata_value, compared_data,e,"def aboveOrbelow_data_validation_groupreporter")
        pass
    finally:
        return flag_difference
def aboveOrbelow_data_validation_groupreporter_with_fliter_df_flag_True(aboveOrbelow_parameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,fliter_df_flag=True,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    flag_difference = aboveOrbelow_data_validation_groupreporter(aboveOrbelow_parameter, df_gr, testtypedata_value, csv_file,
                                               select_Testtype, testtypedata_data_key, compared_data, flag_difference,
                                               fliter_df_flag, df_gr_filtered_by)
    return flag_difference
def aboveOrbelow_data_validation_groupreporter_with_fliter_df_flag_Flase(aboveOrbelow_parameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,fliter_df_flag=False,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    flag_difference = aboveOrbelow_data_validation_groupreporter(aboveOrbelow_parameter, df_gr, testtypedata_value, csv_file,
                                               select_Testtype, testtypedata_data_key, compared_data, flag_difference,
                                               fliter_df_flag, df_gr_filtered_by)
    return flag_difference
def betweenOrto_data_validation_groupreporter(aboveOrbelow_parameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,fliter_df_flag,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    try:
        parameter = aboveOrbelow_parameter
        start_range, end_range = testtypedata_data_key.split('to')
        start_range = extract_numeric_value(text=start_range)
        end_range = extract_numeric_value(text=end_range)
        value = re.sub(r'[A-Za-z]', '', testtypedata_value)
        ndecimalpoint = count_decimal_points(value.replace("%",""))
        df = df_gr
        if df_gr_filtered_by is not None:
            for Columnheader, filtered_by in df_gr_filtered_by.items():
                df = filter_df(df, Columnheader, filtered_by)
        data_list = None
        data_list1 = None
        if fliter_df_flag == True:
            data_list1 = values_list_for_particular_header(df, csv_file, select_Testtype,parameter, testtypedata_data_key, testtypedata_value,compared_data)
            data_list = data_list1
        elif fliter_df_flag == False:
            data_list1 = values_list_for_particular_header(df, csv_file, select_Testtype, parameter,testtypedata_data_key, testtypedata_value, compared_data)
            data_list = values_list_for_particular_header(df_gr, csv_file, select_Testtype, parameter,testtypedata_data_key, testtypedata_value, compared_data)
        filtered_data_list = values_list_betweenOrto(data_list1,start_range,end_range)
        percentage_for_below_comprasion = comparsion_between_group_reporter_values_against_the_calculated_value
        flag_difference = percentage_for_below_comprasion(f"{percentage(df_data=data_list, filtered_data_list=filtered_data_list):.{ndecimalpoint}f}", csv_file, select_Testtype,parameter, testtypedata_data_key, value, testtypedata_value, compared_data, flag_difference)
    except Exception as e:
        error_statment_for_group_reporter_for_data_validation(csv_file, select_Testtype, aboveOrbelow_parameter,testtypedata_data_key, testtypedata_value, compared_data,e,"def betweenOrto_data_validation_groupreporter")
        pass
    finally:
        return flag_difference
def betweenOrto_data_validation_groupreporter_with_fliter_df_True(aboveOrbelow_parameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,fliter_df_flag=True,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    flag_difference = betweenOrto_data_validation_groupreporter(aboveOrbelow_parameter, df_gr, testtypedata_value, csv_file,
                                              select_Testtype, testtypedata_data_key, compared_data, flag_difference,
                                              fliter_df_flag, df_gr_filtered_by)
    return flag_difference
def betweenOrto_data_validation_groupreporter_with_fliter_df_Flase(aboveOrbelow_parameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,fliter_df_flag=False,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    flag_difference = betweenOrto_data_validation_groupreporter(aboveOrbelow_parameter, df_gr, testtypedata_value, csv_file,
                                              select_Testtype, testtypedata_data_key, compared_data, flag_difference,
                                              fliter_df_flag, df_gr_filtered_by)
    return flag_difference
def Dropped_Packets_data_validation_groupreporter(dropparameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    try:
        # testtypedata_value = 0.00%(0)
        value1 = re.split("%", testtypedata_value)[0]
        value2 = re.split("%", testtypedata_value)[1].replace("(", "").replace(")", "")
        parameter = dropparameter
        df = df_gr
        if df_gr_filtered_by is not None:
            for Columnheader, filtered_by in df_gr_filtered_by.items():
                df = filter_df(df, Columnheader, filtered_by)
        filtered_data_list = values_list_for_particular_header(df, csv_file,select_Testtype, parameter, testtypedata_data_key,testtypedata_value, compared_data)
        data_list = values_list_for_particular_header(df_gr, csv_file, select_Testtype, parameter,testtypedata_data_key, testtypedata_value, compared_data)
        ndecimalpoint = count_decimal_points(value2)
        count_comparsion = comparsion_between_group_reporter_values_against_the_calculated_value
        percentage_comparsion = comparsion_between_group_reporter_values_against_the_calculated_value
        flag_difference = percentage_comparsion(f"{percentage(df_data=data_list, filtered_data_list=filtered_data_list):.{ndecimalpoint}f}",csv_file, select_Testtype, parameter, testtypedata_data_key, value2,testtypedata_value, compared_data, flag_difference)
        flag_difference = count_comparsion(len(filtered_data_list), csv_file, select_Testtype, parameter,testtypedata_data_key, value1, testtypedata_value, compared_data,flag_difference)
    except Exception as e:
        error_statment_for_group_reporter_for_data_validation(csv_file, select_Testtype, dropparameter,testtypedata_data_key, testtypedata_value, compared_data,e,"def Dropped_Packets_data_validation_groupreporter")
        pass
    finally:
        return flag_difference

def count_data_validation_groupreporter(countparameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    try:
        value = testtypedata_value
        parameter = countparameter
        df = df_gr
        if df_gr_filtered_by is not None:
            for Columnheader, filtered_by in df_gr_filtered_by.items():
                df = filter_df(df, Columnheader, filtered_by)
        data_list = values_list_for_particular_header(df, csv_file, select_Testtype,parameter, testtypedata_data_key, testtypedata_value,compared_data)
        count_comparsion = comparsion_between_group_reporter_values_against_the_calculated_value
        flag_difference = count_comparsion(Counter(list(data_list)).total(), csv_file, select_Testtype, parameter, testtypedata_data_key,value, testtypedata_value, compared_data, flag_difference)
    except Exception as e:
        error_statment_for_group_reporter_for_data_validation(csv_file,select_Testtype,countparameter,testtypedata_data_key,testtypedata_value,compared_data,e,"def Count_data_validation_groupreporter")
        pass
    finally:
        return flag_difference

def error_statment_for_group_reporter_for_data_validation(csv_file,select_Testtype,parameter,testtypedata_data_key,testtypedata_value,compared_data,e,funcname):
    comprasion_data = {"File": f'({csv_file + "  " + select_Testtype}):- {parameter}',
                       "Group reporter key": testtypedata_data_key,
                       "Group reporter value": f"{testtypedata_value}",
                       "calculated csv value": "Not calculated",
                       "Data validation": f"{testtypedata_data_key} : notcal due error  got in the function def {funcname}: {e}"}
    compared_data.append(comprasion_data)

def stringvaluesInlist_data_validation_groupreporter(stringvaluesparameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    try:
        value = testtypedata_value.split(",")
        parameter = stringvaluesparameter
        df = df_gr
        if df_gr_filtered_by is not None:
            for Columnheader, filtered_by in df_gr_filtered_by.items():
                df = filter_df(df, Columnheader, filtered_by)
        data_list = values_list_for_particular_header(df, csv_file, select_Testtype, parameter,testtypedata_data_key, testtypedata_value, compared_data)
        data_list = list(set([str(df_data1).split("_")[-1] for df_data1 in data_list]))
        OperatorNames_comparsion = comparsionvaluesinlist_between_group_reporter_values_against_the_calculated_value
        data = data_list
        # data = str(data_list).replace("['", "").replace("']", "").replace("'", "").replace(" ", "")
        flag_difference = OperatorNames_comparsion(data, csv_file, select_Testtype, parameter, testtypedata_data_key,value, testtypedata_value, compared_data, flag_difference)
    except Exception as e:
        error_statment_for_group_reporter_for_data_validation(csv_file, select_Testtype, stringvaluesparameter,testtypedata_data_key, testtypedata_value, compared_data,e,"def OperatorNames_data_validation_groupreporter")
        pass
    finally:
        return flag_difference
def Number_of_Detected_Operators_data_validation_groupreporter(detected_operatorsparameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    try:
        value = testtypedata_value
        parameter = detected_operatorsparameter
        df = df_gr
        if df_gr_filtered_by is not None:
            for Columnheader, filtered_by in df_gr_filtered_by.items():
                df = filter_df(df, Columnheader, filtered_by)
        data_list = values_list_for_particular_header(df, csv_file, select_Testtype, parameter,testtypedata_data_key, testtypedata_value, compared_data)
        data_list = list(set([str(df_data1).split("_")[0] for df_data1 in data_list]))
        count_comparsion = comparsion_between_group_reporter_values_against_the_calculated_value
        flag_difference = count_comparsion(len(data_list), csv_file, select_Testtype, parameter, testtypedata_data_key,value, testtypedata_value, compared_data, flag_difference)
    except Exception as e:
        error_statment_for_group_reporter_for_data_validation(csv_file, select_Testtype, detected_operatorsparameter,testtypedata_data_key, testtypedata_value, compared_data,e,"def Number_of_Detected_Operators_data_validation_groupreporter")
        pass
    finally:
        return flag_difference

def sum_data_validation_groupreporter(totaltestconductedparameter,df_gr,testtypedata_value,csv_file,select_Testtype,testtypedata_data_key,compared_data,flag_difference,df_gr_filtered_by:Optional[OrderedDict] = None) -> OrderedDict:
    try:
        value = testtypedata_value
        ndecimalpoint = count_decimal_points(value)
        parameter = totaltestconductedparameter
        df = df_gr
        if df_gr_filtered_by is not None:
            for Columnheader, filtered_by in df_gr_filtered_by.items():
                df = filter_df(df, Columnheader, filtered_by)
        data_list = values_list_for_particular_header(df, csv_file, select_Testtype, parameter,testtypedata_data_key, testtypedata_value, compared_data)
        count_comparsion = comparsion_between_group_reporter_values_against_the_calculated_value
        flag_difference = count_comparsion(f"{sum(data_list):.{ndecimalpoint}f}", csv_file, select_Testtype, parameter, testtypedata_data_key,value, testtypedata_value, compared_data, flag_difference)
    except Exception as e:
        error_statment_for_group_reporter_for_data_validation(csv_file, select_Testtype, totaltestconductedparameter,testtypedata_data_key, testtypedata_value, compared_data,e,"def Total_Test_Conducted_data_validation_groupreporter")
        pass
    finally:
        return flag_difference

def group_reporter_data_validation(df_gr,testtypedata,select_Testtype,csv_file,func_for_testtype,Title,result_same,result_Difference,result_status):
    flag_difference = False
    compared_data = []
    for i, testtypedata1 in testtypedata.items():
        for testtypedata_data_key, testtypedata_value in testtypedata1.items():
            comprasion_data = "None"
            parameter = "Notmentioned"
            try:
                test = testtypedata_data_key.strip()
                values_and_param = None# Remove leading and trailing spaces from test
                dlorul_flag = False
                df_gr_DLorUl = None
                if select_Testtype == "TCPiPerfTest" or select_Testtype == "UDPiPerfTest":
                    if i == 1:
                        dlorul = "DL"
                        dlorulvalues = func_for_testtype[dlorul]
                        for pattern, values in dlorulvalues.items():
                            if re.search(pattern.replace(" ", "").lower(), test.replace(" ", "").lower(), re.IGNORECASE) or compare_values(pattern.replace(" ", "").lower(),test.replace(" ", "").lower()) or re.match(pattern.replace(" ", "").lower(), test.replace(" ", "").lower(), re.IGNORECASE) :
                                values_and_param = values
                                break
                        if values_and_param != None:
                            if not re.search("Number of Detected Operators",test.replace(" ", "").lower(),re.IGNORECASE) and not re.search("Operator Names",test.replace(" ","").lower(),re.IGNORECASE):
                                dlorul_flag = True
                                df_gr_DLorUl = filter_df(df_gr,Columnheader="TestType",item="TCPiPerfDownload|UDPiPerfDownload|Download")
                    elif i == 2:
                        dlorul = "UL"
                        dlorulvalues = func_for_testtype[dlorul]
                        for pattern, values in dlorulvalues.items():
                            if re.search(pattern.replace(" ", "").lower(), test.replace(" ", "").lower(), re.IGNORECASE) or compare_values(pattern.replace(" ", "").lower(),test.replace(" ", "").lower()) or re.match(pattern.replace(" ", "").lower(), test.replace(" ", "").lower(), re.IGNORECASE):
                                values_and_param = values
                                break
                        if values_and_param != None:
                            if not re.search("Number of Detected Operators",test.replace(" ", "").lower(),re.IGNORECASE) and not re.search("Operator Names",test.replace(" ","").lower(),re.IGNORECASE):
                                dlorul_flag = True
                                df_gr_DLorUl = filter_df(df_gr,Columnheader="TestType",item="TCPiPerfUpload|UDPiPerfUpload|Upload")
                    elif i == 0:
                        for dlorul, dlorulvalues in func_for_testtype.items():
                            for pattern, values in dlorulvalues.items():
                                if re.search(pattern.replace(" ", "").lower(), test.replace(" ", "").lower(), re.IGNORECASE) or compare_values(pattern.replace(" ", "").lower(),test.replace(" ", "").lower()) or re.match(pattern.replace(" ", "").lower(), test.replace(" ", "").lower(), re.IGNORECASE):
                                    values_and_param = values
                                    break
                            if values_and_param != None:
                                if dlorul == "DL" and not re.search("Number of Detected Operators",test.replace(" ", "").lower(),re.IGNORECASE) and not re.search("Operator Names",test.replace(" ","").lower(),re.IGNORECASE):
                                    dlorul_flag = True
                                    df_gr_DLorUl = filter_df(df_gr,Columnheader="TestType",item="TCPiPerfDownload|UDPiPerfDownload|Download")
                                elif dlorul == "UL" and not re.search("Number of Detected Operators",test.replace(" ", "").lower(),re.IGNORECASE) and not re.search("Operator Names",test.replace(" ","").lower(),re.IGNORECASE):
                                    dlorul_flag = True
                                    df_gr_DLorUl = filter_df(df_gr,Columnheader="TestType",item="TCPiPerfUpload|UDPiPerfUpload|Upload")
                                break
                else :
                    for pattern, values in func_for_testtype.items():
                        if re.search(pattern.replace(" ","").lower(),test.replace(" ","").lower(),re.IGNORECASE)  or compare_values(pattern.replace(" ", "").lower(),test.replace(" ", "").lower()) or re.match(pattern.replace(" ", "").lower(), test.replace(" ", "").lower(), re.IGNORECASE):
                            values_and_param = values
                            break
                if values_and_param != None:
                    for func, parameters in values_and_param.items():
                        parameter = parameters[0]
                        replace_flag = False
                        replaced_by = None
                        if "StreamTest" == select_Testtype or "WebTest" == select_Testtype:
                            if parameters[1] is not None:
                                for Columnheader, filtered_by in parameters[1].items():
                                    if '"_"' == filtered_by:
                                        replaced_by = testtypedata_data_key.split("-")[1]
                                        parameters[1][Columnheader]= testtypedata_data_key.split("-")[1]
                                        replace_flag = True
                                        testtypedata_data_key = testtypedata_data_key.split("-")[0]
                                        break
                        if dlorul_flag == False:
                            if not df_gr.empty:
                                flag_difference = func(parameter, df_gr, testtypedata_value,csv_file, select_Testtype, testtypedata_data_key, compared_data,flag_difference,df_gr_filtered_by=parameters[1])
                            elif df_gr.empty:
                                comprasion_data = {"File": f'({csv_file + "  " + select_Testtype}):- {parameter}',
                                                   "Group reporter key": testtypedata_data_key,
                                                   "Group reporter value": f"{testtypedata_value}",
                                                   "calculated csv value": "0",
                                                   "Data validation": f"{testtypedata_data_key} : not calcaluated because values/data is not present in csv. Please check in csv."}
                                compared_data.append(comprasion_data)
                        elif dlorul_flag == True:
                            if not df_gr_DLorUl.empty:
                                flag_difference = func(parameter, df_gr_DLorUl, testtypedata_value,csv_file, select_Testtype, testtypedata_data_key, compared_data,flag_difference,df_gr_filtered_by=parameters[1])
                            elif df_gr_DLorUl.empty:
                                comprasion_data = {"File": f'({csv_file + "  " + select_Testtype}):- {parameter}',
                                                   "Group reporter key": testtypedata_data_key,
                                                   "Group reporter value": f"{testtypedata_value}",
                                                   "calculated csv value": "0",
                                                   "Data validation": f"{testtypedata_data_key} : not calcaluated because values/data is not present in csv. Please check in csv."}
                                compared_data.append(comprasion_data)
                        if replace_flag == True:
                            if parameters[1] is not None:
                                for Columnheader, filtered_by in parameters[1].items():
                                    if replaced_by == filtered_by:
                                        parameters[1][Columnheader]= '"_"'
                                        break
                elif values_and_param == None:
                    comprasion_data = {"File": f'({csv_file + "  " + select_Testtype}):- {parameter}',"Group reporter key": testtypedata_data_key,"Group reporter value": f"{testtypedata_value}","calculated csv value": f"notcal","Data validation": f"{testtypedata_data_key} : Notcal"}
                    compared_data.append(comprasion_data)
            except Exception as e:
                print(testtypedata_value)
                comprasion_data = {"File": f'({csv_file + "  " + select_Testtype}):- {parameter}',"Group reporter key": testtypedata_data_key,"Group reporter value": f"{testtypedata_value}","calculated csv value": f"notcal","Data validation": f"{testtypedata_data_key}: Notcal"}
                compared_data.append(comprasion_data)
    if flag_difference == False:
        r_result = status(Title=Title, component=select_Testtype, status="PASSED", comments="Values are same")
        result_same.put(compared_data)
        result_status.put(r_result)
    elif flag_difference == True:
        r_result = status(Title=Title, component=select_Testtype, status="FAILED", comments="Values are different")
        result_Difference.put(compared_data)
        result_status.put(r_result)
    df = pd.DataFrame(compared_data)
    allure.attach(df.to_html(), f"Table data{str(select_Testtype)}", AttachmentType.HTML)
