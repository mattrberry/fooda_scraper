from flask import Flask

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import os

import json

fooda_base_url = 'https://app.fooda.com'
fooda_email = os.environ['fooda_email']
fooda_password = os.environ['fooda_password']

app = Flask(__name__)

driver = webdriver.Remote(command_executor='http://chrome:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
driver.implicitly_wait(3)
driver.get('https://mattrb.com')


@app.route('/')
def hello_world():
    return 'Flask Dockerized'


@app.route('/fooda')
def get_menus():
    driver.get(fooda_base_url)
    login = driver.find_element_by_css_selector('a[href="/login"]')
    login.click()
    email_box = driver.find_element_by_id('user_email')
    email_box.send_keys(fooda_email)
    password_box = driver.find_element_by_id('user_password')
    password_box.send_keys(fooda_password)
    submit = driver.find_element_by_css_selector('input[value="Log In"]')
    submit.click()

    locations_to_check = []

    dropdown_wrapper = driver.find_elements_by_class_name('secondary-bar__event-dropdown')

    if len(dropdown_wrapper) == 0:
        locations_to_check.append(driver.current_url)
    elif len(dropdown_wrapper) == 1:
        links = dropdown_wrapper[0].find_elements_by_class_name('js-selection-target')
        for link in links:
            locations_to_check.append(link.get_attribute('href'))
    else:
        return 'ERROR: TOO MANY DROPDOWN WRAPPERS WITH CLASS "secondary-bar__event-dropdown'

    location_info = check_locations(locations_to_check)

    driver.delete_all_cookies()

    return json.dumps(location_info)


def check_locations(locations):
    location_info = []

    for location in locations:
        driver.get(location)
        restaurant = driver.find_element_by_class_name('myfooda-event__restaurant')
        image_url = restaurant.find_element_by_class_name('myfooda-event__photo').get_attribute('src')
        name = restaurant.find_element_by_class_name('myfooda-event__name').get_attribute('innerHTML')
        address = restaurant.find_element_by_class_name('myfooda-vendor-location-name').get_attribute('innerHTML')
        cuisines = [c.get_attribute('innerHTML') for c in restaurant.find_elements_by_class_name('myfooda-event__cuisine')]
        location_info.append({
            'image_url': image_url,
            'name': name,
            'address': address,
            'cuisines': cuisines
        })

    return location_info


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
