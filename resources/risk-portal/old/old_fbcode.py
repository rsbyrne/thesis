import os
import shutil
import time
import random
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common import exceptions

MAXWAIT = 60.
TIMEOUT = 60

def format_href(href):
    if '%3A' in href:
        return href[-18:].replace('%3A', '').replace('+', '-')
    elif '%20' in href:
        return href[-17:].replace('%20', '-')
    else:
        return href[-15:].replace('+', '-')
# def check_href(href):
#     if '%3A' in href:
#         return href[-21:-18] == 'ds=' and format_href(href).replace('-', '').isnumeric()
#     else:
#         return href[-18:-15] == 'ds=' and format_href(href).replace('-', '').isnumeric()

def random_sleep(factor = 1.):
    sleepTime = (random.random() + 1.) * factor
    time.sleep(sleepTime)
    return sleepTime

def wait_check(
        condition,
        message = None,
        repeatAction = None,
        repeatException = True,
        waitInterval = 1.,
        maxWait = None
        ):
    waited = 0.
    while not condition():
        if not message is None:
            print(message)
        waitTime = random_sleep(waitInterval)
        waited += waitTime
        if not maxWait is None:
            if waited > maxWait:
                raise Exception("Wait time exceeded!")
        if not repeatAction is None:
            if repeatException:
                repeatAction()
            else:
                try:
                    repeatAction()
                except:
                    pass

def _file_check(fp):
    if os.path.isfile(fp):
        return os.stat(fp).st_size
    return False

def download(
        driver,
        link,
        downloadDir,
        outDir,
        outExt,
        maxWait = MAXWAIT
        ):
    global TIMEOUT
    driver.set_page_load_timeout(3)
    newFilename = format_href(link) + outExt
    outcome = False
    if newFilename in os.listdir(outDir):
        pass
#         print("File already exists - skipping.")
    else:
        random_sleep(0.3)
        try:
            driver.get(link)
        except exceptions.TimeoutException:
            wait_check(lambda: len(os.listdir(downloadDir)), maxWait = maxWait)
            checkFilenames = [
                fp for fp in os.listdir(downloadDir) \
                    if fp.endswith(outExt)
                ]
            assert len(checkFilenames) == 1
            oldFilename = checkFilenames[0]
            oldFilepath = os.path.join(downloadDir, oldFilename)
            wait_check(lambda: _file_check(oldFilepath), maxWait = maxWait)
            newFilepath = os.path.join(outDir, newFilename)
            random_sleep(0.2)
            shutil.copyfile(oldFilepath, newFilepath)
            random_sleep(0.2)
            wait_check(lambda: _file_check(newFilepath), maxWait = maxWait)
            for filename in os.listdir(downloadDir):
                filepath = os.path.join(downloadDir, filename)
                os.remove(filepath)
                wait_check(
                    lambda: not os.path.isfile(filepath),
                    maxWait = maxWait
                    )
            print("Downloaded:", newFilename)
            outcome = True
        except:
            print(f"Something went wrong downloading {link}; skipping.")
    driver.set_page_load_timeout(TIMEOUT)
    return outcome

class Driver:
    def __init__(self, options, profile, logDir = '.'):
        self.options, self.profile, self.logDir = options, profile, logDir
    def __enter__(self):
        global TIMEOUT
        self.driver = webdriver.Firefox(
            options = self.options,
            firefox_profile = self.profile
            )
        self.driver.set_page_load_timeout(TIMEOUT)
        return self.driver
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_value:
            print("An error has occurred. Saving screenshot to target directory and exiting.")
            try:
                errorFilePath = os.path.join(self.logDir, str(int(time.time())) + '.png')
                self.driver.save_screenshot(errorFilePath)
            except:
                print("Another error occurred: could not save screenshot.")
        self.driver.quit()
        if os.path.isfile('geckodriver.log'):
            os.remove('geckodriver.log')
        if exc_type is not None:
            return False
        else:
            return True

class TempDir:
    def __init__(self, path, maxWait = None):
        self.path = path
        self.maxWait = maxWait
    def __enter__(self):
        os.makedirs(self.path, exist_ok = False)
        wait_check(lambda: os.path.isdir(self.path), maxWait = self.maxWait)
    def __exit__(self, exc_type, exc_value, exc_traceback):
        shutil.rmtree(self.path, ignore_errors = True)
        wait_check(lambda: not os.path.isdir(self.path), maxWait = self.maxWait)
        if exc_type is not None:
            return False
        else:
            return True

def pull_datas(
        dataURL,
        loginName,
        loginPass,
        outDir,
        dataMime,
        outExt,
        maxWait = MAXWAIT
        ):

    parsed = urlparse(dataURL)
    loginURL = '://'.join(parsed[:2])
#     loginURL = 'https://en-gb.facebook.com/'

    outDir = os.path.abspath(outDir)
    if not os.path.isdir(outDir):
        os.makedirs(outDir, exist_ok = True)

    downloadDir = os.path.join(outDir, '_temp')

    with TempDir(downloadDir, maxWait = maxWait):

        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", downloadDir)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", dataMime)
        options = Options()
        options.add_argument("--headless")

        with Driver(options, profile, outDir) as driver:

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

            print("Navigating to data page...")
            try:
                driver.get(dataURL)
            except exceptions.WebDriverException:
                raise ValueError("Bad data URL!")
            print("Navigated to data page.")

            random_sleep(0.5)

            print("Finding data...")
#             links = [
#                 elem.get_attribute("href")
#                     for elem in driver.find_elements_by_xpath("//a[@href]")
#                         if check_href(elem.get_attribute("href"))
#                 ]
            alllinks = [
                elem.get_attribute("href")
                    for elem in driver.find_elements_by_xpath("//a[@href]")
                ]
            links = [link for link in alllinks if 'downloads/vector' in link]
            if not len(links):
                raise Exception("No data found at destination!")
            print("Downloading all...")
            ndown = 0
            for link in links[::-1]:
                outcome = download(
                    driver,
                    link,
                    downloadDir,
                    outDir,
                    outExt,
                    maxWait,
                    )
                if outcome:
                    ndown += 1
                    if ndown == 12:
                        break
            print("Done.")

#             submit.click()
#             if normalLogin:
#                 try:
#                     loginForm = driver.find_element_by_id("login_form")
#                     raise ValueError("Bad login credentials!")
#                 except exceptions.NoSuchElementException:
#                     pass
#             else:
#                 e = "Sorry, something went wrong."
#                 if driver.find_element_by_id("facebook").text.startswith(e):
#                     raise ValueError("Bad login credentials!")
