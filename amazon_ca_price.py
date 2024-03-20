try:
    import sys
    import platform
    from PIL import Image
    from keywords.playwright_keywords import PlaywrightKeywords
    from playwright.sync_api import sync_playwright, TimeoutError
    import re
    import time
    import csv
    import datetime
    import os
    import random
    import string
    import pyautogui
    import pytesseract
    from parsing_tools import ParsingTools
    import tkinter
    import logger
    from bs4 import BeautifulSoup
    import json
    import pandas as pd
    import requests
    import chardet
    import math
except Exception as e:
    print(f"couldn't load library: {e}")

# Resource blocking added by Rye on 2/7/23
block_resources = {
    "extensions": {".jpg", ".jpeg", ".csv", ".png", ".woff", ".woff2", ".pixel", ".gif", ".svg"},
    "domains": {},
    "types": {"media", "font", "image"},
}

home_page_url = 'https://www.amazon.ca/'  #### 3702
page_and_host = 'www.amazon.ca'  #### 3702
captcha_exist = '//form[@action="/errors/validateCaptcha"]'
zip_code_xpath = '//button[@name="select-location-button"]'
postal_code_textbox_xpath = '//div/div/input[contains(@id,"Zip")]'
submit_zip_code_xpath = '//button[@type="submit"]'
# choose_location = '//i[@class="ld ld-ChevronRight"]'
choose_location = '(//div[contains(@id,"location")]/span/a/div[1]|//div/span/a/div[1]|//a[@id="nav-global-location-popover-link"])[1]'
set_zip_code = '//div/div/input[contains(@id,"Zip")]'
press_and_hold = '//div/div[contains(@aria-label,"Press &")]'

long_timeout = 120000
mid_timeout = 30000
small_timeout = 15000
# mid_timeout=10000
mini_timeout = 7000
micro_timeout = 2000
max_retry_limit = 4
max_retry_limit_inner = 4  ## 3   #3-07-2021
# my_logger = []
home_page1 = None
home_page_context1 = None
home_page_browser1 = None
browser_exception = 'No'
submit_success = None
captcha_text_list = []

# extra raw.csv columns
list_of_input_id = []
list_of_ext_id = []
list_of_location = []
list_of_site = []
list_of_error_codes = []
list_of_errors = []
captcha_dict = {}

##3702
list_of_error_flag = []
list_of_SNAPSHOT_URL = []

# For Scraping of Page

list_of_price = []
list_of_unit_price = []
list_of_unit_measure = []
list_of_unit_number = []
list_of_price_sale = []
list_of_price_coupon = []
list_of_currency = []
list_of_price_cart = []
list_of_price_shipping = []
list_of_tax = []
list_of_promo_text = []
list_of_promo_date = []
list_of_promo_offer = []
list_of_promo_rebate = []
list_of_availability = []
list_of_condition = []
list_of_sold_by = []
list_of_timeframe = []
list_of_seller_id = []
list_of_fulfilled_by = []
list_of_seller_rating = []
list_of_seller_rating_count = []
list_of_seller_index = []
list_of_customer_review_score = []
list_of_customer_review_count = []
list_of_quantity = []
list_of_percentage = []
captcha_rows = []


def click_by_javascript(page, x_locator, message, click=None):
    logger.info("Inside click_by_javascript method")
    try:
        if click is None:
            output_var = page.evaluate(
                f"document.evaluate('{x_locator}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.getBoundingClientRect().toJSON();")
        else:
            output_var = page.evaluate(
                f"document.evaluate('{x_locator}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.click()")
        logger.info(f"{message}:{output_var}")
        return output_var
    except Exception as e:
        # logger.notice(str(e))
        logger.info("Exception from click_by_javascript method")
        return None


def _somewhere_random_close(x, y, max_dist=120):
    """
    Find a random position close to (x, y)
    with maximal dist @max_dist
    """
    shape = pyautogui.size()
    cnt = 0

    while True:
        randX = random.randrange(1, max_dist)
        randY = random.randrange(1, max_dist)

        if random.random() > 0.5:
            randX *= -1

        if random.random() > 0.5:
            randY *= -1

        if x + randX in range(0, shape.width) and y + randY in range(0, shape.height):
            return (x + randX, y + randY)

        cnt += 1

        if cnt > 15:
            return (x, y)


def _tiny_sleep():
    time.sleep(random.uniform(0.005, 0.009))


def print_n_log(message, error_context=None):
    """Log and print the message
        @param message Message that need to be log and print
        @param error_context set error_context="error" when want to log message as error(logger.error)
        """
    # my_logger_element = my_logger[0]
    print(message, flush=True)
    if error_context is not None:
        logger.error(message)
    else:
        logger.notice(message)


def load_home_page(inputs, playwright, keywords_py, browser_url):
    """ This method is to load home page/first url """
    try:
        set_page_content_browser = keywords_py.fetch_with_object_return(url=home_page_url, playwright=playwright)
        # set_page_content_browser = keywords_py.fetch_with_object_return(url=home_page_url, playwright=playwright)
        # keywords_py.wait_for_timeout(14000)
        if set_page_content_browser is None:
            print_message = 'Forbidden'
            raise Exception(print_message)
        else:
            page, browser, context = set_page_content_browser
    except Exception as pageNotLoaded:
        print_n_log(pageNotLoaded, error_context="error")
    return [page, context, browser]


def submit_url_on_page(inputs, home_page, keywords_py, default_output_dir, retry_counter=0):
    """ This method is to reach to the price page from where extraction to be done """

    captcha_filled = True
    # content_status=True
    try:
        print_n_log(f"entered to list/price page block with counter:{retry_counter} ")
        home_page.goto(inputs['URL'], timeout=long_timeout)
        # home_page.wait_for_selector('//span[contains(text(),"Add to cart")]')
        captcha_status = home_page.is_visible('//form[@action="/errors/validateCaptcha"]')
        # content_status = home_page.is_visible('//h2[contains(text(),"Customer reviews & ratings")]')
        page_data = home_page.content()

        # page_locator=home_page.locator('//h2[contains(text(),"Customer reviews & ratings")]').count()
        # if page_locator>0:
        #     content_status=True
        # else:
        #     content_status=False
        if re.search('Customer reviews', page_data) is not None or re.search('This page could not be found', page_data):
            content_status = True
        else:
            content_status = False
            # file_name = str(inputs['input_id'])+str('_counter')+str(retry_counter) + str('_captcha.html')
            # print_n_log(f"printing snapshot filename:{str(file_name)}")
            # data_page=home_page.content()
            # save_screenshot_snapshot(home_page=home_page, file_name=file_name, default_output_dir=default_output_dir)
        print_n_log(f"printing content available status:{str(content_status)}")
        # del page_data

        if not captcha_status or content_status:
            # file_name = str(inputs['input_id'])+str('_counter')+str(retry_counter) + str('_mid.html')
            # print("printing snapshot filename")
            # data_page=home_page.content()
            # save_screenshot_snapshot(home_page=home_page, file_name=file_name, default_output_dir=default_output_dir)
            # home_page.wait_for_selector('//h2[contains(text(),"Customer reviews ")]', timeout=50000)
            return captcha_filled
        if captcha_status and not content_status:
            print_n_log(f"captcha page status:{captcha_status}")
            captcha_filled = captcha_check(home_page, keywords_py, settings, keydown_wait_time=15000,
                                           default_output_dir=default_output_dir, inputs=inputs)

            print_n_log(f"printing captcha filled status:{str(captcha_filled)}")
            if captcha_filled is None:
                print_message = "Not able to solve captcha on list page"
                raise Exception(print_message)
            if captcha_status and captcha_filled is not None:
                home_page.goto(inputs['URL'], timeout=long_timeout)
                # home_page.wait_for_selector('//span[contains(text(),"Add to cart")]')
                home_page.wait_for_timeout(mini_timeout)
                captcha_filled = home_page.wait_for_selector('//div[@id="aod-container"]')
                if captcha_filled:
                    captcha_filled = True
                return captcha_filled
    except Exception as page_not_load:
        print_n_log(f"enter into submit page exception block:{str(page_not_load)}")
        if retry_counter < max_retry_limit_inner and re.search('Not able to solve captcha', str(page_not_load)) is None:
            # retry_counter = retry_counter + 1
            return submit_url_on_page(inputs, home_page, keywords_py, default_output_dir,
                                      retry_counter=retry_counter + 1)
        else:
            return None


def solve_image_captcha(settings, home_page, selector_to_wait, keywords_py, default_output_dir, keydown_wait_time,
                        inputs, retry_counter=0):
    """ This method is solves the captcha by press and hold """
    try:
        print_n_log("***Start Solving Captcha")
        print_n_log(f"***Solving captcha counter-{retry_counter} ")
        page_status = home_page.is_visible('//form[@action="/errors/validateCaptcha"]')
        update_location_check = home_page.is_visible('//div[contains(@id,"location")]/span/a/div[1]')
        logger.notice(f"update location link check:{update_location_check} ")
        logger.notice(f"page_status:{page_status} ")
        # if update_location_check:
        #     message = "when update location, captcha cannot be filled in any number of tries"
        #     raise Exception(message)
        # home_page.pause()
        captcha_txt = ''
        homecontent = home_page.content()
        image_url = ''
        if page_status:
            image_url = re.search('(http[^"]+.jpg)', re.search('img\s*src="([^"]+.jpg)', homecontent).group()).group()
        logger.notice(f"image_url:{image_url}")
        if page_status:
            logger.notice(f"length of captcha_dict:{len(captcha_dict)}")
            if len(captcha_dict) < 10:
                support_dir = "/caesius/cluster/global/amazon/captcha.csv" if settings.dev_mode == False else "D:\\scripts\\homegoods\\pricing\\amazon\\captcha.csv"
                logger.notice(support_dir)
                if os.path.exists(support_dir):
                    logger.notice("reading captcha file from global filebase")
                    with open(support_dir, 'r',
                              encoding=chardet.detect(open(support_dir, 'rb').read())['encoding']) as file:
                        csvreader = csv.reader(fix_nulls(file), quoting=csv.QUOTE_ALL)
                        for row in csvreader:
                            if '\0' not in row and row is not None:
                                captcha_rows.append(row)
            logger.notice(f"length of captcha_rows:{len(captcha_rows)}")

            for item in captcha_rows:
                # logger.notice(item)
                try:
                    if len(item[0]) > 0 and len(item[1]) > 0:
                        if re.search('([\da-zA-Z]+\/Captcha_[\da-zA-Z]+)', item[0]) is not None:
                            captcha_dict.update({str(re.search('([\da-zA-Z]+\/Captcha_[\da-zA-Z]+)',
                                                               item[0]).group()).lower(): item[1].lower()})
                            if item[0] in str(image_url):
                                captcha_txt = item[1]
                                logger.notice(f"matched captcha text from file:{captcha_txt}")
                except Exception as e:
                    pass
                    # logger.notice(f"exception in checking captcha in rows:{str(e)}")
            if len(captcha_txt) != 6:
                # if page_status:
                # solve the captcha
                #     target_url=image_url
                target_url = home_page.url
                list_page = home_page.content()
                try:
                    captcha_txt = ''
                    logger.notice("checking captcha exist")
                    if (keywords_py.captcha_exists(website_url=target_url, html=list_page)):
                        print_n_log("Found Captcha on the page")
                        captcha_txt = keywords_py.solve_captchas(website_url=target_url, html=list_page)
                        logger.notice("Captcha was solved with response " + captcha_txt)

                except:
                    pass
                if len(captcha_txt) == 6:
                    logger.notice("adding new captcha to the captcha file in global filebase")
                    # add to file so that it can be reused later on
                    file_path = "/caesius/cluster/global/amazon/captcha.csv" if settings.dev_mode == False else "D:\\scripts\\homegoods\\pricing\\amazon\\amazon_captcha.csv"
                    # file_path = "/caesius/cluster/global/amazon/amazon_captcha.csv"
                    image_url_to_save = re.search('([\da-zA-Z]+\/Captcha_[\da-zA-Z]+)', image_url).group()
                    captcha_info = {"image_url": [image_url_to_save], "captcha_text": [captcha_txt]}
                    logger.notice(captcha_info)
                    df = pd.DataFrame(captcha_info)
                    df.to_csv(file_path, mode='a', index=False, header=False)
                    logger.notice("new captcha added to the captcha file")
                else:
                    print_n_log("No Captcha on the page")
                    home_page.goto(home_page_url, wait_until="domcontentloaded", timeout=170000)
            if len(captcha_txt) == 6:
                logger.notice("filling captcha on the page")
                home_page.fill('//input[@id="captchacharacters"]', captcha_txt)
                time.sleep(5)
                print_n_log("Typed captcha_txt " + str(captcha_txt))
                keywords_py.click(page=home_page, xpath_locator='//button[@class="a-button-text"]')
                home_page.wait_for_timeout(20000)
                home_page.is_visible('//div[contains(@id,"location")]/span/a/div[1]')
            else:
                message = "Again Captcha"
                raise Exception(message)

        page_status = home_page.is_visible(
            '//input[@data-action-type="SELECT_LOCATION"]|//a[@id="nav-global-location-popover-link"]')
        logger.notice(f"printing page status after captcha solved once:{page_status}")
        technical_error_check = home_page.is_visible('//div[@class="nav-bb-left"]//a[contains(text(),"Departments")]')
        logger.notice(f"Need reload:{technical_error_check}")
        # home_page.pause()
        file_name = str(inputs['input_id'].replace('_', '__')) + str('_counter_') + str(retry_counter) + str(
            '_after_captcha_solve_try.html')
        # logger.notice(f"screenshot in solve_image_captcha :{str(file_name)}")
        # save_screenshot_snapshot(home_page=home_page, file_name=file_name, default_output_dir=default_output_dir)
        # print_n_log(f"Page could not be found for input id:{str(inputs['input_id'])}", error_context="error")
        if technical_error_check:
            try:
                home_page.reload(timeout=long_timeout)
            except:
                home_page.wait_for_timeout(20000)
        page_status = home_page.is_visible('//form[@action="/errors/validateCaptcha"]')
        if page_status:
            message = "Again Captcha"
            raise Exception(message)
        else:
            return True
    except Exception as Page_Not_Loaded:
        print_n_log(Page_Not_Loaded)
        # logger.notice(f"solve captcha counter:{retry_counter}")
        if retry_counter <= max_retry_limit_inner and re.search("technical error page",
                                                                str(Page_Not_Loaded)) is None:  # and re.search("when update location", str(Page_Not_Loaded)) is None and
            return solve_image_captcha(settings, home_page, selector_to_wait, keywords_py, default_output_dir,
                                       keydown_wait_time, inputs, retry_counter=retry_counter + 1)
        else:
            return None


def fix_nulls(s):
    for line in s:
        yield line.replace('\0', '')


def captcha_check(home_page, keywords_py, settings, keydown_wait_time, default_output_dir, inputs):
    """ This method is to check Press and Hold captcha on any page """
    logger.notice("Inside check_captcha method")
    page_content = home_page.content()
    captcha_locator_count = home_page.locator(captcha_exist).count()
    if captcha_locator_count > 0:
        zip_selector = choose_location
        captcha_done = solve_image_captcha(settings, home_page=home_page, selector_to_wait=zip_selector,
                                           keywords_py=keywords_py, default_output_dir=default_output_dir,
                                           keydown_wait_time=keydown_wait_time, inputs=inputs)
        if captcha_done is None:
            print("printing captcha done status False")
            return None
        else:
            # home_page.wait_for_selector(zip_selector)
            print("printing captcha done status", captcha_done)
            zip_check = click_by_javascript(page=home_page, x_locator=zip_selector,
                                            message="address div element visibility check using javascript in captcha_check function")
            captcha_locator_count = home_page.locator(zip_selector).count()
            if captcha_locator_count == 0 and zip_check is not None:
                captcha_locator_count = 1

            if captcha_done:
                # if captcha_done is not None:
                print_n_log("captcha solve done")
                return captcha_locator_count
            else:
                return None


def submit_zipcode(home_page, keywords_py, inputs, location, update_location_check, retry_counter=0):
    """ This method is to submit zipcode from the inputs on the website """
    # retry_counter = 0
    try:
        print_n_log(f"zip code submit try counter-{retry_counter}")
        # home_page.type(set_zip_code, location)
        # zip_code_text_box_check =
        ###home_page.fill(set_zip_code, location )   ### update 3702

        try:
            home_page.fill('//input[@id="GLUXZipUpdateInput_0"]', location[0:3])  ### enter zip code    3702
        except:
            home_page.fill('//div[@id="GLUXZipInputSection"]//input[@id="GLUXZipUpdateInput_0"]',
                           location[0:3])  ### enter zip code    3702

        home_page.wait_for_timeout(500)

        try:
            home_page.fill('//input[@id="GLUXZipUpdateInput_1"]', location[4:7])  ### enter zip code    3702
        except:
            home_page.fill('//div[@id="GLUXZipInputSection"]//input[@id="GLUXZipUpdateInput_1"]',
                           location[4:7])  ### enter zip code    3702

        time.sleep(5)
        print_n_log("Typed zip code " + str(location))
        logger.notice("Typed zip code " + str(location))

        ### '//span[text()="Apply"]' >>> apply_button         ### 3702    use apply button
        apply_button = '//div[@role="button"]//span[@data-action="GLUXPostalUpdateAction"]//span[@id="GLUXZipUpdate-announce"]'  ##666

        try:
            keywords_py.click(page=home_page, xpath_locator=apply_button)
            zip_status = home_page.is_visible(apply_button)
            if zip_status:
                keywords_py.click(page=home_page, xpath_locator=apply_button)
            zip_status = home_page.is_visible(apply_button)
            if zip_status:
                raise Exception("Retry by js")
            logger.notice("Clicked store location")
        except:
            pickup_store_click = click_by_javascript(page=home_page, x_locator=apply_button,
                                                     message="clicking pickup store using javascript in submit_zipcode methos",
                                                     click="yes")
        time.sleep(2)
        try:
            keywords_py.click(page=home_page,
                              xpath_locator='//div[@class="a-popover-footer"]/span/span[contains(@data-action,"Confirm")]//span[text()="Continue"]|//button[@name="glowDoneButton"]')
        except:
            time.sleep(10)
            done_status = home_page.is_visible('//span[@id="glow-ingress-line2"]')  ### 3702
            if done_status:
                pickup_store_click = click_by_javascript(page=home_page, x_locator='//button[@name="glowDoneButton"]',
                                                         message="clicking done using javascript in submit_zipcode method",
                                                         click="yes")
                time.sleep(10)
        logger.notice("Successfully entered the location. Now able to move onto product pages. ")
        time.sleep(10)
        return True

    except Exception as page_no_loaded:
        if retry_counter < max_retry_limit_inner:
            try:
                home_page.reload(timeout=long_timeout)
                home_page.wait_for_timeout(20000)
            except:
                home_page.wait_for_timeout(20000)
            keywords_py.click(page=home_page, xpath_locator=choose_location)
            print_n_log(page_no_loaded)
            return submit_zipcode(home_page, keywords_py, inputs, location, update_location_check,
                                  retry_counter=retry_counter + 1)
        else:
            return None


def save_screenshot_snapshot(home_page, file_name, default_output_dir):
    file_path = str(default_output_dir) + str('/') + str(file_name)
    print(f"saving to filepath:{file_path}")
    # screenshot_path = default_output_dir + file_name
    file_path_screenshot = str(default_output_dir) + str('/') + str(file_name).replace('.html', '.png')
    home_page.screenshot(path=file_path_screenshot)
    html_content = home_page.content()
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        f.close()
    del html_content


# def data_extraction(home_page,inputs,keywords_py)

def scrap_web(line_item, playwright, keywords_py, settings, default_output_dir, mod_value, browser_url, index):
    """ This is the main crawling method in which all other methods are presents """
    global home_page1
    global home_page_context1
    global home_page_browser1
    global submit_success
    global browser_exception
    retry_counter = 0
    max_retry = 2
    captcha_filled = True
    inputs = keywords_py.input_variables(line_item)
    if '/gp/' in inputs['input_path']:
        ##inputs['URL']='https://www.amazon.com/gp/aod/ajax/ref=dp_aod_NEW_mbc?asin='+re.search('\W([A-Z\d]{10})\W',inputs['input_path']).group()[1:11]+'&m=&pinnedofferhash=&qid=&smid=&sourcecustomerorglistid=&sourcecustomerorglistitemid=&sr='
        ###3702
        inputs['URL'] = 'https://www.amazon.ca/gp/product/ajax/ref=auto_load_aod?asin=' + re.search('\W([A-Z\d]{10})\W',
                                                                                                    inputs[
                                                                                                        'input_path']).group()[
                                                                                          1:11] + '&pc=dp&experienceId=aodAjaxMain'

    else:
        inputs['URL'] = inputs['input_path']
    if inputs['location'] == 'NATIONAL':
        location = 'M5V 2E3'  ### 3702
    else:
        location = inputs['location']

    while retry_counter < max_retry:
        print("Executing input_id: " + str(inputs['input_id']) + "- " + str(retry_counter))
        try:
            print_n_log("*****Start Loading Home Page****")
            print_n_log(f"printing home page status:{home_page1}")
            browser_exception = "No"
            if home_page1 is None:  # if the browser is already closed or if it the first input then global state will be none. So need to open the session/browser with load_home_page. Otherwise directly hit the product page on the opened browser
                home_page_status = load_home_page(inputs, playwright, keywords_py, browser_url)
                home_page = home_page_status[0]
                home_page1 = home_page_status[0]
                home_page_context1 = home_page_status[1]
                home_page_context = home_page_status[1]
                home_page_browser1 = home_page_status[2]
                home_page_browser = home_page_status[2]
                page_data = home_page.content()
                print_n_log("*******************************")
                pt = ParsingTools(page_data)
                captcha_text = "Enter the characters you see below"
                captcha_status = pt.page_should_contain(text=captcha_text)
                print_n_log("*****checking for captcha*****")
                print(f"printing page url={home_page.url}")
                page_url_split = re.split('/', home_page.url)
                print(page_url_split)
                page_url = page_url_split[2]
                if page_and_host != page_url:
                    print_message = "page redircted to incorrect pos"
                    raise Exception(print_message)
                if captcha_status:
                    print_n_log(f"captcha page status:{captcha_status}")
                    # calling this method to check and solve captcha
                    captcha_filled = captcha_check(home_page, keywords_py, settings, keydown_wait_time=10000,
                                                   default_output_dir=default_output_dir, inputs=inputs)
                    page_status = home_page.is_visible('//form[@action="/errors/validateCaptcha"]')
                    update_location_check = home_page.is_visible('//div[contains(@id,"location")]/span/a/div[1]')
                    if not page_status and captcha_status is None and update_location_check:
                        try:
                            keywords_py.click(page=home_page,
                                              xpath_locator='//input[@data-action-type="SELECT_LOCATION"]')
                            page_status = home_page.is_visible('//form[@action="/errors/validateCaptcha"]')
                            if page_status:
                                captcha_filled = None
                                logger.notice("Printing Captcha Solve Status", captcha_filled)

                        except:
                            home_page.wait_for_timeout(10000)
                            click_update_javascript = click_by_javascript(page=home_page,
                                                                          x_locator='//div[contains(@id,"location")]/span/a/div[1]',
                                                                          message="clicking update using javascript in scrap_web",
                                                                          click="yes")
                            page_status = home_page.is_visible('//form[@action="/errors/validateCaptcha"]')
                            if page_status:
                                captcha_filled = None
                                logger.notice("Printing Captcha Solve Status", captcha_filled)

                    else:
                        print("Printing Captcha Solve Status", captcha_filled)
                    if captcha_filled is None:
                        print_message = "Not able to solve captcha"
                        raise Exception(print_message)
                if re.search('\d+', location) is not None:
                    print_n_log("*****Submit Zip codes*****")
                    home_page.wait_for_timeout(10000)
                    technical_issue_check = home_page.is_visible(
                        '//div[@class="nav-bb-left"]//a[contains(text(),"Departments")]')
                    if technical_issue_check:
                        try:
                            home_page.reload(timeout=long_timeout)
                        except:
                            home_page.wait_for_timeout(20000)
                    update_location_check = home_page.is_visible(
                        '//input[@data-action-type="SELECT_LOCATION"]|//a[@id="nav-global-location-popover-link"]')
                    # if update_location_check:
                    #     message = "when update location, captcha cannot be filled in any number of tries"
                    #     raise Exception(message)
                    if not update_location_check:
                        home_page.wait_for_selector(choose_location, timeout=long_timeout)
                        zip_location_selector_check_javascript = click_by_javascript(page=home_page,
                                                                                     x_locator=choose_location,
                                                                                     message="address visibility check using javascript in scrap_web method")
                        try:
                            zip_location_selector = home_page.is_visible(choose_location)
                            keywords_py.click(page=home_page, xpath_locator=choose_location)
                        except:
                            if zip_location_selector_check_javascript is not None:
                                zip_location_selector_click_ajavscript = click_by_javascript(page=home_page,
                                                                                             x_locator=choose_location,
                                                                                             message="clicking address using javascript in scrap_web method",
                                                                                             click="yes")
                            else:
                                message = "address not visible from scrap_web method"
                                raise Exception(message)
                    else:
                        try:
                            zip_location_selector = home_page.is_visible(choose_location)
                        except:
                            pass
                        keywords_py.click(page=home_page, xpath_locator=choose_location)
                        print_n_log(f"zip location selector status is:{zip_location_selector}")
                    zip_code_submit_status = submit_zipcode(home_page, keywords_py, inputs, location,
                                                            update_location_check=update_location_check,
                                                            retry_counter=0)
                    if zip_code_submit_status is None:
                        print_message = "Zip code not submitted"
                        raise Exception(print_message)
            else:
                home_page = home_page1
                home_page_context = home_page_context1
                home_page_browser = home_page_browser1

            # keywords_py.type_text(text=inputs['location'],page=home_page,xpath_locator='//input[@name="postalCode"]')
            # now hitting the actual price url from the inputs
            print_n_log("***************")
            print_n_log("******Moving to Price Page/List Page*******")
            # time.sleep(30)
            # if submit_success is None:
            #     time.sleep(30)
            # else:
            #     time.sleep(2)
            # home_page.wait_for_load_state('networkidle',timeout=60000)
            # print("request finished wait")
            # home_page.expect_request_finished()
            list_page = submit_url_on_page(inputs, home_page, keywords_py, default_output_dir)
            print_n_log(f"list Page Status: {list_page}")
            if list_page is None:  # print_n_log(f"Captcha found on product page for input id:{str(inputs['input_id'])}", error_context="error")
                print_message = "list Page Not Loaded"
                raise Exception(print_message)
            else:
                data_page = home_page.content()
                data_available = False
                if (re.search(
                        'This page could not be found|Currently, there are no other sellers|Sorry! We couldn''t find that page. Try searching or go to Amazon''s home page',
                        data_page) is None) or (re.search('aod-offer-heading', data_page) is not None):
                    data_available = True
                    dseries = scrape_page(home_page, index, default_output_dir, inputs, location, keywords_py)
                    file_name = str(inputs['input_id']) + str('_counter_') + str(retry_counter) + str(
                        '_amazon_price_page.html')
                    print("printing snapshot filename")
                    # keywords_py.save_snapshot(variable=data_page, file_name=file_name)
                    # save_screenshot_snapshot(home_page=home_page, file_name=file_name, default_output_dir=default_output_dir)
                    if dseries["INPUT_ID"].isin([str(inputs['input_id']).replace("_", ":")]).any():
                        pass
                    else:
                        if inputs['location'] == 'NATIONAL':
                            location = 'M5V 2E3'  ### 3702
                        else:
                            location = inputs['location']
                        bad_product_page(home_page, index, default_output_dir, inputs, location)
                    mod_value = 9 if (re.search(
                        'Sorry! We couldn''t find that page. Try searching or go to Amazon''s home page|Sorry! Something went wrong on our end. Please go back and try again or go to Amazon',
                        data_page) is not None) else mod_value
                else:
                    file_name = str(inputs['input_id']) + str('_counter_') + str(retry_counter) + str(
                        '_page_not_found.html')
                    print("printing snapshot filename")
                    # save_screenshot_snapshot(home_page=home_page, file_name=file_name, default_output_dir=default_output_dir)
                    print_n_log(f"Page could not be found for input id:{str(inputs['input_id'])}",
                                error_context="error")
                    # update 16-08-20223

                    CUSTOMER_REVIEW_SCORE = ''
                    CUSTOMER_REVIEW_COUNT = ''
                    list_of_customer_review_count.clear()
                    list_of_customer_review_score.clear()
                    list_of_customer_review_count.append(CUSTOMER_REVIEW_COUNT)
                    list_of_customer_review_score.append(CUSTOMER_REVIEW_SCORE)
                    # end update 16-08-20223
                    bad_product_page(home_page, index, default_output_dir, inputs, location)
                if mod_value == 9:
                    home_page_context.close()
                    # home_page_browser.close()
                print_n_log("***************")
                print_n_log("******Execution Finish*********")
                submit_success = "Yes"
                break
        except Exception as pageNotLoaded:
            print_n_log(message=pageNotLoaded, error_context="error")
            retry_counter = int(retry_counter) + 1
            home_page1 = home_page_context1 = home_page_browser1 = None
            browser_exception = None
            submit_success = None
            print("Entered into main exception block of scrap_web function")
            if retry_counter == max_retry and re.search('Not able to solve captcha', str(pageNotLoaded)) is not None:
                print_n_log(f"Captcha found on product page for input id:{str(inputs['input_id'])}",
                            error_context="error")
            try:
                home_page_context.close()
                # home_page_browser.close()
                if re.search('Not able to solve captcha', str(pageNotLoaded)) is not None:
                    keywords_py.renew_proxy("captcha not solved")
                    keywords_py.cleanup()
                else:
                    keywords_py.cleanup()
            except Exception as e:
                print(e)
                keywords_py.cleanup()


def bad_product_page(page, index, default_output_dir, inputs, location):
    logger.notice("bad_product_page")

    # Unavailable
    list_of_price.append("")
    list_of_unit_number.append("")
    list_of_currency.append("")
    list_of_price_shipping.append("")
    list_of_availability.append("")
    list_of_condition.append("")
    list_of_sold_by.append("")
    list_of_seller_index.append("")
    list_of_customer_review_score.append("")
    list_of_customer_review_count.append("")
    list_of_quantity.append("")
    list_of_fulfilled_by.append("")
    # Others
    list_of_unit_price.append("")
    list_of_unit_measure.append("")
    list_of_price_sale.append("")
    list_of_price_coupon.append("")
    list_of_price_cart.append("")
    list_of_tax.append("")
    list_of_promo_text.append("")
    list_of_promo_date.append("")
    list_of_promo_offer.append("")
    list_of_promo_rebate.append("")
    list_of_timeframe.append("")
    list_of_seller_id.append("")
    list_of_seller_rating.append("")
    list_of_seller_rating_count.append("")
    list_of_percentage.append("")
    list_of_error_codes.append("300")
    list_of_errors.append("No pricing information found at: " + str(page.url))
    list_of_error_flag.append("")  ##3702    66
    list_of_SNAPSHOT_URL.append("")  ##3702   666

    # extras for raw.csv
    list_of_input_id.append(str(inputs['input_id']).replace("_", ":"))
    # list_of_ext_id.append(str(inputs['ext_id']))
    list_of_ext_id.append(str(inputs['ext_id']).replace('None', ''))
    list_of_location.append(str(location))
    list_of_site.append(str(inputs['site_code']))
    df = write_to_csv(page, index, default_output_dir, inputs)
    return df


def see_cart_price_in_multiple_sellers(page, count):
    logger.notice("Inside of see_cart_price_in_multiple_sellers")
    logger.notice('Count is: ' + str(count))
    xpath = '(//button[@class="w_B0 w_B2 w_B5 w_B7"])[' + str(count) + ']'
    # xpath = '(//button[@class="w_B0 w_B2 w_B5 w_B7"])[4]'
    page.click(xpath, delay=7)
    logger.notice('just clicked')
    # get the price
    html3 = page.content()
    soup3 = BeautifulSoup(html3, "html.parser")
    search3 = soup3.find_all("div", {"class": "f5 lh-copy h2-l f4-l lh-title-l b black tr"})
    cart_price = search3[0].get_text()
    cart_price = cart_price.replace('$', '')
    list_of_price_cart.append(cart_price)
    # click remove item to empty cart - IGNORE NOT NEEDED


def scrape_page(page, index, default_output_dir, inputs, location, keywords_py):
    # exit out of panel
    # Scrape page
    logger.notice("scrape_page")
    logger.notice(page.url)
    html = page.content()
    sp = BeautifulSoup(html, "html.parser")
    soup = sp.find(id="aod-pinned-offer")
    soup_00 = soup

    # SCRAPE ITEMS - First one do 1,4,6a,8,14,15,16,20,21,22,23
    # 1. PRICE
    search = sp.find_all("span", {"class": "a-offscreen"})
    search_11 = sp.find_all("span", {"class": "a-size-small a-color-secondary aok-align-center"})
    error_handling = sp.find_all("span", {"id": "a-autoid-2-offer-0-announce"})
    add_to_cart_page = sp.find_all("span", {"class": "a-size-small a-color-base"})
    add_to_cart_extract = re.findall('id="aod-generic-map-\d+">([^<]+)</span>', str(add_to_cart_page))
    # logger.info(f"add_to_cart_extract:{add_to_cart_extract}")
    # logger.info(f"add_to_cart_page:{add_to_cart_page}")
    # logger.info(f"error_handling:{error_handling}")
    if len(search) == 0:
        bad_product_page(page, index, default_output_dir, inputs, location)
        return df

    else:
        logger.info('print enter the else loop')
        record_total = re.search('value="(\d+)(?:" id="aod-total| other options)', html).group()
        record_on_first_page = len(sp.find_all("div", {"id": "aod-offer"}))
        print_n_log(record_on_first_page)
        append_to_lists(page, index, default_output_dir, inputs, location)
        # USED TO BE HERE TO CHECK FOR BAD PAGE
        # PRICE = "No pricing information found at: " + str(page.url)
        priceInCart = ""

    if soup is not None:
        if 'price in cart' in str(search):
            logger.notice("PRICE IS IN CART ALERT")
            strSoup = str(soup)
            strSoup = strSoup.split(',"amount":')
            priceInCart = strSoup[1].split(',')[0]
            list_of_price_cart.append(priceInCart)
            PRICE = ""
            PRICE_SELL = ""  ## update 19-06-2023
        else:
            list_of_price_cart.append("")
            price = search[0].get_text()
            PRICE = str(price.split('$')[1])
            PRICE_SELL = ''
            try:
                if 'class="a-size-small a-color-secondary aok-align-center">' in str(soup):
                    try:
                        if search[4] is not None:
                            PRICE_SELL = search_11[0].get_text()  ## update 19-06-2023
                            PRICE_SELL = str(PRICE_SELL).strip()
                            logger.info(f'print search[3].get_text() PRICE_SELL {PRICE_SELL}')
                            PRICE_SELL = str(PRICE_SELL.split('$')[1])  ## update 19-06-2023
                            # logger.info(f'print search[1].get_text() PRICE_SELL 22 {PRICE_SELL}')
                        else:
                            PRICE_SELL = search[2].get_text()  ## update 19-06-2023
                            PRICE_SELL = str(PRICE_SELL).strip()
                            logger.info(f'print search[2].get_text() PRICE_SELL {PRICE_SELL}')
                            PRICE_SELL = str(PRICE_SELL.split('$')[1])  ## update 19-06-2023
                            # logger.info(f'print search[1].get_text() PRICE_SELL 22 {PRICE_SELL}')

                    except:
                        PRICE_SELL = search[1].get_text()  ## update 19-06-2023
                        PRICE_SELL = str(PRICE_SELL).strip()
                        # logger.info(f'print search[2].get_text() PRICE_SELL {PRICE_SELL}')
                        PRICE_SELL = str(PRICE_SELL.split('$')[1])  ## update 19-06-2023
                        # logger.info(f'print search[1].get_text() PRICE_SELL 22 {PRICE_SELL}')


            except:
                PRICE_SELL = ''
            PRICE = PRICE.replace(",", "")  ## update 19-06-2023
            PRICE_SELL = PRICE_SELL.replace(",", "")  ## update 19-06-2023

        PRICE
        PRICE_SELL
        logger.info(f'print first PRICE {PRICE}')
        logger.info(f'print first price PRICE_SELL {PRICE_SELL}')

        try:
            if PRICE is '' and PRICE_SELL is '':
                PRICE_00 = ''
                PRICE_SELL_00 = ''
            elif PRICE is '' and PRICE_SELL is not '':
                PRICE_00 = PRICE_SELL
                PRICE_SELL_00 = ''
            elif PRICE is not '' and PRICE_SELL is '':
                PRICE_00 = PRICE
                PRICE_SELL_00 = ''
            elif float(PRICE) > float(PRICE_SELL):
                PRICE_00 = PRICE
                PRICE_SELL_00 = PRICE_SELL
            elif float(PRICE) < float(PRICE_SELL):
                PRICE_1 = PRICE
                PRICE_00 = PRICE_SELL
                PRICE_SELL_00 = PRICE_1
            elif float(PRICE) == float(PRICE_SELL):
                PRICE_00 = PRICE
                PRICE_SELL_00 = ''
            else:
                PRICE_00 = PRICE
                PRICE_SELL_00 = PRICE_SELL
        except:
            pass
            logger.info('print except price and price sell 1')

        logger.notice('PRICE_00: ' + PRICE_00)
        list_of_price_sale.append(PRICE_SELL_00.replace(",", ""))
        list_of_price.append(PRICE_00.replace(",", ""))

        # 4. UNIT_NUMBER
        UNIT_NUMBER = str(1)
        logger.notice('UNIT_NUMBER: ' + UNIT_NUMBER)
        list_of_unit_number.append(str(UNIT_NUMBER))

        # 6a. CURRENCY
        CURRENCY = 'CAD'
        logger.notice('CURRENCY: ' + CURRENCY)
        list_of_currency.append(CURRENCY)
        delivery_charge = '//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()[1]'
        # shipping_regex = re.compile('data-csa-c-delivery-price\s*=\s*"\s*([FREE\$\d.,]+)\s*"')
        # Changes for price shipping
        shipping = re.findall('data-csa-c-delivery-price\s*=\s*"\s*([FREE\$\d.,]+)\s*"', str(soup))

        ### start 3702 ## 666
        if len(shipping) == 0:
            shipping = re.findall('id="mir-layout-DELIVERY_BLOCK"[^<]+<[^<]+<[^<>]+>([^<]+)', str(soup))
        else:
            shipping = shipping
        ### end 3702 ## 666

        # 8. PRICE SHIPPING
        # shipping = soup.find(text=shipping_regex) #logic added above
        logger.notice(shipping)
        if shipping is None:
            PRICE_SHIPPING = ""
        elif "Free shipping" in shipping:
            PRICE_SHIPPING = str(0)
        elif "FREE delivery" in shipping:
            PRICE_SHIPPING = str(0)
        elif "FREE" in shipping:
            PRICE_SHIPPING = str(0)
        elif 'delivery-price="FREE"' in shipping:
            PRICE_SHIPPING = str(0)

        elif "Free pickup" in shipping:
            PRICE_SHIPPING = ""
        elif "out of stock" in shipping:
            PRICE_SHIPPING = ""
        elif len(shipping) > 0:
            PRICE_SHIPPING = shipping[0]
        else:
            PRICE_SHIPPING = ''
        PRICE_SHIPPING = str(PRICE_SHIPPING)
        PRICE_SHIPPING = PRICE_SHIPPING.replace("$", "")
        PRICE_SHIPPING = PRICE_SHIPPING.replace(" shipping", "")
        PRICE_SHIPPING = PRICE_SHIPPING.replace(", ", "")
        PRICE_SHIPPING = PRICE_SHIPPING.replace(",", "")
        try:
            PRICE_SHIPPING = float(PRICE_SHIPPING)
        except:
            PRICE_SHIPPING = ''
            pass

        logger.notice('PRICE_SHIPPING: ' + str(PRICE_SHIPPING))
        list_of_price_shipping.append(PRICE_SHIPPING)

        # 14. Availability
        AVAILABILITY = {}
        time_regex = re.search('data-csa-c-delivery-time="([^"]+)', str(soup))
        # 8. PRICE SHIPPING

        try:
            if time_regex is not None:
                estimated_delivery = re.search('"([^"]+)', time_regex.group()).group().replace('"', '').strip()
                logger.notice(estimated_delivery)
            else:
                estimated_delivery = ''
        except:
            estimated_delivery = estimated_delivery.replace("Want it faster? Add an address to see options", "")
            estimated_delivery = estimated_delivery.replace("Currently out of stock", "")

        search = soup.find_all("div", {"id": "aod-offer-shipsFrom"})

        search_unavailable = soup.find_all("div", {"id": "aod_ship_charge_row"})  # 3702 420
        if search_unavailable is not None:  # 3702 420
            web_availability_unavailable = str(search_unavailable[0].get_text()).strip()  # 3702 420

        # logger.notice(search)
        if len(search) > 0:
            web_availability = str(search[0].get_text()).replace("Ships from", "").strip()
        else:
            web_availability = ''
        # list_of_fulfilled_by.append(web_availability)
        list_of_fulfilled_by.append(
            re.sub(r'This item is shipped from[^>]+', '', web_availability).strip())  ## 3702 6666

        if 'out of stock' in web_availability:
            web_availability = "Out of stock"
        elif 'currently unavailable' in web_availability_unavailable:  ##3702  66 20-01-23
            web_availability = "Out of stock"
        elif web_availability is not None:
            web_availability = 'In Stock'
        else:
            web_availability = 'Out of stock'

        AVAILABILITY['WEB_AVAILABILITY'] = web_availability
        AVAILABILITY['STORE_AVAILABILITY'] = ''
        AVAILABILITY['ESTIMATED_DELIVERY'] = estimated_delivery
        AVAILABILITY = json.dumps(AVAILABILITY, separators=(',', ':'))
        # logger.notice(type(AVAILABILITY))
        logger.notice(AVAILABILITY)
        list_of_availability.append(AVAILABILITY)
        # logger.notice(list_of_availability)

        # 15. CONDITION
        search = soup.find_all("div", {"id": "aod-offer-heading"})
        try:
            condition = str(
                search[0].get_text().replace('"', '').replace('}', '').strip())
        except IndexError:
            try:
                condition = str(
                    search[0].get_text().replace('"', '').replace('}', '').strip())
            except:
                condition = ''

        logger.notice('condition: ' + condition)
        list_of_condition.append(condition)

        # 16. SOLD_BY
        search = soup.find_all("div", {"id": "aod-offer-soldBy"})
        try:
            if search[0] is not None:

                SOLD_BY = str(search[0].get_text().split('Sold by')[1]).split('(')[0].rstrip().lstrip().replace(
                    'Just launched', '')
                # SOLD_BY = ''.join(SOLD_BY)
                SOLD_BY = SOLD_BY.encode('ascii', 'ignore').decode('utf-8')
                if 'New Seller' in SOLD_BY:
                    SOLD_BY = SOLD_BY.replace('New Seller', '').strip()
                else:
                    SOLD_BY = SOLD_BY.strip()
                logger.notice(f"SOLD_BY_CHECK: {SOLD_BY}")
            else:
                SOLD_BY = ''
        except IndexError:
            try:
                SOLD_BY = search[1].get_text().split('Sold by')[1].split('(')[0].replace('Just launched',
                                                                                         '').rstrip().lstrip()
                SOLD_BY = SOLD_BY.encode('ascii', 'ignore').decode('utf-8')
            except:
                SOLD_BY = ''

        list_of_sold_by.append(re.sub(r'\s*[\d.]+%[^>]+', '', str(SOLD_BY)).strip())  ## 3702  420

        # 20. SELLER_INDEX
        SELLER_INDEX = str(1)
        logger.notice('SELLER_INDEX: ' + SELLER_INDEX)
        list_of_seller_index.append(str(SELLER_INDEX))

        # 21. CUSTOMER_REVIEW_SCORE
        # try:
        #     search = soup.find_all("span", {"class": "black inline-flex ml1"})
        #     CUSTOMER_REVIEW_SCORE = str(search[0]).split('aria-label="')[1].split(',')[0][:3]
        # except IndexError:
        search = re.search('class="a-icon a-icon-star(?:-mini)? a-star(?:-mini)?-([\d-]+)', str(sp))
        try:
            if search is not None:
                CUSTOMER_REVIEW_SCORE = str(re.search('(\d[-\d]*)', str(search.group())).group()).replace('-', '.')
            else:
                CUSTOMER_REVIEW_SCORE = ''


        except:
            CUSTOMER_REVIEW_SCORE = ''

        logger.notice('CUSTOMER_REVIEW_SCORE: ' + CUSTOMER_REVIEW_SCORE)
        list_of_customer_review_score.append(CUSTOMER_REVIEW_SCORE)

        # 22. CUSTOMER_REVIEW_COUNT
        search = soup.find_all("span", {"id": "aod-asin-reviews-count-title"})
        try:
            if len(search) > 0:
                CUSTOMER_REVIEW_COUNT = str(
                    search[0].get_text().replace('ratings', '').replace('rating', '').replace(' s', '').replace(
                        'Justlaunched', '').replace(',', '')).strip()
            else:
                CUSTOMER_REVIEW_COUNT = ''
        except IndexError:
            try:
                CUSTOMER_REVIEW_COUNT = str(
                    search[0].get_text().replace('ratings', '').replace('rating', '').replace(' s', '').replace(
                        'Justlaunched', '').replace(',', '')).strip()
            except:
                CUSTOMER_REVIEW_COUNT = ''
        if 'New Seller' in CUSTOMER_REVIEW_COUNT:
            CUSTOMER_REVIEW_COUNT = CUSTOMER_REVIEW_COUNT.replace('New Seller', '').strip()
        else:
            CUSTOMER_REVIEW_COUNT = CUSTOMER_REVIEW_COUNT.strip()
        logger.notice('CUSTOMER_REVIEW_COUNT: ' + CUSTOMER_REVIEW_COUNT)
        list_of_customer_review_count.append(CUSTOMER_REVIEW_COUNT)

        # 22. promo_text
        regex = re.compile('.*coupon.*')
        search = soup.find_all("label", {"id": regex})

        # search_2 = soup.find_all("span", {"class": "a-size-medium-plus a-color-price aok-align-center centralizedApexPriceSavingsPercentageMargin centralizedApexPriceSavingsOverrides"})
        # #logger.info(f'print promo text search_2 {search_2}')
        # if len(search) == 0:
        #     search = search_2

        try:
            promo_text = str(
                search[0].get_text().replace('Terms', '').replace('"', '').rstrip())
        except IndexError:
            try:
                promo_text = str(
                    search[0].get_text().replace('"', '').strip())
            except:
                promo_text = ''

        if promo_text is '' and PRICE_SELL is '' and PRICE is '':
            promo_text = ''
        elif promo_text is '' and PRICE_SELL is not '':
            promo_text = float(
                f'{((float(PRICE_00.replace(",", "")) - float(PRICE_SELL_00.replace(",", ""))) / float(PRICE_00.replace(",", ""))) * 100}')
            promo_text = (
                (f'-{round(promo_text)}%').replace('--', '-').replace('Shop items', '').replace('|', '')).strip()
        else:
            promo_text = (promo_text.replace('--', '-').replace('Shop items', '').replace('|', '')).strip()

        logger.notice('Promo Text: ' + promo_text)
        list_of_promo_text.append(promo_text)

        # 21. SELLER_REVIEW_SCORE
        # try:
        #     search = soup.find_all("span", {"class": "black inline-flex ml1"})
        #     CUSTOMER_REVIEW_SCORE = str(search[0]).split('aria-label="')[1].split(',')[0][:3]
        # except IndexError:
        search = re.search('a-star[^\d]+([\d-]+)', str(soup))
        try:
            if search is not None:
                seller_REVIEW_SCORE = str(re.search('(\d[-\d]*)', str(search.group())).group()).replace('-', '.')
            else:
                seller_REVIEW_SCORE = ''
        except:
            seller_REVIEW_SCORE = ''

        logger.notice('seller_REVIEW_SCORE: ' + seller_REVIEW_SCORE)
        list_of_seller_rating.append(seller_REVIEW_SCORE)

        # 22. SELLER_REVIEW_COUNT
        search = soup.find_all("span", {"id": "seller-rating-count-{iter}"})
        try:
            if search[0] is not None:
                SELLER_REVIEW_COUNT = str(search[0].get_text().split(')')[0]).replace('ratings', '').replace('rating',
                                                                                                             '').replace(
                    ' s', '').replace('(',
                                      '').strip().replace(
                    'Just launched', '')
            else:
                SELLER_REVIEW_COUNT = ''
        except IndexError:
            try:
                SELLER_REVIEW_COUNT = str(
                    search[0].get_text().replace('ratings', '').replace('rating', '').replace(' s', '').replace(' ',
                                                                                                                '').replace(
                        ',', '')).replace('Just launched',
                                          '')
            except:
                SELLER_REVIEW_COUNT = ''
        if 'New Seller' in SELLER_REVIEW_COUNT:
            SELLER_REVIEW_COUNT = SELLER_REVIEW_COUNT.replace('New Seller', '').strip()
        else:
            SELLER_REVIEW_COUNT = SELLER_REVIEW_COUNT.strip()

        logger.notice('SELLER_REVIEW_COUNT: ' + SELLER_REVIEW_COUNT)
        ##list_of_seller_rating_count.append(SELLER_REVIEW_COUNT)

        SELLER_REVIEW_COUNT = re.sub(r'%\s*positive over[^>]+', '', SELLER_REVIEW_COUNT).strip()  ###3702  420
        list_of_seller_rating_count.append(
            ''.join(re.findall('[\d.,]+', str(SELLER_REVIEW_COUNT))).strip())  ###3702  420

        # 23. PERCENTAGE
        try:
            seller_percent = re.search('(\d+)',
                                       re.search('(?:<br/>\s*([\d]+)% |<br>\s*([\d]+)\% )', str(soup)).group()).group()
            seller_percent = seller_percent.replace('%', '')
        except:
            seller_percent = ''
        logger.notice('seller_percent: ' + seller_percent)

        if seller_percent == '0':  ### 3702  420
            seller_percent = ''
        else:
            pass

        list_of_percentage.append(str(seller_percent))

        try:
            seller_id = re.search('=([A-Za-z\d]+)', re.search('seller=\s*([^&]+)&', str(soup)).group()).group().replace(
                '=', '')
            seller_id = seller_id.replace('&', '')
        except:
            seller_id = ''
        logger.notice('seller_id: ' + seller_id)
        list_of_seller_id.append(str(seller_id))
        # timeframe
        try:
            print_n_log(re.search('over last ([\d months]+)', str(soup)).group())
            timeframe = re.search('(\d[\d months]+)',
                                  re.search('over last ([\d months]+)', str(soup)).group()).group().replace('=', '')
        except:
            timeframe = ''
        logger.notice('timeframe: ' + timeframe)
        list_of_timeframe.append(str(timeframe))

        # 23. QUANTITY
        try:
            qn_regex = re.search('(\d+)', re.search(
                '([\d,]+)\s*(?:-)?\s*Pack|([\d,]+)\s*(?:-)?\s*Pk|Set of ([\d,]+)|([\d,]+)\s*(?:-)?\s*ST-Set\s*(?:,|-)?\s*|([\d,]+)\s*(?:-)?\s*Set\s*(?:,|-)?\s*|([\d,]+)\s*(?:-)?\s*PR-Pair\s*(?:,|-)?\s*|([\d,]+)\s*(?:-)?\s*Pair\s*(?:,|-)?\s*|([\d,]+)\s*(?:-)?\s*bundle\s*(?:,|-)?\s*|Set/([\d,]+)',
                html).group()).group()
            QUANTITY = qn_regex.replace(',', '')
        except:
            QUANTITY = str(1)
        logger.notice('QUANTITY: ' + QUANTITY)
        list_of_quantity.append(str(QUANTITY))
        # CHECK IF MULTIPLE SELLERS
        xpath = '//*[text()="Next" and @href]'
        try:
            logger.notice(str(record_on_first_page) + ' total ' + str(record_total))
            logger.notice("MULTIPLE SELLERS")
            pageno = 2

            total_records = int(re.search('(\d+)', record_total).group())
            logger.info(f"total_records{total_records}")
            while (int(record_on_first_page) < int(re.search('(\d+)', record_total).group())):

                # while int(record_on_first_page) <= int(total_records):
                try:
                    # page.click(xpath[1], delay=7)
                    page.goto(inputs['URL'] + '&pageno=' + str(pageno), timeout=long_timeout)
                    logger.notice("Next Page")
                except:
                    page.goto(inputs['URL'] + '&pageno=' + str(pageno), timeout=long_timeout)
                record_on_first_page = int(record_on_first_page) + 10
                pageno = int(pageno) + 1
                # get the new html
                html2 = page.content()
                html = html + html2
                # print(html)
        except:
            logger.notice("ONE SELLER ONLY")
            # list_of_price.append(PRICE)
            # list_of_sold_by.append(SOLD_BY)
        soup = BeautifulSoup(html, "html.parser")
        soup_customer_count = soup  ###add update 11/16/2022

        # get extra prices
        listOfExtraPrices = []
        soup2 = soup.find_all("div", {"id": "aod-offer"})
        if len(soup2) == 0:
            soup2 = soup.find_all("span", {"id": "aod-offer"})
        # logger.info(f"soup2: {soup2}")
        logger.notice('LEN of Search1: ' + str(len(soup2)))
        for i in range(len(soup2)):
            ###if i > -1: #skip the first one so to not duplicate
            soup = soup2[i]
            soup_11 = soup2[i]
            append_to_lists(page, index, default_output_dir, inputs, location)
            search = soup_11.find_all("span", {"class": "a-offscreen"})
            search_122 = soup_11.find_all("span", {"class": "a-size-small a-color-secondary aok-align-center"})
            logger.info(f"search: {search}")
            logger.info(f"search_112: {search_122}")

            # PRICE = "No pricing information found at: " + str(page.url)
            priceInCart = ""
            # if len(add_to_cart_extract) >= 1 :
            try:
                # if 'price in cart' in str(search):
                if len(search) == 0 and len(search_122) == 0:
                    logger.notice("PRICE IS IN CART ALERT enter")
                    oid = re.findall('oid":"([^"]+)', str(soup_11))
                    oid = oid[0]
                    # logger.info(f'print  oid {oid}')
                    asin = re.findall('asin":"([^"]+)', str(soup_11))
                    asin = asin[0]
                    logger.info(f'print  asin {asin}')

                    try:
                        refTag = re.findall('refTag":"aod_dpdsk_new_([^"]+)', str(soup_11))
                        refTag_1 = str(refTag[0])
                        logger.info(f'print  refTag_1 {refTag_1}')
                    except:
                        refTag_1 = ''
                        logger.info(f'print except refTag_1 {refTag_1}')

                    url_add_cart_all_seller = (
                        f'https://www.amazon.com/dp/{str(asin)}/ref=olp-opf-redir?aod=1&ie=UTF8&condition=ALL')
                    page.goto(url_add_cart_all_seller, timeout=60000)
                    page.wait_for_timeout(7000)

                    # page.click('//span[@id="aod-filter-string"]')  # filter
                    # page.wait_for_timeout(1000)
                    # page.click('//span[@class="a-size-base a-color-base" and text()="New"]')  # New click
                    # page.wait_for_timeout(2000)

                    # click on second page 'multiple seller'
                    try:
                        second_page_x_path = '//div[@class="a-scroller a-scroller-vertical"]'
                        page.click(second_page_x_path)
                        page.wait_for_timeout(1000)
                    except:
                        pass

                    page.wait_for_timeout(2000)
                    refTag = str(refTag_1)
                    counter = 0  ##scrolling
                    for x in range(1, 5):
                        page.mouse.wheel(counter, 750 + counter)
                        page.wait_for_timeout(2000)
                        counter += 750
                    page.wait_for_timeout(5000)

                    add_to_card = f'//span[@id="a-autoid-2-offer-{str(refTag)}-announce" and contains(text(),"Add to Cart")]/parent::*/parent::*/parent::*//*[@id="a-autoid-2-offer-{str(refTag)}"]'
                    logger.info(f'print add_to_card {add_to_card} ----- &&& {page.is_visible(add_to_card)}')
                    # click add to card button
                    # page.pause()
                    try:
                        page.locator(add_to_card).click()
                        page.click(add_to_card, timeout=4000)
                    except:
                        page.locator(add_to_card)
                    page.wait_for_timeout(4000)
                    keywords_py.save_screenshot(page=page, file_name='add_to_cart_click.png')

                    # click view  button
                    direct_view_card_url = 'https://www.amazon.com/gp/cart/view.html?ref_=nav_cart'
                    view_card = f'//span[@id="aod-offer-view-cart-{str(refTag)}-announce" and contains(text()," View Cart ")]/parent::*/parent::*/parent::*'
                    if page.is_visible(view_card):
                        page.locator(view_card).click()
                        page.wait_for_timeout(8000)
                        logger.info('print view_card')
                    else:
                        page.goto(direct_view_card_url, timeout=5000)
                        page.wait_for_timeout(7000)
                        logger.info('print direct_view_card_url')

                    resp1 = page.content()
                    resp_22 = resp1.encode('ascii', 'ignore').decode('utf-8')
                    if 'Your Amazon Cart is empty' in resp_22:
                        print_message_1 = 'Your Amazon Cart is empty'
                        raise Exception(print_message_1)

                    # logger.info(f'print resp_22 {resp_22}')
                    pt = ParsingTools(resp_22)
                    keywords_py.save_screenshot(page=page, file_name='add_to_cart.png')
                    priceInCart = ', '.join(pt.get_elements_by_xpath(
                        '//span[@class="a-size-medium a-color-base sc-price sc-white-space-nowrap sc-product-price a-text-bold"]/text()'))
                    if priceInCart is '':
                        priceInCart = re.findall(
                            '<span id="sc-subtotal-amount-buybox"\s*class="[^"]+">&nbsp;<span class="[^"]+">([^<]+)<\/span><\/span>',
                            str(resp_22))[0]
                        priceInCart = ''.join(priceInCart)
                        logger.info(f'priceInCart_Extraction {priceInCart}')
                    priceInCart = priceInCart.replace("$", "")
                    logger.info(f'print priceInCart {priceInCart}')
                    list_of_price_cart.append(priceInCart)
                    PRICE = ""
                    PRICE_SELL = ""

                    # remove card price in card
                    remove_card_price = '//input[@value="Delete"]'
                    page.locator(remove_card_price).click()
                    page.wait_for_timeout(2000)

                ###### #### ##### #############################33
                else:
                    list_of_price_cart.append("")
                    price = search[0].get_text()
                    PRICE = str(price.split('$')[1])
                    PRICE_SELL = ''

                    try:
                        if 'class="a-size-small a-color-secondary aok-align-center">' in str(soup_11):

                            try:
                                PRICE_SELL = search_122[0].get_text()  ## update 19-06-2023
                                PRICE_SELL = str(PRICE_SELL).strip()
                                # logger.info(f'print search[3].get_text() PRICE_SELL22 {PRICE_SELL}')
                                PRICE_SELL = str(PRICE_SELL.split('$')[1])  ## update 19-06-2023
                                logger.info(f'print search[1].get_text() PRICE_SELL 22 {PRICE_SELL}')

                            except:
                                PRICE_SELL = search[1].get_text()  ## update 19-06-2023
                                PRICE_SELL = str(PRICE_SELL).strip()
                                # logger.info(f'print search[2].get_text() PRICE_SELL {PRICE_SELL}')
                                PRICE_SELL = str(PRICE_SELL.split('$')[1])  ## update 19-06-2023
                                logger.info(f'print search[1].get_text() PRICE_SELL 22 {PRICE_SELL}')

                    except:
                        PRICE_SELL = ''

                PRICE_11 = PRICE.replace(",", "")
                PRICE_SELL_22 = PRICE_SELL.replace(",", "")

                logger.info(f'print else PRICE_11 {PRICE_11}')
                logger.info(f'print else price PRICE_SELL_22 {PRICE_SELL_22}')

            except:
                PRICE = ''
                PRICE_SELL = ''
                PRICE_11 = PRICE.replace(",", "")
                PRICE_SELL_22 = PRICE_SELL.replace(",", "")

                logger.info(f'print except PRICE_11 {PRICE_11}')
                logger.info(f'print except price PRICE_SELL_22 {PRICE_SELL_22}')

            try:
                if PRICE_11 is '' and PRICE_SELL_22 is '':
                    PRICE_0 = ''
                    PRICE_SELL_0 = ''
                elif PRICE_11 is '' and PRICE_SELL_22 != '':
                    PRICE_0 = PRICE_SELL_22
                    PRICE_SELL_0 = ''
                elif PRICE_11 != '' and PRICE_SELL_22 is '':
                    PRICE_0 = PRICE_11
                    PRICE_SELL_0 = ''
                elif float(PRICE_11) > float(PRICE_SELL_22):
                    PRICE_0 = PRICE_11
                    PRICE_SELL_0 = PRICE_SELL_22
                elif float(PRICE_11) < float(PRICE_SELL_22):
                    PRICE_1 = PRICE_11
                    PRICE_0 = PRICE_SELL_22
                    PRICE_SELL_0 = PRICE_1
                elif float(PRICE_11) == float(PRICE_SELL_22):
                    PRICE_0 = PRICE_11
                    PRICE_SELL_0 = ''
                else:
                    PRICE_0 = PRICE_11
                    PRICE_SELL_0 = PRICE_SELL_22
            except:
                pass

                logger.info('print except price and price sell 2')

            # try:
            logger.notice('PRICE_SELL_0 : ' + PRICE_SELL_0)
            list_of_price_sale.append(PRICE_SELL_0.replace(",", ""))
            logger.notice('PRICE_0 : ' + PRICE_0)
            list_of_price.append(PRICE_0.replace(",", ""))
            # except:
            #     pass
            # 4. UNIT_NUMBER
            UNIT_NUMBER = str(1)
            logger.notice('UNIT_NUMBER: ' + UNIT_NUMBER)
            list_of_unit_number.append(str(UNIT_NUMBER))
            # 23. QUANTITY
            logger.notice('QUANTITY: ' + QUANTITY)
            list_of_quantity.append(str(QUANTITY))
            # list_of_customer_review_score.append("")
            # list_of_customer_review_count.append("")
            # 6a. CURRENCY
            CURRENCY = 'CAD'
            logger.notice('CURRENCY: ' + CURRENCY)
            list_of_currency.append(CURRENCY)
            delivery_charge = '//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()[1]'
            # shipping_regex = re.compile('data-csa-c-delivery-price\s*=\s*"\s*([FREE\$\d.,]+)\s*"')
            # Changes for price shipping
            shipping = re.findall('data-csa-c-delivery-price\s*=\s*"\s*([FREE\$\d.,]+)\s*"', str(soup))

            ### start 3702 ## 666
            if len(shipping) == 0:
                shipping = re.findall('id="mir-layout-DELIVERY_BLOCK"[^<]+<[^<]+<[^<>]+>([^<]+)', str(soup))
            else:
                shipping = shipping

            ### end 3702 ## 666

            # 8. PRICE SHIPPING
            # shipping = soup.find(text=shipping_regex) #logic added above
            logger.notice(shipping)
            try:
                if shipping is None:
                    PRICE_SHIPPING = ""
                elif "Free shipping" in shipping:
                    PRICE_SHIPPING = str(0)
                elif "FREE delivery" in shipping:
                    PRICE_SHIPPING = str(0)
                elif "FREE" in shipping:
                    PRICE_SHIPPING = str(0)
                elif 'delivery-price="FREE"' in shipping:
                    PRICE_SHIPPING = str(0)

                elif "Free pickup" in shipping:
                    PRICE_SHIPPING = ""
                elif "out of stock" in shipping:
                    PRICE_SHIPPING = ""
                elif len(shipping) > 0:
                    PRICE_SHIPPING = shipping[0]
                else:
                    PRICE_SHIPPING = ''
                PRICE_SHIPPING = str(PRICE_SHIPPING)
                PRICE_SHIPPING = PRICE_SHIPPING.replace("$", "")
                PRICE_SHIPPING = PRICE_SHIPPING.replace(" shipping", "")
                PRICE_SHIPPING = PRICE_SHIPPING.replace(", ", "")
                try:
                    PRICE_SHIPPING = float(PRICE_SHIPPING)
                except:
                    PRICE_SHIPPING = None
                    pass
            except:
                PRICE_SHIPPING = ''

            logger.notice('PRICE_SHIPPING: ' + str(PRICE_SHIPPING))
            list_of_price_shipping.append(PRICE_SHIPPING)

            # 14. Availability
            AVAILABILITY = {}
            time_regex = re.search('data-csa-c-delivery-time="([^"]+)', str(soup))
            # 8. PRICE SHIPPING

            try:
                try:
                    estimated_delivery = re.search('"([^"]+)', time_regex.group()).group().replace('"', '').strip()
                    logger.notice(estimated_delivery)
                except:
                    estimated_delivery = ''
                estimated_delivery = estimated_delivery.replace("Want it faster? Add an address to see options", "")
                estimated_delivery = estimated_delivery.replace("Currently out of stock", "")

                search = soup.find_all("div", {"id": "aod-offer-shipsFrom"})
                search_unavailable = soup.find_all("div", {"id": "aod_ship_charge_row"})  ## 3702    420

                if search_unavailable is not None:  ## 3702    420
                    web_availability_unavailable = str(search_unavailable[0].get_text()).strip()  ## 3702    420

                # logger.notice(search)
                if search is not None:
                    web_availability = str(search[0].get_text()).replace("Ships from", "").strip()
                    # list_of_fulfilled_by.append(web_availability)
                    list_of_fulfilled_by.append(
                        re.sub(r'This item is shipped from[^>]+', '', web_availability).strip())  ##3702  66

                if 'out of stock' in web_availability:
                    web_availability = "Out of stock"
                elif 'currently unavailable' in web_availability_unavailable:  ##3702  66 20-01-23
                    web_availability = "Out of stock"
                elif web_availability is not None:
                    web_availability = 'In Stock'
                else:
                    web_availability = 'Out of stock'

                AVAILABILITY['WEB_AVAILABILITY'] = web_availability
                AVAILABILITY['STORE_AVAILABILITY'] = ''
                AVAILABILITY['ESTIMATED_DELIVERY'] = estimated_delivery
                AVAILABILITY = json.dumps(AVAILABILITY, separators=(',', ':'))
                # logger.notice(type(AVAILABILITY))
            except:
                AVAILABILITY = ''
            logger.notice(AVAILABILITY)
            list_of_availability.append(AVAILABILITY)
            logger.notice(f'print list_of_availability {list_of_availability}')
            # logger.notice(list_of_availability)
            # 23. PERCENTAGE
            try:
                seller_percent = re.search('(\d+)', re.search('(?:<br/>\s*([\d]+)% |<br>\s*"([\d]+)%)',
                                                              str(soup)).group()).group()
                seller_percent = seller_percent.replace('%', '')
            except:
                seller_percent = ''
            logger.notice('seller_percent: ' + seller_percent)

            if seller_percent == '0':  ### 3702  420
                seller_percent = ''
            else:
                pass

            list_of_percentage.append(str(seller_percent))

            # seller id
            try:
                seller_id = re.search('=([A-Za-z\d]+)',
                                      re.search('seller=\s*([^&]+)&', str(soup)).group()).group().replace('=', '')
                seller_id = seller_id.replace('&', '')
            except:
                seller_id = ''
            logger.notice('seller_id: ' + seller_id)
            list_of_seller_id.append(str(seller_id))

            # timeframe
            try:
                timeframe = re.search('(\d[\d months]+)',
                                      re.search('over last ([\d months]+)', str(soup)).group()).group().replace('=', '')
            except:
                timeframe = ''
            if timeframe == '':
                timeframe = re.findall('<br/>\d+.\s*\w+\s*over (\w+)</span> </span> </div>', str(soup))
                timeframe = ''.join(timeframe)
            else:
                pass
            logger.notice('timeframe: ' + timeframe)
            list_of_timeframe.append(str(timeframe))

            # 15. CONDITION
            search = soup.find_all("div", {"id": "aod-offer-heading"})
            try:
                condition = str(
                    search[0].get_text().replace('"', '').replace('}', '')).strip()
            except IndexError:
                try:
                    condition = str(
                        search[0].get_text().replace('"', '').replace('}', '')).strip()
                except:
                    condition = ''

            logger.notice('condition: ' + condition)
            list_of_condition.append(condition)

            # 16. SOLD_BY
            try:
                try:
                    search = soup.find_all("div", {"id": "aod-offer-soldBy"})
                    # logger.notice(search)

                    # ###   420   start
                    sold_by_remove_unwanted_source = str(search[0]).encode('ascii', 'ignore').decode('utf-8')  ###   420
                    SOLD_BY = ''.join(re.findall('aria-label="Opens a new page"[^>]+>([^<]+)',
                                                 str(sold_by_remove_unwanted_source)))  ###   420

                    if len(SOLD_BY) == 0:
                        SOLD_BY = \
                        search[0].find_all("div", {"class": "a-fixed-left-grid-col a-col-right"})[0].get_text().split(
                            '(')[0].replace('Just launched', '').replace('Terms',
                                                                         '').rstrip().lstrip()  # ###   420   end

                    SOLD_BY = SOLD_BY.encode('ascii', 'ignore').decode('utf-8')

                except IndexError:
                    try:
                        search = soup.find_all("div", {"id": "aod-offer-soldBy"})
                        SOLD_BY = search.get_text().split('Sold by')[1].split(' ')[0].split('(')[
                            0].rstrip().lstrip().replace('Just launched', '')
                        SOLD_BY = SOLD_BY.encode('ascii', 'ignore').decode('utf-8')
                    except:
                        SOLD_BY = ''
            except:
                SOLD_BY = ''
            if 'New Seller' in SOLD_BY:
                SOLD_BY = SOLD_BY.replace('New Seller', '').strip()
            else:
                SOLD_BY = SOLD_BY.strip()
            logger.notice('SOLD_BY: ' + SOLD_BY)
            list_of_sold_by.append(re.sub(r'\s*[\d.]+%[^>]+', '', str(SOLD_BY)).strip())  ## 3702  420

            SELLER_INDEX = int(SELLER_INDEX)
            SELLER_INDEX += 1
            list_of_seller_index.append(str(SELLER_INDEX))

            # 21. SELLER_REVIEW_SCORE
            # try:
            #     search = soup.find_all("span", {"class": "black inline-flex ml1"})
            #     CUSTOMER_REVIEW_SCORE = str(search[0]).split('aria-label="')[1].split(',')[0][:3]
            # except IndexError:
            search = re.search('a-star[^\d]+([\d-]+)', str(soup))
            try:
                if search is not None:
                    CUSTOMER_REVIEW_SCORE = str(re.search('(\d[-\d]*)', str(search.group())).group()).replace('-', '.')
                else:
                    CUSTOMER_REVIEW_SCORE = ''

            except:
                CUSTOMER_REVIEW_SCORE = ''

            logger.notice('CUSTOMER_REVIEW_SCORE: ' + CUSTOMER_REVIEW_SCORE)
            list_of_seller_rating.append(CUSTOMER_REVIEW_SCORE)
            # 22. promo_text
            regex = re.compile('.*coupon.*')
            search = soup.find_all("label", {"id": regex})
            # search_2 = soup.find_all("span", {"class": "a-size-medium-plus a-color-price aok-align-center centralizedApexPriceSavingsPercentageMargin centralizedApexPriceSavingsOverrides"})
            #
            # if len(search) == 0:
            #     search = search_2
            try:
                promo_text = str(
                    search[0].get_text().replace('"', '').strip())
            except IndexError:
                try:
                    promo_text = str(
                        search[0].get_text().replace('"', '').strip())
                except IndexError:
                    promo_text = ''

            try:
                if promo_text is '' and PRICE_SELL_0 is '' and PRICE_0 is '':
                    promo_text = ''
                elif promo_text is '' and PRICE_SELL_0 is not '':
                    promo_text = float(
                        f'{((float(PRICE_0.replace(",", "")) - float(PRICE_SELL_0.replace(",", ""))) / float(PRICE_0.replace(",", ""))) * 100}')
                    promo_text = ((f'-{round(promo_text)}%').replace('--', '-').replace('Shop items', '').replace('|',
                                                                                                                  '')).strip()
                else:
                    promo_text = (promo_text.replace('--', '-').replace('Shop items', '').replace('|', '')).strip()
            except:
                pass

            logger.notice('Promo Text: ' + promo_text)
            list_of_promo_text.append(promo_text)

            # 22. SELLER_REVIEW_COUNT
            search = soup.find_all("span", {"id": "seller-rating-count-{iter}"})
            try:
                if len(search) > 0:
                    CUSTOMER_REVIEW_COUNT = str(search[0].get_text().split(')')[0]).replace('ratings', '').replace(
                        'rating', '').replace(' s', '').replace('(', '').strip().replace('Just launched', '')
                else:
                    CUSTOMER_REVIEW_COUNT = ''
            except IndexError:
                try:
                    CUSTOMER_REVIEW_COUNT = str(
                        search[0].get_text().replace('ratings', '').replace('rating', '').replace(' ', '').replace(' s',
                                                                                                                   '').replace(
                            ',', '')).replace('Just launched', '')
                except:
                    CUSTOMER_REVIEW_COUNT = ''
            if 'New Seller' in CUSTOMER_REVIEW_COUNT:
                CUSTOMER_REVIEW_COUNT = CUSTOMER_REVIEW_COUNT.replace('New Seller', '').strip()
            else:
                CUSTOMER_REVIEW_COUNT = CUSTOMER_REVIEW_COUNT.strip()
            logger.notice(
                'CUSTOMER_REVIEW_COUNT: ' + str(inputs['input_id']).replace("_", ":") + '  ' + CUSTOMER_REVIEW_COUNT)

            CUSTOMER_REVIEW_COUNT_seller = re.sub(r'%\s*positive over[^>]+', '',
                                                  CUSTOMER_REVIEW_COUNT).strip()  ###3702  420
            ##list_of_seller_rating_count.append(CUSTOMER_REVIEW_COUNT)
            ##list_of_seller_rating_count.append(re.sub(r'%\s*positive over[^>]+', '', CUSTOMER_REVIEW_COUNT).strip())

            list_of_seller_rating_count.append(
                ''.join(re.findall('[\d.,]+', str(CUSTOMER_REVIEW_COUNT_seller))).strip())  ###3702  420

            # 21. CUSTOMER_REVIEW_SCORE   again    update
            # try:
            #     search = soup.find_all("span", {"class": "black inline-flex ml1"})
            #     CUSTOMER_REVIEW_SCORE = str(search[0]).split('aria-label="')[1].split(',')[0][:3]
            # except IndexError:
            search = re.search('class="a-icon a-icon-star(?:-mini)? a-star(?:-mini)?-([\d-]+)', str(sp))
            logger.info(f"print search score {search} ")
            try:
                if search is not None:
                    CUSTOMER_REVIEW_SCORE = str(re.search('(\d[-\d]*)', str(search.group())).group()).replace('-',
                                                                                                              '.')
                else:
                    CUSTOMER_REVIEW_SCORE = ''

                logger.notice('CUSTOMER_REVIEW_SCORE in try 22: ' + CUSTOMER_REVIEW_SCORE)

            except:
                CUSTOMER_REVIEW_SCORE = ''

                logger.notice('CUSTOMER_REVIEW_SCORE IndexError 22: ' + CUSTOMER_REVIEW_SCORE)
            list_of_customer_review_score.append(CUSTOMER_REVIEW_SCORE)

            # 22. CUSTOMER_REVIEW_COUNT   #again update

            search = soup_customer_count.find_all("span", {"id": "aod-asin-reviews-count-title"})
            # logger.info(f"print search count_2 {search} ")

            try:
                if len(search) > 0:
                    CUSTOMER_REVIEW_COUNT = str(
                        search[0].get_text().replace('ratings', '').replace('rating', '').replace(' s', '').replace(
                            'Justlaunched', '').replace(',', '')).strip()
                    logger.notice('CUSTOMER_REVIEW_COUNT in try 1 : ' + CUSTOMER_REVIEW_COUNT)
                else:
                    CUSTOMER_REVIEW_COUNT = ''


            except IndexError:
                try:
                    CUSTOMER_REVIEW_COUNT = str(
                        search[0].get_text().replace('ratings', '').replace('rating', '').replace(' s', '').replace(
                            'Justlaunched', '').replace(',', '')).strip()
                except:
                    CUSTOMER_REVIEW_COUNT = ''

            logger.notice('CUSTOMER_REVIEW_COUNT IndexError 1: ' + CUSTOMER_REVIEW_COUNT)
            list_of_customer_review_count.append(CUSTOMER_REVIEW_COUNT)
    df = write_to_csv(page, index, default_output_dir, inputs)
    return df


def append_to_lists(page, index, default_output_dir, inputs, location):
    # Others
    list_of_unit_price.append("")
    list_of_unit_measure.append("")
    list_of_price_coupon.append("")
    list_of_tax.append("")
    list_of_promo_date.append("")
    list_of_promo_offer.append("")
    list_of_promo_rebate.append("")
    # list_of_price_sale.append("")
    list_of_error_codes.append("")
    list_of_errors.append("")
    list_of_error_flag.append("")  ##  3702   66
    list_of_SNAPSHOT_URL.append("")  ## 3702 66

    # extras for raw.csv
    list_of_input_id.append(str(inputs['input_id']).replace("_", ":"))
    # list_of_ext_id.append(str(inputs['ext_id']))
    list_of_ext_id.append(str(inputs['ext_id']).replace('None', ''))
    list_of_location.append(str(location))
    list_of_site.append(str(inputs['site_code']))


def write_to_csv(page, index, default_output_dir, inputs):
    logger.notice("IN write_to_csv")
    logger.notice(len(list_of_input_id))
    logger.notice(len(list_of_ext_id))
    logger.notice(len(list_of_location))
    logger.notice(len(list_of_site))
    logger.notice(len(list_of_price))
    logger.notice(len(list_of_unit_price))
    logger.notice(len(list_of_unit_measure))
    logger.notice(len(list_of_unit_number))
    logger.notice(len(list_of_price_sale))
    logger.notice(len(list_of_price_coupon))
    logger.notice(len(list_of_currency))
    logger.notice(len(list_of_price_cart))
    logger.notice(len(list_of_price_shipping))
    logger.notice(len(list_of_tax))
    logger.notice(len(list_of_promo_text))
    logger.notice(len(list_of_promo_date))
    logger.notice(len(list_of_promo_offer))
    logger.notice(len(list_of_promo_rebate))
    logger.notice(len(list_of_availability))
    logger.notice(len(list_of_condition))
    logger.notice(len(list_of_sold_by))
    logger.notice(len(list_of_fulfilled_by))
    logger.notice(len(list_of_seller_rating))
    logger.notice(len(list_of_seller_rating_count))
    logger.notice(len(list_of_seller_index))
    logger.notice(len(list_of_customer_review_score))
    logger.notice(len(list_of_customer_review_count))
    logger.notice(len(list_of_quantity))
    logger.notice(len(list_of_error_codes))
    logger.notice(len(list_of_errors))
    logger.notice(len(list_of_error_flag))
    logger.notice(len(list_of_SNAPSHOT_URL))

    df = pd.DataFrame(list_of_input_id, columns=["INPUT_ID"])
    df['EXT_ID'] = pd.Series(list_of_ext_id)
    df['LOCATION'] = pd.Series('')  ##pd.Series(list_of_location)    ###3702
    df['SITE_CODE'] = pd.Series(list_of_site)
    df['PRICE'] = pd.Series(list_of_price)
    df['UNIT PRICE'] = pd.Series(list_of_unit_price)
    df['UNIT_OF_MEASURE'] = pd.Series(list_of_unit_measure)
    df['UNIT_NUMBER'] = pd.Series(list_of_unit_number)
    df['PRICE_SALE'] = pd.Series(list_of_price_sale)
    df['CURRENCY'] = pd.Series(list_of_currency)
    df['PRICE_CART'] = pd.Series(list_of_price_cart)
    # df['PRICE_SHIPPING'] = list_of_price_shipping
    df['PRICE_SHIPPING'] = pd.Series(
        [str(v).replace('0.0', '0').replace('None', '') for v in list_of_price_shipping])  ##add
    df['TAX'] = pd.Series(list_of_tax)
    # df['PROMO_TEXT'] = list_of_promo_text
    df['PROMO_TEXT'] = pd.Series(
        [v.replace('    Terms', '').replace('Terms', '').strip() for v in list_of_promo_text])  ##add
    df['PROMO_DATE'] = pd.Series(list_of_promo_date)
    df['PROMO_OFFER'] = pd.Series(list_of_promo_offer)
    df['PROMO_REBATE'] = pd.Series(list_of_promo_rebate)
    df['AVAILABILITY'] = pd.Series(list_of_availability)
    df['CONDITION'] = pd.Series(list_of_condition)
    df['SOLD_BY'] = pd.Series(list_of_sold_by)
    df['FULFILLED_BY'] = pd.Series(list_of_fulfilled_by)
    df['SELLER_RATING'] = pd.Series(list_of_seller_rating)  # all blanks
    df['SELLER_PERCENTAGE'] = pd.Series(list_of_percentage)
    df['SELLER_RATING_COUNT'] = pd.Series(list_of_seller_rating_count)
    df['SELLER_INDEX'] = pd.Series(list_of_seller_index)
    df['QUANTITY'] = pd.Series(list_of_quantity)
    df['SNAPSHOT_TEXT_1'] = pd.Series(list_of_timeframe)
    df['SNAPSHOT_TEXT_2'] = pd.Series('')  ##pd.Series(list_of_seller_id)   ###3702
    df['SNAPSHOT_TEXT_3'] = pd.Series(list_of_promo_rebate)  # all blanks
    df['PRICE_COUPON'] = pd.Series(list_of_promo_rebate)
    df['SNAPSHOT_TEXT_5'] = pd.Series(list_of_promo_rebate)  # all blanks
    df['MISCELLANEOUS'] = pd.Series(list_of_promo_rebate)  # all blanks
    # df['CUSTOMER_REVIEW_COUNT'] = list_of_customer_review_count
    df['CUSTOMER_REVIEW_COUNT'] = pd.Series([i for i in list_of_customer_review_count if i])  ##add new
    # df['CUSTOMER_REVIEW_SCORE'] = list_of_customer_review_score
    df['CUSTOMER_REVIEW_SCORE'] = pd.Series([i for i in list_of_customer_review_score if i])  ### add new
    df['ERROR_CODE'] = list_of_error_codes
    df['ERROR_MESSAGE'] = list_of_errors
    df['ERROR_FLAG'] = list_of_error_flag  ## 3702   666
    df['SNAPSHOT_URL'] = list_of_SNAPSHOT_URL  ##  3702  666
    df['SNAPSHOT_TEXT_2'].duplicated(keep='first')
    df = df[(df["CONDITION"] == "New") | (df["ERROR_MESSAGE"] != '')]
    logger.notice('Index is')
    logger.notice(df['INPUT_ID'])
    logger.notice(index)
    logger.notice("DF")
    logger.notice(df)
    # save raw.csv here
    file_path = default_output_dir.split('/debug')[0]
    file_path = file_path + '/raw.csv'
    df.to_csv(file_path, index=False, header=False, quoting=csv.QUOTE_ALL, quotechar='"')
    logger.notice("DONE WRITING TO CSV")
    return df


def run(global_variables):
    if 'script_config' in global_variables:
        global_variables["block_resources"] = block_resources  # Resource blocking added by Rye on 2/7/23
        logger = global_variables['logger']
        keywords_py = PlaywrightKeywords(global_variables)
        line_items = keywords_py.line_items
        settings = global_variables['settings']
        manifest = global_variables['manifest']['webql-field']
        settings = global_variables['settings']
        # keywords_py.settings.ip_address='23.226.40.246'
        # keywords_py.settings.mitm= False
        default_output_dir = settings.output_dir + '/debug'
        browser_url = settings.browser
        # my_logger.append(global_variables['logger'])
        line_item_count = len(line_items)

        with sync_playwright() as playwright:
            for index, line_item in enumerate(line_items):
                print_n_log(f"print index:{index} ")
                print_n_log(f"enter to mod condition:{index % 20}")
                mod_value = index % 20
                if index % 20 == 0:  # start new session on every 10th input and set the global state of the playwright objects to None
                    global home_page1
                    global home_page_browser1
                    global home_page_context1
                    home_page1 = None
                    home_page_context1 = None
                    home_page_browser1 = None
                # if browser_exception is not None:
                #     with sync_playwright() as playwright:
                #         scrap_web(line_item, playwright, keywords_py, settings, default_output_dir)
                # else:
                logger.notice("FULL QSCRAPE")
                scrap_web(line_item, playwright, keywords_py, settings, default_output_dir, mod_value, browser_url,
                          index)
                logger.notice("INDEX " + str(index) + " COMPLETE.")
            logger.notice("EXECUTION COMPLETELY FINISHED")

# $Id: amazon_ca_price.py 835106 2023-10-23 11:03:45Z rakesh_dhinwa $
