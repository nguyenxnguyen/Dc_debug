from Tkinter import *
import ttk
import tkMessageBox
import ScrolledText
import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import socket
from time import sleep


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


def dc_debug(driver_use, da, list_ip, filter_var, id_list, choose_view, set_ip_enable):
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
        #if ip not in set_ip_enable:
        if ip:
            enable_poll_url = 'http://%s:8581/dcdebug/enabledebug.jsp?nextAction=Poll' % da
            driver.get(enable_poll_url)

            ip_address_field_xpath = '//*[@id="ipAddress"]'
            ip_address_field = waiting_for_xpath(driver, ip_address_field_xpath, '')
            ip_address_field.send_keys(ip)

            if filter_var == 'None':
                pass
            else:
                if filter_var == 'Group':
                    filter_button_xpath = '//*[@id="idFilterBy"]/option[2]'
                elif filter_var == 'Item':
                    filter_button_xpath = '//*[@id="idFilterBy"]/option[3]'

                filter_button_logging = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, filter_button_xpath)))
                filter_button_logging.click()

                filter_field_xpath = '//*[@id="idFilterText"]'
                filter_field = waiting_for_xpath(driver, filter_field_xpath, '')
                filter_field.send_keys(id_list)

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
        view_button_web = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, view_xpath)))
        view_button_web.click()

        response_xpath = '//*[@id="content"]/pre'
        response = waiting_for_xpath(driver, response_xpath, 'innerHTML')

        return response, ip

set_ip_enable_p = set()


def view():
    if load_chrome.get():
        driver_p = 'chrome'
    else:
        driver_p = ''
    msg = ''
    da = da_entry.get().strip()
    ip = ip_entry.get().strip()
    filter_var = var_filter.get()
    if filter_var == 'None':
        id_list = ''
    else:
        id_list = filter_id_entry.get()
    try:
        socket.inet_aton(ip)
    except socket.error:
        ip_entry.delete(0, END)
        msg += 'illegal IP address string\n'

    list_ip = []

    if not da:
        msg += 'Missing Machine information\n'
    if not ip:
        msg += 'Missing or wrong IP information\n'
    if msg:
        tkMessageBox.showwarning('Warning!!!', msg)
    else:
        choose_view = var_radio.get()
        list_ip.append(ip)
        print 'Set of enabled ip: %s' % set_ip_enable_p
        response, ip = dc_debug(driver_p, da, list_ip, filter_var, id_list, choose_view, set_ip_enable_p)
        re_scroll_text.delete(0.0, END)
        re_scroll_text.insert(INSERT, response)
        set_ip_enable_p.add(ip)

root = Tk()
#root.resizable(width=False, height=False)
root.title("DC Debug Tool")

note_book = ttk.Notebook(root)
page1 = ttk.Frame(note_book)
page2 = ttk.Frame(note_book)
note_book.add(page1, text='General')
note_book.add(page2, text='Extensions')
note_book.pack(expand=1, fill="both")
note_book.select(0)

frame1 = Frame(page1)
frame1.grid(column=1, row=1, sticky=W+N)

frame2 = Frame(page1)
frame2.grid(column=2, row=1, sticky=W)

frame11 = Frame(frame1)
frame11.grid(column=1, row=1, sticky=W)

frame12 = Frame(frame1)
frame12.grid(column=1, row=2, sticky=W)

frame13 = Frame(frame1)
frame13.grid(column=1, row=3, sticky=W)

frame14 = Frame(frame1)
frame14.grid(column=1, row=4, sticky=W)

frame21 = Frame(frame2)
frame21.grid(column=1, row=1, sticky=W)

# ------------frame11-----------------
blank_label = Label(frame11, text="", width=5)
blank_label.grid(column=1, row=1, sticky=W)
blank_label = Label(frame11, text="", width=5)
blank_label.grid(column=3, row=1, sticky=W)

label_title = Label(frame11, text="Data Collector Debug", font='Helvetica 10 bold')
label_title.grid(column=2, row=2, sticky=W+N+E+S)

# ------------frame12-----------------
blank_label = Label(frame12, text="", width=5)
blank_label.grid(column=1, row=1, sticky=W)

# load chrome checkbox
load_chrome = IntVar()
load_chrome_checkbox = Checkbutton(frame12, text="Load Chrome", variable=load_chrome)
load_chrome_checkbox.grid(column=2, row=2)

da_label = Label(frame12, text="Machine   :")
da_label.grid(column=2, row=3, sticky=W)
da_entry = Entry(frame12, width=20)
da_entry.grid(column=3, row=3, sticky=W)

ip_label = Label(frame12, text="IP Address:")
ip_label.grid(column=2, row=4, sticky=W)
ip_entry = Entry(frame12, width=20)
ip_entry.grid(column=3, row=4, sticky=W)

var_filter = StringVar()
var_filter.set('None')

filter_label = Label(frame12, text="Filtering:")
filter_label.grid(column=2, row=5, sticky=W)

filter_none_radio = Radiobutton(frame12, text="None", variable=var_filter, value='None')
filter_none_radio.grid(column=3, row=5, sticky=W)

filter_group_radio = Radiobutton(frame12, text="Poll Group IDs", variable=var_filter, value='Group')
filter_group_radio.grid(column=3, row=6, sticky=W)

filter_item_radio = Radiobutton(frame12, text="Item IDs", variable=var_filter, value='Item')
filter_item_radio.grid(column=3, row=7, sticky=W)

filter_id_label = Label(frame12, text="ID List:")
filter_id_label.grid(column=2, row=8, sticky=W)
filter_id_entry = Entry(frame12, width=20)
filter_id_entry.grid(column=3, row=8, sticky=W)

# ------------frame13-----------------
blank_label = Label(frame13, text="", width=5)
blank_label.grid(column=1, row=1, sticky=W)
var_radio = StringVar()
var_radio.set('pc')
radio_button_1 = Radiobutton(frame13, text="Discover Logging by IP",
                             variable=var_radio, value='dl')
radio_button_1.grid(column=2, row=2, sticky=W)
radio_button_2 = Radiobutton(frame13, text="Poll Errors by IP",
                             variable=var_radio, value='pe')
radio_button_2.grid(column=2, row=3, sticky=W)
radio_button_2 = Radiobutton(frame13, text="Polling Configuration by IP",
                             variable=var_radio, value='pc')
radio_button_2.grid(column=2, row=4, sticky=W)
radio_button_2 = Radiobutton(frame13, text="Display Polled Devices",
                             variable=var_radio, value='dpd')
radio_button_2.grid(column=2, row=5, sticky=W)
radio_button_2 = Radiobutton(frame13, text="Display Known SNMP Profiles",
                             variable=var_radio, value='dksp')
radio_button_2.grid(column=2, row=6, sticky=W)

# ------------frame14-----------------
blank_label = Label(frame14, text="", width=5)
blank_label.grid(column=1, row=1, sticky=W)
view_button = Button(frame14, text=" View ", command=view, relief=RAISED)
view_button.grid(column=2, row=2, sticky=W+E+N+S)


# ------------frame21-----------------
blank_label = Label(frame21, text="", width=5)
blank_label.grid(column=1, row=1, sticky=W)
blank_label = Label(frame21, text="", width=5)
blank_label.grid(column=3, row=1, sticky=W)
re_scroll_text = ScrolledText.ScrolledText(frame21, width=120, height=50)
re_scroll_text.grid(column=2, row=2)

root.mainloop()
sys.exit(0)

