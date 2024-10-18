from utils.library import *

def login_module_controllers():
    login_runvalue = Testrun_mode(value="Login")
    return login_runvalue
def logout_module_controllers():
    logout_runvalue = Testrun_mode(value="Logout")
    return logout_runvalue
def remote_module_controllers():
    remotetest_runvalue = Testrun_mode(value="Remote Test")
    return remotetest_runvalue
def protestdata_module_controllers():
    protestdata_runvalue = Testrun_mode(value="Pro TestData")
    return protestdata_runvalue
def litetestdata_module_controllers():
    litetestdata_runvalue = Testrun_mode(value="LITE TestData")
    return litetestdata_runvalue
def device_custom_query_module_controllers():
    device_custom_query_runvalue = Testrun_mode(value="Device(Custom Query)")
    return device_custom_query_runvalue
def date_and_time_module_controllers():
    datetime_runvalue = Testrun_mode(value="Date and Time")
    return datetime_runvalue
def module_controllers_for_testing_min():
    testing_min_runvalue = Testrun_mode(value="Testing min")
    return testing_min_runvalue

def exports_module_controllers():
    exports_runvalue = Testrun_mode(value="Exports")
    return exports_runvalue
def default_settings_module_controllers():
    Default_settings_runvalue = Testrun_mode(value="Default Settings")
    return Default_settings_runvalue
def change_settings_module_controllers():
    Change_settings_runvalue = Testrun_mode(value="Change Settings")
    return Change_settings_runvalue

def operatorcomparison_vs_pdf_module_controllers():
    Operator_vs_pdf_runvalue = Testrun_mode(value="Map view(NQC-operator comparison V/S PDF Export)")
    return Operator_vs_pdf_runvalue

def floorplan_module_controllers():
    floorplan_for_map_and_pdf_view = Testrun_mode(value="Floor Plan")
    return floorplan_for_map_and_pdf_view

def account_setting_change_password_module_controllers():
    account_setting_change_password = Testrun_mode("Change password(account settings)")
    return account_setting_change_password

def forgot_password_module_controllers():
    forgot_password = Testrun_mode("Forgot Password")
    return forgot_password

def groupreporter_module_controllers():
    groupreporter_runvalue = Testrun_mode(value="Group Reporter")
    return groupreporter_runvalue

def chart_module_controllers():
    chart_runvalue = Testrun_mode(value="Chart")
    return chart_runvalue

def alarms_module_controllers():
    chart_runvalue = Testrun_mode(value="Alarms")
    return chart_runvalue

def apk_download_module_controllers():
    apk_download_runvalue = Testrun_mode(value="APK Download")
    return apk_download_runvalue

