import os, allure, pytest, datetime
from configurations.config import ReadConfig as config
from pageobjects.Alarms import main_func_alarms
from pageobjects.Change_Password import main_func_account_setting_change_password
from pageobjects.Reset_Password import main_func_reset_password
from pageobjects.Chart import chart_main_section
from pageobjects.group_reporter import main_func_group_reporter_for_daily_automation
from pageobjects.remote_test import remote_test_
from utils.createxl import create_workbook, create_workbook_for_data_store
from utils.readexcel import *
from pageobjects.login_logout import *
from utils.updateexcelfile import *
from utils.library import *
from pageobjects.Dashboard import *
from pageobjects.Settings import *
from module_controllers.module_controllers import *
from pageobjects.APK_Download import apk_download_main_function
class Test_Campaign_Driver:
    driver = None
    @pytest.mark.parametrize("environment,url,userid,password",fetch_enviroment())
    def test_daily_automation_test_cases(self,setup, environment, url, userid,password):
        global Excel_report_file_path
        driver,test_case_downloading_files_path= setup
        f1 = open(config.test_run_excelreportdata_path, "r")
        testrunexcelfolder = f1.read()
        f1.close()
        password = encrypte_decrypte(text=password)
        # Create XL file to capture data points for each component
        timestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        driver.implicitly_wait(30)
        try:
            Excel_report_file_path = config.excel_report_path + testrunexcelfolder
            if os.path.exists(Excel_report_file_path):
                print("test run excel folder is exist")
            if not os.path.exists(Excel_report_file_path):
                pytest.fail("test run excel folder is not exist")
            excelpath = Excel_report_file_path + "\\"+ userid.split("@")[0] + "_" + environment + timestamp + ".xlsx"
            create_workbook(excelpath)
        except Exception as e:
            with allure.step(f"Check {Excel_report_file_path}{e}"):
                print(f"Check {Excel_report_file_path}{e}")
                assert False

        default_settings_match = "OCvspdf_DATAMATCH_defaultsettings"
        default_settings_notmatch = "OCvspdf_DATANOTMATCH_defaultsettings"
        change_settings_match = "OCvspdf_DATAMATCH_changesettings"
        change_settings_notmatch = "OCvspdf_DATANOTMATCH_changesettings"

        add_headers_and_data(file_path=excelpath, headers=['Title', 'Status', 'Comments'],sheet_name='HIGH_MODULE_STATUS')
        add_headers_and_data(file_path=excelpath, headers=['Title','Componentname','Status', 'Comments'], sheet_name='COMPONENTSTATUS')
        add_headers_and_data(file_path=excelpath, headers=["File", "Group reporter key","Group reporter value", "calculated csv value","Data validation"], sheet_name="Gr_DATA_MATCH")
        add_headers_and_data(file_path=excelpath, headers=["File", "Group reporter key","Group reporter value", "calculated csv value","Data validation"], sheet_name="Gr_DATA_NOT_MATCH")
        add_headers_and_data(file_path=excelpath, headers=['Usercampaignname, Classifier, Device','Component Type', 'Data validation'], sheet_name=default_settings_match)
        add_headers_and_data(file_path=excelpath, headers=['Usercampaignname, Classifier, Device','Component Type', 'Data validation'], sheet_name=default_settings_notmatch)
        add_headers_and_data(file_path=excelpath, headers=['Usercampaignname, Classifier, Device','Component Type', 'Data validation'], sheet_name=change_settings_match)
        add_headers_and_data(file_path=excelpath, headers=['Usercampaignname, Classifier, Device','Component Type', 'Data validation'], sheet_name=change_settings_notmatch)

        campaigns_created = []

        campaigns_datas = fetch_camapaigns()

        with allure.step("Downloading apk"):
            apk_download_main_function(driver, url, excelpath,downloadpath=test_case_downloading_files_path+"\\")

        # # Launch browser and Navigate to RantCell Application LoginPage
        with allure.step("Launch and navigating to RantCell Application LoginPage"):
            Navigate_to_loginPage(driver, url)

        # Login to RantCell Application
        with allure.step("Login to RantCell Application"):
            login_user(driver, userid, password,excelpath)


        with allure.step("Floor Plan --> scenario"):
            floor_plan_for_individual_campaign(driver, userid, password, excelpath,test_case_downloading_files_path = test_case_downloading_files_path)

        with allure.step("Remote Test - Run test"):
            device = remote_test_(driver,campaigns_datas,campaigns_created,excelpath)
            print(device)

        with allure.step("Default Settings for extraction"):
            main_func_default_settings(driver, environment, userid)

        with allure.step("Group Reporter"):
            main_func_group_reporter_for_daily_automation(driver, environment, userid, campaigns_datas = campaigns_datas, downloadpath = test_case_downloading_files_path,excelpath=excelpath)

        with allure.step("Device - Custom Query"):
            device_custom_query(driver, campaigns_datas, userid, password, excelpath)

        with allure.step("date and time"):
            date_and_time_main_function(driver, excelpath)

        with allure.step("Alarm"):
            main_func_alarms(driver,excelpath,test_case_downloading_files_path + "\\")

        if campaigns_created != []:

            with allure.step("Chart"):
                chart_main_section(driver,userid, password, campaigns_datas, excelpath,campaigns_created,device)

            final_result_default_settings = {"Operator_Comparison": [], "Map_Legend": [], "Pdf_Data": []}
            final_result_change_settings = {"Operator_Comparison": [], "Map_Legend": [], "Pdf_Data": [], "SETTINGS": []}
            # """
            #     below for loop is used for executing the following modules "Export", "Default Settings", "Map view(NQC-operator comparison V/S PDF Export)"
            #     of each campagins generated in above "Remote Test - Run test" module.
            #     Note:- Default Settings module values will be related to other module in application and also Default Settings values
            #     will be updated in above function "Default Settings for extraction".
            #     """

            for remote_test_campaign,campaigns_data in zip_longest(campaigns_created,campaigns_datas):
                device_testdata, campaign, usercampaignsname_testdata, testgroup = campaigns_data

                with allure.step(f"Usercampaignname:{remote_test_campaign},Classifier:{campaign},Device:{device}"):
                    updatecomponentstatus("Usercampaignname,Classifier,Device", f"Usercampaignname:{remote_test_campaign},Classifier:{campaign},Device:{device}" , "EXECUTED","Usercampaignname,Classifier,Device is executed.", excelpath)
                    excelpath_for_each_campaigns = Excel_report_file_path + "\\" + campaign + "_" + remote_test_campaign + "_" + device + "_" + userid.split("@")[0] + "_" + environment + timestamp + ".xlsx"
                    print(excelpath_for_each_campaigns)
                    create_workbook_for_data_store(excelpath_for_each_campaigns)

                    downloadfilespath = specifying_download_path(driver, test_case_downloading_files_path + "\\", campaign + "_" +remote_test_campaign )
                    protestdata_runvalue = protestdata_module_controllers()
                    litetestdata_runvalue = litetestdata_module_controllers()
                    typeoftest = None
                    if "Yes".lower() == protestdata_runvalue[-1].strip().lower():
                        typeoftest = "ProTest data"
                    elif "Yes".lower() == litetestdata_runvalue[-1].strip().lower():
                        typeoftest = "LiteTest data"

                    with allure.step(f"Navigating to [Android TestData  >>> {typeoftest}  >>>  Device  >>>  {str(campaign)}]"):
                        side_menu_Components_(driver, device, remote_test_campaign, userid, password, excelpath)

                    with allure.step("Default Settings"):
                        main_default_settings(driver, campaign, remote_test_campaign, device, excelpath, environment, userid, final_result_default_settings,excelpath_for_storedata=excelpath_for_each_campaigns)

                    # Download CSV files from Exports
                    with allure.step("List Of Campaigns Export in Dashboard"):
                        Export_Dashboard(driver,excelpath, campaign, downloadfilespath + "\\")

                    with allure.step("Map view(NQC-operator comparison V/S PDF Export)"):
                       Mapview_Operator_comparison_vs_PDF(driver, campaign, excelpath, downloadfilespath, "Default Settings",excelpath_for_storedata=excelpath_for_each_campaigns,data_match_sheet=default_settings_match,data_not_match_sheet=default_settings_notmatch,remote_test_campaign=remote_test_campaign,device=device)

            Change_settings_runvalue = change_settings_module_controllers()
            change_settings_title = "Change Settings"
            if "Yes".lower() == Change_settings_runvalue[-1].strip().lower():

                with allure.step("Change Settings Extraction"):
                    main_func_change_settings(driver, environment, userid)
                # """
                #     below for loop is used for executing the following modules "Change Settings", "Map view(NQC-operator comparison V/S PDF Export)"
                #     of each campagins generated in above "Remote Test - Run test" module.
                #     Note:- Change Settings module values will be related to other module in application and also Change Settings values
                #     will be updated in above function "Change Settings Extraction".
                #     """
                for remote_test_campaign,campaigns_data in zip_longest(campaigns_created,campaigns_datas):
                    device_testdata, campaign, usercampaignsname_testdata, testgroup = campaigns_data

                    excelpath_for_each_campaigns_change_settings = Excel_report_file_path + "\\" + campaign + "_" + remote_test_campaign + "_" + device + "_" + userid.split("@")[0] + "_" + environment + timestamp + "_change.xlsx"
                    print(excelpath_for_each_campaigns)
                    create_workbook_for_data_store(excelpath_for_each_campaigns_change_settings)
                    with allure.step(f"Usercampaignname:{remote_test_campaign},Classifier:{campaign},Device:{device}--->> Change Settings"):

                        updatecomponentstatus("Usercampaignname,Classifier,Device",f"Usercampaignname:{remote_test_campaign},Classifier:{campaign},Device:{device}","EXECUTED","Usercampaignname,Classifier,Device is executed for change setting.",excelpath)
                        downloadfilespath = specifying_download_path(driver, test_case_downloading_files_path + "\\", campaign + "_" +remote_test_campaign+"_change")
                        protestdata_runvalue = protestdata_module_controllers()
                        litetestdata_runvalue = litetestdata_module_controllers()
                        typeoftest = None
                        if "Yes".lower() == protestdata_runvalue[-1].strip().lower():
                            typeoftest = "ProTest data"
                        elif "Yes".lower() == litetestdata_runvalue[-1].strip().lower():
                            typeoftest = "LiteTest data"

                        with allure.step(f"Navigating to [Android TestData  >>> {typeoftest}  >>>  Device  >>>  {str(campaign)}]"):
                            side_menu_Components_(driver, device, remote_test_campaign, userid, password, excelpath)

                        with allure.step("Change Settings"):
                            main_change_settings(driver, campaign, environment, userid, excelpath,remote_test_campaign,device,final_result_change_settings,excelpath_for_storedata=excelpath_for_each_campaigns_change_settings)

                        with allure.step("Map view(NQC-operator comparison V/S PDF Export)"):
                           Mapview_Operator_comparison_vs_PDF(driver, campaign, excelpath, downloadfilespath,"Change Settings",excelpath_for_storedata=excelpath_for_each_campaigns_change_settings,data_match_sheet=change_settings_match,data_not_match_sheet=change_settings_notmatch,remote_test_campaign=remote_test_campaign,device=device)

            elif "No".lower() == Change_settings_runvalue[-1].strip().lower():
                statement = "You have selected Not to execute"
                with allure.step(statement):
                    updatecomponentstatus(change_settings_title, "Not to execute", "SKIPPED", "You have selected No for execute",excelpath)
                    updatehighmodulestatus(change_settings_title, "SKIPPED", "You have selected No for execute", excelpath)
                    pass

        ################################## Add the title names accordingly for the above integrated modules ####################################################################################################################################################################################
            update_module_status_based_on_reading_component_status(modules= {"Exports":"WARNING|FAILED", "Default Settings":"WARNING|FAILED","Change Settings":"WARNING|FAILED","Map view(NQC-operator comparison V/S PDF Export)":"WARNING|FAILED","Chart":"WARNING|FAILED"}, excelpath= excelpath)
            updating_datavalidation_for_each_module(excelpath,modules={"Default Settings": final_result_default_settings,"Change Settings": final_result_change_settings})

        else:
            statement = "campaign has not been created hence further related modules will not be executed"
            with allure.step(statement):
                updatecomponentstatus("", "Not to execute", "SKIPPED", "You have selected No for execute", excelpath)
                updatehighmodulestatus("", "SKIPPED", statement, excelpath)

        # Logout from RantCell Application
        with allure.step("Logout to RantCell Application"):
            logout_user(driver,excelpath)

        with allure.step("Forgot Password"):
            newpassword , reset_password_flag = main_func_reset_password(driver, emailId=userid, url=url,oldpassword=password,excelpath=excelpath)

        with allure.step("Account setting change password"):
            main_func_account_setting_change_password(driver, currentPassword=newpassword,oldpassword=password,excelpath=excelpath,url=url,emailId=userid,reset_password_flag=reset_password_flag)

        # Read the component statues from Excel Report
        status = readcomponentstatus(excelpath)
        format_workbook(excelpath)

        # Mark the test case as failed if any component is field
        if 'FAILED' not in status:
            assert True
        else:
            assert False
