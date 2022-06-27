import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import time

class Parser:

    def __init__(self, url):
        ua = UserAgent()
        self.session = requests.Session()
        self.session.headers = {'User-Agent': ua.random}
        self.url = url

    def get_html(self):
        response = self.session.get(url=self.url)
        print('Status code:', response.status_code)
        if response.status_code == 200:
            with open('wild.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            return response
        else:
            return 'Ошибка в выполнении запроса'

    def get_soup(self):
        response = self.get_html()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def parse(self):
        soup = self.get_soup()
        # product = soup.find('h1', class_=True).text                      # OZON
        product = soup.find('h1', class_=True).text                        # WILDBERRIES
        # price = soup.find('span', class_='nm4 nm5').find('span').text    # OZON
        price = soup.find('span', class_='price-block__final-price').text  # WILDBERRIES
        return {'product': product, 'price': price}

    def write_to_db(self):
        pass

URL_OZON = 'https://www.ozon.ru/product/kapsulnaya-kofemashina-krups-piccolo-xs-krasnyy-178842724/?sh=yr-vOjksrA'
# URL_WILDBERRIES = 'https://www.wildberries.ru/catalog/18256273/detail.aspx?targetUrl=MI'
# parser = Parser(URL_WILDBERRIES)
# print(parser.parse())

# --------------------------------------
driver = webdriver.Chrome('../MISC/TESTS/driver/chromedriver.exe')
driver.maximize_window()
driver.get(url=URL_OZON)
time.sleep(5)
find_more_element = driver.find_element(by=By.XPATH, value='//*[@id="section-description"]')
actions = ActionChains(driver)
actions.move_to_element(find_more_element).perform()
time.sleep(3)
with open("ozon.html", "w", encoding='utf-8') as file:
    file.write(driver.page_source)