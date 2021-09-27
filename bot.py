import os
import time
import io
import re
import requests
from urllib.parse import urljoin, urlparse
import traceback

from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

from selenium.webdriver.common.keys import Keys



CATEGORIES = {
    "Weight Room" : 1, 
    "Badminton": 2, 
    "Basketball" : 3 ,
    "Swimming Deep End": 4, 
    "Swimming Shallow End": 5
}

URL = "https://shop.westernmustangs.ca/"


def get_date_from_slot_div(div):
    return div.find_elements_by_class_name("pull-left")[0].get_attribute('innerHTML').strip()

def get_time_from_slot_div(div):
    full_str = div.find_element_by_tag_name('small').get_attribute('innerHTML')
    only_time = full_str[:full_str.index("<")].strip()

    # print (only_time.strip())
    return only_time


def get_filtered_time_slots(driver, user_dates, user_time_slots):
    # users selected time slots	
    user_dates = [ "Thursday, September 16, 2021"]
    user_time_slots = [ set(["12:30 PM - 1:15 PM"])]


    # find next available slot from preferences
    all_slots_divs = driver.find_elements_by_class_name("program-schedule-card-caption")
    #TODO invert equality7
    all_slots_available =  [div for div in all_slots_divs if div.find_elements_by_class_name("pull-right")[0].find_element_by_tag_name('small').get_attribute('innerHTML').strip() != "No Spots Available"]


    final_slots = []
    for div in all_slots_available:
        for date_index in range(len(user_dates)):
            slot_date = get_date_from_slot_div(div)
            # print(slot_date)
            if slot_date in user_dates[date_index]:
                slot_time = get_time_from_slot_div(div)
                # print(slot_time)
                if slot_time in user_time_slots[date_index]: #Getting time slot for that date
                    final_slots.append(div)
 
    print([(get_date_from_slot_div(div), get_time_from_slot_div(div)) for div in final_slots])
    return final_slots


def register_time_slot_before_log_in(driver, div, logged_in=False):

    # try:
    #     already_registered_html_optional = div.find_element_by_class_name('btn-default').get_attribute('innerHTML')
    # except:
    #     already_registered_html_optional = None
    #     print("Already logged in 'Details' element not found")


    try:
        register_button = div.find_element_by_tag_name('a')
    except:
        register_button = None
        print("Did not register a slot")

    if register_button is not None: 
        register_button.click()
        print("Clicked on register button before logging in!")
        time.sleep(5)

    return driver



def register_time_slot_after_log_in(driver, div, logged_in=True):

    try:
        already_registered_html_optional = div.find_element_by_class_name('btn-default').get_attribute('innerHTML')
    except:
        already_registered_html_optional = None
        print("Already logged in 'Details' element not found")

    if logged_in and  already_registered_html_optional == "Details":
        print("Already registered")
        return driver
    

    try:
        register_button = div.find_elements_by_class_name('btn-primary')[0]
    except:
        register_button = None
        print("Did not register a slot")

    if register_button is not None: 
        register_button.click()
        print("Registered!")
        time.sleep(5)

    return driver

def check_all_boxes(driver):
    #find all inputs
    all_checkboxes = driver.find_elements_by_id('rbtnYes')
    for checkbox in all_checkboxes:
        checkbox.click()
    
    time.sleep(2)

    form = driver.find_elements_by_tag_name('textarea')
    form.send_keys("124 511 5555")
    
    time.sleep(2)

    driver.execute_script("window.scrollBy(0,750)") 

    all_buttons = driver.find_elements_by_class_name('btn-primary')

    add_to_cart_button = [button for button in all_buttons if button.get_attribute('innerHTML') == 'Add to Cart'][0]

    time.sleep(1)
    add_to_cart_button.click()


    return driver


def login(driver): 
    #Login
    login_button = driver.find_elements_by_class_name("loginOption")
    login_button[0].click()

    #Enter Username and Password
    user_id_field = driver.find_elements_by_id("userId")
    user_id_field[0].send_keys("MSINGHAL")
    
    password_field = driver.find_elements_by_id("password")
    password_field[0].send_keys("Billionaire@337")


    login_form_button = driver.find_elements_by_class_name("adt-primaryAction")
    time.sleep(5)
    login_form_button[0].click()

    time.sleep(15)

    return driver




def main():

    driver =  webdriver.Chrome('chromedriver', chrome_options=chrome_options)

    driver.get(URL)


    login_button = None
    western_student_login_button = None

    reservation_link = driver.find_elements_by_class_name('Menu-Item')[0].get_attribute('href')
    driver.get(reservation_link)
    # swimming link
    weight_room_link = driver.find_elements_by_class_name('list-group-item')[4].click()

    time_slots = get_filtered_time_slots(driver, None, None) 

    #Select the div according to some algorithm
    selected_div = time_slots[0]
    # print(get_date_from_slot_div(selected_div), get_time_from_slot_div(selected_div))
    
    slot_data_id = selected_div.get_attribute("data-instance-id")
    print("Data Instance ID: ", slot_data_id)

    driver = register_time_slot_before_log_in(driver, selected_div, logged_in = False)
    logged_in_driver = login(driver)

    selected_div_refreshed = logged_in_driver.find_elements_by_xpath(f"//div[@data-instance-id='{slot_data_id}']")[0]
    
    # print(get_date_from_slot_div(selected_div_refreshed[0]), get_time_from_slot_div(selected_div_refreshed[0]))
    
    registration_check_driver = register_time_slot_after_log_in(logged_in_driver, selected_div_refreshed, logged_in = True)
    time.sleep(5)
    
    check_all_boxes(registration_check_driver)


if __name__ == "__main__":
    main()
# book




