import time
from builtins import range

from module_controllers.module_controllers import *
from locators.locators import *

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure
import time


def apk_download_main_function(driver, url, excelpath, downloadpath):
    Title = "APK Download"
    apk_download_main_function = apk_download_module_controllers()

    all_operations_passed = True  # Flag to track overall success

    if "Yes".lower() == apk_download_main_function[-1].strip().lower():
        downloadpath_apk = specifying_download_path(driver, downloadpath, "APK_Download")
        with allure.step("APK Download"):
            launchbrowser(driver, url)
            try:
                # Click the first button and wait for the loading to complete
                clickec(driver, downloading_apk_file.whats_new_btn)
                if WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//section[@id='contact-info']//div[@class='row']"))):
                    # Click the second button to download the document
                    clickec(driver, downloading_apk_file.download_document)
                    try:
                        waiting_for_particular_file_to_download_specfic_path(sec=61, downloadfolderpath=downloadpath_apk, filenameortypeoffile="RantCell Feature Document 2024")
                        updatecomponentstatus(Title, "Download Document", "PASSED", "RantCell Feature Document 2024 downloaded successfully.", excelpath)
                    except Exception as e:
                        updatecomponentstatus(Title, "Download Document", "FAILED", f"Failed to download RantCell Feature Document 2024: {e}", excelpath)
                        all_operations_passed = False  # Mark failure

                    time.sleep(5)
                    # Click the third button to download the startup manual
                    clickec(driver, downloading_apk_file.download_startup_maual)
                    try:
                        waiting_for_particular_file_to_download_specfic_path(sec=61, downloadfolderpath=downloadpath_apk, filenameortypeoffile="RantCell Latest StartUp manual")
                        updatecomponentstatus(Title, "Download Startup Manual", "PASSED", "RantCell Latest StartUp manual downloaded successfully.", excelpath)
                    except Exception as e:
                        updatecomponentstatus(Title, "Download Startup Manual", "FAILED", f"Failed to download RantCell Latest StartUp manual: {e}", excelpath)
                        all_operations_passed = False  # Mark failure

                    # Click the final button to download the APK
                    clickec(driver, downloading_apk_file.download_apk)
                    try:
                        waiting_for_particular_file_to_download_specfic_path(sec=61, downloadfolderpath=downloadpath_apk, filenameortypeoffile="*.apk")
                        updatecomponentstatus(Title, "Download APK", "PASSED", "APK downloaded successfully.", excelpath)
                    except Exception as e:
                        updatecomponentstatus(Title, "Download APK", "FAILED", f"Failed to download APK: {e}", excelpath)
                        all_operations_passed = False  # Mark failure

            except Exception as e:
                allure.attach(driver.get_screenshot_as_png(), name="APK Download Error", attachment_type=allure.attachment_type.PNG)
                updatecomponentstatus(Title, "APK Download", "FAILED", f"Error during APK download process: {e}", excelpath)
                all_operations_passed = False  # Mark failure

            finally:
                change_the_download_path(driver, downloadpath)
                # Update the high module status based on the flag
                if all_operations_passed:
                    updatehighmodulestatus(Title, status="PASSED", comments="All files were downloaded successfully.", path=excelpath)
                else:
                    updatehighmodulestatus(Title, status="FAILED", comments="One or more downloads failed.", path=excelpath)

    else:
        # If the condition is not met, skip the execution
        updatecomponentstatus(Title, "APK Download", "SKIPPED", "You have selected No for execute", excelpath)
        updatehighmodulestatus(Title, status="SKIPPED", comments="You have selected No for execute", path=excelpath)



def waiting_for_particular_file_to_download_specfic_path(sec: int, downloadfolderpath, filenameortypeoffile):
    for i in range(sec):
        time.sleep(1)
        # Use glob to match any file that contains the specified string in the filename
        list_of_files = glob.glob(os.path.join(downloadfolderpath, f"*{filenameortypeoffile}*"))
        if len(list_of_files) != 0:
            break
    else:
        raise Exception(f"File containing '{filenameortypeoffile}' not found within the time limit")