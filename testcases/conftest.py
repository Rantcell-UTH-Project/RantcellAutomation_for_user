import os
import queue
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.createFolderforRantcell_automation_DataandReports import create_folder_for_rantcell_data_and_ExcelReport, \
    Updating_source_folder, \
    create_folder_for_excelreport, excel_report_path_, testRun_downloadfile_path, \
    create_folder_for_downloads
from configurations.config import ReadConfig
from utils.library import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Counter for active parallel threads
active_threads = 0
threads =0

def pytest_sessionstart(session):
    if active_threads == 0:
        try:
            if not os.path.exists(ReadConfig.test_data_folder_rootpath):
                e = Exception
                raise e
            if (os.path.exists(ReadConfig.test_data_folder_rootpath)):
                try:
                    create_folder_for_rantcell_data_and_ExcelReport(ReadConfig.test_data_folder_rootpath, ReadConfig.source_dest)
                except Exception:
                    print(str(Exception))
                finally:
                    testRun_downloadfile_path(ReadConfig.test_run_download_file_path)
                    time.sleep(2)
                    excel_report_path_(ReadConfig.test_run_excelreportdata_path)
                    f1 = open(ReadConfig.test_run_download_file_path, "r")
                    testrundownloadfolder = f1.read()
                    f1.close()
                    test_case_downloading_files_path_timestamps = ReadConfig.test_case_downloading_files_path_timestamp + testrundownloadfolder
                    create_folder_for_downloads(destination_folder=test_case_downloading_files_path_timestamps)
                    f1 = open(ReadConfig.test_run_excelreportdata_path, "r")
                    testrunexcelfolder = f1.read()
                    f1.close()
                    test_run_excel_report_pathtimestamp = ReadConfig.excel_report_path + testrunexcelfolder
                    create_folder_for_excelreport(destination_folder=test_run_excel_report_pathtimestamp)
                    Updating_source_folder(ReadConfig.updating_source_folders, ReadConfig.test_data_folder_rootpath)
            else:
                pass
        except Exception as e:
            with allure.step(f"Goto the directory {ReadConfig.test_data_folder_rootpath} and update the file as per your requirement, then re-run"):
                if not os.path.exists(ReadConfig.test_data_folder_rootpath):
                    create_folder_for_rantcell_data_and_ExcelReport(ReadConfig.test_data_folder_rootpath, ReadConfig.source_dest)
                    Updating_source_folder(ReadConfig.updating_source_folders, ReadConfig.test_data_folder_rootpath)
                    pytest.fail(f"Goto the directory {ReadConfig.test_data_folder_rootpath} and update the file as per your requirement")

def sanitize_folder_name(name):
    # Remove characters that are not valid for a folder name
    forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*','[',']','(',')','{','}']
    for char in forbidden_chars:
        name = name.replace(char, '')
    # Truncate or pad the name to have a length of 30
    sanitized_name = name[:40].ljust(40)
    return sanitized_name

@pytest.fixture(scope='function')
def setup(request):
    global driver,test_case_downloading_files_path
    chrome_options = Options()
    f1 = open(ReadConfig.test_run_download_file_path, "r")
    testrundownloadfolder = f1.read()
    f1.close()
    # Set the root path for test data and reports
    test_data_folder_rootpath = ReadConfig.test_case_downloading_files_path_timestamp + testrundownloadfolder
    if os.path.exists(test_data_folder_rootpath):
        print("test run downloading files folder path")
    if not os.path.exists(test_data_folder_rootpath):
        pytest.fail("test run downloading files folder path is not exist")
    random_length = random.randint(3, 5)
    random_alphabet = generate_random_alphabet(random_length)
    timestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    test_case_name = sanitize_folder_name(request.node.name) + timestamp + random_alphabet
    test_case_downloading_files_path = test_data_folder_rootpath + "\\" + str(test_case_name)
    os.makedirs(test_case_downloading_files_path, exist_ok=True)
    prefs = {
        'profile.default_content_setting_values.automatic_downloads': 1,
        "download.default_directory": test_case_downloading_files_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=ChromeService(webdriver_path()),options=chrome_options)
    driver.implicitly_wait(10)
    global active_threads
    active_threads += 1
    yield driver,test_case_downloading_files_path
    driver.quit()


def pytest_collection_modifyitems(config, items):
    config.collected_items_count = len(items)
    global threads
    threads = config.collected_items_count

def pytest_sessionfinish(session):
    item_count = threads
    if active_threads == item_count:
        try:
            if os.path.exists(ReadConfig.test_data_folder_rootpath):
                with allure.step("Data file is present"):
                    with allure.step(f"Item count: {item_count}"):
                        f1 = open(ReadConfig.test_run_excelreportdata_path, "r")
                        testrunexcelfolder = f1.read()
                        test_run_excel_report_pathtimestamp = ReadConfig.excel_report_path + testrunexcelfolder
                        if os.path.exists(test_run_excel_report_pathtimestamp):
                            print("test run excel folder is exist")
                        if not os.path.exists(test_run_excel_report_pathtimestamp):
                            pytest.fail("test run excel folder is not exist")


        except Exception as e:
            with allure.step(f"Item count: {item_count}"):
                with allure.step(f"Goto the directory {ReadConfig.test_data_folder_rootpath} and update the file as per your requirement, then re-run"):
                    if not os.path.exists(ReadConfig.test_data_folder_rootpath):
                        create_folder_for_rantcell_data_and_ExcelReport(ReadConfig.test_data_folder_rootpath, ReadConfig.source_dest)
                        Updating_source_folder(ReadConfig.updating_source_folders, ReadConfig.test_data_folder_rootpath)
                        pytest.fail(f"Goto the directory {ReadConfig.test_data_folder_rootpath} and update the file as per your requirement")