import logging
import os

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from utils.OSUtils import OSUtils


class SeleniumUtil:

    @staticmethod
    def get_chrome_keys():
        result = list(filter(lambda k: not k[0].startswith('__'), Keys.__dict__.copy().items()))
        #logging.info(f'Supported keys: {str(result)}')
        return result

    @staticmethod
    def get_webdriver4_chrome_with_performance_tracing():
        wdpath = os.path.realpath('webdriver') + '/' + OSUtils.get_sytem() + '/chromedriver'
        down_path = os.path.realpath('download')

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        prefs = {"profile.default_content_settings.popups": 0,
                 "download.default_directory": down_path,
                 "directory_upgrade": True}

        options.add_experimental_option("prefs", prefs)

        caps = DesiredCapabilities.CHROME.copy()
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        driver: WebDriver = webdriver.Chrome(executable_path=wdpath, chrome_options=options, desired_capabilities=caps)
        return driver

    @staticmethod
    def is_web_driver(chrome) -> bool:
        return isinstance(chrome, WebDriver)

    @staticmethod
    def get_webdriver4_chrome() -> WebDriver:
        wdpath = os.path.realpath('webdriver') + '/' + OSUtils.get_sytem() + '/chromedriver'
        down_path = os.path.realpath('download')

        logging.info(f'Loading webdriver from: ${wdpath}, Download folder: ${down_path}')

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        prefs = {"profile.default_content_settings.popups": 0,
                 "download.default_directory": down_path,
                 "directory_upgrade": True}

        options.add_experimental_option("prefs", prefs)

        return webdriver.Chrome(executable_path=wdpath, options=options)

    """ UI 5 specific"""

    @staticmethod
    def ui5_change_checkbox(chrome, checkboxid, trueOrFalse):
        # sap.ui.getCore().byId('idCommentTable-sa').setSelected(false)
        # SeleniumUtil.call_js(chrome, 'sap.ui.getCore().byId("' + checkboxid + '").setSelected(' + trueOrFalse + '); ')

        SeleniumUtil.call_js(chrome, 'sap.ui.getCore().byId("' + checkboxid + '").setSelected(' + trueOrFalse + '); ')

    @staticmethod
    def ui5_select_checkbox(chrome, checkboxid):
        SeleniumUtil.call_js(chrome, 'sap.ui.getCore().byId("' + checkboxid + '").fireSelect();')

    @staticmethod
    def ui5_click_button(chrome, buttonId):
        # sap.ui.getCore().byId('__button11').firePress()
        SeleniumUtil.call_js(chrome, 'sap.ui.getCore().byId("' + buttonId + '").firePress();')

    @staticmethod
    def remove_footer(chrome):
        SeleniumUtil.call_js(chrome,
                            "var fts = document.getElementsByTagName('footer'); if(!!fts && fts.length > 0) fts[0].remove();")

    """ Common """

    @staticmethod
    def call_js(chrome, js):
        logging.info('call_js :' + js)
        chrome.execute_script(js)

    @staticmethod
    def get_id(ele):
        return ele.get_attribute('id')

    @staticmethod
    def wait_for_seconds(chrome, seconds):
        logging.info('wait_for_seconds start:' + str(seconds))
        chrome.implicitly_wait(seconds)
        logging.info('wait_for_seconds end:' + str(seconds))

    @staticmethod
    def move_to_ele_then_click(chrome, ele):
        ActionChains(chrome).move_to_element(ele).click(ele).perform()

    @staticmethod
    def move_to_ele(chrome, ele):
        ActionChains(chrome).move_to_element(ele).perform()

    @staticmethod
    def find_elements_by_css(chrome, cssSelector=".sapMTableTBody .sapMListTblNavCol .sapMLIBImgNav",
                             ):
        logging.info('findElements- by cssSelector:' + cssSelector)
        return chrome.find_elements(By.CSS_SELECTOR, cssSelector)

    @staticmethod
    def find_element_by_css(chrome, cssSelector):
        logging.info('findElement- by cssSelector:' + cssSelector)
        return chrome.find_element(By.CSS_SELECTOR, cssSelector)

    @staticmethod
    def select_value_by_id(chrome, id, val):
        Select(chrome.find_element(By.ID, id)).select_by_value(val)
        return chrome

    @staticmethod
    def find_element_by_link(chrome, lt):
        logging.info('find_element_by_link:' + lt)
        return chrome.find_element(By.LINK_TEXT, lt)

    @staticmethod
    def find_element_by_id(chrome, id):
        logging.info('find_element_by_id:' + id)
        return chrome.find_element(By.ID, id)

    @staticmethod
    def find_elements_by_x_path(chrome, xpath):
        logging.info('find_elements_by_x_path:' + xpath)
        return chrome.find_elements(By.XPATH,xpath)

    @staticmethod
    def find_element_by_x_path(chrome, xpath):
        logging.info('find_element_by_x_path:' + xpath)
        return chrome.find_element(By.XPATH, xpath)

    @staticmethod
    def find_sub_element_by_x_path(ele, xpath):
        logging.info('find_sub_element_by_x_path:' + xpath + ', parent:' + SeleniumUtil.get_id(ele))
        return ele.find_element(By.XPATH, xpath)

    @staticmethod
    def get_data(url, chrome, colcount=11, cssSelector=".sapMTableTBody .sapMListTblCell .sapMText",
                 xpath="//tr/td/span",
                 timeoutInSeconds=200):

        if (chrome is None):
            logging.info("start getting page from url: " + url)
            chrome = SeleniumUtil.get_page(url, xpath, timeoutInSeconds)

        rows = []
        if (chrome is not None):
            logging.info("find_elements_by_css_selector: " + cssSelector)
            foundElements = chrome.find_elements(By.CSS_SELECTOR, cssSelector)
            logging.info('find_elements_by_css_selector, found total: ' + str(foundElements.__len__()))

            logging.info('getting values from UI')
            rows = SeleniumUtil.get_data_from_ele(foundElements, colcount, SeleniumUtil.text_lambda())
            logging.info('getting values from UI, found total: ' + str(rows.__len__()))

        return rows, chrome

    @staticmethod
    def text_lambda():
        return lambda input: str(input.text)

    @staticmethod
    def get_data_arr_from_ele(foundElements, fun):
        data = []
        for idx, ele in enumerate(foundElements):
            data.append(fun(ele))

        logging.info("get_data_arr_from_ele element count:" + str(foundElements.__len__())
                     + ", data:" + str(data))

        return data

    @staticmethod
    def get_inner_html_by(chrome, xpath):
        chrome = SeleniumUtil.wait_for_element_xpath_visible(chrome, xpath)
        if chrome is not None:
            ele = SeleniumUtil.find_element_by_x_path(chrome, xpath)
            return ele.text
        else:
            logging.error('unable to find element via xpath:' + xpath)
            return None

    @staticmethod
    def get_data_from_ele(foundElements, colcount, fun):
        rows = []
        col = []
        for idx, span in enumerate(foundElements):
            col.append(fun(span))
            if ((idx + 1) % colcount == 0):
                rows.append(list(col))
                col.clear()

        logging.info("get_data_from_ele element count:" + str(foundElements.__len__())
                     + ", colcount:" + str(colcount)
                     + ", found row: " + str(rows.__len__())
                     + ", rows:" + str(rows))

        return rows

    @staticmethod
    def move_to_crm_target_frame(crmurl):

        chrome = SeleniumUtil.get_page_from_url(crmurl)

        chrome = SeleniumUtil.wait_for_element_id_visible(chrome, 'CRMApplicationFrame')
        chrome.switch_to.frame('CRMApplicationFrame')

        if (chrome is None):
            return

        SeleniumUtil.wait_for_element_id_visible(chrome, 'WorkAreaFrame1')
        chrome.switch_to.frame('WorkAreaFrame1')

        return chrome

    @staticmethod
    def move_to_crm_target_header(crmurl):

        chrome = SeleniumUtil.get_page_from_url(crmurl)

        chrome = SeleniumUtil.wait_for_element_id_visible(chrome, 'CRMApplicationFrame')
        chrome.switch_to.frame('CRMApplicationFrame')

        if (chrome is None):
            return

        SeleniumUtil.wait_for_element_id_visible(chrome, 'HeaderFrame')
        chrome.switch_to.frame('HeaderFrame')

        return chrome

    @staticmethod
    def move_back2_parent_frame(chrome):
        chrome.switch_to.parent_frame()
        return chrome

    @staticmethod
    def move2_frame(chrome, frame):
        chrome = SeleniumUtil.wait_for_element_id_visible(chrome, frame)
        chrome.switch_to.frame(frame)
        return chrome

    @staticmethod
    def get_page_from_url(crmurl):
        chrome = SeleniumUtil.get_webdriver4_chrome()
        chrome.get(crmurl)

        return chrome

    @staticmethod
    def move_to_target_frame(chrome, frames):
        try:
            for idx, frm in enumerate(frames):
                chrome = SeleniumUtil.wait_for_element_id_visible(chrome, frm)
                chrome.switch_to.frame(frm)
                logging.info("move_to_target_frame: " + frm + "@" + str(idx))
                SeleniumUtil.wait_for_seconds(chrome, 1)

            return chrome
        except:
            chrome.quit()
            logging.error("move_to_target_frame - fail to move_to_target_frame:" + str(frames))
            return None

    @staticmethod
    def get_email_page(url):
        chrome = SeleniumUtil.get_webdriver4_chrome()
        logging.info("page start get_email_page ...")
        chrome.get(url)
        return SeleniumUtil.wait_then_return(chrome, "//table/tbody/tr/td/button", 200)

    @staticmethod
    def get_page(url, xpath, timeoutInSeconds):
        chrome = SeleniumUtil.get_webdriver4_chrome()
        # chrome.fullscreen_window()
        chrome.maximize_window()
        logging.info("page start rendering...")
        chrome.get(url)
        return SeleniumUtil.wait_then_return(chrome, xpath, timeoutInSeconds)

    @staticmethod
    def full_screen(chrome):
        chrome.maximize_window()
        logging.info('full_screen - maximize_window')

    @staticmethod
    def screenshot(chrome, picname):
        SeleniumUtil.full_screenshot(chrome, os.path.realpath('screenshot') + '/' + picname)

    @staticmethod
    def screenshot_with_crop_by_xpath(chrome, xpath, picname):
        SeleniumUtil.screenshot_by_x_path(chrome, xpath, os.path.realpath('screenshot') + '/' + picname,
                                          os.path.realpath('screenshot') + '/fullscreen_tmp.png')

    @staticmethod
    def full_screenshot(chrome, filepath):
        chrome.save_screenshot(filepath)
        logging.info('Capture full screenshot to: ' + filepath)

    @staticmethod
    def screenshot_by_x_path(chrome, xpath, filepath, tmppic_path):

        SeleniumUtil.wait_for_element_xpath_visible(chrome, xpath)
        element = chrome.find_element(By.XPATH, xpath)
        location = element.location
        size = element.size

        chrome.save_screenshot(tmppic_path)

        # crop image
        x = location['x']
        y = location['y']
        width = location['x'] + size['width']
        height = location['y'] + size['height']

        SeleniumUtil.image_crop(filepath, x, y, width, height)

    @staticmethod
    def screenshot_with_crop(chrome, left, top, right, bottom, filepath, tmppic_path, show=False, format=None):
        chrome.save_screenshot(tmppic_path)
        SeleniumUtil.image_crop(tmppic_path,filepath, left, top, right, bottom, show, format)

    @staticmethod
    def image_crop(filepath,targetpath, x, y, x2, y2, show=False, format=None):
        im = Image.open(filepath)
        im = im.crop((x, y, x2, y2))
        logging.info('image_crop file:' + filepath + ' [left:' + str(x) + ', top:' + str(y) + ', right:' + str(
            x2) + ', lower:' + str(y2) + ']')
        if show:
            im.show()

        im.save(targetpath, format=format, quality=95, subsampling=0)

    @staticmethod
    def wait_then_return(chrome, xpath, timeoutInSeconds):
        logging.info("waiting page rendering.")
        try:
            element = WebDriverWait(chrome, timeoutInSeconds).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            logging.info("page rendered as excepted.")
            return chrome
        except:
            chrome.quit()
            logging.error("wait_then_return - fail to loading page, xpath:" + xpath)
            return None

    @staticmethod
    def wait_for_element_id_visible(chrome, eleId, to=60):
        logging.info("start waiting wait_for_element_id_visible:" + eleId)
        try:
            WebDriverWait(chrome, to).until(EC.visibility_of_element_located((By.ID, eleId)))
            logging.info("done waiting wait_for_element_id_visible:" + eleId)
            return chrome
        except:
            logging.error(f"wait_for_element_id_visible - fail to wait within {to} seconds, associated with eleId:" + eleId)
            return None

    @staticmethod
    def wait_for_element_id_presence(chrome, eleId, to=60):
        logging.info("start waiting wait_for_element_id_presence:" + eleId)
        try:
            WebDriverWait(chrome, to).until(EC.presence_of_element_located((By.ID, eleId)))
            logging.info("done waiting wait_for_element_id_presence:" + eleId)
            return chrome
        except:
            logging.error(
                f"wait_for_element_id_presence - fail to wait within {to} seconds, associated with eleId:" + eleId)
            return None

    @staticmethod
    def wait_for_element_css_visible(chrome, cssSelector, to=60):
        logging.info("start waiting wait_for_element_css_visible:" + cssSelector)
        try:
            WebDriverWait(chrome, to).until(EC.visibility_of_element_located((By.CSS_SELECTOR, cssSelector)))
            logging.info("done waiting wait_for_element_css_visible:" + cssSelector)
            return chrome
        except:
            logging.error(
                f"wait_for_element_css_visible - fail to wait within {to} seconds, associated with css:" + cssSelector)
            return None

    @staticmethod
    def wait_for_element_css_presence(chrome, cssSelector, to=60):
        logging.info("start waiting wait_for_element_css_presence:" + cssSelector)
        try:
            WebDriverWait(chrome, to).until(EC.presence_of_element_located((By.CSS_SELECTOR, cssSelector)))
            logging.info("done waiting wait_for_element_css_presence:" + cssSelector)
            return chrome
        except:
            logging.error(
                f"wait_for_element_css_presence - fail to wait within {to} seconds, associated with css:" + cssSelector)
            return None

    @staticmethod
    def wait_for_element_xpath_visible(chrome, xpath, to=60):
        logging.info("start waiting wait_for_element_xpath_visible:" + xpath)
        try:
            WebDriverWait(chrome, to).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            logging.info("done waiting wait_for_element_xpath_visible:" + xpath)
            return chrome
        except:
            logging.error("wait_for_element_xpath_visible - fail to wait associated with xpath:" + xpath)
            return None

    @staticmethod
    def wait_for_element_xpath_presence(chrome, xpath, to=60):
        logging.info("start waiting wait_for_element_xpath_presence:" + xpath)
        try:
            WebDriverWait(chrome, to).until(EC.presence_of_element_located((By.XPATH, xpath)))
            logging.info("done waiting wait_for_element_xpath_presence:" + xpath)
            return chrome
        except:
            logging.error("wait_for_element_xpath_presence - fail to wait associated with xpath:" + xpath)
            return None

    @staticmethod
    def wait_for_element_xpath_presence_then_move2(chrome, xpath, to=60):
        logging.info("start waiting wait_for_element_xpath_presence_then_move2:" + xpath)
        try:
            WebDriverWait(chrome, to).until(EC.presence_of_element_located((By.XPATH, xpath)))
            logging.info("done waiting wait_for_element_xpath_presence:" + xpath)
            SeleniumUtil.move_to_ele(chrome, SeleniumUtil.find_element_by_x_path(chrome, xpath))
            return chrome
        except:
            logging.error("wait_for_element_xpath_presence - fail to wait associated with xpath:" + xpath)
            return None

    @staticmethod
    def wait_for_element_link_visible(chrome, link, to=60):
        logging.info("start waiting wait_for_element_link_visible:" + link)
        try:
            WebDriverWait(chrome, to).until(EC.visibility_of_element_located((By.LINK_TEXT, link)))
            logging.info("done waiting wait_for_element_link_visible:" + link)
            return chrome
        except:
            logging.error("wait_for_element_link_visible - fail to wait associated with link:" + link)
            return None

    @staticmethod
    def wait_for_element_link_presence(chrome, link, to=60):
        logging.info("start waiting wait_for_element_link_presence:" + link)
        try:
            WebDriverWait(chrome, to).until(EC.presence_of_element_located((By.LINK_TEXT, link)))
            logging.info("done waiting wait_for_element_link_presence:" + link)
            return chrome
        except:
            logging.error("wait_for_element_link_presence - fail to wait associated with link:" + link)
            return None

    @staticmethod
    def wait_ele_visiable_then_click_by_xpath(chrome, xpath, fn=None):
        chrome = SeleniumUtil.wait_for_element_xpath_visible(chrome, xpath)
        ele = SeleniumUtil.find_element_by_x_path(chrome, xpath)
        if fn is None:
            ele.click()
        elif fn(ele):
            logging.info(f'fn return true, click on: {xpath}')
            ele.click()
        else:
            logging.info(f'fn return false, skip click on: {xpath}')
        return chrome
