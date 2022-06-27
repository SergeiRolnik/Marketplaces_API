from selenium import webdriver
from selenium.webdriver.common.by import By

URL = 'https://www.wildberries.ru/catalog/18256273/detail.aspx?targetUrl=MI'
CHROME_WEBDRIVER_LOCATION = 'driver/chromedriver.exe'
driver = webdriver.Chrome(CHROME_WEBDRIVER_LOCATION)
driver.get(URL)
driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")

product = driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div[2]/h1/span[2]').text
print('Товар:', product)

price = driver.find_element(By.XPATH, '//*[@id="infoBlockProductCard"]/div[2]/div/div/p/span').text
print('Цена:', price)

description = driver.find_element(By.XPATH, '//*[@id="container"]/div[3]/div[1]/section[3]/div[2]/div[1]/p').text
print('Описание:', description)

driver.close()