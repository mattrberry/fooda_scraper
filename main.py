from flask import Flask

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import os

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
    driver.get('https://app.fooda.com')
    login = driver.find_element_by_css_selector('a[href="/login"]')
    login.click()
    email_box = driver.find_element_by_id('user_email')
    email_box.send_keys(fooda_email)
    password_box = driver.find_element_by_id('user_password')
    password_box.send_keys(fooda_password)
    submit = driver.find_element_by_css_selector('input[value="Log In"]')
    submit.click()
    
    return 'hello'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
