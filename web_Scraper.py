#######DISCLAIMER!!!!#######
#This code is not mine(from 98%), i reverse-engineered it and retrofitted it to my needs, all credits go to our lecturer/teacher

#now trying scraping MOJEAP website to get all groups in the FVT faculty

#So Far we have:
# webscraper that logs into the website
# is capable of scraping all pages of the study programs
# Find out "ids" of the other faculties(FVL is 633)
# other sources?
# Extract all study groups from FVT faculty study programs
# Extract all study groups from other faculties
# Include website that defines University groups
# cross refference the groups with rest of the sources and create externalIds accordingly(if missing)
# First TODO Finished (06.06. 2024)
# Revision 08/06/2024: # - for systemdata.json add "externalids", "externalidtypes" and "exterlanidcategories"
# - Switch for sources(0 - study plan, 1 - MojeAP, 2 - dymado)
# - make single systemdata.json output
# - add switch so dymado doesnt get error when trying to access key "ID" which is none("UIC")
# - load systemdata again and check for non uuid mastergroups, if yes, sift through dymado and replace with ID


#TODO 2
# dymado is manualy created(but only one source) is it neccessary to "automate"?


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

from data_Cruncher import merge_function, save_as_json

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
        time.sleep(3)
        return driver

    def scrapepage(self, url):
        "ziska driver (pokud poprve, provede inicializaci), prihlasi se do aplikace (jestli neni jeste prihlasen), otevre page a vrati jeji obsah"

        # appid = self.guessAppId(url)
        webdriver = self.loginApp()
        # webdriver = self.openWeb()

        webdriver.get(url)
        time.sleep(1)
        # mozna budete muset zmenit podminku, pokud zdroj vyuziva intenzivne javascript (kresli stranku na klientovi)
        #  WebDriverWait(webdriver, self.timeout).until(
        #      expected_conditions.presence_of_element_located((By.ID, "FakultaCard"))
        # )
        WebDriverWait(webdriver, self.timeout).until(
            expected_conditions.presence_of_element_located((By.ID, "StudiumSkupinaProgram"))
        )
        result = webdriver.page_source
        return result


    def openUrl(self, url):
        """vytvari index stranek, aby se minimalizovala komunikace se serverem,
        stranky se ukladaji do adresare,
        pokud zdroj nema permalinky, ma tento pristup stinne stranky = stejna url maji jiny obsah
        index je ulozen jako json, keys jsou urls, values jsou uuids = nazvy souboru, kde jsou stranky ulozeny
        """
        # print(self.pageindex.get(url, None))
        if "/MojeAP/" in url:
            self.cachedir = "pagecache/MojeAP/"
            Path(self.cachedir).mkdir(exist_ok=True)
        else:
            self.cachedir = "pagecache/"

        pageid = self.pageindex.get(url, None)

        result = ""
        if pageid:
            filename = self.cachedir + pageid + ".html"
            # print(filename)

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

        return result

username = ""
password = ""

# load creds in order to login
with open("res/credentials.json","r",encoding="utf-8") as creds:
    c = json.load(creds)
    username = c["user"]
    password = c["login"]

# create instance of ScraperBase
scBase = ScraperBase(username, password)


# faculties contains all study programs of VLF FVL and FVT faculties in format{faculty: [study programs], etc...}
faculties = json.load(open("res/faculties.json", "r", encoding="utf-8"))
skupiny = {'MojeAP': {"FVL": [],"FVT": [], "VLF": []}}
with open ("pages/pageindex.json", "r", encoding="utf-8") as f:
    pages = json.load(f)
    #TODO
    # - is it neccessary to split into separate dicts(still haven't used it)?, but looks nice
    # idea - maybe when defining master groups, instead of faculty(plain) we use corresponding faculties?
    tempDict = {"FVL": {}, "FVT": {}, "VLF": {}}
    for fakulta in faculties:
        # print(fakulta)
        for program in faculties[fakulta]:
            url = f"https://apl.unob.cz/MojeAP/Program/{program}"
            test = scBase.openUrl(url)
            # retrieve div class "studiumSkupina"
            mDrive = scBase.getDriver()
            if pages.get(url, None) is not None:
                mDrive.get(f"file:///{Path.cwd()}/{scBase.cachedir}{pages.get(url, None)}.html")
                # get element of groups, iterate and save id and name(for references)
                # save list as separate json
                study_groups = mDrive.find_elements(By.ID, "StudiumSkupina")
                for group in study_groups:
                    group_ID = group.find_element(By.TAG_NAME, "a").get_attribute('href').split("Uic/")[1]
                    group_Name = group.text
                    # print(f"ID: {group_ID} - Name: {group_Name}")
                    tempDict[fakulta][group_ID] = group_Name
            else:
                pass

            # mDrive.get(f"pagecache/{pages.get(url, None)}")

for fakulta in faculties:
    for group in tempDict[fakulta]:
        skupiny['MojeAP'][fakulta].append(dict({"id": group, "name": tempDict[fakulta][group]}))

save_as_json("res/MojeAP_groups_rev1.0", skupiny)