import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
# Import ait for sending credentials to pop up authentication and then to normal auth
import ait
# Import Keys and ActionChains for normal auth
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


def popup_logon(_creds):
    time.sleep(1)
    ait.write(_creds["user"] + "\t")
    time.sleep(0.5)
    ait.write(_creds["login"] + "\n")


def log_me(_creds, _actions):
    _actions.send_keys(_creds["user"], Keys.TAB, _creds["login"], Keys.ENTER)
    _actions.perform()


website = 'https://apl.unob.cz/rozvrh/api/read/rozvrh?id=7'

driver = webdriver.Firefox()
driver.get(website)

# wait for browser to load popup
time.sleep(2.5)

actions = ActionChains(driver)

with open("res/credentials.json", 'r') as file:
    creds = json.loads(file.read())
    # logs in the popup login screen
    popup_logon(creds)
    # wait for site to load
    time.sleep(3)
    # logs in on normal login site
    log_me(creds, actions)

# wait for site to fully load
time.sleep(10)
matches = driver.find_element(By.TAG_NAME, "pre").text
# parse the plaintext to json
# TODO check the delay in case the json parse happens sooner than data fetch
data = json.loads(matches)

# TODO Save json

# print(data)

driver.quit()
