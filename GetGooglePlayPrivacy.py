import csv
import itertools
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import urllib3
from google_play_scraper import app
from selenium.common.exceptions import TimeoutException, WebDriverException

import GetCommon


def get_all_privacy_threaded():
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_THREADS) as executor:
        for batch in batch_iterator(app_info_datas, BATCH_SIZE):  # Process batch by batch
            list(executor.map(process_item, batch))  # Map ensures tasks complete in this batch

def batch_iterator(iterable, batch_size):
    """Yield items from iterable in chunks (batches) of batch_size."""
    iterator = iter(iterable)
    while batch := list(itertools.islice(iterator, batch_size)):
        yield batch

def process_item(item):
    with driver_lock:  # Ensure thread-safe access to the driver
        get_app_details(item)

def get_app_details(app_id):
    print(f"enter get_app_details app_id: {app_id}")
    results = {}

    try:
        result = app(app_id, lang="en", country="us")  # 你可以修改语言和国家
        results = {
            "title": result.get("title"),
            "app_id": app_id,
            "installs": result.get("installs"),
            "score": result.get("score"),
            "ratings": result.get("ratings"),
            "reviews": result.get("reviews"),
            "privacyPolicy": result.get("privacyPolicy"),
            "developerEmail": result.get("developerEmail"),
            "developerWebsite": result.get("developerWebsite"),
            "app_url": f"https://play.google.com/store/apps/datasafety?id={app_id}&hl=en"
        }
        policy_url = results["privacyPolicy"]

        if policy_url:

            try:
                driver.set_page_load_timeout(20)
                driver.get(policy_url)

                time.sleep(limit_time)
                try:
                    privacy_data = GetCommon.get_privacy_original(driver.page_source)

                    if privacy_data != "":
                        # 重新获取 <a> 标签，防止 stale element
                        try:
                            # 🔥 获取可见的 "privacy" 链接
                            visible_privacy_links = GetCommon.get_visible_privacy_links(driver)

                            if len(visible_privacy_links) != 0:
                                try:
                                    filtered_urls = GetCommon.filter_urls(visible_privacy_links, policy_url)

                                    if len(filtered_urls) != 0:
                                        try:
                                            privacy_data, results = GetCommon.wait_extra_privacy(results, privacy_data,filtered_urls, driver,logger)

                                            with open(f"Policy_google/{app_id}_policy", "w", encoding="utf-8") as f:
                                                f.write(privacy_data)
                                            logger.warning((json.dumps(results, ensure_ascii=False)))
                                            print("successful!")

                                        except TimeoutException:
                                            print("TimeoutException")
                                            logger.error(f"TimeoutException:{(json.dumps(results, ensure_ascii=False))}")
                                            return
                                        except Exception as e:
                                            logger.error(
                                                f"wait_extra_privacy: {(json.dumps(results, ensure_ascii=False))}----{e}")
                                            return
                                    else:
                                        logger.warning((json.dumps(results, ensure_ascii=False)))
                                        with open(f"Policy_google/{app_id}_policy", "w", encoding="utf-8") as f:
                                            f.write(privacy_data)
                                        print("successful!")
                                        return

                                except Exception as e:
                                    logger.error(
                                        f"filter_urls: {(json.dumps(results, ensure_ascii=False))}----{e}")
                                    return

                            else:
                                logger.warning((json.dumps(results, ensure_ascii=False)))
                                with open(f"Policy_google/{app_id}_policy", "w", encoding="utf-8") as f:
                                    f.write(privacy_data)
                                print("successful!")
                                return

                        except Exception as e:
                            logger.error(f"visible_privacy_links: {(json.dumps(results, ensure_ascii=False))}----{e}")
                            return
                    else:
                        logger.error(f"privacy_data is null results:{(json.dumps(results, ensure_ascii=False))}")
                        print("privacy_data is null")
                        return

                except Exception as e:
                    logger.error(f"get_privacy_original: {(json.dumps(results, ensure_ascii=False))}----{e}")
                    return

            except Exception as e:
                logger.error(f"enter wrong privacy_url: {(json.dumps(results, ensure_ascii=False))}----{e}")
                return
        else:
            logger.error(f"get wrong privacy_url: {(json.dumps(results, ensure_ascii=False))}")
            return

    except Exception as e:
        logger.error(f"get wrong results: {app_id}----{e}")
        return

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
                GetCommon.save_add_json_file(r"AppInfo_google\empty_privacy_url.json",app_id)

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
                                    with open(f"Policy_google/{app_id}_policy", "w", encoding="utf-8") as f:
                                        f.write(privacy_data)
                                    print("successful!")
                                except Exception as e:
                                    logger.error(f"wait_extra_privacy: {(json.dumps(results, ensure_ascii=False))}")
                                    continue
                    else:
                        driver.get(privacy_url)
                        privacy_data = GetCommon.get_privacy_original(driver.page_source)
                        with open(f"Policy_google/{app_id}_policy", "w", encoding="utf-8") as f:
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
    MAX_CONCURRENT_THREADS = 20  # Limit concurrent threads
    BATCH_SIZE = 200  # Control how many items to load into memory at a time
    limit_time = 1

    logger = GetCommon.getLogger("GooglePlayPrivacyLoop5")
    # app_info_datas = GetCommon.get_app_info(r"AppInfo_google\loop4\error_appId_privacy_error_more_links.json")
    app_info_datas=[]
    driver_lock = threading.Lock()
    driver = GetCommon.setup_driver()
    # handel_all_sub_privacy(r"data_csv\google_appInfo_49.csv")

    handel_diff_sub_privacy(r"AppInfo_google\diff_sub_privacy_url_1.json")
    # get_all_privacy_threaded()
    driver.quit()