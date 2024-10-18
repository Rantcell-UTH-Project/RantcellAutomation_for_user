import csv, glob, os, time, allure,openpyxl,datetime,shutil,re
import io
import pathlib
import random
import statistics
import string
import numpy as np
import pandas as pd
from allure_commons.types import AttachmentType
from openpyxl.utils.dataframe import dataframe_to_rows
from selenium.common import NoSuchElementException, TimeoutException, ElementClickInterceptedException, \
    NoAlertPresentException, UnexpectedAlertPresentException, StaleElementReferenceException, \
    ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from utils.createFolderforRantcell_automation_DataandReports import create_folder_for_downloads
from utils.updateexcelfile import *
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, Font,Border,Side
from selenium.webdriver import *
from configurations.config import ReadConfig as config
from itertools import zip_longest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Optional
from locators.locators import select_Map_View_Components
import msoffcrypto

global timeout
timeout = 60

################################################################-- LAUNCHBROWSER --########################################################################################################################################################################
# Function:launchbrowser - Launches the browser and navigates to the URL
# Parameters:
#           url:https://preproductionpro.rantcell.com/
#           title:https://preproductionpro.rantcell.com/
def launchbrowser(driver, url):
    """
    Launch a web browser and navigate to a specified URL.
    Args:
        driver (WebDriver): The WebDriver object for interacting with the web application.
        url (str): The URL to navigate to.
    Returns:
        bool: True if the browser was successfully launched and navigated to the specified URL, False otherwise.
    Notes:
        This function launches a web browser, navigates to the specified URL, maximizes the browser window, and then
        verifies if the actual URL matches the expected URL. If all these steps are successful, it returns True; otherwise,
        it returns False. Screenshots are attached to the Allure report for documentation.
    """
    try:
        with allure.step("Launch the browser and navigate to " + url):
            driver.get(url)
            driver.maximize_window()
            actualtitle = driver.current_url
            allure.attach(driver.get_screenshot_as_png(), name=f"URL : {str(url)}",attachment_type=allure.attachment_type.PNG)
            return actualtitle == url
    except Exception as e:
        with allure.step("Unable to launch the browser " + url):
            with allure.step(f"Actual URL sent from Test_Data.xlsx[ENVIRONMENTS_USERINPUT_LOGIN] : {str(url)}"): pass
            with allure.step(f"Expected URL loading from browser : {str(driver.current_url)}"): pass
            allure.attach(driver.get_screenshot_as_png(), name="URL_screenshot",attachment_type=allure.attachment_type.PNG)
            return False
##################################################################-- CLICK --##############################################################################################################################################################################
def action_chain_click(driver,locatortype, locatorProperty):
    element = driver.find_element(locatortype, locatorProperty)
    action = ActionChains(driver)
    action.move_to_element(element).click().perform()
# #####################################################################################################################################################################################################################################################
# Function:click - Clicks on particular element
# Parameters:
#           locators: (By.ID, textbox_username_id)
def click(driver, locators):
    """
    Click an element on a web page with explicit waits and handle potential click intercept exceptions.
    Args:
        driver (WebDriver): The WebDriver object for interacting with the web application.
        locators (tuple): A tuple specifying how to locate the element (locatortype, locatorProperty, elementname).
    Returns:
        bool: True if the element was successfully clicked, False otherwise.
    Notes:
        This function attempts to click an element on a web page using explicit waits and handles scenarios where the
        click may be intercepted. It first waits for the element to be visible using explicit waits and then clicks it.
        If the click is intercepted (e.g., by an overlay), it tries to move to the element and click it using ActionChains.
        If that also fails, it retries to click the element using explicit waits. If any of these attempts succeed, the
        function returns True; otherwise, it returns False.
    """
    locatortype, locatorProperty, elementname = locators[:3]
    Locators = (locatortype, locatorProperty)
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(Locators))
        driver.find_element(locatortype, locatorProperty).click()
        return True
    except ElementClickInterceptedException:
        try:
            action_chain_click(driver,locatortype, locatorProperty)
            return True
        except:
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(Locators)).click()
                return True
            except Exception as e:
                raise e
    except Exception as e:
        with allure.step(f"Failed to click on {elementname} element"):
            allure.attach(driver.get_screenshot_as_png(), name=f"{elementname}_screenshot",attachment_type=allure.attachment_type.PNG)
            time.sleep(2)
            return False
##############################################################################################################################################################################################################################################################
def clickec(driver, locators):
    """
    Click an element on a web page with explicit waits and handling potential click intercept exceptions.
    Args:
        driver (WebDriver): The WebDriver object for interacting with the web application.
        locators (tuple): A tuple specifying how to locate the element (locatortype, locatorProperty, elementname).
    Returns:
        bool: True if the element was successfully clicked, False otherwise.
    Notes:
        This function attempts to click an element on a web page using explicit waits and handles scenarios where the
        click may be intercepted. It first waits for the element to be clickable using explicit waits. If the click is
        intercepted (e.g., by an overlay), it tries to move to the element and click it using ActionChains. If that also
        fails, it retries to click the element using explicit waits. If any of these attempts succeed, the function returns
        True; otherwise, it returns False.
    """
    locatortype, locatorProperty, elementname = locators[:3]
    Locators = locators[:2]
    try:
        element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(Locators))
        element.click()
        return True
    except ElementClickInterceptedException:
        try:
            action_chain_click(driver,locatortype, locatorProperty)
            return True
        except:
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(Locators)).click()
                return True
            except Exception as e:
                raise e
    except ElementNotInteractableException:
        try:
            action_chain_click(driver,locatortype, locatorProperty)
            return True
        except:
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(Locators)).click()
                return True
            except Exception as e:
                raise e
    except Exception as e:
        with allure.step(f"Failed to click on {elementname} element"):
            allure.attach(driver.get_screenshot_as_png(), name=f"{elementname}_screenshot",attachment_type=allure.attachment_type.PNG)
            return False
#################################################################-- INPUTTEXT --##########################################################################################################################################################
# Function:inputtext - Enters the value in Text Edit Field
# Parameters:
#           locators: (By.ID, textbox_username_id)
#           value   : eva@rantcell.com
def inputtext(driver, locators, value):
    """
    Input text into a specified input field on a web page.
    Args:
        driver (WebDriver): The WebDriver object for interacting with the web application.
        locators (tuple): A tuple specifying how to locate the input field (locatortype, locatorProperty, elementname).
        value (str): The text value to input into the field.
    Returns:
        bool: True if text input was successful, False otherwise.
    Notes:
        This function locates and inputs text into an input field on a web page. It uses explicit waits to ensure
        the input field is visible and ready for interaction. If successful, it returns True; otherwise, it returns False.
    """
    try:
        locatortype, locatorProperty, elementname = locators
        Locators = (locatortype, locatorProperty)
        with allure.step(f"Enter value in {elementname} edit field"):
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(Locators))
            driver.find_element(*Locators).clear()
            driver.find_element(*Locators).send_keys(value)
            return True
    except Exception as e:
        with allure.step(f"Failed to enter the value in {elementname} text field element"):
            allure.attach(driver.get_screenshot_as_png(), name=f"{elementname}_screenshot",attachment_type=allure.attachment_type.PNG)
        return False
#####################################################################-- VERIFYELEMENTISPRESENT --##########################################################################################################################################
def verifyelementispresent(driver, Locators):
    """Function Name: verifyelementispresent
        Purpose:
            The verifyelementispresent function is designed to verify the presence of a specific element on a web page.
             It allows you to check whether a particular element, identified by its locators, is present or not.
        Arguments:
            driver (WebDriver): This argument expects a WebDriver object, which is responsible for interacting with the web application.
                                It is used to locate and verify the presence of the element.
            Locators (tuple): This argument is a tuple that contains information about how to locate the element to be verified.
                                It includes the following elements:
            locatortype: A string representing the locator strategy (e.g., "XPath," "CSS selector") to be used to find the element.
            locatorProperty: A string representing the specific value or property that helps locate the element.
            elementName: A descriptive name or identifier for the element. This provides context for the verification.
        Returns:
            The function returns a boolean value.
            It returns True if the specified element is present on the web page and successfully located, and False if there was an issue or an exception occurred during the process.
        Notes:
            The primary purpose of this function is to verify the presence of a specific element on a web page.
        """
    locatortype, locatorProperty, elementName = Locators
    locators = (locatortype, locatorProperty)
    try:
        with allure.step(f"Verify {elementName} element is present"):
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locators))
            element = driver.find_element(*locators)
            allure.attach(element.screenshot_as_png, name=elementName, attachment_type=allure.attachment_type.PNG)
            return True
    except Exception as e:
        with allure.step(f"Failed to verify the {elementName} element"):
            allure.attach(driver.get_screenshot_as_png(), name=f"{elementName}_screenshot", attachment_type=allure.attachment_type.PNG)
        return False
####################################################################################################################################################################################################################
class StepFailure(Exception):
    pass

#############################################################################################################################################################################################################################################
def encrypte_decrypte(text):
    result ="None"
    def en_de_special_symbols(char):
        # Define a dictionary for character mappings
        char_mappings = {
            '@': '/',
            '/': '@',
            '|': '=',
            '=': '|',
            '%': '#',
            '#': '%',
            '+': '-',
            '-': '+',
            '[': ']',
            ']': '[',
            '(': ')',
            ')': '(',
            '{': '}',
            '}': '{',
            '<': '>',
            '>': '<',
            '*': '&',
            '&': '*',
            '^': '~',
            '~': '^',
            '!': '?',
            '?': '!',
            '$': '`',
            '`': '$',
            ':': ';',
            ';': ':',
            '.': ',',
            ',': '.',
            '"': "'",
            "'": '"',
            ' ': ' ',
            "_":"_"# You can add more mappings as needed
        }
        # Use the dictionary to look up the mapped character
        return char_mappings.get(char, char)
    def en_de(value,text):
        result = []
        for char in text:
            offset = ord(char)
            if 'a' <= char <= 'z':
                result.append(value+chr(((offset - ord('a') + 13) % 26) + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(value+chr(((offset - ord('A') + 13) % 26) + ord('A')))
            elif '0' <= char <= '9':
                result.append(value+chr(((offset - ord('0') + 5) % 10) + ord('0')))  # Apply ROT5 to numerals
            else:
                char = en_de_special_symbols(char)
                result.append(value+char)  # Non-alphanumeric characters remain unchanged
        return ''.join(result)
    pattern = "XAXCXBX"
    # Check if the pattern is present in the text
    match = re.search(pattern, text)
    if match:
        # If the pattern is found, remove it
        text = re.sub(pattern, '', text)
        result = en_de(value="",text=text)
    elif not match:
        result = en_de(value=pattern,text=text)
        result +=pattern
    return result

#########################################################################################################################################################################################################################################################
def Testrun_mode(value):
    try:
        pattern_mapping_df = pd.read_excel(config.test_data_path,sheet_name="TEST_RUN")
    except Exception as e:
        with allure.step(f"Check {config.test_data_path}"):
            print(f"Check {config.test_data_path}")
            assert False
    # Select columns starting from the second column (index 1) to the last column
    pattern_mapping_df = pattern_mapping_df.iloc[:, 1:3]
    pattern_mapping = pattern_mapping_df.set_index('Module').apply(lambda x: x.dropna().tolist(),axis=1).to_dict()
    test = value.strip()
    txt =[]# Remove leading and trailing spaces from test
    for pattern, values in pattern_mapping.items():
        if pattern.lower() == test.lower():
            txt = values
            break
        else:
            txt = []
    return txt

def generate_random_alphabet(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def sort_restructured_dict(source_dict, target_dict, key_mapping):
    for key in source_dict:
        try:
            # Get the order from source_dict for the current key
            order_source = [key_mapping(item) for item in source_dict[key]]
            # Sort target_dict based on the order from source_dict for the current key
            target_dict[key] = sorted(target_dict[key],key=lambda x: order_source.index(key_mapping(x)) if key_mapping(x) in order_source else float('inf'))
        except Exception as e:
            continue

def webdriver_path():
    try:
        driver_path = ChromeDriverManager().install()
        if driver_path.__contains__("chromedriver.exe"):
            print(driver_path)
        else:
            print(driver_path)
            driver_path = driver_path.split("/")[0]
            driver_path = os.path.join(driver_path, "chromedriver.exe")
            print(driver_path)
        return driver_path
    except Exception as e:
        raise e
def status(Title,component,status,comments):
    df_Values = {'Title':[Title], 'Componentname': [component],'Status':[status], 'Comments':[comments]}
    return df_Values

def Page_up(driver):
    """
        Scroll the web page up by simulating the PAGE UP key press and other methods.
        Args:
            driver: The WebDriver instance for the web page or application.
        Returns:
            None
        """
    try:
        actions = ActionChains(driver)
        for i in range(1, 5):
            time.sleep(1)
            actions.send_keys(Keys.PAGE_UP).perform()
            time.sleep(1)
            actions.send_keys(Keys.CONTROL + Keys.HOME).perform()
            actions.key_down(Keys.CONTROL).send_keys(Keys.HOME).key_up(Keys.CONTROL).perform()
            driver.execute_script("window.scrollBy(0, -window.innerHeight);")
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollTop - 1000);")
            driver.execute_script("window.scrollTo(0, 0);")
    except Exception as e:
        print("Error occurred while performing page up:", e)
###########################################################################################################################################################################################################################
def Page_Down(driver):
    """
        Scroll the web page down by simulating the PAGE DOWN key press.
        Args:
            driver: The WebDriver instance for the web page or application.
        Returns:
            None
        """
    try:
        actions = ActionChains(driver)
        for i in range(1, 5):
            actions.send_keys(Keys.PAGE_DOWN).perform()
    except Exception as e:
        print("Error occurred while performing Page_Down:", e)

def alert_accept(driver):
    """
        Accept and close an alert dialog in a web page.
        Args:
            driver (WebDriver): The WebDriver object for interacting with the web application.
        Returns:
            str: The text message displayed in the alert dialog before it was accepted and closed.
        Notes:
            This function switches the WebDriver's context to an alert dialog, retrieves the text displayed in the alert,
            accepts (clicks the OK button), and then returns the text message. It is commonly used for handling alert dialogs
            or pop-up windows in web applications where user confirmation or acknowledgment is required.
        """
    alert = driver.switch_to.alert
    alert_text = alert.text
    alert.accept()
    return alert_text

def convert_to_float(value):
    """
        Convert a value to a float if possible; otherwise, return the original value.
        Args:
            value: The value to be converted.
        Returns:
            float or original value: The converted float value or the original value if conversion is not possible.
        """
    try:
        return float(value)
    except (ValueError, TypeError):
        return value

##########################################################################################################################################################################################################
def countdown_timer(seconds):
    if isinstance(seconds,int):
        while seconds:
            mins, secs = divmod(seconds, 60)
            hours, mins = divmod(mins, 60)
            timer = f'{hours:02}:{mins:02}:{secs:02}'
            print(f'Time remaining: {timer}', end="\r")
            time.sleep(1)
            print("Time's up!")
            return True
        return False
    else:
        return True
def enable_of_element_untill_loaded(driver,locator,time,seconds:Optional[int]=None)->[int]:
    flag_enabled = False
    try:
        while WebDriverWait(driver, time).until(EC.presence_of_element_located(locator)) and countdown_timer(seconds):
            flag_enabled = False
            if isinstance(seconds,int):
                seconds -= 1
            try:
                element = WebDriverWait(driver,time).until(EC.presence_of_element_located(locator))
                if element.is_enabled():
                    flag_enabled = True
                    break
            except Exception as e:
                pass
    except Exception as e:
        pass
    finally:
        return flag_enabled
###################################################################################################################################################################################################################
def select_from_listbox_ECs(driver, listbox_locator, nested_locators, option_text_list, Title, path):
    """
        Purpose:
                The select_from_listbox_ECs function is designed for the purpose of interacting with listboxes on web pages and selecting
                multiple options from them. It is equipped with explicit waits to ensure that the listbox and option elements are
                visible and interactable, making it a reliable choice for automating interactions with listboxes containing nested
                option elements.

            Arguments:
                driver (WebDriver): This argument expects a WebDriver object, which is essentially the driver for the
                                    web application being automated. It allows the function to interact with and control the web page.
                listbox_locator (tuple): This argument should be provided as a tuple, representing the
                                        locator strategy (e.g., "XPath," "CSS selector") and the corresponding value
                                        to locate the listbox element on the web page. This is the element that opens
                                        up the list of options.
                nested_locators (list): To locate and interact with the individual options within the listbox,
                                        a list of dictionaries containing locators is expected. Each dictionary in the
                                        list should contain two key-value pairs: "locator by" and "locator." "Locator by"
                                        specifies the strategy to locate the option element (e.g., "XPath," "CSS selector"),
                                        while "locator" provides the specific locator value with a placeholder for the option text.
                                        The function will iterate through this list to select each option.
                option_text_list (list): This is a list of option texts that you want to select from the listbox.
                                        The function will click on each option from this list in the listbox.
                Title (str): This argument expects a string that represents the title or name of the web page or application being automated.
                            It helps in providing context for reporting and debugging purposes.
                path (str): The path to the current test case or script. This is useful for tracking the location of
                            the test case or script being executed.
            Returns:
                The function returns a tuple containing two values:
                flag: This is an indicator of success or failure. It will be set to 0 for success and 1 for failure.
                alert_text: If an alert dialog is encountered during the operation, this value will contain the text message displayed in the alert. If no alert is present, it will be None.
                Notes:
                The primary purpose of this function is to interact with listboxes on web pages and select options from them.
                It does so by clicking on each option individually.
                Explicit waits are used to ensure that the listbox and option elements are visible and can be interacted with.
                This enhances the reliability of the automation.
                The function is equipped to handle exceptions that may occur during the operation, such as ElementClickInterceptedException, TimeoutException, UnexpectedAlertPresentException, and NoAlertPresentException.
                The explicit waits and handling of exceptions make this function suitable for scenarios where web pages contain complex listboxes with nested option elements.
                The function returns a flag to indicate the success or failure of the operation and any alert text encountered during the process. This information can be valuable for reporting and debugging purposes.
        """
    option_text1 = None
    option_element = None
    alert_text = None
    option_text = None
    flag = 1
    alert_text = None
    try:
        try:
            # Wait for the listbox to be visible
            listbox_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(listbox_locator))
            # Click on the listbox to open it
            listbox_element.click()
        except (ElementClickInterceptedException or TimeoutException):
            listbox_element = driver.find_element(*listbox_locator)
            try:
                action = ActionChains(driver)
                action.move_to_element(listbox_element).click().perform()
            except:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(listbox_locator)).click()
        except Exception as e:
            raise e
        for option_text in option_text_list:
            option_text1 = option_text
            # Find the nested option element
            option_locator = None
            for locator_dict in nested_locators:
                locator = (locator_dict['locator by'], locator_dict['locator'].format(option_text))
                option_element = driver.find_element(*locator)
                break
            try:
                option_element.click()
            except ElementClickInterceptedException:
                # If the option is covered by another element, try scrolling to it first
                action = ActionChains(driver)
                action.move_to_element(option_element).click().perform()
            except Exception as e:
                raise e
        time.sleep(1.2)
        try:
            alert_text = alert_accept(driver)
        except UnexpectedAlertPresentException:
            alert_text = alert_accept(driver)
        except NoAlertPresentException:
            pass
        flag = 0
        with allure.step(f'Successfully selected options from listbox'):
            allure.attach(driver.get_screenshot_as_png(), name="listbox_screenshot",attachment_type=allure.attachment_type.PNG)
        return flag, alert_text
    except Exception as e:
        updatecomponentstatus(Title, option_text, "FAILED","Unable to locate the element/No such element found and so error in selecting " + option_text + " from listbox", path)
        raise e
###################################################################################################
def clickEC_for_listbox(driver, locators, Title, path):
    """
        Click on an element within a listbox using Expected Conditions (EC).
        Args:
            driver: The WebDriver instance for the web page or application.
            locators (tuple): The locators (By, value) used to locate the element within the listbox.
            Title (str): The title of the test case.
            path (str): The path for saving screenshots.
        Returns:
            tuple: A tuple containing a flag (0 for success, 1 for failure) and an alert text (if any).
        """
    flag = 1
    alert_text = None
    option_text = locators[2]
    Locators = [locators[0], locators[1]]
    try:
        try:
            # Wait for the element to be clickable and click it
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(Locators))
            element.click()
            time.sleep(0.5)
        except ElementClickInterceptedException:
            # Handle ElementClickInterceptedException by moving to the element and clicking
            element1=driver.find_element(*Locators)
            action = ActionChains(driver)
            action.move_to_element(element1).click().perform()
        try:
            # Check for and accept any alert present after the click
            alert_text = alert_accept(driver)
        except UnexpectedAlertPresentException as e:
            alert_text = alert_accept(driver)
        except NoAlertPresentException as e:
            pass
        flag =0 # Indicate success
        return flag,alert_text
    except Exception as e:
        with allure.step("Failed to click on " + option_text + "element"):
            # Attach a screenshot to the Allure report for debugging
            allure.attach(driver.get_screenshot_as_png(), name=f"{option_text}_screenshot",attachment_type=allure.attachment_type.PNG)
            # Update the test case status and log the error message
            updatecomponentstatus(Title, option_text, "FAILED","Unable to locate the element/No such element found and so error in selecting " + option_text + " from listbox", path)
            raise e

#######################################################################################################################################################################################################
def interact_with_blobmap(driver, blobmap_locator, mapelement, elementname):

    blob_found_flag = None
    try:

        # Wait for the map element to be displayed
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located(blobmap_locator))
        blob_found_flag = finding_blob(driver, blobmap_locator, elementname, mapelement)
        return blob_found_flag
    except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name=f"{elementname}_Blob_Not_Found",attachment_type=allure.attachment_type.PNG)
            return blob_found_flag

######################################################################### finding blob ###########################################################################################
def finding_blob(driver,blobmap_locator,elementname,mapelement):

    blobmaps = driver.find_elements(*blobmap_locator)

    if any(blob.is_displayed() for blob in blobmaps):
        blob_found_flag = "Blob found"
        allure.attach(driver.get_screenshot_as_png(), name=f"{elementname}_Blob_Visible",attachment_type=allure.attachment_type.PNG)
        return blob_found_flag

    else:
        blob_found_flag = "Blob not found"
        return blob_found_flag

#########################################################################################################################################################################################################

def uncheck_listOfcampaign(driver, locators):
    """
    Function Name: uncheck_listOfcampaign
        Purpose:
                The uncheck_listOfcampaign function is designed to uncheck a checkbox element on a web page.
                It allows you to programmatically unselect a checkbox, which is a common interaction in web testing scenarios.

        Arguments:
        driver (WebDriver): This argument expects a WebDriver object, which is responsible for interacting with the web application.
                            It is used to locate and manipulate the checkbox element.
        locators (tuple): This argument is a tuple that contains information about how to locate the checkbox element.
                            It includes the following elements:
        locatortype: A string representing the locator strategy (e.g., "XPath," "CSS selector") to be used to find the checkbox.
        locatorProperty: A string representing the specific value or property that helps locate the checkbox.
        elementname: A descriptive name or identifier for the checkbox element. This provides context for the operation.
        Returns:
            The function returns a boolean value. It returns True if the checkbox was successfully unchecked, and False if there was an issue or an exception occurred during the process.
        Notes:
            The primary purpose of this function is to uncheck a checkbox element on a web page.
        The function follows these steps:
            It uses the provided locators tuple to locate the checkbox element on the web page.
            If the checkbox is currently selected (checked), it clicks on it to uncheck it.
            The function returns True to indicate a successful unchecking of the checkbox.
            If there is any issue during the process, such as the checkbox not being found or an exception occurring,the function captures a screenshot of the web page for debugging purposes and returns False to indicate the failure to uncheck the checkbox.
            This function is suitable for web testing scenarios where you need to automate interactions with checkboxes, specifically unchecking them.
            It provides a way to handle checkbox interactions in a robust manner.
            """
    elementname = None
    try:
        locatortype, locatorProperty, elementname = locators
        List_of_Campaigns_checkBox = driver.find_element(locatortype,locatorProperty)  # List of Campaigns CheckBox
        if List_of_Campaigns_checkBox.is_selected():
            List_of_Campaigns_checkBox.click()
        return True
    except Exception as e:
        with allure.step(f"Failed to uncheck the {elementname} checkbox"):
            allure.attach(driver.get_screenshot_as_png(), name=f"{elementname}_screenshot", attachment_type=allure.attachment_type.PNG)
        return False

######################################################################################################################################################################
def change_the_download_path(driver,downloadpath):
    """
        Change the default download path or environment-set path during driver initialization to a user-defined path.
        Args:
            driver (WebDriver): The WebDriver instance for the web page or application.
            downloadpath (str): The user-defined download path where files will be saved.
        Returns:
            None
        """
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior','params': {'behavior': 'allow', 'downloadPath':downloadpath}}
    driver.execute("send_command", params)

##############################################################################################################################################
def readCSVSheet(Title, txt,result_status,downloadfilespath):
    """
        Read and process CSV files, append data to an Excel worksheet, and handle exceptions.
        This function seems to be designed to work with export views
        Args:
            driver (WebDriver): The WebDriver object for interacting with the web application.
            Title (str): The title or description of the operation being performed.
            txt (str): The text or type of CSV file to be processed.
            path (str): The path to the Excel workbook where data will be appended.
            downloadfilespath (str): The path to the folder containing CSV files.
        Returns:
            None
        Raises:
            StepFailure: If no CSV files are found, or if errors occur during processing.
        """
    file_path=None
    headerdata =None
    datas = None
    file_name = None
    data1 = None
    CSVFILE = None
    CSVFILE = []
    try:
        list_of_files = glob.glob(downloadfilespath + "\\*.csv")
        if list_of_files.__len__() == 0:
            position = 0
            CSVFILE.insert(position,"No CSV FILE")
            e = Exception
            raise e
        elif list_of_files.__len__() != 0:
            position = 0
            CSVFILE.insert(position,"CSV file is present")
        if CSVFILE[0] == "CSV file is present":
            try:
                file_names_path = []
                file_path = ""
                # Iterate over all items in the folder
                for item in os.listdir(downloadfilespath):
                    # Check if the item is a file and has a .csv extension
                    if item.lower().endswith(".csv"):
                        file_path = os.path.join(downloadfilespath, item)
                        if "Combined Binary Export" == str(txt) and re.search("Binary_Combined", item,re.IGNORECASE):
                            file_names_path.append(file_path)
                        elif "Hand OverExport" == str(txt) and re.search("Hand Over", item, re.IGNORECASE):
                            file_names_path.append(file_path)
                        elif "Export TableSummary" == str(txt) and re.search("TableSummary", item, re.IGNORECASE):
                            file_names_path.append(file_path)
                        elif "Survey Test Export" == str(txt) and re.search("Survey", item, re.IGNORECASE):
                            file_names_path.append(file_path)
                        else:
                            file_names_path.append(file_path)
                for file_path in file_names_path:
                    # Iterate over the 'datas' list and write each row to the destination worksheet
                    df = pd.read_csv(file_path)
                    df_data = df.to_dict(orient='list')
                    file_name = os.path.basename(file_path)
                    try:
                        if len(df_data) != 0:
                            CSVFILE = [f"CSV file is not empty {str(file_name)}"]
                            updatecomponentstatus2 = status(Title, txt, "PASSED", f"Passed step :- {CSVFILE[0]}")
                            result_status.put(updatecomponentstatus2)
                            # Convert the DataFrame to an HTML table
                            html_table = df.to_html()
                            df_data[f"{str(txt)}"] = [str(file_name)] * len(df)
                            # Attach the HTML content to the Allure report
                            allure.attach(html_table, f"Table data{str(file_name)}", AttachmentType.HTML)
                        elif len(df_data) ==0:
                            dfdata = {}
                            dfdata[f"{str(txt)}"] = [" CSV file is empty {str(file_name)}"]
                            df1 = pd.DataFrame(dfdata)
                            # Convert the DataFrame to an HTML table
                            html_table = df1.to_html()
                            # Attach the HTML content to the Allure report
                            allure.attach(html_table, f"Table data{str(file_name)}", AttachmentType.HTML)
                            CSVFILE = [f"CSV file is empty {str(file_name)}"]
                            e = Exception
                            raise e
                    except Exception as e:
                        continue
            except Exception as e:
                raise StepFailure(e)
    except Exception as e:
        with allure.step(f"failed step :- {CSVFILE[0]}"):
            updatecomponentstatus2 = status(Title, txt, "FAILED", f"failed step :- {CSVFILE[0]}")
            result_status.put(updatecomponentstatus2)
            dfdata1 ={}
            dfdata1[f"{str(txt)}"] = [f"failed step :- {str(file_name)} {CSVFILE[0]}"]
            raise StepFailure(e)
    finally:
        list_of_files = glob.glob(downloadfilespath + "\\*.csv")
        if list_of_files.__len__() != 0:
            csv_files = os.listdir(downloadfilespath + "\\")  # Get the list of CSV files in the folder
            for csv_file in list_of_files:
                csv_file_path = os.path.join(downloadfilespath + "\\", csv_file)
                xlsx_file_path = os.path.join(downloadfilespath + "\\", csv_file.rsplit('.', 1)[0] + '.xlsx')
                data = pd.read_csv(csv_file_path)  # Read the CSV file using pandas
                data.to_excel(xlsx_file_path, index=False)
                os.remove(csv_file_path)

########################################################################################################################################
def compare_values(value1, value2):
    """
        Compare two values while handling various data types (string, float, int, string with numeric values).
        Args:
            value1: The first value for comparison.
            value2: The second value for comparison.
        Returns:
            bool: True if the values are equal, False otherwise.
        """
    try:
        if str(value1).lower() == 'NaN'.lower() or str(value1).lower() == ' '.lower() or str(value1).lower() == ''.lower() :
            value1 = 'None'
    except:
        pass
    try:
        if str(value2).lower() == 'NaN'.lower() or str(value2).lower() == ' '.lower() or str(value2).lower() == ''.lower():
            value2 = 'None'
    except:
        pass
    if not value1 is None and not value2 is None:
        value1 = convert_to_float(value1)
        value2 = convert_to_float(value2)
        value1 = handling_all_data_type_for_comparsion(value1)
        value2 = handling_all_data_type_for_comparsion(value2)
    if value1 is None and value2 is None:
        return str(value1) == str(value2)
    elif is_numeric(value1) and is_numeric(value2):
        # Compare floats with a tolerance of 1e-6 to handle small differences due to float representation
        return value1 == value2
    else:
        str_value1 = str(value1).lower().strip()
        str_value2 = str(value2).lower().strip()
        return str_value1 == str_value2

###############################################################################################################################
def handling_all_data_type_for_comparsion(value):
    """
        Handle and normalize various data types (string, float, int, string with numeric values) for comparison.
        Args:
            value: The value to be processed.
        Returns:
            str: The normalized and processed value for comparison.
        """
    try:
        if str(value).lower() == 'NaN'.lower() or str(value).lower() == ' '.lower() or str(value).lower() == ''.lower():
            value = 'None'
    except:
        pass
    if not value is None:
        value = convert_to_float(value)
    try:
        numeric_part = re.search(r'([a-zA-Z]+)?(\d+(\.\d+)?|\.\d+)([a-zA-Z]+)?', value)
        if numeric_part:
            prefix = numeric_part.group(1) or ''
            numeric_value = numeric_part.group(2)
            suffix = numeric_part.group(4) or ''
            return f'{prefix}{float(numeric_value)}{suffix}'.lower().strip().replace(" ", '')
        else:
            return str(value).lower().strip().replace(" ", '')
    except (ValueError, TypeError):
        return str(value).lower().strip().replace(" ", '')
########################################################################################################################################
def is_numeric(value):
    """
        Check if a value is of a numeric data type (e.g., float or int).
        Args:
            value: The value to be checked.
        Returns:
            bool: True if the value is numeric, False otherwise.
        """
    return pd.api.types.is_numeric_dtype(value)
####################################################################################################################################
def update_module_status_based_on_reading_component_status(modules,excelpath):
    for module , status_for_failed  in modules.items():
        runvalue = Testrun_mode(value=module)
        if "Yes".lower() == runvalue[-1].strip().lower():
            status_text = readcomponentstatus_(status_word=status_for_failed, path=excelpath, Titlename=module,condition="contains")
            if status_text == "FAILED":
                updatehighmodulestatus(module, status_text, comments=f"This module is failed", path=excelpath)
            elif status_text == "PASSED":
                updatehighmodulestatus(module, status_text, comments=f"This module is passed", path=excelpath)
        elif "No".lower() == runvalue[-1].strip().lower():
            updatehighmodulestatus(module, status = "SKIPPED", comments=f"You have selected No for execute", path=excelpath)

######################################################################################################################################################
def readcomponentstatus_(status_word, path, Titlename,condition):
    df = pd.read_excel(path,sheet_name= "COMPONENTSTATUS")
    df_title = None
    if not df.empty:
        if condition == "eq":
            df_title = df[df["Title"].eq(Titlename)]
        elif condition == "contains":
            df_title = df[df["Title"].str.contains(Titlename, case=False, na=False)]
        if not df_title.empty:
            df_list = df_title["Status"].tolist()
            if df_list.__contains__(status_word):
                return "FAILED"
            elif not df_list.__contains__(status_word):
                return "PASSED"
        elif df_title.empty:
            return "FAILED"
    elif df.empty:
        return "FAILED"

def extract_table_datas_span(driver, table_locator,tablename,elementname,Title,path):
    """
        Extract data from an HTML table on a web page using <span> elements.
        Args:
            driver (WebDriver): The WebDriver object for interacting with the web application.
            table_locator (tuple): A tuple representing the locator strategy and value to locate the table.
            tablename (str): The name or description of the table element.
            elementname (str): The name or description of the specific table element being extracted.
            Title (str): The title or description of the operation being performed.
            path (str): The path to the Excel workbook where data will be appended.
        Returns:
            list: A list containing the extracted table data.
        Raises:
            StepFailure: If no data is present in the table or if an exception occurs during extraction.
        """
    headers = None
    table = None
    data = None
    try:
        data = []
        table = WebDriverWait(driver, 10).until(EC.presence_of_element_located(table_locator))
        action = ActionChains(driver)
        action.move_to_element(table).perform()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(table_locator))
        time.sleep(2)
        if table.is_displayed():
            data = html_table_datas_using_span(driver, table,tablename)
        return data
    except Exception as e:
        updatecomponentstatus(Title,elementname, "FAILED", f"In {tablename} for {elementname} No data in table/No table",path)
        raise StepFailure(e)

def html_table_datas_using_span(driver,table,tablename):
    """
        Extract data from an HTML table on a web page using <span> elements.
        Args:
            driver (WebDriver): The WebDriver object for interacting with the web application.
            table (WebElement): The WebElement representing the HTML table.
            tablename (str): The name or description of the table element.
        Returns:
            list: A list containing the extracted table data.
        Raises:
            StepFailure: If no data is present in the table.
        """
    headers = None
    rows = table.find_elements(By.TAG_NAME, "tr")
    data1 = []
    if rows[0].find_elements(By.TAG_NAME, "th"):
        headers = [th.text for th in rows[0].find_elements(By.TAG_NAME, "th")]
        if len(headers) !=0:
            data1.append(headers)
        data = []
        for row in rows[1:]:
            row_data = []
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds)!=0:
                for i in range(len(headers)):
                    try:
                        cell_text = tds[i].find_element(By.TAG_NAME, "span").text
                    except NoSuchElementException:
                        cell_text = tds[i].text
                    row_data.append(cell_text)
                data.append(row_data)
                data1.append(row_data)
    # rows = table.find_elements(By.TAG_NAME, "tr")
    # data1 = []
    #
    # # Check if the first row contains headers
    # if rows[0].find_elements(By.TAG_NAME, "th"):
    #     # Use a lambda to extract the text from <th> elements
    #     headers = list(map(lambda th: th.text, rows[0].find_elements(By.TAG_NAME, "th")))
    #
    #     if len(headers) != 0:
    #         data1.append(headers)
    #
    #     # Initialize data for storing the row data
    #     data = []
    #
    #     # Iterate over each row after the header row
    #     for row in rows[1:]:
    #         tds = row.find_elements(By.TAG_NAME, "td")
    #
    #         if len(tds) != 0:
    #             # Use a lambda inside the list comprehension to handle cell extraction
    #             row_data = [
    #                 (lambda td: td.find_element(By.TAG_NAME, "span").text
    #                 if td.find_elements(By.TAG_NAME, "span")
    #                 else td.text)(td)
    #                 for td in tds[:len(headers)]  # Ensure we don't go beyond headers length
    #             ]
    #
    #             data.append(row_data)
    #             data1.append(row_data)
    else:
        data = []
        for row in rows:
            row_data = []
            tds = row.find_elements(By.TAG_NAME, "td")

            for td in tds:
                try:
                    span_text = td.find_element(By.TAG_NAME, "span").text
                except NoSuchElementException:
                    span_text =  td.text
                row_data.append(span_text)
            data.append(row_data)
    with allure.step(f"Extracted table data from {tablename}"):
        table_html = "<table>"
        if rows[0].find_elements(By.TAG_NAME, "th"):
            table_html += "<tr>"
            for header in headers:
                table_html += "<th>" + header + "</th>"
            table_html += "</tr>"
        for row in data:
            table_html += "<tr>"
            for cell in row:
                table_html += "<td>" + cell + "</td>"
            table_html += "</tr>"
        table_html += "</table>"
        allure.attach(table_html, "Table data", AttachmentType.HTML)
        allure.attach(driver.get_screenshot_as_png(), name="Table data", attachment_type=allure.attachment_type.PNG)
        if data1.__len__() == 0:
            e = Exception
            raise StepFailure(e)
    return data1

def check_selected_and_finding_enable_and_disabled_checkboxes_(driver, checkboxes_locators):
    """
        Uncheck selected checkboxes, find enabled checkboxes, and identify disabled checkboxes within a specified container.
        Args:
            driver (WebDriver): The WebDriver instance for the web page or application.
            checkboxes_locators: The locator(s) for the container containing the checkboxes.
        Returns:
            tuple: A tuple containing two lists - a list of enabled checkboxes and a list of disabled checkboxes.
        """
    disabled_checkboxes = []
    enabled_checkboxes = []
    try:
        # Find the parent element that contains the checkboxes
        checkboxes_parent = driver.find_element(*checkboxes_locators)
        # Find all checkboxes within the parent element
        checkboxes = checkboxes_parent.find_elements(By.TAG_NAME, "label")
        # Iterate through the checkboxes
        for checkbox in checkboxes:
            checkbox_inputs = checkbox.find_elements(By.TAG_NAME, "input")
            for checkbox_input in checkbox_inputs:
                try:
                    if not checkbox_input.is_selected():
                        checkbox_input.click()
                        time.sleep(1)
                    if checkbox_input.is_enabled():
                        text = checkbox.get_attribute("outerText")
                        if text == '' or text == None:
                            text = checkbox.get_attribute("innerText")
                        if text == '' or text == None:
                            text = checkbox.text
                        if text == '' or text == None:
                            text = checkbox.get_attribute("textContent")
                        enabled_checkboxes.append(text)
                    else:
                        text = checkbox.get_attribute("outerText")
                        if text == '' or text == None:
                            text = checkbox.get_attribute("innerText")
                        if text == '' or text == None:
                            text = checkbox.text
                        if text == '' or text == None:
                            text = checkbox.get_attribute("textContent")
                        disabled_checkboxes.append(text)
                except Exception as e:
                    print(f"Error occurred while unchecking checkbox: {str(e)}")
    except Exception as e:
        print(f"Error occurred while finding checkboxes: {str(e)}")
    return enabled_checkboxes, disabled_checkboxes

def extract_table_datas_span1(driver, table_locator,tablename,elementname,Title,path):
    """
        Extract data from an HTML table on a web page using <span> elements.
        Args:
            driver (WebDriver): The WebDriver object for interacting with the web application.
            table_locator (tuple): A tuple representing the locator strategy and value to locate the table.
            tablename (str): The name or description of the table element.
            elementname (str): The name or description of the specific table element being extracted.
            Title (str): The title or description of the operation being performed.
            path (str): The path to the Excel workbook where data will be appended.
        Returns:
            list: A list containing the extracted table data.
        Raises:
            StepFailure: If no data is present in the table or if an exception occurs during extraction.
        """
    headers = None
    table = None
    data = None
    try:
        table = WebDriverWait(driver,0.1).until(EC.presence_of_element_located(table_locator))
        action = ActionChains(driver)
        action.move_to_element(table).perform()
        if table.is_displayed():
            data = html_table_datas_using_span(driver, table,tablename)
        return data
    except Exception as e:
        raise StepFailure(e)

def html_for_csv(data,file_name):
    """
        Create an HTML table representation of CSV data and attach it to an Allure report.
        Args:
            data (list of lists): The CSV data as a list of lists.
            file_name (str): The name of the CSV file (used for the attachment name).
        Returns:
            None
        """
    html = ['<table class="my-table">', '<style>',
            '.my-table { font-family: Arial, sans-serif; border-collapse: collapse; width: 100%; }',
            '.my-table th, .my-table td { border: 1px solid #ddd; padding: 8px; }',
            '.my-table th { background-color: #f2f2f2; }',
            '.my-table td { transition: background-color 0.3s; }',
            '.my-table td:hover { background-color: #f8f8f8; }',
            '.my-table.fade-in { animation: fade-in 1s ease-in; }',
            '@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }',
            '</style>']
    for i, sublist in enumerate(data):
        if i < 2:
            html.append('<tr>')
            html.extend([f'<th>{cell}</th>' for cell in sublist])
            html.append('</tr>')
        else:
            html.append('<tr class="fade-in">')
            html.extend([f'<td>{cell}</td>' for cell in sublist])
            html.append('</tr>')
    html.append('</table>')
    allure.attach(''.join(html), f"Table data{file_name}", AttachmentType.HTML)

def updating_datavalidation_for_each_module(excelpath,modules):
    for module, result in modules.items():
        runvalue = Testrun_mode(value=module)
        if "Yes".lower() == runvalue[-1].strip().lower():
            if "Default Settings" == module:
                updating_comparison_results_to_excel1(result,excelpath, "RESULTS_DEFAULT_SETTINGS")
            elif "Change Settings" == module:
                updating_comparison_results_to_excel1(result, excelpath, "RESULTS_CHANGE_SETTINGS")

def extract_table_datas_content(driver, table_locator,time,elementname,Title,path,extracttype,sub_tags: Optional[List[str]] = None) -> List[List[str]]:
    """
        Extract and return content data from an HTML table on a web page.
        Args:
            driver (WebDriver): The WebDriver object for interacting with the web application.
            table_locator: Locator for finding the HTML table element.
            elementname (str): The name or description of the element being processed.
            Title (str): The title or description of the operation being performed.
            path (str): The path to the Excel workbook where data will be appended.
            extracttype (str): The type of extraction ("text" for .text, "textContent" for textContent).
            sub_tags (Optional[List[str]]): A list of tag names to look for within table cells, or None to skip sub-tag extraction.
        Returns:
            list: A list containing the extracted content data from the HTML table.
            """
    headers = None
    table= None
    try:
        table = WebDriverWait(driver, time).until(EC.presence_of_element_located(table_locator))
        datacontent = html_table_datas_for_content(driver, table,extracttype,"tr","td",sub_tags)
        return datacontent
    except Exception as e:
        updatecomponentstatus(Title,elementname, "FAILED", "No data in table",path)
        raise StepFailure(e)

def html_table_datas_for_content(driver: WebDriver, table: WebElement, extracttype: str = "text", row_tag: str = "tr", cell_tag: str = "td", sub_tags: Optional[List[str]] = None) -> List[List[str]]:
    """
    Extract and process HTML table data containing content, converting it into a structured format.

    Args:
        driver (WebDriver): The WebDriver object for interacting with the web application.
        table (WebElement): The HTML table element containing content to be processed.
        extracttype (str): The type of extraction ("text" for .text, "html" for innerHTML).
        row_tag (str): The tag name for table rows. Default is "tr".
        cell_tag (str): The tag name for table cells. Default is "td".
        sub_tags (Optional[List[str]]): A list of tag names to look for within table cells, or None to skip sub-tag extraction.

    Returns:
        List[List[str]]: A list of lists representing the extracted content data from the HTML table.
    """
    rows = table.find_elements(By.TAG_NAME, row_tag)
    datacontent = []

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, cell_tag)
        row_data = []

        if len(cells) != 0:
            for cell in cells:
                cell_text = ""
                if sub_tags:
                    for tag in sub_tags:
                        try:
                            element = cell.find_element(By.TAG_NAME, tag)
                            if extracttype == "text":
                                cell_text = element.text
                            elif extracttype == "textContent":
                                cell_text = element.get_attribute('textContent')
                            break
                        except NoSuchElementException:
                            continue
                else:
                    if extracttype == "text":
                        cell_text = cell.text
                    elif extracttype == "textContent":
                        cell_text = cell.get_attribute('textContent')

                # Exclude cells with class "ng-binding ng-hide"
                if "ng-binding ng-hide" not in cell.get_attribute("class"):
                    row_data.append(str(cell_text).strip())
            datacontent.append(row_data)

    return datacontent

def comparsion_values_in_bw_two_list(list1,list2):
    """
        Compare two lists with constraints, handling various data types in the elements.
        Args:
            list1 (list): The first list for comparison.
            list2 (list): The second list for comparison.
        Returns:
            bool: True if the lists are equal with constraints, False otherwise.
        """
    list1_normalized = [handling_all_data_type_for_comparsion(x) for x in list1]
    list2_normalized = [handling_all_data_type_for_comparsion(x) for x in list2]
    print(list2_normalized)
    print(list1_normalized)
    return all(x in list2_normalized for x in list1_normalized) and all(y in list1_normalized for y in list2_normalized)

def count_decimal_points(value):
    # Convert the value to a string
    value_str = str(convert_to_float(value)).replace(" ","")

    # Check if there's a decimal point
    if '.' in value_str or re.search(".",value_str,re.IGNORECASE):
        # Split by the decimal point and get the part after it
        decimal_part = value_str.split('.')[1]
        # Return the length of the decimal part
        return len(decimal_part)
    else:
        # If there's no decimal point, return 0
        return 0

###############################################################################################################################################
def filter_df(df,Columnheader,item):
    if Columnheader not in df.columns:
        raise ValueError(f"Column '{Columnheader}' does not exist in the DataFrame.")
    if re.match("~",item,re.IGNORECASE) or re.search("~",item,re.IGNORECASE):
        item = str(item).replace("~","")
        item = convert_to_float(item)
        if isinstance(item,float):
            df[Columnheader] = pd.to_numeric(df[Columnheader], errors='coerce')
            df = df[df[Columnheader] > -1]
            df = df[~df[Columnheader].eq(float(item))]
        else:
            df[Columnheader] = df[Columnheader].astype(str).fillna('')
            # pattern = r'\b{}\b'.format(str(item))
            pattern = r'(?:^|[_\s]){}(?:[_\s]|$)'.format(item)
            df = df[~df[Columnheader].str.contains(pattern,case=False,na=False)]
    elif not re.match("~",item,re.IGNORECASE) or not re.search("~",item,re.IGNORECASE):
        if isinstance(item,float):
            df[Columnheader] = pd.to_numeric(df[Columnheader], errors='coerce')
            df = df[df[Columnheader] > -1]
            df = df[df[Columnheader].eq(float(item))]
        else:
            df[Columnheader] = df[Columnheader].astype(str).fillna('')
            # pattern = r'\b{}\b'.format(str(item))
            pattern = r'(?:^|[_\s]){}(?:[_\s]|$)'.format(item)
            df = df[df[Columnheader].str.contains(pattern, case=False, na=False)]
    return df
###############################################################################################################################################
def df_to_values_list_for_particular_header(parameter,df_gr):
    try:
        df_data = df_gr[parameter].tolist()
        return df_data
    except Exception as e:
        raise e

def avg(numbers):
    try:
        # average = sum(numbers)/len(numbers)
        average = statistics.mean(numbers)
        return average
    except Exception as e:
        raise e

def values_list_below(df_values,start_range):
    filtered_data_list = [v for v in df_values if start_range >= v]
    return filtered_data_list

def values_list_above(df_values,start_range):
    filtered_data_list = [v for v in df_values if start_range <= v]
    return filtered_data_list
def values_list_betweenOrto(df_values,start_range,end_range):
    filtered_data_list = [v for v in df_values if start_range <= v <= end_range]
    return filtered_data_list
def percentage(**params):
    df_data = params.get('df_data')
    filtered_data_list = params.get('filtered_data_list')

    if df_data is None or filtered_data_list is None:
        raise ValueError("Both 'df_data' and 'filtered_data_list' must be provided as parameters.")

    percentage_value = (len(filtered_data_list) / len(df_data)) * 100 if len(df_data) > 0 else 0
    formatted_percentage = percentage_value
    return formatted_percentage

def extract_numeric_value(text):
    # Replace non-numeric characters with whitespace and leading/trailing whitespaces
    numeric_part = ''.join(filter(lambda x: x.isdigit() or x in '. ', text)).strip()

    if numeric_part:
        return float(numeric_part)
    else:
        return None


def time_differnce_in_minute_sec_start_time_end_time(start_time, end_time, time_format: Optional = None):
    from datetime import datetime
    if time_format is None:
        # Define the time format
        time_format = "%H:%M:%S"

    # Convert the strings to datetime objects
    t1 = datetime.strptime(start_time, time_format)
    t2 = datetime.strptime(end_time, time_format)

    # Calculate the difference in seconds
    time_difference = (t2 - t1).total_seconds()

    # Convert the difference to minutes and seconds
    minutes = time_difference // 60
    seconds = time_difference % 60

    time_difference_value = f"{int(minutes)}:{int(seconds)}"
    print(time_difference_value)
    return time_difference_value

def time_difference_in_seconds(start_time: str, end_time: str, time_format: Optional[str] = None) -> int:
    from datetime import datetime
    if time_format is None:
        time_format = "%H:%M:%S"  # Default time format including date and time

    # Convert the strings to datetime objects
    t1 = datetime.strptime(start_time, time_format)
    t2 = datetime.strptime(end_time, time_format)

    # Calculate the time difference in seconds
    time_difference_in_seconds = (t2 - t1).total_seconds()

    return int(time_difference_in_seconds)

# Function to wait until a numeric value is present in the element
def wait_for_numeric_value(driver, locator, timeout, getattribute_value=None):
    # WebDriverWait to wait for a numeric value in the element
    return WebDriverWait(driver, timeout).until(lambda d: check_for_numeric_value(d, locator, getattribute_value))

# Helper function to check if the element contains a numeric value
def check_for_numeric_value(driver, locator,getattribute_value=None):
    element = driver.find_element(*locator)
    if getattribute_value != None:
        element_text = element.get_attribute(getattribute_value)
    else:
        element_text = element.text

    # Check if there is any numeric value in the text
    if re.search(r'\d+', element_text):  # '\d+' matches one or more digits
        return True
    return False

# Function to read encrypted Excel by specifying a sheet name
def return_df_of_encrypted_excel_file(file_path, sheet_name,password):
    try:
        # Open the encrypted file
        with open(file_path, 'rb') as encrypted_file:
            # Initialize the msoffcrypto OfficeFile object
            encrypted = msoffcrypto.OfficeFile(encrypted_file)

            # Provide the password directly in the code
            encrypted.load_key(password=password)

            # Create a BytesIO object to store the decrypted data
            decrypted_file = io.BytesIO()

            # Decrypt the Excel file
            encrypted.decrypt(decrypted_file)

            # Use openpyxl to read the decrypted file
            decrypted_file.seek(0)

            df = pd.read_excel(decrypted_file,sheet_name=sheet_name)

            return df
    except Exception as e:
        print("Error reading file:", e)
        return None

def specifying_download_path(driver,downloadfilespath,foldername):
    downloadpath= create_folder_for_downloads(destination_folder=downloadfilespath+foldername)
    change_the_download_path(driver,downloadpath)
    return downloadpath

def check_dir_where_all_read_csv_file_contains_data(folderpath):
    try:
        list_of_files = glob.glob(folderpath + "\\*.csv")
        not_empty_file_flag = True
        empty_csv_files = []
        if list_of_files.__len__() != 0:
            for csvfile in list_of_files:
                df = pd.read_csv(csvfile)
                if not df.empty:
                    pass
                elif df.empty:
                    not_empty_file_flag = False
                    empty_csv_files.append(csvfile)
            return not_empty_file_flag , empty_csv_files
        elif list_of_files.__len__() == 0:
            not_empty_file_flag = None
            empty_csv_files.append("No csv found in this directory")
            return not_empty_file_flag , empty_csv_files
    except Exception as e:
        pass
