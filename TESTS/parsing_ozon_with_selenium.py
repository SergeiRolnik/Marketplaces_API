from selenium import webdriver
from selenium.webdriver.common.by import By

URL = 'https://www.ozon.ru/product/kapsulnaya-kofemashina-krups-piccolo-xs-krasnyy-178843825/?sh=yr-vOjksrA'
CHROME_WEBDRIVER_LOCATION = 'driver/chromedriver.exe'
driver = webdriver.Chrome(CHROME_WEBDRIVER_LOCATION)
driver.get(URL)

# иммитируем скроллинг до конца страницы
driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")

product = driver.find_element(By.TAG_NAME, 'h1').text
print(product)

price = driver.find_element(By.CSS_SELECTOR, 'div[data-widget="webPrice"]').text
print(price)

# это кусок кода не работает из-за того, что невозможно иммитировать скроллинг до раздела Описание
# description = driver.find_element(By.CSS_SELECTOR, 'div[data-widget="webDescription"]').text
# print(description)

driver.close()