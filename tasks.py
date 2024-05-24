import time
import os
import requests
from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from RPA.Tables import Tables
from RPA.Robocorp.WorkItems import WorkItems

class AliExpressScraper:
    def __init__(self):
        self.browser = Selenium()
        self.tables = Tables()
        self.workitems = WorkItems()
        self.headers = ["Description of product", "Price of product", "Product File Name", "Free Shipping", "Contain Money"]
        self.output_folder = "images"
        self.output_csv = "output/ali_express_automateData.csv"

    def ali_express_automate(self):
        self.opening_ali_express_site()
        ali_express_data = self.datascraping_result()
        self.save_to_csv(ali_express_data)

    def opening_ali_express_site(self):
        self.browser.open_available_browser("https://best.aliexpress.com/", maximized=True, alias="FirstBrowser")
        time.sleep(5)

    def datascraping_result(self):
        data = self.browser.find_elements("xpath://div[contains(@class,'water-fall--ele--17TIGw2')]")
        ali_express_data = []

        for element in data:
            self.browser.capture_element_screenshot(element)
            description = self.get_result_description(element)
            price = self.get_result_price(element)
            image_url = self.get_image_url(element)
            free_shipping = self.get_result_free_shipping(element)
            contain_money = self.check_contain_money(description)
            ali_express_list = [description, price, image_url, free_shipping, contain_money]
            ali_express_data.append(ali_express_list)
        return ali_express_data

    def get_result_description(self, result):
        try:
            description_element = result.find_element("xpath", ".//div[@title]")
            return description_element.text
        except:
            return ""

    def get_result_price(self, result):
        try:
            price_element = result.find_element("xpath", ".//span[@class='rc-modules--price--1NNLjth']/span[2]")
            return price_element.text
        except:
            return ""

    def get_result_free_shipping(self, result):
        try:
            free_shipping_element = result.find_element("xpath", ".//span[@class='rc-modules--text--3kpyr_j']")
            return True if free_shipping_element.text else False
        except:
            return ""

    def check_contain_money(self, text):
        try:
            money_keywords = ["$", "USD", "PKR", "€", "EUR", "£", "GBP", "¥", "JPY", "₹", "INR"]
            for keyword in money_keywords:
                if keyword in text:
                    return True
            return False
        except:
            return ""

    def get_image_url(self, result):
        try:
            image_element = result.find_element("xpath", ".//img[@class='rc-modules--image--juUYhtJ']")
            return image_element.get_attribute("src")
        except:
            return ""

    def download_image(self, url, folder, filename):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                os.makedirs(folder, exist_ok=True)
                file_path = os.path.join(folder, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Image downloaded: {file_path}")
                return file_path
            else:
                print(f"Failed to download image: {url}")
                return ""
        except Exception as e:
            print(f"Error downloading image {url}: {e}")
            return ""

    def save_to_csv(self, ali_express_data):
        try:
            image_url_index = self.headers.index("Product File Name")
            for item in ali_express_data:
                image_url = item[image_url_index]
                if image_url:
                    filename = f"{image_url.split('/')[-1]}"
                    file_path = self.download_image(image_url, self.output_folder, filename)
                    item[image_url_index] = file_path if file_path else image_url
            ali_express_table = self.tables.create_table(ali_express_data, columns=self.headers)
            self.tables.write_table_to_csv(ali_express_table, self.output_csv)
            print(f"Data saved to {self.output_csv}")
        except Exception as e:
            print(f"Error saving data to CSV: {e}")

@task
def ali_express_automate_task():
    scraper = AliExpressScraper()
    scraper.ali_express_automate()
