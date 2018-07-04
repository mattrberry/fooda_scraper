import json
import os
from string import Template
from threading import Thread
from typing import List, Dict

import requests
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

fooda_base_url = 'https://app.fooda.com'
fooda_email = os.environ['fooda_email']
fooda_password = os.environ['fooda_password']

slack_fooda_template = Template("""*${name}*
${address} ~ _${cuisines}_""")


app = Flask(__name__)

driver = webdriver.Remote(command_executor='http://chrome:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
driver.implicitly_wait(3)


@app.route('/')
def scrape_fooda(dump_to_string: bool = True):
    login_fooda()
    location_urls = get_location_urls()
    location_info = check_locations(location_urls)

    driver.delete_all_cookies()

    return json.dumps(location_info) if dump_to_string else location_info


@app.route('/slack', methods=['POST'])
def get_slack_formatted_message():
    response_url = request.form['response_url']

    thread = Thread(target=handle_slack_callback, args=(response_url,))
    thread.start()

    return json.dumps({
        'text': 'generating response.........'
    })


def handle_slack_callback(response_url):
    requests.post(response_url, json={
        'text': '\n'.join([slack_fooda_template.substitute(popup) for popup in scrape_fooda(False)]),
        'username': 'markdownbot',
        'mrkdwn': True
    })


def login_fooda() -> None:
    driver.get(fooda_base_url)
    login = driver.find_element_by_css_selector('a[href="/login"]')
    login.click()
    email_box = driver.find_element_by_id('user_email')
    email_box.send_keys(fooda_email)
    password_box = driver.find_element_by_id('user_password')
    password_box.send_keys(fooda_password)
    submit = driver.find_element_by_css_selector('input[value="Log In"]')
    submit.click()


def get_location_urls() -> List[str]:
    dropdown_wrapper = driver.find_elements_by_class_name('secondary-bar__event-dropdown')
    if len(dropdown_wrapper) == 0:
        return [driver.current_url]
    elif len(dropdown_wrapper) == 1:
        return [link.get_attribute('href') for link in dropdown_wrapper[0].find_elements_by_class_name('js-selection-target')]
    else:
        return []


def check_locations(locations: List[str]) -> List[Dict]:
    location_info = []

    for location in locations:
        driver.get(location)
        restaurant = driver.find_element_by_class_name('myfooda-event__restaurant')
        image_url = restaurant.find_element_by_class_name('myfooda-event__photo').get_attribute('src')
        name = restaurant.find_element_by_class_name('myfooda-event__name').get_attribute('innerHTML')
        address = restaurant.find_element_by_class_name('myfooda-vendor-location-name').get_attribute('innerHTML')
        cuisines = ', '.join([c.get_attribute('innerHTML') for c in restaurant.find_elements_by_class_name('myfooda-event__cuisine')])
        location_info.append({
            'image_url': image_url,
            'name': name,
            'address': address,
            'cuisines': cuisines
        })

    return location_info


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
