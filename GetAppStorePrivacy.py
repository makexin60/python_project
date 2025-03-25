import csv
import itertools
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import urllib3
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import GetCommon


def get_privacy():
    # 遍历 data 数组中的每个字典对象
    for item in app_info_datas:
        get_all_privacy(item["url"],item["id"],item["name"])
        print("successful!")

def find_privacy_cards(app_url,json_url):

    try:
        driver.set_page_load_timeout(10)  # 限制为 10 秒
        # Open the App Store page
        driver.get(app_url)

        # 等待隐私卡片的出现（以类名为 app-privacy__cards 的元素为例）
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "app-privacy__cards"))
        )
        # 滚动页面，确保卡片加载
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # time.sleep(time_limit)  # 等待内容加载

        # 继续滚动页面，直到找到隐私卡片
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(time_limit)  # 等待卡片出现

        # 获取页面源代码并解析
        source = driver.page_source
        soup = BeautifulSoup(source, "html.parser")

        # 查找包含隐私卡片的部分
        privacy_cards = soup.find_all("div", class_="app-privacy__cards")

        print("leave find_privacy_cards")
        return privacy_cards

    except TimeoutException:
        logger.error(f"error find_privacy_cards: {(json.dumps(json_url, ensure_ascii=False))}")
        print(f"❌ 访问 {json_url} 超时，跳过！")
        return None

    except Exception as e:
        logger.error(f"error find_privacy_cards: {(json.dumps(json_url, ensure_ascii=False))}")
        print(f"error find_privacy_cards: {e}")
        return None


def click_developer_privacy(json_url):
    print("enter click_developer_privacy")

    try:
        # 等待按钮变为可点击
        button = WebDriverWait(driver, 17).until(
            EC.element_to_be_clickable((By.XPATH, "//a[text()='developer’s privacy policy']"))
        )

        # 滚动到按钮位置
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(time_limit)  # 短暂等待滚动完成

        # 确保按钮可见并点击
        if button.is_displayed():
            driver.execute_script("arguments[0].click();", button)
            print(f"Button 'developer’s privacy policy' clicked")

            time.sleep(time_limit)  # 等待卡片出现
            original_url = driver.current_url

            print(f"leave click_developer_privacy json_url{(json.dumps(json_url, ensure_ascii=False))}")
            return original_url

        else:
            logger.error(f"Error click_developer_privacy json_url: {(json.dumps(json_url, ensure_ascii=False))}")
            return None

    except TimeoutException as e:
        logger.error(f"Error click_developer_privacy json_url: {(json.dumps(json_url, ensure_ascii=False))}")
        return None

    except Exception as e:
        logger.error(f"Error click_developer_privacy json_url: {(json.dumps(json_url, ensure_ascii=False))}")
        return None

def get_all_privacy(app_url,app_id,app_name):
    print(f"enter get_all_privacy app_url:{app_url}")
    json_url = {
        "id": app_id,
        "name":app_name,
        "app_url": app_url
    }

    privacy_cards = find_privacy_cards(app_url,json_url)
    if privacy_cards:

        original_url = click_developer_privacy(json_url)
        if original_url:
            try:
                json_url = {
                    "id": app_id,
                    "name": app_name,
                    "app_url": app_url,
                    "privacy_url": original_url
                }

                if app_id == 284882215:
                    GetCommon.wait_span_highlights("//span[text()='Highlights']",driver)

                page_source = driver.page_source
                privacy_data = GetCommon.get_privacy_original(page_source)

                # **如果有数据，执行 A 标签查找**
                if privacy_data != "":

                    if app_id != 284882215 and app_id != 389801252:
                        try:

                            visible_privacy_links = GetCommon.get_visible_privacy_links(driver)

                            if len(visible_privacy_links) != 0:
                                filtered_urls = GetCommon.filter_urls(visible_privacy_links, original_url)

                                if len(filtered_urls) != 0:
                                    privacy_data, results = GetCommon.wait_extra_privacy(json_url, privacy_data, filtered_urls,driver,logger)
                            else:
                                print(" no find extra <a>")

                            logger.warning(json.dumps(json_url, ensure_ascii=False))
                            GetCommon.save_new_txt_file(f"Policy_appstore/{app_id}_policy",privacy_data)
                            return

                        except TimeoutException:
                            logger.warning(json.dumps(json_url, ensure_ascii=False))
                            GetCommon.save_new_txt_file(f"Policy_appstore/{app_id}_policy",privacy_data)
                            return

                        except Exception as e:
                            logger.error((json.dumps(json_url, ensure_ascii=False)))
                            print(e)
                            return

                    else:
                        GetCommon.save_new_txt_file(f"Policy_appstore/{app_id}_policy", privacy_data)
                        logger.warning((json.dumps(json_url, ensure_ascii=False)))
                        return

                else:
                    logger.error(f"privacy_data is null {(json.dumps(json_url, ensure_ascii=False))}")
                    return

            except urllib3.exceptions.ReadTimeoutError as e:
                logger.error((json.dumps(json_url, ensure_ascii=False)))
                print(f"urllib3.exceptions.ReadTimeoutError exception: {e}")

            except Exception as e:
                logger.error((json.dumps(json_url, ensure_ascii=False)))
                print(f"waiting for the privacy section exception: {e}")
        else:
            return
    else:
        return


def process_item(item):
    with driver_lock:  # Ensure thread-safe access to the driver
        get_all_privacy(item["url"], item["id"], item["name"])  # Pass the shared driver

def batch_iterator(iterable, batch_size):
    """Yield items from iterable in chunks (batches) of batch_size."""
    iterator = iter(iterable)
    while batch := list(itertools.islice(iterator, batch_size)):
        yield batch

def get_all_privacy_threaded():
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_THREADS) as executor:
        for batch in batch_iterator(app_info_datas, BATCH_SIZE):  # Process batch by batch
            list(executor.map(process_item, batch))  # Map ensures tasks complete in this batch


def handel_all_sub_privacy(original_path):
    with open(original_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            app_id = row["app_id"]
            original_url = row["privacy_url"]

            json_url = {
                "id": app_id,
                "privacy_url": original_url
            }
            print(json_url)
            logger.warning(json.dumps(json_url, ensure_ascii=False))
            if original_url:
                try:
                    driver.get(original_url)
                    if app_id != 284882215 and app_id != 389801252:
                        try:
                            visible_privacy_links = GetCommon.get_visible_privacy_links(driver)

                            if len(visible_privacy_links) != 0:
                                filtered_urls = GetCommon.filter_urls(visible_privacy_links, original_url)

                                if len(filtered_urls) != 0:
                                    json_url = {
                                        "id": app_id,
                                        "privacy_url": original_url,
                                        "sub-section_urls": filtered_urls
                                    }
                                    logger.warning(json.dumps(json_url, ensure_ascii=False))
                                else:
                                    logger.warning(json.dumps(json_url, ensure_ascii=False))
                            else:
                                print(" no find extra <a>")
                                logger.warning(json.dumps(json_url, ensure_ascii=False))

                        except TimeoutException:
                            logger.warning(json.dumps(json_url, ensure_ascii=False))

                        except Exception as e:
                            logger.error((json.dumps(json_url, ensure_ascii=False)))
                            print(e)
                    else:
                        logger.warning((json.dumps(json_url, ensure_ascii=False)))

                except urllib3.exceptions.ReadTimeoutError as e:
                    logger.error((json.dumps(json_url, ensure_ascii=False)))
                    print(f"urllib3.exceptions.ReadTimeoutError exception: {e}")

                except Exception as e:
                    logger.error((json.dumps(json_url, ensure_ascii=False)))
                    print(f"waiting for the privacy section exception: {e}")
            else:
                GetCommon.save_add_json_file(r"AppInfo_appstore\empty_privacy_url.json", app_id)

def handel_diff_sub_privacy(param):
    results=[]
    try:
        with open(param, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for entry in data:
            app_id = entry.get("id")
            privacy_url = entry.get("privacy_url")
            new_sub_privacy_url = entry.get("new_sub_privacy_url", None)

            results = {
                "app_id": app_id,
                "privacy_url": privacy_url
            }
            print(results)
            if privacy_url:
                try:
                    if new_sub_privacy_url:
                        # Convert string representation of list to actual list
                        new_sub_privacy_url_list = json.loads(new_sub_privacy_url) if new_sub_privacy_url else []
                        driver.set_page_load_timeout(10)
                        driver.get(privacy_url)
                        privacy_data = GetCommon.get_privacy_original(driver.page_source)
                        if privacy_data != "":
                            if len(new_sub_privacy_url_list) !=0:
                                print(f"Visiting URL: {new_sub_privacy_url_list}")
                                try:
                                    privacy_data, results = GetCommon.wait_extra_privacy(results, privacy_data,new_sub_privacy_url_list, driver,logger)
                                    with open(f"Policy_appstore/{app_id}_policy", "w", encoding="utf-8") as f:
                                        f.write(privacy_data)
                                    print("successful!")
                                except Exception as e:
                                    logger.error(f"wait_extra_privacy: {(json.dumps(results, ensure_ascii=False))}")
                                    continue
                    else:
                        driver.get(privacy_url)
                        privacy_data = GetCommon.get_privacy_original(driver.page_source)
                        with open(f"Policy_appstore/{app_id}_policy", "w", encoding="utf-8") as f:
                            f.write(privacy_data)
                        print("successful!")
                except TimeoutException as e:
                    print(f"[TimeoutException] App: {app_id} 页面加载超时: {e}")
                    logger.error(f"[TimeoutException] {app_id}: {json.dumps(results, ensure_ascii=False)}")
                    continue
                except WebDriverException as e:
                    print(f"[WebDriverException] App: {app_id} 页面渲染异常: {e}")
                    logger.error(f"[WebDriverException] {app_id}: {json.dumps(results, ensure_ascii=False)}")
                    continue
                except Exception as e:
                    print(f"[General Exception] App: {app_id} 加载页面失败: {e}")
                    logger.error((json.dumps(results, ensure_ascii=False)))
                    continue
    except Exception as e:
        print(f"Error occurred: {e}")
        logger.error({(json.dumps(results, ensure_ascii=False))})

if __name__ == "__main__":

    country = "ie"  # Ireland, change as needed
    time_limit = 1

    logger = GetCommon.getLogger("AppStorePrivacyLoop5")
    # app_info_datas = GetCommon.get_app_info(f"AppInfo_appstore/error_appInfo_privacy_1.json")
    app_info_datas=[]

    MAX_CONCURRENT_THREADS = 10  # Limit concurrent threads
    BATCH_SIZE = 200  # Control how many items to load into memory at a time
    # Global driver instance (must be accessed in a thread-safe way)
    driver_lock = threading.Lock()
    driver = GetCommon.setup_driver()  # Or any other browser

    handel_diff_sub_privacy(r"AppInfo_appstore\diff_sub_privacy_url_4.json")

    # Call the function
    # get_all_privacy_threaded()
    # Quit driver after all tasks are done
    driver.quit()
