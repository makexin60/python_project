import itertools
import threading
from concurrent.futures import ThreadPoolExecutor

import urllib3
from selenium.common import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import GetCommon


def get_structure_data(url):
    # 存储解析结果
    result = []

    try:
        # 查找所有 class="Mf2Txd" 的 div 大模块
        parent_divs = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "Mf2Txd"))
        )

        if parent_divs:
            # 遍历每个父级 div
            for parent in parent_divs:
                try:
                    # 获取 h2 标签 title Data shared
                    h2_element = parent.find_element(By.TAG_NAME, "h2").text if parent.find_elements(By.TAG_NAME,
                                                                                              "h2") else None

                    # 获取子元素 class="ivTO9c" title Data shared 后面跟着的解释
                    ivTO9c_div = parent.find_element(By.CLASS_NAME, "ivTO9c").text if parent.find_elements(By.CLASS_NAME,
                                                                                                           "ivTO9c") else None
                    title = h2_element if h2_element else ""
                    if ivTO9c_div:
                        title += f" ( {ivTO9c_div} )"

                    # **处理特殊情况：Security practices**
                    if h2_element == "Security practices":
                        security_practices = []

                        # 获取所有 h3 标签（标题）
                        h3_elements = parent.find_elements(By.TAG_NAME, "h3")
                        h3_texts = [h3.text for h3 in h3_elements]

                        # 获取所有 class="fozKzd" 的 div（内容）
                        fozKzd_elements = parent.find_elements(By.CLASS_NAME, "fozKzd")
                        fozKzd_texts = [fz.text for fz in fozKzd_elements]

                        # 确保 h3 和 fozKzd 数量一致
                        if len(h3_texts) == len(fozKzd_texts):
                            security_practices = [{key: value} for key, value in zip(h3_texts, fozKzd_texts)]

                        result.append({
                            "Security practices": security_practices
                        })
                        continue  # ⚠️ 跳过后续处理，进入下一个 parent

                    else:
                        # 查找 `jscontroller="ojPjfd"` 的 div（确保它在当前 `parent` 里）详情
                        ojPjfd_divs = parent.find_elements(By.XPATH, ".//div[@jscontroller='ojPjfd']")

                        details = []
                        # 遍历所有 `jscontroller="ojPjfd"` 作为新父级
                        for ojPjfd_div in ojPjfd_divs:

                            # 子元素 详情内容 Personal info
                            h3_element = ojPjfd_div.find_element(By.TAG_NAME, "h3").text if ojPjfd_div.find_elements(
                                By.TAG_NAME, "h3") else "Unknown"

                            #Name, Email address, User IDs, Address, Phone number, and Other info
                            h3_content = ojPjfd_div.find_element(By.CLASS_NAME,
                                                                    "fozKzd").text if ojPjfd_div.find_elements(
                                By.CLASS_NAME, "fozKzd") else "Unknown"

                            # 详细解释标题
                            ZirXzb = ojPjfd_div.find_element(By.CLASS_NAME,
                                                            "ZirXzb").text if ojPjfd_div.find_elements(
                                By.CLASS_NAME, "ZirXzb") else None

                            # 查找 `jscontroller="ojPjfd"` 的 div（确保它在当前 `parent` 里）详情
                            GcNQi = ojPjfd_div.find_elements(By.CLASS_NAME, "GcNQi")

                            big_details_exp = []  # 存储最终 JSON 结果的列表

                            for GcNQi_div in GcNQi:
                                h4_elements = [h4.text for h4 in GcNQi_div.find_elements(By.TAG_NAME, "h4")]
                                FnWDnes = [fn.text for fn in GcNQi_div.find_elements(By.CLASS_NAME, "FnWDne")]

                                if len(h4_elements) == len(FnWDnes):
                                    json_obj = {key: value for key, value in zip(h4_elements, FnWDnes)}  # 直接组合成字典
                                    big_details_exp.append(json_obj)  # 追加到最终数组

                            details.append({
                                h3_element: h3_content,
                                ZirXzb: big_details_exp
                            })

                        result.append({
                            title:details
                        })

                except Exception as e:
                    print(f"解析错误: {e}")
                    logger.error(f"解析错误:{url} Exception: {e}")
        else:
            print(f"class='Mf2Txd' 的 div 大模块 获取失败:{url}")
            logger.error(f"class='Mf2Txd' 的 div 大模块 获取失败:{url}")

    except urllib3.exceptions.ReadTimeoutError as e:
        logger.error(f"ReadTimeoutError: url: {url} Exception: {e}")
        print(f"ReadTimeoutError occurred, skipping url: {url}")

    except Exception as e:
        print(f"class='Mf2Txd' 的 div 大模块 获取失败:{url}---- {e}")
        logger.error(f"class='Mf2Txd' 的 div 大模块 获取失败:{url}---- {e}")

    logger.warning(url)
    print(f"result: {result}")
    return result

def get_data_safety(app_id):
    print(f"enter get_data_safety {app_id}")
    url = f"https://play.google.com/store/apps/datasafety?id={app_id}&hl=en"
    driver.get(url)

    wait_open_i()

    parsed_data = get_structure_data(url)

    GetCommon.save_new_json_file(f"Label_google/{app_id}_label.json",parsed_data)

    print("successful!")

def wait_open_i():
    print("enter wait_open_i")

    try:
        # **等待 'expand_more' 的 <i> 标签出现**
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//i[text()='expand_more']"))
        )

        if element:
            print("Found 'expand_more', performing actions...")

            # **查找所有 'expand_more' 的 <i> 标签**
            expand_more_icons = driver.find_elements(By.XPATH, "//i[text()='expand_more']")

            for icon in expand_more_icons:
                try:
                    # **滚动到元素**
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", icon)

                    # **使用 JavaScript 强制点击**
                    driver.execute_script("arguments[0].click();", icon)

                except ElementClickInterceptedException:
                    print("ElementClickInterceptedException: 其他元素遮挡，使用 JS 点击失败")

                except Exception as e:
                    print(f"Error clicking 'expand_more': {e}")

    except TimeoutException:
        print("TimeoutException wait_open_i: 找不到 'expand_more' 按钮")

    except Exception as e:
        print("Error wait_open_i:", e)

    print("leave wait_open_i")

def process_item(item):
    with driver_lock:  # Ensure thread-safe access to the driver
        get_data_safety(item)  # Pass the shared driver

def batch_iterator(iterable, batch_size):
    """Yield items from iterable in chunks (batches) of batch_size."""
    iterator = iter(iterable)
    while batch := list(itertools.islice(iterator, batch_size)):
        yield batch

def get_all_privacy_threaded():
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_THREADS) as executor:
        for batch in batch_iterator(app_info_datas, BATCH_SIZE):  # Process batch by batch
            list(executor.map(process_item, batch))  # Map ensures tasks complete in this batch

if __name__ == "__main__":
    logger = GetCommon.getLogger("GooglePlayLabel")

    app_info_datas = GetCommon.get_app_info(f"AppInfo_google/appInfo_google_new_28.json")

    MAX_CONCURRENT_THREADS = 20  # Limit concurrent threads
    BATCH_SIZE = 200  # Control how many items to load into memory at a time
    # Global driver instance (must be accessed in a thread-safe way)
    driver_lock = threading.Lock()
    driver = GetCommon.setup_driver()  # Or any other browser
    # Call the function
    get_all_privacy_threaded()
    driver.quit()