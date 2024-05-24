import time
import requests
from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from RPA.Tables import Tables
from RPA.Robocorp.WorkItems import WorkItems

browser = Selenium()
tables = Tables()
workitems = WorkItems()
is_available=True

headers = ["Description of product","Price of product","Product File Name","Free Shipping","Contain Money"]

@task
def ali_express_automate():
    opening_ali_express_site()
    ali_express_data = datascraping_result()
    save_to_csv(ali_express_data)

def opening_ali_express_site():
    browser.open_available_browser("https://best.aliexpress.com/", maximized=True, alias="FirstBrowser")
    time.sleep(5)

def datascraping_result():
    data = browser.find_elements("xpath://div[contains(@class,'water-fall--ele--17TIGw2')]")
    ali_express_data = []

    for element in data:
        browser.capture_element_screenshot(element)
        description=get_result_description(element)
        price = get_result_price(element)
        image_url=get_image_url(element)
        free_shipping=get_result_free_shipping(element)
        contain_money=check_contain_money(description)
        ali_express_list = [description,price,image_url,free_shipping,contain_money]
        ali_express_data.append(ali_express_list)
    return ali_express_data

def get_result_description(result):
    try:
        description_element=result.find_element("xpath", ".//div[@title]")
        return description_element.text
    except:
        return ""

def get_result_price(result):
    try:
        price_element = result.find_element("xpath", ".//span[@class='rc-modules--price--1NNLjth']/span[2]")
        return price_element.text
    except:
        return ""

def get_result_free_shipping(result):
    try:
        free_shipping_element=result.find_element("xpath",".//span[@class='rc-modules--text--3kpyr_j']")
        return True if free_shipping_element.text else False
    except:
        return ""

def check_contain_money(text):
    try:
        money_keywords = ["$", "USD", "PKR", "€", "EUR", "£", "GBP", "¥", "JPY", "₹", "INR"]
        for keyword in money_keywords:
            if keyword in text:
                return True
        return False
    except:
        return ""

def get_image_url(result):
    try:
        image_element=result.find_element("xpath", ".//img[@class='rc-modules--image--juUYhtJ']")
        return image_element.get_attribute("src")
    except:
        return ""
    

def download_image(url, filename):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Image downloaded: {filename}")
        else:
            print(f"Failed to download image: {url}")
    except:
        return ""


def save_to_csv(ali_express_data):
    try:
        image_url_index = headers.index("Product File Name")
        for item in ali_express_data:
            image_url = item[image_url_index]
            if image_url:
                filename = f"{image_url.split('/')[-1]}"
                download_image(image_url, filename)
                item[image_url_index] = filename 
        ali_express_table = tables.create_table(ali_express_data, columns=headers)
        output_path = "output/ali_express_automateData.csv"
        tables.write_table_to_csv(ali_express_table, output_path)
        print(f"Data saved to {output_path}")
    except:
        return ""



