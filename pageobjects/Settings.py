import time
from module_controllers.module_controllers import default_settings_module_controllers, \
    change_settings_module_controllers
from utils.library import *
from locators.locators import *
from pageobjects.login_logout import *
from pageobjects.Dashboard import *
import pandas as pd
from utils.updateexcelfile import *
import re
################################################ For all 26 parameters and it's data in Settings section [Default] ###################################################################################################
def dashboard_default_setting(driver,combine_dict):
    Page_Down(driver)
    clickec(driver, settings_1.btn_setting)
    time.sleep(2)
    Page_Down(driver)
    try:
        WebDriverWait(driver, 90).until(EC.presence_of_element_located(settings_1.default_settings1))
    except:
        pass
    clickec(driver, settings_1.default_settings_btn)
    time.sleep(2)
    clickec(driver, settings_1.save_settings_btn)
    time.sleep(2)
    data_extraction_settings(driver, combine_dict)
    click(driver=driver, locators=Login_Logout.dashboard_id)

############################################# Extraction of data in Map Legend and NQC Table ########################################################################################################################################3
def Map_legend_and_NQC(driver,campaign,excelpath,datas1,datas2,excelpath_for_storedata):
    driver.implicitly_wait(5)

    remote_test_point, map_start_point, graph_start_point, export_start_point, load_start_point, PDF_Export_index_start_point, END_index = fetch_input_points()
    tests = fetch_components(campaign, map_start_point, graph_start_point)
    skip_tests = ['Failed Call', 'Web test', 'Sent SMS', 'Received SMS', 'Failed SMS', 'nrArfcn', 'nrPCI', 'nrCID','ECNO', 'BCCH_ARFCN', 'PSC', 'PCI', 'Data Type', 'Network Type', 'Arfcn', 'lteCID']
    # tests = [test for test in tests_list if test not in skip_tests]
    map_legend_nqc_components(driver,tests,excelpath, datas1, datas2,excelpath_for_storedata,skip_tests)
    driver.implicitly_wait(30)
def map_legend_nqc_components(driver,tests,excelpath, datas1, datas2,excelpath_for_storedata,skip_tests):
    Title = "MAP VIEW"
    e_flag = None
    try:
        # Notestdatafound_elements = driver.find_elements(*select_Map_View_Components.No_test_data_element)
        try:
            while WebDriverWait(driver, 2).until(EC.visibility_of_element_located(select_Map_View_Components.No_test_data_element)):
                if WebDriverWait(driver, 3).until(EC.invisibility_of_element_located(select_Map_View_Components.No_test_data_element)):
                    break
        except Exception as e:
            pass
        try:
            enable_of_element_untill_loaded(driver, select_Map_View_Components.Expand_Map_View[:2], 1)
            clickec(driver, select_Map_View_Components.Expand_Map_View)
            while WebDriverWait(driver, 1).until( EC.invisibility_of_element_located(close_button.closeFullTableView[:2])):
                clickec(driver, select_Map_View_Components.Expand_Map_View)
                if WebDriverWait(driver, 3).until(EC.visibility_of_element_located(close_button.closeFullTableView[:2])):
                    break
        except Exception as e:
            pass
            # Load pattern mapping from Excel file
        if WebDriverWait(driver, 3).until(EC.invisibility_of_element_located(select_Map_View_Components.No_test_data_element)):
            try:
                pattern_mapping_df = pd.read_excel(config.settings_path,sheet_name="MAP_SETTINGS")
            except Exception as e:
                with allure.step(f"Check {config.settings_path}"):
                    print(f"Check {config.settings_path}")
                    assert False
            pattern_mapping = pattern_mapping_df.set_index('TC Sheet Components').apply(lambda x: x.dropna().tolist(),axis=1).to_dict()
            try:
                pattern_mapping_df1 = pd.read_excel(config.map_view_components_excelpath)
            except Exception as e:
                with allure.step(f"Check {config.map_view_components_excelpath}"):
                    print(f"Check {config.map_view_components_excelpath}")
                    assert False
            # Convert pattern mapping to dictionary
            pattern_mapping1 = pattern_mapping_df1.set_index('Map view Components').apply(lambda x: x.dropna().tolist(),axis=1).to_dict()
            txt = []
            if tests.__len__() == 0:
                statement = f"Map-View  --  Nothing is marked 'Yes' in {str(config.test_data_path)}"
                with allure.step(f"Nothing is marked 'Yes' in {str(config.test_data_path)} for 'Map-View"):
                    # updatename(excelpath, statement)
                    updatecomponentstatus(Title, "", "FAILED", f"Nothing marked in {str(config.test_data_path)}",excelpath)
                    e = Exception
                    raise e
            else:
                for test in tests:
                    test = test.strip()
                    for pattern, values in pattern_mapping.items():
                        if pattern.lower() == test.lower():
                            txt = values[1:3]
                            test = values[0]
                            break
                        else:
                            txt = []
                    # extraction of operator comparison for skipped tests for running "operator comparison v/s PDF Export"
                    if txt == []:
                        for pattern1, values1 in pattern_mapping1.items():
                            if pattern1.lower() == test.lower():
                                txt = values1
                                break
                            else:
                                txt = []
                    # time.sleep(0.1)
                    try:
                        try:
                            listbox = WebDriverWait(driver, 0.1).until(EC.visibility_of_element_located(select_Map_View_Components.map_menu_dropdown))
                            if listbox.is_displayed():
                                listbox_btn = WebDriverWait(driver, 1.2).until(EC.visibility_of_element_located(select_Map_View_Components.Test_Type_Dropdown))
                                listbox_btn.click()
                        except:
                            pass
                        Map_view_Search_Box_not_visible_do_page_up_(driver)
                        data = read_map_legend(driver, select_Map_View_Components.Test_Type_Dropdown,select_Map_View_Components.nested_locators1,select_Map_View_Components.Call_Test_locator, txt, test, Title,excelpath, test,excelpath_for_storedata,skip_tests)
                        if not skip_tests.__contains__(test):
                            if data['operator_comparsion_table_data']:
                                if test not in datas1:
                                    datas1[test] = []
                                datas1[test].extend(data['operator_comparsion_table_data'])

                            if data['map_legend_data']:
                                if test not in datas2:
                                    datas2[test] = []
                                datas2[test].extend(data['map_legend_data'])
                    except Exception as e:
                        continue
            click_closeButton(driver)
        elif WebDriverWait(driver, 3).until(EC.visibility_of_element_located(select_Map_View_Components.No_test_data_element)):
            statement = f"Failed to click on the expand for {Title}"
            with allure.step(statement):
                allure.attach(driver.get_screenshot_as_png(), name=f"Expand_Map_View_screenshot",attachment_type=allure.attachment_type.PNG)
                e = Exception
                raise e
    except Exception as e:
        Notestdatafound_elements = driver.find_elements(By.XPATH,"// h3[contains(text(), 'No test data found. Please try different date and ')]")
        closeFullTableView_elements = driver.find_elements(close_button.closeFullTableView[0],close_button.closeFullTableView[1])
        if len(closeFullTableView_elements) == 0:
            statement = f"Failed to click on expand button for {Title}"
            # Failupdatename(excelpath, statement)
            updatecomponentstatus(Title, "Expand_Map_View", "FAILED", statement, excelpath)
        elif e_flag == 1:
            print('select Map View Components fail')
        elif len(Notestdatafound_elements) != 0:
            statement = f"No test data found. 'Please try different date in Map View' statement is present due to that map didn't load"
            # Failupdatename(excelpath, statement)
            updatecomponentstatus(Title, "No test data found. Please try different date", "FAILED", statement,excelpath)
def read_map_legend(driver, listbox_locator, nested_locators1, Call_Test_locator, option_text_list, elementname,Title, excelpath, test,excelpath_for_storedata,skip_tests):
    ListboxSelectstatus = "None"
    map_legend_data = []
    operator_comparsion_table_data = []
    with allure.step(f"Map View Select '{elementname}' and Read Data"):
        try:
            # time.sleep(1)
            try:
                wait_for_loading_elements(driver)
            except:
                pass
            l_flag = 0
            if option_text_list.__len__() == 0:
                with allure.step(f"In input data from {str(config.map_view_components_excelpath)} for 'Map-View for '{test}' in header of Map view Components column value against the 2nd row of headers of Map view in {str(config.test_data_path)} is mismatch/empty"):
                    l_flag = 2
                    allure.attach(driver.get_screenshot_as_png(), name=f"{elementname}_screenshot",attachment_type=allure.attachment_type.PNG)
                    e = Exception
                    raise e
            elif ["Call Test", "Call Test"] != option_text_list and ['Call Test','Failed Calls'] != option_text_list:
                ListboxSelectstatus, alert_text = select_from_listbox_ECs(driver, listbox_locator, nested_locators1,option_text_list, Title, excelpath)
                l_flag = 1
            elif ["Call Test", "Call Test"] == option_text_list:
                clickEC_for_listbox(driver, Map_View_Select_and_ReadData.Test_Type_Dropdown_for_call_Test, Title, excelpath)
                clickEC_for_listbox(driver, Map_View_Select_and_ReadData.Call_Test_locator2, Title, excelpath)
                ListboxSelectstatus, alert_text = clickEC_for_listbox(driver, Call_Test_locator, Title, excelpath)
                l_flag = 1
            elif ['Call Test', 'Failed Calls'] == option_text_list:
                clickEC_for_listbox(driver, Map_View_Select_and_ReadData.Test_Type_Dropdown_for_call_Test, Title,excelpath)
                clickEC_for_listbox(driver, Map_View_Select_and_ReadData.Call_Test_locator2, Title, excelpath)
                ListboxSelectstatus, alert_text = clickEC_for_listbox(driver,Map_View_Select_and_ReadData.Failed_calls_locator,Title, excelpath)
                l_flag = 1
            # time.sleep(1)
            try:
                wait_for_loading_elements(driver)
            except:
                pass
            if alert_text == None and l_flag == 1:
                try:
                    try:
                        Webtest = operator_comparison_table.operator_comparison_web
                        result_list = extract_table_datas_span1(driver, Webtest,"Operator comparsion table",option_text_list[-1], Title,excelpath)
                        result_list1 = []
                        try:
                            webtest2 = operator_comparison_table.operator_comparison_web_siblingtable
                            result_list1 = extract_table_datas_span1(driver, webtest2, "Operator comparsion table",option_text_list[-1], Title, excelpath)
                        except:
                            pass
                        operator_comparsion_table_data_for_store = []
                        for i in range(len(result_list[0])):
                            operator_comparsion_table_data_for_store.append([result_list[0][i], result_list[1][i]])
                        for i in range(len(result_list1[0])):
                            operator_comparsion_table_data_for_store.append([result_list1[0][i], result_list1[1][i]])
                    except:
                        operator_comparsion_table = operator_comparison_table.Operator_comparison_data
                        operator_comparsion_table_data_for_store = extract_table_datas_span1(driver,operator_comparsion_table,"Operator comparsion table",option_text_list[-1], Title,excelpath)
                except:
                    pass
                # This below try expect is exceuted to extract the operator comparison data from map.
                # where this data used for NQC-operator comparison V/S PDF Export table.
                try:
                    Title_ocvspdf = "Map view(NQC-operator comparison V/S PDF Export)"
                    try:
                        if len(operator_comparsion_table_data_for_store) != 0:
                            operator_comparsion_table_data_for_store.insert(0, [option_text_list[-1]])
                            operator_comparsion_table_data_for_store.append(["ENDHERE"])
                            export_pdf_update_to_excel(operator_comparsion_table_data_for_store,"OPERATOR_COMPARISON", option_text_list[-1], excelpath_for_storedata)
                            updatecomponentstatus(Title_ocvspdf, str(test), "PASSED",f"Passed step :- In Operator comparison table for {option_text_list[-1]} data is found in table",excelpath)
                        elif len(operator_comparsion_table_data_for_store) == 0 or operator_comparsion_table_data_for_store == None:
                            e = Exception
                            raise e
                    except Exception:
                        if len(operator_comparsion_table_data_for_store) == 0 or operator_comparsion_table_data_for_store == None:
                            with allure.step(f"Failed step :- In Operator comparsion table for {option_text_list[-1]} No data in table/No table"):
                                statement = f"No data found in operator comparison table for {option_text_list[-1]}"
                                updatecomponentstatus(Title_ocvspdf, "Operator comparison table data", "FAILED", statement,excelpath)
                                # Failupdatename(excelpath,f"Failed step :- In Operator comparsion table for {option_text_list[-1]} No data in table")
                                raise Exception
                        elif len(operator_comparsion_table_data_for_store) != 0:
                            with allure.step(f"Failed step :- In Operator comparsion table for {option_text_list[-1]} error in insert/appending data to Excel report"):
                                statement = f"Error in insert/appending data to excel report for {option_text_list[-1]}"
                                updatecomponentstatus(Title_ocvspdf, "Operator comparison table data", "FAILED", statement, excelpath)
                                # Failupdatename(excelpath, f"Failed step :- In Operator comparsion table for {option_text_list[-1]} error in insert/appending data to Excel report")
                                raise Exception
                except:
                    pass
                if not skip_tests.__contains__(test):
                    try:
                        # time.sleep(1)
                        operator_data = driver.find_elements(*settings_1.operator_comparison_data)
                        for i in range(len(operator_data)):
                            j = operator_data[i].text
                            list_a = ['>=', 'B/w', 'below', '-', '>', 'Bw', 'above', '<=']
                            list_b = ["to",">"]
                            list_c = ["Call"]
                            if any(a.lower() in j.lower() for a in list_a) and not any(c.lower() in j.lower() for c in list_c):
                                operator_comparsion_table_data.append(j)
                            elif any(b.lower() in j.lower() for b in list_b) and test == "Call Test" and i<=3:
                                operator_comparsion_table_data.append(j)
                    except:
                        pass
                    try:
                        if len(operator_comparsion_table_data) != 0:
                            with allure.step("Operator Comparison Data Extraction"):
                                # updatecomponentstatus("MAP VIEW", str(test), "PASSED",f"Passed step :- In Operator comparison table for {option_text_list[-1]} data is found in table",excelpath)
                                allure.attach(driver.get_screenshot_as_png(), name="Operator Comparison Data",attachment_type=allure.attachment_type.PNG)
                        elif (len(operator_comparsion_table_data) == 0 or operator_comparsion_table_data == None) and test != "iperf Download Test" and test != "iperf Upload Test":
                            e = Exception
                            raise e
                    except Exception:
                        if len(operator_comparsion_table_data) == 0 or operator_comparsion_table_data == None:
                            with allure.step(f"Failed step :- In Operator comparsion table for {option_text_list[-1]} No data in table"):
                                statement = f"No data found in operator comparison table for {option_text_list[-1]}"
                                updatecomponentstatus(Title, "Operator comparison table data", "FAILED", statement, excelpath)
                                # Failupdatename(excelpath,f"Failed step :- In Operator comparison table for {option_text_list[-1]} No data in table")
                                raise Exception
                    try:
                        # time.sleep(1)
                        map_legend = driver.find_elements(*settings_1.map_legend_each_elements)
                        for m in range(len(map_legend)):
                            l = map_legend[m].text
                            if test != "Call Test" and test != "Stream Test" and l.lower().replace(" ","") != "dropped packets".lower().replace(" ",""):
                                map_legend_data.append(l)
                    except:
                        pass
                    try:
                        if len(map_legend_data) != 0:
                            with allure.step("Map Legend Data Extraction"):
                                # updatecomponentstatus("MAP VIEW", str(test), "PASSED",f"Passed step :- In Map Legend for {option_text_list[-1]} data is found",excelpath)
                                allure.attach(driver.get_screenshot_as_png(), name="Map Legend Data",attachment_type=allure.attachment_type.PNG)
                        elif len(map_legend_data) == 0 or map_legend_data == None and test != "Call Test" and test != "Stream Test":
                            e = Exception
                            raise e
                    except Exception:
                        if len(map_legend_data) == 0 or map_legend_data == None:
                            with allure.step(f"Failed step :- In Map Legend for {option_text_list[-1]}there is no data"):
                                statement = f"No data found in map legend for {option_text_list[-1]}"
                                updatecomponentstatus(Title, "Map Legend data", "FAILED", statement, excelpath)
                                # Failupdatename(excelpath,f"Failed step :- In Map Legend for {option_text_list[-1]} there is no data")
                                raise Exception
            elif ListboxSelectstatus == 0 and alert_text != None and l_flag == 1:
                e = Exception
                with allure.step(f"failed step :- Alert Found is '{alert_text}' for Map View to select {elementname}"):
                    updatecomponentstatus(Title, elementname, "FAILED",f"Alert Found is '{alert_text}' for Map View to select {elementname}",excelpath)
                    raise e
        except Exception as e:
            print("Map View Select and Read Data fail")
            if l_flag == 0:
                statement = f"Unable to locate the element/No such element found and so error in selecting " + str(option_text_list) + " from listbox"
                with allure.step(statement):
                    allure.attach(driver.get_screenshot_as_png(), name=f"{elementname}_screenshot",attachment_type=allure.attachment_type.PNG)
                    updatecomponentstatus(Title, "Map View select and Read data", "FAILED", statement, excelpath)
                    # Failupdatename(excelpath, statement)
                    raise e
            elif option_text_list.__len__() == 0 and l_flag == 2:
                statement = f"In input data from {str(config.map_view_components_excelpath)} for 'Map-View for '{test}' in header of Map view Components column value against the 2nd row of headers of Map view in {str(config.test_data_path)} is mismatch/empty"
                with allure.step(statement):
                    allure.attach(driver.get_screenshot_as_png(), name=f"{elementname}_screenshot",attachment_type=allure.attachment_type.PNG)
                    # Failupdatename(excelpath, statement)
                    updatecomponentstatus("MAP VIEW", str(test), "FAILED", statement, excelpath)
                    raise e
            elif alert_text != None and l_flag == 1:
                statement = f"Alert Found is '{alert_text}' for Map View to select {elementname}"
                with allure.step(statement):
                    allure.attach(driver.get_screenshot_as_png(), name=f"{elementname}_screenshot",attachment_type=allure.attachment_type.PNG)
                    # Failupdatename(excelpath, statement)
                    raise e
    return {'map_legend_data': map_legend_data, 'operator_comparsion_table_data': operator_comparsion_table_data}

def settings_pdf(driver, campaign, data_combine_dict, excelpath):
    remote_test_point, map_start_point, graph_start_point, export_start_point, load_start_point, PDF_Export_index_start_point, END_index = fetch_input_points()
    tests_list = fetch_components(campaign, PDF_Export_index_start_point, END_index)
    # List of parameters
    skip_tests = ['Failed Call', 'Web test', 'Sent SMS', 'Received SMS', 'Failed SMS', 'nrArfcn', 'nrPCI', 'nrCID','ECNO', 'BCCH_ARFCN', 'PSC', 'PCI', 'Data Type', 'Network Type', 'Arfcn', 'lteCID']
    tests = [test for test in tests_list if test not in skip_tests]
    settings_pdf_data(driver, tests, data_combine_dict, excelpath)
def settings_pdf_data(driver,tests,data_combine_dict,excelpath):
    Title = "PDF Data"
    with allure.step("PDF Data Extraction"):
        time.sleep(1)
        List_of_options_txt = ["Export As PDF"]
        allure.attach(driver.get_screenshot_as_png(), name="PDF Data Extraction",attachment_type=allure.attachment_type.PNG)
        try:
            select_from_listbox_ECs(driver, List_Of_Campaigns_Export_Dashboard.List_Of_Campaigns_Export_Dropdown,List_Of_Campaigns_Export_Dashboard.List_Of_Campaigns_Export_Dropdown_Options,List_of_options_txt, Title, excelpath)
        except:
            pass
        time.sleep(4)
        driver.switch_to.window(driver.window_handles[1])
        try:
            pdf_listbox_locator = (By.XPATH, "//div[@id='checkboxes']//input[@type='checkbox']")
            WebDriverWait(driver, 2).until(EC.visibility_of_element_located(pdf_listbox_locator))
        except Exception as e:
            try:
                driver.close(driver.window_handles[1])
                driver.switch_to.window(driver.window_handles[0])
                List_of_options_txts = [["Export"], ["Export As PDF"]]
                allure.attach(driver.get_screenshot_as_png(), name="PDF Data Extraction",attachment_type=allure.attachment_type.PNG)
                for List_of_options_txt in List_of_options_txts:
                    try:
                        select_from_listbox_ECs(driver,List_Of_Campaigns_Export_Dashboard.List_Of_Campaigns_Export_Dropdown,List_Of_Campaigns_Export_Dashboard.List_Of_Campaigns_Export_Dropdown_Options,List_of_options_txt, Title, excelpath)
                    except:
                        pass
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[1])
            except Exception as e:
                pass
        time.sleep(2)
        try:
            pattern_mapping_df = pd.read_excel(config.settings_path,sheet_name="PDF_SETTINGS")
        except Exception as e:
            with allure.step(f"Check {config.settings_path}"):
                print(f"Check {config.settings_path}")
                assert False
        pattern_mapping = pattern_mapping_df.set_index('pdf_export').apply(lambda x: x.dropna().tolist(),axis=1).to_dict()
        txt = []
        if tests.__len__() == 0:
            statement = f"Map-View  --  Nothing is marked 'Yes' in {str(config.test_data_path)}"
            with allure.step(f"Nothing is marked 'Yes' in {str(config.test_data_path)} for 'Map-View"):
                # updatename(excelpath, statement)
                updatecomponentstatus(Title, "", "FAILED", f"Nothing marked in {str(config.test_data_path)}",excelpath)
                e = Exception
                raise e
        else:
            for test in tests:
                test = test.strip()
                for pattern, values in pattern_mapping.items():
                    if pattern.lower() == test.lower():
                        txt = values
                        break
                    else:
                        txt = []
                if len(txt) !=0:
                    # parameters = ['Ping Test', 'Download Test', 'Upload Test', 'Http Download Test','Http Upload Test','iPerf Test','Call Test','Stream Test','RSSI/RSCP','RSRP','RSRQ','nrSsRsrp','nrSsRsrq','lteSNR','nrSsSinr']  # Add your parameters here
                    parameter = txt[0]
                    try:
                        parameter1 = parameter.replace(" ","")
                        driver.execute_script(f"window.scrollTo({int(0)}, {int(0)})")
                        checkbox_xpath = (By.XPATH, f"//div[@id='checkboxes']//*[contains(., '{parameter1}')]",parameter1)
                        # Find and click the checkbox for the current parameter
                        checkbox = driver.find_element(*checkbox_xpath[:2])
                        if checkbox.is_enabled():
                            # checkbox.click()
                            clickec(driver,checkbox_xpath)
                            time.sleep(8)
                        else:
                            print(f"Checkbox corresponding to parameter '{parameter}' is not enabled. Skipping.")
                            continue  # Skip collecting PDF data for this parameter if checkbox is not enabled
                    except (NoSuchElementException, ElementNotInteractableException):
                        print(f"Checkbox corresponding to parameter '{parameter}' not found or not interactable.")
                        continue  # Skip collecting PDF data for this parameter if checkbox is not found or not interactable
                    locator = None
                    pdf_data = []  # Reset pdf_data for each parameter
                    try:
                        testtype = str(txt[1]).replace(' ','')
                        # locator = (By.XPATH,f"//div[@id ='{testtype}']//td[1]//span")
                        locator = (By.XPATH, f"//table[@id='{testtype}']//td[1]")

                        if locator:
                            time.sleep(2)
                            elements = driver.find_elements(*locator)
                            # for element in elements:
                            for i in range(len(elements)):
                                j = elements[i].text
                                try:
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});",elements[i])
                                except Exception as e:
                                    pass
                                list_a = ['>=', 'B/w', 'below', '-', '>', 'Bw', 'above', '<=']
                                list_b = ["to",">"]
                                list_c = ["Call"]
                                if any(a.lower() in j.lower() for a in list_a) and not any(c.lower() in j.lower() for c in list_c):
                                    pdf_data.append(j)
                                elif any(a.lower() in j.lower() for a in list_b) and parameter == "Call Test" and i <= 3:
                                    pdf_data.append(j)
                    except Exception as e:
                        pass
                    if pdf_data:  # Check if pdf_data is not empty
                        data_combine_dict[parameter] = pdf_data
                allure.attach(driver.get_screenshot_as_png(), name="PDF Data",attachment_type=allure.attachment_type.PNG)
        try:
            time.sleep(2)
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            # Print or return the combined values
            print(data_combine_dict)
        except:pass
def main_func_default_settings(driver,environment,userid):
    Default_settings_runvalue = default_settings_module_controllers()
    # runvalue = Testrun_mode(value="Default Settings")
    if "Yes".lower() == Default_settings_runvalue[-1].strip().lower():
        combine_dict = {}
        dashboard_default_setting(driver,combine_dict)
        combine_dict1 = {}
        data = {
            'Test_Type': [],
            'Parameter': [],
        }
        for key, values in combine_dict.items():
            combine_dict1[key] = [{setting: extract_numerical_values(setting)} for setting in values]
        for test_type, values in combine_dict1.items():
            for value in values:
                for param, param_values in value.items():
                    data['Test_Type'].append(test_type)
                    data['Parameter'].append(param)
        # Convert to DataFrame
        df = pd.DataFrame(data)
        default_excel_path = config.test_data_folder_rootpath +f"\\testdata\\{environment}_{userid}_default_setting.xlsx"
        # Write DataFrame to Excel
        df.to_excel(default_excel_path, index=False)
def main_default_settings(driver, campaign, remote_test_campaign, device, excelpath, environment, userid, final_result,excelpath_for_storedata):
    Default_settings_runvalue = default_settings_module_controllers()
    # runvalue = Testrun_mode(value="Default Settings")
    Title = "Default Settings"
    datas1 = {}
    datas2 = {}
    data_combine_dict = {}
    combine_dict1 = {}
    if "Yes".lower() == Default_settings_runvalue[-1].strip().lower():
        default_excel_path = config.test_data_folder_rootpath +f"\\testdata\\{environment}_{userid}_default_setting.xlsx"
        df = pd.read_excel(default_excel_path)
        combine_dict = df.groupby("Test_Type")["Parameter"].apply(list).to_dict()
        Map_legend_and_NQC(driver,campaign,excelpath,datas1,datas2,excelpath_for_storedata)
        settings_pdf(driver, campaign, data_combine_dict, excelpath)
        # Updating settings, Operator Comparison, Map Legend and PDF Data to excel
        updating_settings_data_extraction_to_excel(combine_dict, datas1, datas2, data_combine_dict, excelpath_for_storedata,"DATA_EXTRACTION_SETTINGS")

        # Extracting only numerical values from the "Settings" section
        for key, values in combine_dict.items():
            combine_dict1[key] = [extract_numerical_values(setting) for setting in values]
        # Calling comparison function to compare the settings data against operator comparison, map_legend and pdf data
        comparison(datas1, datas2, data_combine_dict, combine_dict1, final_result, Title, excelpath, campaign, remote_test_campaign, device)

    elif "No".lower() == Default_settings_runvalue[-1].strip().lower():
        statement = "You have selected Not to execute"
        with allure.step(statement):
            updatecomponentstatus(Title, "Not to execute", "SKIPPED", "You have selected No for execute", excelpath)
            pass

############################################### Function for comparison settings module #############################################################################################################
def comparison(datas1, datas2, data_combine_dict, combine_dict,final_result,Title,excelpath,campaign, remote_test_campaign, device):
    # Validation point to check whether the data from excel is correctly updated in the Application
    excel_data = pd.read_excel("C:\\RantCell_Automation_Data_and_Reports\\testdata\\Change_settings.xlsx",dtype={'Value': str})
    dict_exceldata = excel_data.groupby("Test_Type")["Value"].apply(list).to_dict()
    testtype =[]
    if Title == "Change Settings":
        for settingparameter, values in dict_exceldata.items():
            if settingparameter in combine_dict:
                flag_failed = True
                observed_values = combine_dict[settingparameter]
                extracted_settings = [numeric_value for observed_numeric_value in observed_values for numeric_value in observed_numeric_value]
                comparison_results = []
                i = 0
                for expected_value in values:
                    i += 1
                    matched = [numeric_value for numeric_value in extracted_settings if compare_values(str(numeric_value).replace("-", ""),str(expected_value).replace("-", ""))]
                    if matched:
                        comparison_results.append({"Usercampaignname,Classifier,Device":f"{remote_test_campaign},{campaign},{device}","SETTINGS_PARAMETER_NAME(Reference)": settingparameter,f"EXCEL VALUE": f"{expected_value}",f"SETTINGS_APPLICATION_VALUE(Reference)": f"{matched}",f"Data validation": "The value is found"})
                    else:
                        flag_failed = False
                        comparison_results.append({"Usercampaignname,Classifier,Device":f"{remote_test_campaign},{campaign},{device}","SETTINGS_PARAMETER_NAME(Reference)": settingparameter,f"EXCEL VALUE": f"{expected_value}",f"SETTINGS_APPLICATION_VALUE(Reference)": f"{extracted_settings[i]}",f"Data validation": "The value is Not Found"})
                final_result["SETTINGS"].extend(comparison_results)
                if flag_failed == True:
                    updatecomponentstatus(Title=Title,componentname=f"{settingparameter} --> Excel Data vs Change Settings Data(Application)",status="PASSED",comments=f"The values are found when comparing Excel Data vs Change Settings Data(Application)",path=excelpath)
                elif flag_failed == False:
                    testtype.append(settingparameter)
                    updatecomponentstatus(Title=Title,componentname=f"{settingparameter} --> Excel Data vs Change Settings Data(Application)",status="FAILED",comments=f"The values are Not found when comparing Excel Data vs Change Settings Data(Application)",path=excelpath)
    # Comparison function starts from here
    dict_list = {
        "Operator_Comparison": datas1,
        "Map_Legend": datas2,
        "Pdf_Data": data_combine_dict
    }
    for reference_key in combine_dict.keys():
        i = 0
        for view_key, other_dict in dict_list.items():
            for other_key, other_values in other_dict.items():
                matched_key = key_match(reference_key, other_key)
                if matched_key:
                    flag_run = []
                    comparison_results = compare_values_setting(combine_dict[reference_key], other_values, view_key, other_key, reference_key,Title,flag_run,testtype,excelpath,remote_test_campaign, campaign, device)
                    if len(flag_run) != 0:
                        final_result[view_key].extend(comparison_results)
                    if "Download" not in reference_key and "Upload" not in reference_key:
                        break
                else:
                    if i == 3:
                        print(f"{reference_key} not found any of the views")
            i += 1
def key_match(reference_key, other_key):
    # Convert keys to lowercase for case-insensitive comparison
    reference_key_lower = reference_key.lower()
    other_key_lower = other_key.lower()
    # Split the other key into parts
    other_parts = other_key_lower.split()
    if len(other_parts) >= 3:
        if all(part in reference_key_lower for part in other_parts[:2]):
            return other_key
    elif len(other_parts) == 2:
        if all(part in reference_key_lower for part in other_parts[:1]):
            return other_key
    elif len(other_parts) == 1:
        reference_key = reference_key_lower.split()
        if all(compare_values(part,reference_key[0])for part in other_parts):
            return other_key
    return None
def contains_only_empty_strings(lst):
    return all(item == '' for item in lst)
def compare_values_setting(value_list, other_dict_list, view_key, other_key, reference_key,Title,flag_run,testtype,excelpath,remote_test_campaign, campaign, device):
    comparison_results = []
    i =0
    flag_failed = True
    if not contains_only_empty_strings(other_dict_list):
        flag_run.append(True)
        for val in value_list:
            a = [value1 for value1 in other_dict_list if all(check_numeric_value(v, value1) for v in val)]
            b = [value1 for value1 in other_dict_list if not any(check_numeric_value(v, value1) for v in val)]
            if a and not reference_key in testtype :
                 comparison_results.append({"Usercampaignname,Classifier,Device":f"{remote_test_campaign},{campaign},{device}","SETTINGS_PARAMETER_NAME(Reference)": reference_key, f"{view_key} PARAMETER": other_key,f"{view_key} VALUE": f"{a}", f"SETTINGS_APPLICATION_VALUE(Reference)": f"{val}",f"Data validation": "The value is found"})
            elif a and reference_key in testtype :
                 comparison_results.append({"Usercampaignname,Classifier,Device":f"{remote_test_campaign},{campaign},{device}","SETTINGS_PARAMETER_NAME(Reference)": reference_key, f"{view_key} PARAMETER": other_key,f"{view_key} VALUE": f"{a}", f"SETTINGS_APPLICATION_VALUE(Reference)": f"{val}",f"Data validation": "The value is found,but settings application value(reference) != excel settings values"})
                 flag_failed = [True,False]
            elif b:
                flag_failed = False
                comparison_results.append({"Usercampaignname,Classifier,Device":f"{remote_test_campaign},{campaign},{device}","SETTINGS_PARAMETER_NAME(Reference)": reference_key, f"{view_key} PARAMETER": other_key,f"{view_key} VALUE": f"{b[i]}", f"SETTINGS_APPLICATION_VALUE(Reference)": f"{val}",f"Data validation": "The value is Not Found"})
            i+=1
            print(i)
        if flag_failed == True and i != 0:
            updatecomponentstatus(Title=Title,componentname=f"{reference_key} == {other_key} --> {view_key} vs Settings", status="PASSED", comments=f"The values are found.", path=excelpath)
        elif flag_failed == False and i != 0:
            updatecomponentstatus(Title=Title,componentname=f"{reference_key} == {other_key} --> {view_key} vs Settings", status="FAILED", comments=f"The values are not found.", path=excelpath)
        elif flag_failed == [True,False] and i != 0:
            updatecomponentstatus(Title=Title,componentname=f"{reference_key} == {other_key} --> {view_key} vs Settings", status="FAILED", comments=f"The values are found,but settings application value(reference) != excel settings values", path=excelpath)
    return comparison_results
########################################################### Change Settings Scenario ####################################################################################################################################################################
def main_func_change_settings(driver,environment,userid):
    time.sleep(10)
    # runvalue = Testrun_mode(value="Change Settings")
    Change_settings_runvalue = change_settings_module_controllers()
    if "Yes".lower() == Change_settings_runvalue[-1].strip().lower():
        combine_dict = {}
        change_settings(driver, combine_dict)
        combine_dict1 = {}
        data = {
            'Test_Type': [],
            'Parameter': [],
        }
        for key, values in combine_dict.items():
            combine_dict1[key] = [{setting: extract_numerical_values(setting)} for setting in values]
        for test_type, values in combine_dict1.items():
            for value in values:
                for param, param_values in value.items():
                    data['Test_Type'].append(test_type)
                    data['Parameter'].append(param)
        # Convert to DataFrame
        df = pd.DataFrame(data)
        change_excel_path = config.test_data_folder_rootpath + f"\\testdata\\{environment}_{userid}_change_setting.xlsx"
        # Write DataFrame to Excel
        df.to_excel(change_excel_path, index=False)

def main_change_settings(driver,campaign,environment,userid,excelpath,remote_test_campaign, device, final_result,excelpath_for_storedata):
    Change_settings_runvalue = change_settings_module_controllers()
    # runvalue = Testrun_mode(value="Change Settings")
    Title = "Change Settings"
    datas1 = {}
    datas2 = {}
    data_combine_dict = {}
    combine_dict1 = {}
    if "Yes".lower() == Change_settings_runvalue[-1].strip().lower():
        change_excel_path = config.test_data_folder_rootpath + f"\\testdata\\{environment}_{userid}_change_setting.xlsx"
        df = pd.read_excel(change_excel_path)
        combine_dict = df.groupby("Test_Type")["Parameter"].apply(list).to_dict()
        Map_legend_and_NQC(driver,campaign,excelpath,datas1,datas2,excelpath_for_storedata)
        settings_pdf(driver, campaign, data_combine_dict, excelpath)

        # Updating settings, Operator Comparison, Map Legend and PDF Data to excel
        updating_settings_data_extraction_to_excel(combine_dict, datas1, datas2, data_combine_dict, excelpath_for_storedata,"DATA_EXTRACTION_CHANGE_SETTINGS")

        # Extracting only numerical values from the "Settings" section
        for key, values in combine_dict.items():
            combine_dict1[key] = [extract_numerical_values(setting) for setting in values]
        # Calling comparison function to compare the settings against operator comparison, map_legend and pdf data
        comparison(datas1, datas2, data_combine_dict, combine_dict1,final_result,Title,excelpath,campaign, remote_test_campaign, device)
    elif "No".lower() == Change_settings_runvalue[-1].strip().lower():
        statement = "You have selected Not to execute"
        with allure.step(statement):
            updatecomponentstatus(Title, "Not to execute", "SKIPPED", "You have selected No for execute", excelpath)
            pass

def change_settings(driver, combine_dict):
    with allure.step("Change Settings scenario"):
        Page_Down(driver)
        clickec(driver, settings_1.btn_setting)
        time.sleep(2)
        excel_data = pd.read_excel("C:\\RantCell_Automation_Data_and_Reports\\testdata\\Change_settings.xlsx", dtype={'Value': str})
        # Define a dictionary to map test types to locators
        test_type_locators = {
            "RSSI/RSCP dBm setting": {
                "Greater than equal to": settings_1.rssi_rscp_1,"Range1": settings_1.rssi_rscp_2,"Range2": settings_1.rssi_rscp_3
            },
            "WIFI RSSI dBm setting": {
                "Greater than equal to": settings_1.wifi_rssi_1,"Range1": settings_1.wifi_rssi_2,"Range2": settings_1.wifi_rssi_3
            },
            "RSRP dBm setting": {
                "Greater than equal to": settings_1.rsrp_1,"Range1": settings_1.rsrp_2,"Range2": settings_1.rsrp_3
            },
            "RSRQ dBm setting": {
                "Greater than equal to": settings_1.rsrq_1,"Range1": settings_1.rsrq_2
            },
            "lteSNR dBm setting": {
                "Greater than equal to": settings_1.ltesnr_1,"Range1": settings_1.ltesnr_2,"Range2": settings_1.ltesnr_3,
                "Range3": settings_1.ltesnr_4,"Range4": settings_1.ltesnr_5,"Range5": settings_1.ltesnr_6,"Range6": settings_1.ltesnr_7
            },
            "CDMA RSSI dBm setting": {
                "Greater than equal to": settings_1.cdma_rssi_1,"Range1": settings_1.cdma_rssi_2,"Range2": settings_1.cdma_rssi_3
            },
            "3G Ec/No dBm setting": {
                "Greater than equal to": settings_1.ecno_1,"Range1": settings_1.ecno_2
            },
            "CDMA SNR dBm setting": {
                "Less than equal to": settings_1.cdma_snr_1,"Range1": settings_1.cdma_snr_2
            },
            "nrSsSINR dBm setting": {
                "Greater than equal to": settings_1.nrSsSINR_1,"Range1": settings_1.nrSsSINR_2,"Range2": settings_1.nrSsSINR_3,
                "Range3": settings_1.nrSsSINR_4,"Range4": settings_1.nrSsSINR_5, "Range5": settings_1.nrSsSINR_6,"Range6": settings_1.nrSsSINR_7,
            },
            "nrSsRSRP dBm setting": {
                "Greater than equal to": settings_1.nrSsRSRP_1,"Range1": settings_1.nrSsRSRP_2,"Range2": settings_1.nrSsRSRP_3
            },
            "nrSsRSRQ dBm setting": {
                "Greater than equal to": settings_1.nrSsRSRQ_1,"Range1": settings_1.nrSsRSRQ_2
            },
            "Ping Test": {
                "Less than equal to   ms": settings_1.ping_1
            },
            "Call Setup Time": {
                "Range1": settings_1.call_setup_time_1,"Greater than   sec and less than equal to   sec": settings_1.call_setup_time_2
            },
            "SMS Sent/Received Duration (Graph view)": {
                "Range1": settings_1.sms_sent_received_1,"Greater than   sec and  Less than equal to  sec": settings_1.sms_sent_received_2
            },
            "Download Test / HTTP Speed Download Test / iPerf DownloadTest": {
                "Greater than equal to   mbps": settings_1.download_http_iperf_1,"Range1": settings_1.download_http_iperf_2
            },
            "Upload Test / HTTP Speed Upload Test / iPerf UploadTest": {
                "Greater than equal to   mbps": settings_1.upload_http_iperf_1,"Range1": settings_1.upload_http_iperf_2
            },
            "Stream Test(Graph view)": {
                "Greater than equal to   mbps": settings_1.stream_1,"Range1": settings_1.stream_2
            }
        }
        # Iterate over each row in the Excel data
        for index, row in excel_data.iterrows():
            test_type = row['Test_Type'].strip()
            parameter = row['Parameter'].strip()
            value = row['Value']
            if test_type in test_type_locators:
                locator_map = test_type_locators[test_type]
                if parameter in locator_map:
                    locator = locator_map[parameter]
                    # data_df[test_type] = [].append([value])
                    inputtext(driver=driver, locators=locator, value=value)
                    with allure.step(test_type):
                        allure.attach(driver.get_screenshot_as_png(), name=f"{test_type}",attachment_type=allure.attachment_type.PNG)
                else:
                    print(f"Parameter '{parameter}' not recognized for test type '{test_type}'.")
            else:
                print(f"Test type '{test_type}' not recognized.")
        # print(data_df)
        time.sleep(1)
        clickec(driver, settings_1.save_settings_btn)
        time.sleep(2)
        data_extraction_settings(driver, combine_dict)
        click(driver=driver, locators=Login_Logout.dashboard_id)

def data_extraction_settings(driver,combine_dict):
    headers_list = []
    header_element = driver.find_elements(*settings_1.all_default_settings_headers)
    for k in range(len(header_element)):
        try:
            d = header_element[k].text
            headers_list.append(d)
            data_default_content = header_element[k].find_elements(*settings_1.all_default_settings_content)
            data_default_values = header_element[k].find_elements(*settings_1.all_default_settings_values)
            value_index = 0  # Initialize index for values
            combined_values = []
            # Loop through each data element
            for i in range(len(data_default_content)):
                data = data_default_content[i].text
                if data != "Dropped packets":
                    # Check if the data contains a hyphen
                    if '-' in data:
                        value_1 = data_default_values[value_index].get_attribute('value')  # Extract corresponding value
                        value_index += 1  # Increment index
                        and_part = ''  # Initialize 'and' part

                        # Check if there is an 'and' part
                        if 'and' in data:
                            and_part = ' and'
                            value_2 = data_default_values[value_index].get_attribute('value')
                            value_index += 1  # Increment index
                        # Format combined value based on the presence of 'and' part
                        combined_value = f"{data.split('-')[0].strip()}-{value_1}{and_part} -{value_2}" if and_part else f"{data.strip()}{value_1}"
                        combined_values.append(combined_value)
                        # Check if all values are processed
                        if value_index >= len(data_default_values):
                            break

                    elif "Sms status failure" in data:
                        values = data_default_values[value_index].get_attribute('value')
                        value_index += 1
                        combined_values.append(f"Less than {values} sec or Sms status failure")

                    elif any(keyword in data for keyword in ("ms", "mbps", "sec")) and not re.search(r'Less than \d+ sec', data):
                        # Split the data by "and" if it's present
                        parts = data.split('and')
                        # Get the values corresponding to the first part
                        value_1 = data_default_values[value_index].get_attribute('value')
                        # Extract the unit from the first part
                        unit_1 = ''.join(parts[0].split()[-1:])
                        # Remove the unit from the first part
                        data_1 = ' '.join(parts[0].split()[:-1])
                        # Add the value before the keyword with a space
                        combined_value = f"{data_1.strip()} {value_1} {unit_1}"
                        # If there is a second part (i.e., "and" is present)
                        if len(parts) > 1:
                            # Get the values corresponding to the second part
                            value_2 = data_default_values[value_index + 1].get_attribute('value')
                            # Extract the unit from the second part
                            unit_2 = ''.join(parts[1].split()[-1:])
                            # Remove the unit from the second part
                            data_2 = ' '.join(parts[1].split()[:-1])
                            # Add the value before the keyword with a space
                            and_part = ' and' if 'and' in data else ''
                            combined_value += f"{and_part} {data_2.strip()} {value_2} {unit_2}"
                            # Increment the value index
                            value_index += 1
                        combined_values.append(combined_value)
                        value_index += 1
                    else:
                        if 'and' in data:
                            parts = data.split('and')
                            if value_index + 1 < len(data_default_values):
                                value_1 = data_default_values[value_index].get_attribute('value')
                                value_2 = data_default_values[value_index + 1].get_attribute('value')
                                combined_value = f"{parts[0].strip()} {value_1} and {value_2}"
                                combined_values.append(combined_value)
                                value_index += 2
                        else:
                            if value_index < len(data_default_values):
                                value = data_default_values[value_index].get_attribute('value')
                                combined_values.append(f"{data.strip()} {value}")
                                value_index += 1
            if len(combined_values) != 0:
                print(combined_values)
                combine_dict[d] = combined_values
        except Exception as e:
            pass
    # Print or return the combined values
    print(combine_dict)
#########################################################################################################################################################################################
