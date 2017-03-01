import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import socket
from time import time
from selenium.webdriver.remote.webelement import WebElement


def waiting_for_xpath(driver, xpath, attribute):
    timeout = 30
    try:
        element_present = EC.presence_of_element_located((By.XPATH, xpath))
        ele = WebDriverWait(driver, timeout).until(element_present)
        if not attribute:
            return ele
        if isinstance(ele, WebElement):
            ele_text = ele.get_attribute(attribute)
            return ele_text
    except TimeoutException:
        print "Timed out waiting for page to load"
        return 'Timeout'


def dc_debug(driver_use, da, list_ip, choose_view, set_ip_enable):
    if not driver_use:
        #driver_use = 'chrome'
        driver_use = 'phantom'

    if driver_use == 'chrome':
        chrome_driver = os.path.dirname(os.path.abspath(__file__)) + '/chromedriver.exe'
        os.environ["webdriver.chrome.driver"] = chrome_driver
        driver = webdriver.Chrome(chrome_driver)
    elif driver_use == 'phantom':
        phantom_driver = os.path.dirname(os.path.abspath(__file__)) + '/phantomjs.exe'
        driver = webdriver.PhantomJS(executable_path=phantom_driver)

    for ip in list_ip:
        if not ip:
            continue
        if ip not in set_ip_enable:
            enable_poll_url = 'http://%s:8581/dcdebug/enabledebug.jsp?nextAction=Poll' % da
            driver.get(enable_poll_url)

            ip_address_field_xpath = '//*[@id="ipAddress"]'
            ip_address_field = waiting_for_xpath(driver, ip_address_field_xpath, '')
            ip_address_field.send_keys(ip)

            enable_poll_logging_xpath = '//*[@id="dcDebugFormEnableLogging"]/div/div[2]/label'
            enable_poll_logging = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, enable_poll_logging_xpath)))
            enable_poll_logging.click()
        else:
            print 'IP was enabled!'

        dc_debug_url = 'http://%s:8581/dcdebug/searchdebug.jsp' % da
        driver.get(dc_debug_url)

        ip_dc_field_xpath = '//*[@id="searchText"]'
        ip_dc_field = waiting_for_xpath(driver, ip_dc_field_xpath, '')
        ip_dc_field.send_keys(ip)
        domanin_field_xpath = '//*[@id="ipDomainText"]/option'
        domanin_field = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, domanin_field_xpath)))
        domanin_field.click()
        # select = Select(driver.find_element_by_xpath('//*[@id="ipDomainText"]'))
        # select.select_by_visible_text('Default Domain')
        # select.select_by_value('Default Domain')
        #driver.implicitly_wait(3)
        choose_view_xpath = {'dl': '//*[@id="dcDebugForm"]/div/div[2]/label',
                              'pe': '//*[@id="dcDebugForm"]/div/div[3]/label',
                              'pc': '//*[@id="dcDebugForm"]/div/div[5]/label',
                              'dpd': '//*[@id="dcDebugForm"]/div/div[6]/label',
                              'dksp': '//*[@id="dcDebugForm"]/div/div[7]/label'
                             }
        ratio_button_xpath = choose_view_xpath[choose_view]
        ratio_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, ratio_button_xpath)))
        ratio_button.click()

        view_xpath = '//*[@id="dcDebugForm"]/div/center/button'
        view_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, view_xpath)))
        view_button.click()

        response_xpath = '//*[@id="content"]/pre'
        response = waiting_for_xpath(driver, response_xpath, 'innerHTML')

        return response, ip
