class ReadConfig():
    # Update the Root Folder Path where testdata and excelreport subfolders are created to store Test_Data.xlsx and Excel Reports
    ################# This path can be changed as per user need , If user need to change the path, use can change ####################################

    test_data_folder_rootpath = "C:\\RantCell_Automation_Data_for_user"

    #################################################### DON'T UPDATE ######################################################################
    # Absolute path of Test_Data.xlsx,Map_View_Component.xlsx,Graph_View_Component.xlsx,Pdf_Export,Table_summary,Parameter_validation,etc excel files
    test_data_path = test_data_folder_rootpath + "\\testdata\\Test_Data.xlsx"
    excel_report_path = test_data_folder_rootpath + "\\excelreport\\"
    source_dest = ["excelreport", "testdata","downloads"]
    excel_report_path_for_timestamp = test_data_folder_rootpath + "\\excelreport"
    excel_report_path_with_timestamp = test_data_folder_rootpath + "\\excelreport\\test_run_excelreport"
    updating_source_folders = ["testdata"]
    test_case_downloading_files_path=test_data_folder_rootpath + "\\downloads"
    test_case_downloading_files_path_timestamp=test_data_folder_rootpath + "\\downloads\\"
    test_run_excelreportdata_path = test_data_folder_rootpath+"\\excelreport\\TestRunFolderName.txt"
    test_run_download_file_path =test_data_folder_rootpath+"\\downloads\\TestRun_downloadfileFolderName.txt"
    map_view_components_excelpath = test_data_folder_rootpath + "\\testdata\\Map_View_Components.xlsx"
    settings_path = test_data_folder_rootpath + "\\testdata\\Map_components_Settings.xlsx"
    pdf_export_excel_path = test_data_folder_rootpath + "\\testdata\\pdf_export.xlsx"
    group_reporter_path = test_data_folder_rootpath + "\\testdata\\Group_reporter.xlsx"
    MegronMail_account_details_excel_path = test_data_folder_rootpath +"\\testdata\\MegronMail_account_details.xlsx"
    ############################################################################################################################################
