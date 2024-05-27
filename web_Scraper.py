#######DISCLAIMER!!!!#######
#This code is not mine(from 98%), i reverse-engineered it and retrofitted it to my needs, all credits go to our lecturer/teacher

#now trying scraping MOJEAP website to get all groups in the FVT faculty

#So Far we have:
# webscraper that logs into the website
# is capable of scraping all pages of the study programs

#TODO
# Find out "ids" of the other faculties(FVL is 633)
# other sources?
# Extract all study groups from FVT faculty study programs
# Extract all study groups from other faculties
# Include website that defines University groups
# cross refference the groups with rest of the sources and create externalIds accordingly(if missing)


from functools import cache, lru_cache
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from pathlib import Path
from uuid import uuid4
import json

ids = ["369"]#, "633"] #after i start working with other faculties
mojeapid = "ctl00_ctl40_g_ba0590ba_842f_4a3a_b2ea_0c665ea80655_ctl00_LvApplicationGroupList_ctrl1_ctl00_LvApplicationsList_ctrl4_btnApp"

class ScraperBase:
    def __init__(self,
             username,
             password,
             cacheFileName="pages/pageindex.json",
             cachedir="pagecache/",
             app_id=mojeapid,
             writer=None
             ):
        # zajisti, ze adresar bude existovat
        Path(cachedir).mkdir(exist_ok=True)

        self.username = username
        self.password = password
        self.cacheFileName = cacheFileName
        self.cachedir = cachedir
        self.app_id = app_id
        self.timeout = 1000
        self.writer = writer

        with open(cacheFileName, "r", encoding="utf-8") as f:
            self.pageindex = json.load(f)
        pass

    def writeCache(self):
        "zapise data do json, prepise soubor kompletne"
        with open(self.cacheFileName, "w", encoding="utf-8") as f:
            json.dump(self.pageindex, f, indent=4)

    @cache
    def getDriver(self):
        "inicializuje driver"
        options = FirefoxOptions()
        options.set_preference('devtools.jsonview.enabled', False)
        driver = webdriver.Firefox(options=options)

        return driver

    @cache
    def login(self):
        "inicializuje driver, prihlasi uzivatele a driver vrati"
        #
        # username, password
        #



        driver = self.getDriver()
        driver.get("https://intranet.unob.cz/aplikace/SitePages/DomovskaStranka.aspx")

        elem = WebDriverWait(driver, 100).until(
            expected_conditions.presence_of_element_located((By.ID, "userNameInput"))
        )

        elem = driver.find_element(By.ID, "userNameInput")
        # elem.clear()
        elem.send_keys(self.username)
        elem.send_keys(Keys.TAB)

        elem = driver.find_element(By.ID, "passwordInput")
        # elem.clear()
        elem.send_keys(self.password)
        elem.send_keys(Keys.RETURN)
        time.sleep(1)

        return driver

    @cache
    def loginApp(self, app_id = 0):
        driver = self.login()
        driver.get("https://intranet.unob.cz/aplikace/SitePages/DomovskaStranka.aspx")
        app_id = "ctl00_ctl40_g_ba0590ba_842f_4a3a_b2ea_0c665ea80655_ctl00_LvApplicationGroupList_ctrl1_ctl00_LvApplicationsList_ctrl3_btnApp"

        # toto ID si najdete a prizpusobte kod
        elem = WebDriverWait(driver, self.timeout).until(
            expected_conditions.presence_of_element_located((By.ID, app_id))
        )
        elem.click()
        time.sleep(1)
        return driver

    def scrapepage(self, url):
        "ziska driver (pokud poprve, provede inicializaci), prihlasi se do aplikace (jestli neni jeste prihlasen), otevre page a vrati jeji obsah"

        # appid = self.guessAppId(url)
        webdriver = self.loginApp()
        # webdriver = self.openWeb()
        print("login successful?")

        webdriver.get(url)
        # mozna budete muset zmenit podminku, pokud zdroj vyuziva intenzivne javascript (kresli stranku na klientovi)
        # WebDriverWait(webdriver, self.timeout).until(
        #     expected_conditions.presence_of_element_located((By.ID, "FakultaCard"))
        # )
        result = webdriver.page_source
        return result

    def openUrl(self, url):
        """vytvari index stranek, aby se minimalizovala komunikace se serverem,
        stranky se ukladaji do adresare,
        pokud zdroj nema permalinky, ma tento pristup stinne stranky = stejna url maji jiny obsah
        index je ulozen jako json, keys jsou urls, values jsou uuids = nazvy souboru, kde jsou stranky ulozeny
        """
        pageid = self.pageindex.get(url, None)
        result = ""
        if pageid:
            filename = self.cachedir + pageid + ".html"
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
                result = "\n".join(lines)
        else:
            pageid = f"{uuid4()}"
            filename = self.cachedir + pageid + ".html"
            self.pageindex[url] = pageid
            result = self.scrapepage(url)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result)
            self.writeCache()

        print("reading successful?")
        return result

username = ""
password = ""

with open("res/credentials.json","r",encoding="utf-8") as creds:
    c = json.load(creds)
    username = c["user"]
    password = c["login"]

scBase = ScraperBase(username, password)


# programs is a list of all study programs in the FVT faculty

programs = ["4", "18", "19", "2949", "2950", "2951", "2968", "2969", "2970", "2979", "2980", "2981", "2998",
            "3884", "3899", "3900"]
for program in programs:
    url = f"https://apl.unob.cz/MojeAP/Program/{program}"
    scBase.openUrl(url)


