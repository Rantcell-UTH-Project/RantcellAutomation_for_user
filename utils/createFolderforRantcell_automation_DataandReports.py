import pathlib, os, shutil
from datetime import datetime
import datetime
def create_folder_for_rantcell_data_and_ExcelReport(RantCell_automation_Data_and_Reports_folder, RantCell_automation_source_folders):
    """
        Create a folder for RantCell automation data and reports, and copy source folders into it.
        Args:
            RantCell_automation_Data_and_Reports_folder (str): The path to the folder where data and reports will be stored.
            RantCell_automation_source_folders (list): A list of source folders to be copied into the destination folder.
        Notes:
            This function creates a folder for RantCell automation data and reports if it doesn't already exist.
            It then copies the specified source folders into the destination folder. The source folders are provided in
            'RantCell_automation_source_folders'.
        Raises:
            AssertionError: If an error occurs during folder creation or copying, an assertion error is raised.
        """
    try:
        if not os.path.exists(RantCell_automation_Data_and_Reports_folder):
            os.makedirs(RantCell_automation_Data_and_Reports_folder)
            print("Folder created successfully.")
        else:
            print("Folder already exists.")
        # Copy the source folders to the destination folder
        for source_folder in RantCell_automation_source_folders:
            path = pathlib.Path(__file__).parent.parent
            source_directory = str(path / source_folder)
            destination_directory = os.path.join(RantCell_automation_Data_and_Reports_folder, os.path.basename(source_folder))
            copy_folder_with_files(source_directory, destination_directory)
        print("Folder copying completed.")
        assert True
    except Exception as e:
        assert False

def copy_folder_with_files(source_directory, destination_directory):
    """
        Copy a folder with its files and subfolders from the source directory to the destination directory.
        Args:
            source_directory (str): The path to the source folder to be copied.
            destination_directory (str): The path to the destination folder where the source folder and its contents will be copied.
        Notes:
            This function recursively copies a folder from the source directory to the destination directory, preserving the folder
            structure and its contents. If the destination directory does not exist, it will be created.
            """
    if not os.path.exists(destination_directory):
        shutil.copytree(source_directory, destination_directory)
        print(f"Copied folder: {source_directory} -> {destination_directory}")
    else:
        for item in os.listdir(source_directory):
            source_item = os.path.join(source_directory, item)
            destination_item = os.path.join(destination_directory, item)
            if os.path.isdir(source_item):
                if not os.path.exists(destination_item):
                    shutil.copytree(source_item, destination_item)
                    print(f"Copied folder: {source_item} -> {destination_item}")
            else:
                if not os.path.exists(destination_item):
                    shutil.copy2(source_item, destination_directory)
                    print(f"Copied file: {source_item} -> {destination_directory}")
def Updating_source_folder(Upadting_RantCell_automation_source_folders,RantCell_automation_Data_and_Reports_folder):
    """
        Update the source folders with any changes from the destination folders.
        Args:
            Updating_RantCell_automation_source_folders (list): A list of source folders to be updated.
            RantCell_automation_Data_and_Reports_folder (str): The path to the destination folder where the source folders are located.
        Notes:
            This function iterates through the list of source folders and checks if there are any changes in the corresponding
            destination folders. If changes are detected, the function copies files or folders from the destination folder back
            to the source folder to update it.
        """
    # Copy the source folders to the destination folder
    for source_folder in Upadting_RantCell_automation_source_folders:
        path = pathlib.Path(__file__).parent.parent
        source_directory = str(path / source_folder)
        destination_directory = os.path.join(RantCell_automation_Data_and_Reports_folder,os.path.basename(source_folder))
        if os.path.exists(destination_directory):
            for item in os.listdir(source_directory):
                source_item = os.path.join(source_directory, item)
                destination_item = os.path.join(destination_directory, item)
                if os.path.isdir(destination_item):
                    if os.path.exists(destination_item):
                        shutil.copytree(destination_item,source_item)
                        print(f"Copied folder: {destination_item} -> {source_item}")
                else:
                    if os.path.exists(destination_item):
                        shutil.copy2(destination_item,source_directory )
                        print(f"Copied file: {destination_item} -> {source_directory}")
def create_folder_for_downloads(destination_folder):
    """
        Create a folder for downloads.
        Args:
            destination_folder (str): The path where the folder for downloads will be created.
        Returns:
            str: The path to the created folder.
        Notes:
            This function creates a folder at the specified 'destination_folder' path for storing downloaded files.
        """
    destination_folder_path = destination_folder
    os.mkdir(destination_folder_path)
    return destination_folder_path

def create_folder_for_excelreport(destination_folder):
    """
        Create a folder for Excel reports.
        Args:
            destination_folder (str): The path where the folder for Excel reports will be created.
        Returns:
            str: The path to the created folder.
        Notes:
            This function creates a folder at the specified 'destination_folder' path for storing Excel reports.
        """
    destination_folder_path = destination_folder
    os.mkdir(destination_folder_path)
    return destination_folder_path

def excel_report_path_(test_run_excelreportdata_path):
    """
        Create a timestamped Excel report folder name and folder name store the timestamp in a text file for future reffernce in test build.
        Args:
            test_run_excelreportdata_path (str): The path where the timestamp file will be created.
        Notes:
            This function creates a timestamped folder with the format 'test_run_excel_report_<timestamp>' and stores the
            timestamp in a file at the specified 'test_run_excelreportdata_path'.
        """
    if os.path.exists(test_run_excelreportdata_path):
        testdata_path = test_run_excelreportdata_path
        if os.path.exists(testdata_path):
            os.remove(testdata_path)
            foldertimestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")
            foldertimestamp = "test_run_excel_report_" + foldertimestamp
            f = open(testdata_path, "x")
            f = open(testdata_path, "a")
            f.write(foldertimestamp)
            f.close()
            f1 = open(testdata_path, "r")
            print(f1.read())
        else:
            foldertimestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")
            foldertimestamp = "test_run_excel_report_" + foldertimestamp
            f = open(testdata_path, "x")
            f = open(testdata_path, "a")
            f.write(foldertimestamp)
            f.close()
            f1 = open(testdata_path, "r")
            print(f1.read())
    else:
        print("Please enter the path in config.py file")
def testRun_downloadfile_path(testRun_downloadfile_path):
    """
        Create a timestamped folder for downloads  and folder name store the timestamp in a text file for future reffernce in test build..
        Args:
            testRun_downloadfile_path (str): The path where the timestamp file will be created.
        Notes:
            This function creates a timestamped folder with the format 'testRun_downloads_<timestamp>' and stores the
            timestamp in a file at the specified 'testRun_downloadfile_path'.
        """
    if os.path.exists(testRun_downloadfile_path):
        testdata_path = testRun_downloadfile_path
        if os.path.exists(testdata_path):
            os.remove(testdata_path)
            foldertimestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")
            foldertimestamp = "testRun_downloads_" + foldertimestamp
            f = open(testdata_path, "x")
            f = open(testdata_path, "a")
            f.write(foldertimestamp)
            f.close()
            f1 = open(testdata_path, "r")
            print(f1.read())
        else:
            foldertimestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")
            foldertimestamp = "testRun_downloads_" + foldertimestamp
            f = open(testdata_path, "x")
            f = open(testdata_path, "a")
            f.write(foldertimestamp)
            f.close()
            f1 = open(testdata_path, "r")
            print(f1.read())
    else:
        print("Please enter the path in config.py file")
