import os
import shutil
import time
import random
import zipfile
import glob
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from PIL import Image as PILImage

from riskengine import aliases

TIMEOUT = 10.

def list_elements(element):
#     return element.find_elements_by_xpath('//*[@id]')
    return element.find_elements_by_css_selector("*")

def get_element_pos(element, centre = False):
    x, y, width, height = element.rect.values()
    if centre:
        return int(x + width / 2), int(y + height / 2)
    return x, y

def click(driver):
    action = webdriver.common.action_chains.ActionChains(driver)
    action.click()
    action.perform()
    random_sleep(1.)

def go_click(driver, refelement, coords):
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element(refelement)
    action.move_by_offset(*coords)
    action.click()
    action.perform()
    random_sleep(1.)

def go_hover(driver, refelement, coords):
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element(refelement)
    action.move_by_offset(*coords)
    action.perform()
    random_sleep(1.)


def go_enter(driver, target, coords, strn):
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element(target)
    action.move_by_offset(*coords)
    action.click()
    action.send_keys(strn)
    action.send_keys(Keys.RETURN)
    action.perform()
    random_sleep(1.)

def screen(target, name = 'screen'):
    filename = f"{name}.png"
    if hasattr(target, 'save_screenshot'):
        target.save_screenshot(filename)
    else:
        target.screenshot(filename)
    return PILImage.open(filename)

def get_element_contains(element, text):
    return element.find_element_by_xpath(
        f'''//*[contains(text(),'{text}')]'''
        )

def login(driver, loginURL, loginName, loginPass):
    print("Navigating to login page...")
    try:
        driver.get(loginURL)
    except exceptions.WebDriverException:
        raise ValueError("No login page found!")
    print("Navigated to login page.")

    print("Logging in...")

    random_sleep(0.5)
    username = driver.find_element_by_id("email")
    password = driver.find_element_by_id("pass")
    username.send_keys(loginName)
    random_sleep(0.2)
    password.send_keys(loginPass)
    random_sleep(0.2)
    try:
        submit = driver.find_element_by_id("loginbutton")
        submit.click()
    except exceptions.NoSuchElementException:
        try:
            submit = driver.find_element_by_name('login')
            submit.click()
        except exceptions.NoSuchElementException:
            password.send_keys(u'\ue007')

    random_sleep(0.5)
    try:
        _ = driver.find_element_by_id("loginbutton")
        raise Exception("Login failed!")
    except exceptions.NoSuchElementException:
        try:
            _ = driver.find_element_by_id("login_form")
            raise Exception("Login failed!")
        except exceptions.NoSuchElementException:
            pass
    print("Logged in.")

def go_to_datapage(driver, dataURL, searchstr):
    driver.get(dataURL)
    random_sleep(0.5)
    target = driver.find_element_by_id("js_1")
    target.click()
    random_sleep(0.5)
    target.send_keys(searchstr)
    random_sleep(0.5)
    return target

def random_sleep(factor = 1.):
    sleepTime = (random.random() + 1.) * factor
    time.sleep(sleepTime)
    return sleepTime

class TimeoutException(Exception):
    ...

def wait_check(
        condition,
        message = None,
        repeatAction = None,
        repeatException = True,
        waitInterval = 1.,
        maxWait = None
        ):
    print(f"Waiting (max = {maxWait})...")
    waited = 0.
    while not condition():
        if not message is None:
            print(message)
        waitTime = random_sleep(waitInterval)
        waited += waitTime
        if not maxWait is None:
            if waited > maxWait:
                raise TimeoutException("Wait time exceeded!")
        if not repeatAction is None:
            if repeatException:
                repeatAction()
            else:
                try:
                    repeatAction()
                except:
                    pass
    print("Waiting over.")


# from PIL import Image as PILImage
# im = PILImage.open('screen.png')
# im.crop((
#     210, 200, # mins
#     310, 250, # maxs
#     ))

class Driver:
    def __init__(self, options, profile, logDir = '.'):
        self.options, self.profile, self.logDir = options, profile, logDir
    def __enter__(self):
#         global TIMEOUT
        driver = self.driver = webdriver.Firefox(
            options=self.options,
            firefox_profile=self.profile
            )
#         driver.set_page_load_timeout(TIMEOUT)
        driver.fullscreen_window()
        return driver
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_value:
            print(
                "An error has occurred."
                " Saving screenshot to target directory and exiting."
                )
            try:
                errorFilePath = os.path.join(
                    self.logDir,
                    str(int(time.time())) + '.png'
                    )
                self.driver.save_screenshot(errorFilePath)
            except:
                print("Another error occurred: could not save screenshot.")
#         driver = self.driver
#         driver_process = psutil.Process(driver.service.process.pid)
#         if driver_process.is_running():
#             firefox_process = driver_process.children()
#             if firefox_process:
#                 firefox_process = firefox_process[0]
#                 if firefox_process.is_running():
#                     driver.quit()
#                 else:
#                     firefox_process.kill()
#         if os.path.isfile('geckodriver.log'):
#             os.remove('geckodriver.log')

class TempDir:
    def __init__(self, path, maxWait = None):
        self.path = path
        self.maxWait = maxWait
    def __enter__(self):
        try:
            os.makedirs(self.path, exist_ok = False)
        except FileExistsError:
            shutil.rmtree(self.path)
            os.makedirs(self.path, exist_ok = False)
        wait_check(lambda: os.path.isdir(self.path), maxWait = self.maxWait)
    def __exit__(self, exc_type, exc_value, exc_traceback):
        shutil.rmtree(self.path, ignore_errors = True)
        wait_check(lambda: not os.path.isdir(self.path), maxWait = self.maxWait)
#         if exc_type is not None:
#             return False
#         else:
#             return True

FBSEARCHSTRS = {
    '786740296523925': ('Melbourne coronavirus disease prevention', 'Movement between tiles'),
    '1391268455227059': ('Victoria State coronavirus disease prevention', 'Movement between tiles'),
    '1527157520300850': ('Sydney coronavirus disease prevention', 'Movement between tiles'),
    '2622370339962564': ('New South Wales coronavirus disease prevention', 'Movement between tiles'),
    }

def pull_data(
        fbid,
        loginName,
        loginPass,
        maxWait = 30,
        ):

    print(f"Downloading for {fbid}...")

    loginURL = 'https://www.facebook.com'
    dataURL = (
        'https://partners.facebook.com/'
        'data_for_good/data/?partner_id=467378274536608'
        )
    dataMime = 'application/zip' #'text/csv'
    searchstr, dataset = FBSEARCHSTRS[fbid]

    outDir = os.path.join(aliases.datadir, 'fb', fbid)
    os.makedirs(outDir, exist_ok = True)

    downloadDir = os.path.join(outDir, '_temp')

    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", downloadDir)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", dataMime)
    profile.set_preference("dom.disable_beforeunload", True)
    profile.set_preference("browser.tabs.warnOnClose", False)
    options = Options()
    options.add_argument("--headless")

    with TempDir(downloadDir, maxWait = maxWait):

        with Driver(options, profile, outDir) as driver:

            login(driver, loginURL, loginName, loginPass)
            driver.get(dataURL)

            print("Finding data link...")
            target = get_element_contains(driver, 'Find datasets by name')
            go_enter(driver, target, (0, 10), searchstr)
            print("Selecting map type...")
            target = get_element_contains(driver, 'Dataset type')
            go_enter(driver, target, (10, 30), dataset)
            print("Hitting download...")
            target = get_element_contains(driver, 'Download')
            target.click()
            print("Hitting download files...")
            target = get_element_contains(driver, 'Download files')
            target.click()

            print("Checking to see if files were downloaded...")
            getzips = lambda: glob.glob(os.path.join(downloadDir, '*.zip'))
            wait_check(getzips, maxWait = maxWait)

        print("Files downloaded; unpacking...")
        zipfilenames = getzips()
        csvfilenames = tuple(map(
            os.path.basename, glob.glob(os.path.join(outDir, '*.csv'))
            ))

        for zipfilename in zipfilenames:

            def open_zipfile():
                return zipfile.ZipFile(os.path.join(downloadDir, zipfilename), 'r')

            def wait_condition():
                try:
                    with open_zipfile() as _:
                        ...
                    return True
                except:
                    return False

            wait_check(wait_condition, maxWait = maxWait)

            with open_zipfile() as zfile:
                for zname in zfile.namelist():
                    if zname in csvfilenames:
                        os.remove(os.path.join(outDir, zname))
                    zfile.extract(zname, outDir)
                    print(f"Downloaded new for {fbid}: {zname}")

    print(f"Downloaded all for {fbid}.")


def pull_datas(fbids, *args, **kwargs):
    for fbid in fbids:
        try:
            pull_data(fbid, *args, **kwargs)
        except Exception as exc:
            print(f"Exception in {fbid}: {exc}")
