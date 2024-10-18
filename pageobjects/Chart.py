from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from locators.locators import Chart_section_Components, hover, hover_over_second_graph, get_secondGraph_data, \
    get_graph_data, hover_over_pie_chart, get_piechart_data
from module_controllers.module_controllers import chart_module_controllers
from pageobjects.Dashboard import side_bar_menu_for_work_list_campaigns
from utils.library import *
from utils.readexcel import *
from utils.updateexcelfile import updatecomponentstatus
from pageobjects.login_logout import *
def chart_main_section(driver,userid, password, campaigns_datas, excelpath,campaigns_created,device):
    chart_Title = "Chart"
    chart_runvalue = chart_module_controllers()
    if "Yes".lower() == chart_runvalue[-1].strip().lower():
        try:
            with allure.step("Side Bar Menu for list of campaigns"):
                side_bar_menu_for_work_list_campaigns(driver, userid, password, campaigns_datas, excelpath,campaigns_created,device)
            with allure.step("Chart module"):
                Chart(driver, campaigns_datas, excelpath, chart_Title)
        except:
            pass
        finally:
            driver.refresh()
            dashboard_loading(driver)
    elif "No".lower() == chart_runvalue[-1].strip().lower():
        updatecomponentstatus(chart_Title, "Not to execute", "SKIPPED", "You have selected No for execute", excelpath)
        pass

def Chart(driver, campaigns_datas, excelpath,chart_Title):
    # Fetch components based on the campaign/classifier "T001","T002" etc
    tests_data1 = []
    for i in range(len(campaigns_datas)):
        # previous_device = []
        device, campaign, usercampaignsname, testgroup = campaigns_datas[i]
        # Fetch components based on the campaign/classifier "T001","T002" etc
        remote_test_point, map_start_point, graph_start_point, export_start_point, load_start_point, PDF_Export_index_start_point, END_index = fetch_input_points()
        tests = fetch_components(campaign, graph_start_point, export_start_point)
        tests_data1.append(tests)
    tests_data = [test_data1 for test_data in tests_data1 for test_data1 in test_data]
    tests_data = list(set(tests_data))
    print("tests_data-------------", tests_data)
    Chart_section(driver, tests_data, excelpath,chart_Title)
def Chart_section(driver,tests,excelpath,chart_Title):
    try:
        try:
            clickec(driver, Chart_section_Components.button_chart)
            try:
                driver.execute_script(f"window.scrollTo({0}, {0});")
            except:
                pass
        except Exception as e:
            statement = f"Failed to click on the Chart button for {chart_Title}"
            with allure.step(statement):
                updatecomponentstatus(chart_Title, statement, "FAILED", f"failed step :No graph found", excelpath)
                allure.attach(driver.get_screenshot_as_png(), name=f"_screenshot",attachment_type=allure.attachment_type.PNG)
                raise e

        try:
            if tests.__len__() == 0:
                    statement = f"Chart section  --  Nothing is marked as 'Yes' in {str(config.test_data_path)}"
                    with allure.step(f"Nothing is marked as 'Yes' in {str(config.test_data_path)} for 'Chart section for '{str(tests)}'"):
                        updatecomponentstatus(chart_Title, statement, "FAILED", f"Nothing marked in {str(config.test_data_path)}", excelpath)
                        e = Exception
                        raise e
            else:
                for test in tests:
                    test = test.strip()  # Remove leading and trailing spaces from test
                    test_1 = str(test).lower().replace("test", "").split()[0].capitalize()
                    test_2 = str(test).lower().replace("test", "").replace("iperf", "").split()[0].upper()
                    try:
                        driver.execute_script(f"window.scrollTo({0}, {0});")
                    except:
                        pass
                    try:
                        try:
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located(Chart_section_Components.drop_down_toggle))
                            driver.find_element(*Chart_section_Components.drop_down_toggle).click()
                            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(Chart_section_Components.dropdown_list_txt))
                            Graph_dropdown_list_txt = driver.find_element(*Chart_section_Components.dropdown_list_txt)

                            if 'ping' in str(test).lower():
                                if 'ping' in str(driver.find_element(*Chart_section_Components.drop_down_toggle).text).lower():
                                    if WebDriverWait(driver, 10).until(EC.visibility_of_element_located(Chart_section_Components.dropdown_list_txt)).is_displayed():
                                        driver.find_element(*Chart_section_Components.drop_down_toggle).click()
                                        time.sleep(0.01)
                                        hover_(driver, test, excelpath, chart_Title)
                                        get_graph_data_(driver, test, excelpath,chart_Title)
                                        hover_piechart(driver, test, excelpath, chart_Title)
                                        get_piechart_data_(driver, test, excelpath, chart_Title)

                                elif test in Graph_dropdown_list_txt.text:
                                    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(Chart_section_Components.dropdown_list_txt))
                                    driver.find_element(By.XPATH, f"//a[contains(.,'{str(test)}')]").click()
                                    hover_(driver, test, excelpath,chart_Title)
                                    get_graph_data_(driver, test, excelpath,chart_Title)
                                    hover_piechart(driver, test, excelpath, chart_Title)
                                    get_piechart_data_(driver, test, excelpath, chart_Title)

                            elif test in Graph_dropdown_list_txt.text:
                                try:
                                    driver.find_element(By.XPATH, f"//a[contains(.,'{str(test)}')]").click()
                                    hover_(driver, test, excelpath,chart_Title)
                                    get_graph_data_(driver, test, excelpath,chart_Title)
                                    hover_piechart(driver, test, excelpath, chart_Title)
                                    get_piechart_data_(driver, test, excelpath, chart_Title)
                                finally:
                                    try:
                                        driver.find_element(*Chart_section_Components.second_graph_position)
                                        hover_over_second_graph_(driver, test, excelpath,chart_Title)
                                        get_secondGraph_data_(driver, test, excelpath,chart_Title)
                                    except:
                                        pass
                            elif test_1 in Graph_dropdown_list_txt.text:
                                try:
                                    driver.find_element(By.XPATH, f"//a[contains(.,'{str(test_1)}')]").click()
                                    hover_(driver, test, excelpath,chart_Title)
                                    get_graph_data_(driver, test, excelpath,chart_Title)
                                    hover_piechart(driver, test, excelpath, chart_Title)
                                    get_piechart_data_(driver, test, excelpath, chart_Title)
                                finally:
                                    try:
                                        driver.find_element(*Chart_section_Components.second_graph_position)
                                        hover_over_second_graph_(driver, test, excelpath,chart_Title)
                                        get_secondGraph_data_(driver, test, excelpath,chart_Title)
                                    except:
                                        pass
                            elif test_2 in Graph_dropdown_list_txt.text:
                                try:
                                    driver.find_element(By.XPATH, f"//a[contains(.,'{str(test_2)}')]").click()
                                    hover_(driver, test, excelpath,chart_Title)
                                    get_graph_data_(driver, test, excelpath,chart_Title)
                                    hover_piechart(driver, test, excelpath, chart_Title)
                                    get_piechart_data_(driver, test, excelpath, chart_Title)
                                finally:
                                    try:
                                        driver.find_element(*Chart_section_Components.second_graph_position)
                                        hover_over_second_graph_(driver, test, excelpath,chart_Title)
                                        get_secondGraph_data_(driver, test, excelpath,chart_Title)
                                    except:
                                        pass
                            try:
                                if 'stream' in str(test).lower():
                                    Page_up(driver)
                            except:
                                pass
                        except:
                            try:
                                if 'stream' in str(test).lower():
                                    Page_up(driver)
                            except:
                                pass
                    except Exception as e:
                        try:
                            if 'stream' in str(test).lower():
                                Page_up(driver)
                        except:
                            pass
                        with allure.step(f"failed step :No graph found"):
                            allure.attach(driver.get_screenshot_as_png(), name="Graphdata", attachment_type=allure.attachment_type.PNG)
                            updatecomponentstatus(chart_Title, test, "FAILED", f"failed step :No graph found", excelpath)
                        continue

            Page_up(driver)
            clickec(driver, Chart_section_Components.closechart_button)
        except Exception as e:
            pass
    except Exception as e:
            Page_up(driver)
            clickec(driver, Chart_section_Components.closechart_button)
            print("Chart section Components fail")

def hover_(driver, test, excelpath,chart_Title):
    time.sleep(4)
    canvas = driver.find_element(*hover.canvas)
    # Create an instance of ActionChains
    action_chains = ActionChains(driver)
    action_chains.move_to_element(canvas).perform()
    canvas_width_2 = int(canvas.size['width']/2)
    for i in range(-(canvas_width_2), canvas_width_2, 30):
        try:
            action_chains.move_to_element_with_offset(canvas, i, -30).perform()
            if driver.find_element(*hover.Graph_Tootip_element).is_displayed():
                    break
        except:
            try:
                action_chains.move_to_element_with_offset(canvas, i, 0).perform()
                if driver.find_element(*hover.Graph_Tootip_element).is_displayed():
                    break
            except:
                action_chains.move_to_element_with_offset(canvas, i, 30).perform()
                if driver.find_element(*hover.Graph_Tootip_element).is_displayed():
                    break
    graphdataTooltipElement = driver.find_element(*hover.Graph_Tootip_element)
    graph_data = graphdataTooltipElement.text
    Graph_Dropdown_btn = driver.find_element(*hover.Dropdown_btn)
    Graph_Dropdown_button = Graph_Dropdown_btn.text
    if graph_data == None:
        graph_data = graphdataTooltipElement.get_attribute("outerText")
    if graph_data == None:
        graph_data = graphdataTooltipElement.get_attribute("innerText")
    if graph_data == None:
        allure.attach(driver.get_screenshot_as_png(), name=f"{test} ==> {Graph_Dropdown_button}", attachment_type=allure.attachment_type.PNG)
        statement = f"There is no data in Graph-View for {test} ==> {Graph_Dropdown_button}"
        updatecomponentstatus(chart_Title, f"{test} ==> {Graph_Dropdown_button}", "FAILED", statement, excelpath)
        e = Exception
        raise e

def hover_over_second_graph_(driver, test, excelpath,chart_Title):
    canvas = driver.find_element(*hover_over_second_graph.canvas)
    # Create an instance of ActionChains
    action_chains = ActionChains(driver)
    action_chains.move_to_element(canvas).perform()
    canvas_width_2 = int(canvas.size['width']/2)
    for i in range(-(canvas_width_2), canvas_width_2, 30):
        try:
            action_chains.move_to_element_with_offset(canvas, i, -10).perform()
            if driver.find_element(*hover_over_second_graph.Graph_Tootip_element).is_displayed():
                break
        except:
            try:
                action_chains.move_to_element_with_offset(canvas, i, 0).perform()
                if driver.find_element(*hover_over_second_graph.Graph_Tootip_element).is_displayed():
                    break
            except:
                action_chains.move_to_element_with_offset(canvas, i, 10).perform()
                if driver.find_element(*hover_over_second_graph.Graph_Tootip_element).is_displayed():
                    break
    graphdataTooltipElement = driver.find_element(*hover_over_second_graph.Graph_Tootip_element)
    graph_data = graphdataTooltipElement.text
    Graph_Dropdown_btn = driver.find_element(*hover_over_second_graph.Dropdown_btn)
    Graph_Dropdown_button = Graph_Dropdown_btn.text
    if graph_data == None:
        graph_data = graphdataTooltipElement.get_attribute("outerText")
    if graph_data == None:
        graph_data = graphdataTooltipElement.get_attribute("innerText")
    if graph_data == None:
        allure.attach(driver.get_screenshot_as_png(), name=f"{test} ==> {Graph_Dropdown_button}", attachment_type=allure.attachment_type.PNG)
        statement = f"There is no data in Graph-View for {test} ==> {Graph_Dropdown_button}"
        updatecomponentstatus(chart_Title, f"{test} ==> {Graph_Dropdown_button}", "FAILED", statement, excelpath)
        e = Exception
        raise e
def get_graph_data_(driver, txt, excelpath,chart_Title):
    Graph_Dropdown_btn = driver.find_element(*get_graph_data.Dropdown_btn)
    Graph_Dropdown_button = Graph_Dropdown_btn.text
    datas = []
    graphdataTooltipElement = driver.find_element(*get_graph_data.graphdataTooltipElement)
    if graphdataTooltipElement.is_displayed():
        with allure.step(f"Graph of '{txt}' ==> {Graph_Dropdown_button}"):
            time.sleep(0.2)
            if graphdataTooltipElement.is_displayed():
                # Extract the graph data from the tooltip element
                graph_data = graphdataTooltipElement.text
                if graph_data == None:
                    graph_data = graphdataTooltipElement.get_attribute("outerText")
                if graph_data == None:
                    graph_data = graphdataTooltipElement.get_attribute("innerText")
                if graph_data == None:
                    e = Exception
                    raise e
                allure.attach(driver.get_screenshot_as_png(), name=f"'{txt}'", attachment_type=allure.attachment_type.PNG)
                rows = graph_data.strip().split('\n')
                data = [row.split('\t') for row in rows[0:]]
                if data.__len__() == 0 or data is None:
                    e = Exception
                    raise e
                elif data.__len__() != 0:
                    datas.append(data)
                    updatecomponentstatus(chart_Title, f"{txt} ==> {Graph_Dropdown_button}", "PASSED",f"There is a data in Graph-View for {txt} ==> {Graph_Dropdown_button}",excelpath)
        if datas.__len__() == 0 or datas is None:
            allure.attach(driver.get_screenshot_as_png(), name=f"{txt} ==> {Graph_Dropdown_button}", attachment_type=allure.attachment_type.PNG)
            statement = f"There is no data in Graph-View for {txt} ==> {Graph_Dropdown_button}"
            updatecomponentstatus(chart_Title, f"{txt} ==> {Graph_Dropdown_button}", "FAILED", statement, excelpath)
            e = Exception
            raise e
    else:
        with allure.step(f"Graph of '{txt}' ==> {Graph_Dropdown_button}"):
            allure.attach(driver.get_screenshot_as_png(), name=f"{txt} ==> {Graph_Dropdown_button}", attachment_type=allure.attachment_type.PNG)
            statement = f"There is no data in Graph-View for {txt} ==> {Graph_Dropdown_button}"
            updatecomponentstatus(chart_Title, f"{txt} ==> {Graph_Dropdown_button}", "FAILED", statement, excelpath)
            e = Exception
            raise e
def get_secondGraph_data_(driver, txt, excelpath,chart_Title):
    Graph_Dropdown_btn = driver.find_element(*get_secondGraph_data.Dropdown_btn)
    Graph_Dropdown_button = Graph_Dropdown_btn.text
    datas = []
    graphdataTooltipElement = driver.find_element(*get_secondGraph_data.graphdataTooltipElement)

    if graphdataTooltipElement.is_displayed():
        with allure.step(f"Graph of '{txt}' ==> {Graph_Dropdown_button}"):
            time.sleep(0.2)
            if graphdataTooltipElement.is_displayed():
                # Extract the graph data from the tooltip element
                graph_data = graphdataTooltipElement.text
                if graph_data == None:
                    graph_data = graphdataTooltipElement.get_attribute("outerText")
                if graph_data == None:
                    graph_data = graphdataTooltipElement.get_attribute("innerText")
                if graph_data == None:
                    e = Exception
                    raise e
                allure.attach(driver.get_screenshot_as_png(), name=f"'{txt}'", attachment_type=allure.attachment_type.PNG)
                rows = graph_data.strip().split('\n')
                data = [row.split('\t') for row in rows[0:]]
                if data.__len__() == 0 or data is None:
                    e = Exception
                    raise e
                elif data.__len__() != 0:

                    datas.append(data)
                    updatecomponentstatus(chart_Title, f"{txt} ==> {Graph_Dropdown_button}", "PASSED",f"There is a data in Graph-View for {txt} ==> {Graph_Dropdown_button}",excelpath)
        if datas.__len__() == 0 or datas is None:
            allure.attach(driver.get_screenshot_as_png(), name=f"{txt} ==> {Graph_Dropdown_button}", attachment_type=allure.attachment_type.PNG)
            statement = f"There is no data in Graph-View for {txt} ==> {Graph_Dropdown_button}"
            updatecomponentstatus(chart_Title, f"{txt} ==> {Graph_Dropdown_button}", "FAILED", statement, excelpath)
            e = Exception
            raise e
    else:
        with allure.step(f"No Graph for '{txt}' ==> {Graph_Dropdown_button}"):
            allure.attach(driver.get_screenshot_as_png(), name=f"{txt} ==> {Graph_Dropdown_button}", attachment_type=allure.attachment_type.PNG)
            statement = f"There is no data in Graph-View for {txt} ==> {Graph_Dropdown_button}"
            updatecomponentstatus(chart_Title, f"{txt} ==> {Graph_Dropdown_button}", "FAILED", statement, excelpath)
            e = Exception
            raise e
def hover_piechart(driver, test, excelpath, chart_Title):
    time.sleep(4)
    piechart = driver.find_element(*hover_over_pie_chart.pie_chart)
    # Create an instance of ActionChains
    action_chains = ActionChains(driver)
    action_chains.move_to_element(piechart).perform()
    canvas_width_2 = int(piechart.size['width']/2)
    for i in range(-(canvas_width_2), canvas_width_2, 30):
        try:
            action_chains.move_to_element_with_offset(piechart, i, -30).perform()
            if driver.find_element(*hover_over_pie_chart.Piechart_Tooltip_element).is_displayed():
                    break
        except:
            try:
                action_chains.move_to_element_with_offset(piechart, i, 0).perform()
                if driver.find_element(*hover_over_pie_chart.Piechart_Tooltip_element).is_displayed():
                    break
            except:
                action_chains.move_to_element_with_offset(piechart, i, 30).perform()
                if driver.find_element(*hover_over_pie_chart.Piechart_Tooltip_element).is_displayed():
                    break
    piechartdataTooltipElement = driver.find_element(*hover_over_pie_chart.Piechart_Tooltip_element)
    graph_data = piechartdataTooltipElement.text
    Graph_Dropdown_btn = driver.find_element(*hover_over_pie_chart.Dropdown_btn)
    Graph_Dropdown_button = Graph_Dropdown_btn.text
    if graph_data == None:
        graph_data = piechartdataTooltipElement.get_attribute("outerText")
    if graph_data == None:
        graph_data = piechartdataTooltipElement.get_attribute("innerText")
    if graph_data == None:
        allure.attach(driver.get_screenshot_as_png(), name=test, attachment_type=allure.attachment_type.PNG)
        statement = f"There is no data in Pie chart for {test}"
        updatecomponentstatus(chart_Title, test, "FAILED", statement, excelpath)
        e = Exception
        raise e
def get_piechart_data_(driver, txt, excelpath,chart_Title):
    Graph_Dropdown_btn = driver.find_element(*get_piechart_data.Dropdown_btn)
    Graph_Dropdown_button = Graph_Dropdown_btn.text
    datas = []
    graphdataTooltipElement = driver.find_element(*get_piechart_data.piechartTooltipElement)
    if graphdataTooltipElement.is_displayed():
        with allure.step(f"Graph of '{txt}'"):
            time.sleep(0.2)
            if graphdataTooltipElement.is_displayed():
                # Extract the graph data from the tooltip element
                graph_data = graphdataTooltipElement.text
                if graph_data == None:
                    graph_data = graphdataTooltipElement.get_attribute("outerText")
                if graph_data == None:
                    graph_data = graphdataTooltipElement.get_attribute("innerText")
                if graph_data == None:
                    e = Exception
                    raise e
                allure.attach(driver.get_screenshot_as_png(), name=f"'{txt}'", attachment_type=allure.attachment_type.PNG)
                rows = graph_data.strip().split('\n')
                data = [row.split('\t') for row in rows[0:]]
                if data.__len__() == 0 or data is None:
                    e = Exception
                    raise e
                elif data.__len__() != 0:
                    datas.append(data)
                    updatecomponentstatus(chart_Title,txt, "PASSED",f"There is a data in Pie chart for {txt}",excelpath)
        if datas.__len__() == 0 or datas is None:
            allure.attach(driver.get_screenshot_as_png(), name=txt, attachment_type=allure.attachment_type.PNG)
            statement = f"There is no data in Pie chart for {txt}"
            updatecomponentstatus(chart_Title, txt, "FAILED", statement, excelpath)
            e = Exception
            raise e
    else:
        with allure.step(f"Graph of '{txt}'"):
            allure.attach(driver.get_screenshot_as_png(), name=txt, attachment_type=allure.attachment_type.PNG)
            statement = f"There is no data in Pie chart for {txt}"
            updatecomponentstatus(chart_Title, txt, "FAILED", statement, excelpath)
            e = Exception
            raise e


