import time
from selenium import webdriver

website = 'https://apl.unob.cz/rozvrh/api/read/rozvrh?id=7'

driver = webdriver.Firefox()
driver.get(website)
