import logging
import os

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from utils.OSUtils import OSUtils


class SeleniumUtil:

    @staticmethod
    def get_chrome_keys():
        result = list(filter(lambda k: not k[0].startswith('__'), Keys.__dict__.copy().items()))
        return result

    @staticmethod
    def is_web_driver(chrome) -> bool:
        return isinstance(chrome, WebDriver)

    @staticmethod
    def get_webdriver4_chrome(download_folder=None) -> WebDriver:
        wdpath: str = os.path.realpath('webdriver') + os.sep + OSUtils.get_system() + os.sep + 'chromedriver' + (
            '.exe' if OSUtils.get_system() == 'win32' else '')
        
        down_path = os.path.join(os.path.realpath('download'), download_folder) \
            if download_folder is not None else os.path.realpath('download')

        OSUtils.create_folder_if_not_existed(down_path)

        logging.info(f'Loading webdriver from: {wdpath}, Download folder: {down_path}')

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        prefs = {"profile.default_content_settings.popups": 0,
                 "download.default_directory": down_path,
                 "directory_upgrade": True}

        options.add_experimental_option("prefs", prefs)

        service = Service(executable_path=wdpath)

        return webdriver.Chrome(options=options, service=service)

    """ UI 5 specific"""

    @staticmethod
    def ui5_change_checkbox(chrome, checkboxid, trueOrFalse):
        SeleniumUtil.call_js(chrome, 'sap.ui.getCore().byId("' + checkboxid + '").setSelected(' + trueOrFalse + '); ')

    @staticmethod
    def ui5_select_checkbox(chrome, checkboxid):
        SeleniumUtil.call_js(chrome, 'sap.ui.getCore().byId("' + checkboxid + '").fireSelect();')

    @staticmethod
    def ui5_click_button(chrome, buttonId):
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
        logging.debug('wait_for_seconds start:' + str(seconds))
        chrome.implicitly_wait(seconds)
        logging.debug('wait_for_seconds end:' + str(seconds))

    @staticmethod
    def move_to_ele_then_click(chrome, ele):
        ActionChains(chrome).move_to_element(ele).click(ele).perform()

    @staticmethod
    def move_to_ele(chrome, ele):
        ActionChains(chrome).move_to_element(ele).perform()

    @staticmethod
    def find_elements_by_css(chrome, cssSelector=".sapMTableTBody .sapMListTblNavCol .sapMLIBImgNav"):
        logging.debug('findElements- by cssSelector:' + cssSelector)
        return chrome.find_elements(By.CSS_SELECTOR, cssSelector)

    @staticmethod
    def find_element_by_css(chrome, cssSelector):
        logging.debug('findElement- by cssSelector:' + cssSelector)
        return chrome.find_element(By.CSS_SELECTOR, cssSelector)

    @staticmethod
    def select_value_by_id(chrome, id, val):
        Select(chrome.find_element(By.ID, id)).select_by_value(val)
        return chrome

    @staticmethod
    def find_element_by_link(chrome, lt):
        logging.debug('find_element_by_link:' + lt)
        return chrome.find_element(By.LINK_TEXT, lt)

    @staticmethod
    def find_element_by_id(chrome, id):
        logging.debug('find_element_by_id:' + id)
        return chrome.find_element(By.ID, id)

    @staticmethod
    def find_elements_by_x_path(chrome, xpath):
        logging.debug('find_elements_by_x_path:' + xpath)
        return chrome.find_elements(By.XPATH, xpath)

    @staticmethod
    def find_element_by_x_path(chrome, xpath):
        logging.debug('find_element_by_x_path:' + xpath)
        return chrome.find_element(By.XPATH, xpath)

    @staticmethod
    def find_sub_element_by_x_path(ele, xpath):
        logging.debug('find_sub_element_by_x_path:' + xpath + ', parent:' + SeleniumUtil.get_id(ele))
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
            logging.debug("find_elements_by_css_selector: " + cssSelector)
            foundElements = chrome.find_elements(By.CSS_SELECTOR, cssSelector)
            logging.debug('find_elements_by_css_selector, found total: ' + str(foundElements.__len__()))

            logging.debug('getting values from UI')
            rows = SeleniumUtil.get_data_from_ele(foundElements, colcount, SeleniumUtil.text_lambda())
            logging.debug('getting values from UI, found total: ' + str(rows.__len__()))

        return rows, chrome

    @staticmethod
    def text_lambda():
        return lambda input: str(input.text)

    @staticmethod
    def get_data_arr_from_ele(foundElements, fun):
        data = []
        for idx, ele in enumerate(foundElements):
            data.append(fun(ele))

        logging.debug("get_data_arr_from_ele element count:" + str(foundElements.__len__())
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

        logging.debug("get_data_from_ele element count:" + str(foundElements.__len__())
                      + ", colcount:" + str(colcount)
                      + ", found row: " + str(rows.__len__())
                      + ", rows:" + str(rows))

        return rows

    @staticmethod
    def get_property_or_attribute(ele, key):
        try:
            return ele.get_property(key)
        except:
            return ele.get_attribute(key)

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
    def get_page_from_url(crmurl, download_folder=None):
        chrome = SeleniumUtil.get_webdriver4_chrome(download_folder)
        chrome.get(crmurl)

        return chrome

    @staticmethod
    def move_to_target_frame(chrome, frames):
        try:
            for idx, frm in enumerate(frames):
                chrome = SeleniumUtil.wait_for_element_id_visible(chrome, frm)
                chrome.switch_to.frame(frm)
                logging.debug("move_to_target_frame: " + frm + "@" + str(idx))
                SeleniumUtil.wait_for_seconds(chrome, 1)

            return chrome
        except:
            chrome.quit()
            logging.error("move_to_target_frame - fail to move_to_target_frame:" + str(frames))
            return None

    @staticmethod
    def get_email_page(url):
        chrome = SeleniumUtil.get_webdriver4_chrome()
        logging.debug("page start get_email_page ...")
        chrome.get(url)
        return SeleniumUtil.wait_then_return(chrome, "//table/tbody/tr/td/button", 200)

    @staticmethod
    def get_page(url, xpath, timeoutInSeconds):
        chrome = SeleniumUtil.get_webdriver4_chrome()
        # chrome.fullscreen_window()
        chrome.maximize_window()
        logging.debug("page start rendering...")
        chrome.get(url)
        return SeleniumUtil.wait_then_return(chrome, xpath, timeoutInSeconds)

    @staticmethod
    def full_screen(chrome):
        chrome.maximize_window()
        logging.debug('full_screen - maximize_window')

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
        logging.debug('Capture full screenshot to: ' + filepath)

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

        SeleniumUtil.image_crop(tmppic_path, filepath, x, y, width, height)

    @staticmethod
    def screenshot_with_crop(chrome, left, top, right, bottom, filepath, tmppic_path, show=False, format=None):
        chrome.save_screenshot(tmppic_path)
        SeleniumUtil.image_crop(tmppic_path, filepath, left, top, right, bottom, show, format)

    @staticmethod
    def image_crop(filepath, targetpath, x, y, x2, y2, show=False, format=None):
        if os.path.isfile(filepath):

            im = Image.open(filepath)
            im = im.crop((x, y, x2, y2))
            im.save(targetpath, format=format, quality=95, subsampling=0)
            logging.debug('image_crop file:' + filepath + ' [left:' + str(x) + ', top:' + str(y) + ', right:' + str(
                x2) + ', lower:' + str(y2) + ']')
            if show:
                im.show()

    @staticmethod
    def wait_then_return(chrome, xpath, timeoutInSeconds):
        logging.debug("waiting page rendering.")
        try:
            element = WebDriverWait(chrome, timeoutInSeconds).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            logging.debug("page rendered as excepted.")
            return chrome
        except:
            chrome.quit()
            logging.error("wait_then_return - fail to loading page, xpath:" + xpath)
            return None

    @staticmethod
    def wait_for_element_id_visible(chrome, eleId, timeout=60):
        logging.debug("start waiting wait_for_element_id_visible:" + eleId)
        try:
            WebDriverWait(chrome, timeout).until(EC.visibility_of_element_located((By.ID, eleId)))
            logging.debug("done waiting wait_for_element_id_visible:" + eleId)
            return chrome
        except:
            logging.warning(
                f"wait_for_element_id_visible - fail to wait within {timeout} seconds, associated with eleId:" + eleId)
            return None

    @staticmethod
    def wait_for_element_id_presence(chrome, eleId, timeout=60):
        logging.debug("start waiting wait_for_element_id_presence:" + eleId)
        try:
            WebDriverWait(chrome, timeout).until(EC.presence_of_element_located((By.ID, eleId)))
            logging.debug("done waiting wait_for_element_id_presence:" + eleId)
            return chrome
        except:
            logging.warning(
                f"wait_for_element_id_presence - fail to wait within {timeout} seconds, associated with eleId:" + eleId)
            return None

    @staticmethod
    def wait_for_element_css_visible(chrome, cssSelector, timeout=60):
        logging.debug("start waiting wait_for_element_css_visible:" + cssSelector)
        try:
            WebDriverWait(chrome, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, cssSelector)))
            logging.debug("done waiting wait_for_element_css_visible:" + cssSelector)
            return chrome
        except:
            logging.warning(
                f"wait_for_element_css_visible - fail to wait within {timeout} seconds, associated with css:" + cssSelector)
            return None

    @staticmethod
    def wait_for_element_css_presence(chrome, cssSelector, timeout=60):
        logging.debug("start waiting wait_for_element_css_presence:" + cssSelector)
        try:
            WebDriverWait(chrome, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, cssSelector)))
            logging.debug("done waiting wait_for_element_css_presence:" + cssSelector)
            return chrome
        except:
            logging.warning(
                f"wait_for_element_css_presence - fail to wait within {timeout} seconds, associated with css:" + cssSelector)
            return None

    @staticmethod
    def wait_for_element_xpath_visible(chrome, xpath, timeout=60):
        logging.debug("start waiting wait_for_element_xpath_visible:" + xpath)
        try:
            WebDriverWait(chrome, timeout).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            logging.debug("done waiting wait_for_element_xpath_visible:" + xpath)
            return chrome
        except:
            logging.warning(
                f"wait_for_element_xpath_visible - fail to wait within {timeout} seconds, associated with xpath:" + xpath)
            return None

    @staticmethod
    def wait_for_element_xpath_presence(chrome, xpath, timeout=60):
        logging.debug("start waiting wait_for_element_xpath_presence:" + xpath)
        try:
            WebDriverWait(chrome, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            logging.debug("done waiting wait_for_element_xpath_presence:" + xpath)
            return chrome
        except:
            logging.warning(
                f"wait_for_element_xpath_presence - fail to wait within {timeout} seconds, associated with xpath:" + xpath)
            return None

    @staticmethod
    def wait_for_element_xpath_presence_then_move2(chrome, xpath, timeout=60):
        logging.debug("start waiting wait_for_element_xpath_presence_then_move2:" + xpath)
        try:
            WebDriverWait(chrome, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            logging.debug("done waiting wait_for_element_xpath_presence:" + xpath)
            SeleniumUtil.move_to_ele(chrome, SeleniumUtil.find_element_by_x_path(chrome, xpath))
            return chrome
        except:
            logging.warning(
                f"wait_for_element_xpath_presence - fail to wait within {timeout} seconds, associated with xpath:" + xpath)
            return None

    @staticmethod
    def wait_for_element_link_visible(chrome, link, timeout=60):
        logging.debug("start waiting wait_for_element_link_visible:" + link)
        try:
            WebDriverWait(chrome, timeout).until(EC.visibility_of_element_located((By.LINK_TEXT, link)))
            logging.debug("done waiting wait_for_element_link_visible:" + link)
            return chrome
        except:
            logging.warning(
                f"wait_for_element_link_visible - fail to wait within {timeout} seconds, associated with link:" + link)
            return None

    @staticmethod
    def wait_for_element_link_presence(chrome, link, timeout=60):
        logging.debug("start waiting wait_for_element_link_presence:" + link)
        try:
            WebDriverWait(chrome, timeout).until(EC.presence_of_element_located((By.LINK_TEXT, link)))
            logging.debug("done waiting wait_for_element_link_presence:" + link)
            return chrome
        except:
            logging.warning(
                f"wait_for_element_link_presence - fail to wait within {timeout} seconds, associated with link:" + link)
            return None

    @staticmethod
    def wait_ele_visiable_then_click_by_xpath(chrome, xpath, fn=None):
        chrome = SeleniumUtil.wait_for_element_xpath_visible(chrome, xpath)
        ele = SeleniumUtil.find_element_by_x_path(chrome, xpath)
        if fn is None:
            ele.click()
        elif fn(ele):
            logging.debug(f'fn return true, click on: {xpath}')
            ele.click()
        else:
            logging.debug(f'fn return false, skip click on: {xpath}')
        return chrome

    @staticmethod
    def get_elements(chrome, by: str, identity: str, timeout=200):
        if by == 'xpath':
            return SeleniumUtil.get_elements_by(chrome, xpath=identity, timeout=timeout)
        if by == 'css':
            return SeleniumUtil.get_elements_by(chrome, css=identity, timeout=timeout)

    @staticmethod
    def get_elements_by(chrome, xpath=None, css=None, timeout=200):

        if not xpath == None:
            c = SeleniumUtil.wait_for_element_xpath_visible(chrome, xpath, timeout)
            if c is None:
                return []
            return SeleniumUtil.find_elements_by_x_path(chrome, xpath)

        if not css == None:
            c = SeleniumUtil.wait_for_element_css_visible(chrome, css, timeout)
            if c is None:
                return []
            return SeleniumUtil.find_elements_by_css(chrome, css)

    @staticmethod
    def get_element_by(chrome, by: str, identity: str, timeout=200):
        if by == 'id':
            return SeleniumUtil.get_element_by_id_with_wait(chrome, identity, timeout=timeout)
        elif by == 'xpath':
            return SeleniumUtil.get_element_by_xpath_with_wait(chrome, identity, timeout=timeout)
        elif by == 'link':
            return SeleniumUtil.get_element_by_link_with_wait(chrome, identity, timeout=timeout)
        elif by == 'css':
            return SeleniumUtil.get_element_by_css_with_wait(chrome, identity, timeout=timeout)
        else:
            raise Exception('unsupported by: ' + by)

    def get_element_by_id_with_wait(chrome, id, timeout=200):
        c = SeleniumUtil.wait_for_element_id_presence(chrome, id, timeout)
        if c is None:
            return None
        ele = SeleniumUtil.find_element_by_id(chrome, id)
        SeleniumUtil.move_to_ele(chrome, ele)
        c = SeleniumUtil.wait_for_element_id_visible(chrome, id, timeout)
        if c is None:
            return None
        return SeleniumUtil.find_element_by_id(chrome, id)

    def get_element_by_xpath_with_wait(chrome, xpath, timeout=200):
        c = SeleniumUtil.wait_for_element_xpath_presence(chrome, xpath, timeout)
        if c is None:
            return None
        ele = SeleniumUtil.find_element_by_x_path(chrome, xpath)
        SeleniumUtil.move_to_ele(chrome, ele)
        c = SeleniumUtil.wait_for_element_xpath_visible(chrome, xpath, timeout)
        if c is None:
            return None
        return SeleniumUtil.find_element_by_x_path(chrome, xpath)

    def get_element_by_link_with_wait(chrome, link, timeout=200):
        c = SeleniumUtil.wait_for_element_link_presence(chrome, link, timeout)
        if c is None:
            return None
        ele = SeleniumUtil.find_element_by_link(chrome, link)
        SeleniumUtil.move_to_ele(chrome, ele)
        c = SeleniumUtil.wait_for_element_link_visible(chrome, link, timeout)
        if c is None:
            return None
        return SeleniumUtil.find_element_by_link(chrome, link)

    def get_element_by_css_with_wait(chrome, css, timeout=200):
        c = SeleniumUtil.wait_for_element_css_presence(chrome, css, timeout)
        if c is None:
            return None
        ele = SeleniumUtil.find_element_by_css(chrome, css)
        SeleniumUtil.move_to_ele(chrome, ele)
        c = SeleniumUtil.wait_for_element_css_visible(chrome, css, timeout)
        if c is None:
            return None
        return SeleniumUtil.find_element_by_css(chrome, css)
