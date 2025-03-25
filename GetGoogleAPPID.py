import threading
import time

import google_play_scraper
from bs4 import BeautifulSoup
from selenium.common import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import GetCommon


def get_app_id_method1():
    print("enter get_app_id_method1")
    base_url = "https://play.google.com/store/apps/category/{}?hl=en&gl=us"
    tem_app_ids = set()

    for category in categories_new:
        url = base_url.format(category)
        try:
            app_ids = GetCommon.scrape_category_click(url,driver)
            tem_app_ids.update(app_ids)  # 去重

        except Exception as e:
            # **其他异常打印错误并抛出**
            print("Error", e)
            logger.error(url)
            continue

    print(f"Num tem1_app_ids: {len(tem_app_ids)}")
    GetCommon.save_add_json_file(appinfo_original_path, list(tem_app_ids))

def get_app_id_method2():
    print("enter get_app_id_method2")

    # 用于去重的集合
    seen_app_ids = set()
    # 存储所有结果
    all_results = []

    # 分批次搜索
    for keyword in categories_new:
        print(f"Searching for: {keyword}")

        try:
            # 获取搜索结果
            result = google_play_scraper.search(
                query=keyword,  # 搜索关键词
                lang="en",  # 语言
                country="us",  # 国家
                n_hits=250  # 每次获取250条数据
            )

            print(f"length:{len(result)}")

            # 过滤重复的APP
            for app in result:
                app_id = app["appId"]
                if app_id not in seen_app_ids:
                    seen_app_ids.add(app_id)
                    all_results.append(app["appId"])

            # 添加延迟，避免触发反爬虫机制
            time.sleep(2)  # 每次请求后休眠2秒

        except Exception as e:
            # **其他异常打印错误并抛出**
            print("Error", e)
            logger.error(keyword)
            continue

    print(f"Num tem2_app_ids: {len(all_results)}")
    GetCommon.save_add_json_file(appinfo_original_path, list(all_results))

def get_app_id_method3():
    print("enter get_app_id_method3")

    base_url = "https://play.google.com/store/search?q={}&c=apps&hl=en&gl=US"
    tem_app_ids = set()

    for category in categories_new:
        url = base_url.format(category)
        try:
            app_ids = GetCommon.scrape_category_no_click(url,driver)
            if app_ids:
                tem_app_ids.update(app_ids)  # 去重
        except Exception as e:
            # **其他异常打印错误并抛出**
            print("Error", e)
            logger.error(url)
            continue

    print(f"Num tem3_app_ids: {len(tem_app_ids)}")
    # 保存到 JSON 文件
    GetCommon.save_add_json_file(appinfo_original_path, list(tem_app_ids))

def get_app_id_method4():
    print("enter get_app_id_method4")

    base_url = "https://play.google.com/store/apps/details?id={}&hl=en&gl=US"
    # https: // play.google.com / store / apps / details?id = com.NICMIT.StrategicDriver & hl = en & gl = US
    a_array= ["See more information on About this app","See more information on Data safety","See more information on Ratings and reviews"]

    for app_info in appinfo_all:
        url = base_url.format(app_info)
        try:
            print(f"enter url:{url}")
            driver.get(url)

            # 等待 a 标签出现，匹配 aria-label 以 "See more information" 开头
            see_more_links = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, '//a[starts-with(@aria-label, "See more information on ")]'))
            )

            hrefs = []
            if len(see_more_links)!= 0:
                for see_more_link in see_more_links:
                    aria_label = see_more_link.get_attribute("aria-label")
                    if aria_label not in a_array:
                        print(f"enter aria_label: {aria_label}")
                        href = see_more_link.get_attribute("href")
                        hrefs.append(href)
            else:
                print(f"⚠️ 未找到 'See more information' 链接，跳过 {url}")
                continue

            if len(hrefs) != 0:
                for href in hrefs:
                    try:
                        app_ids = GetCommon.scrape_category_no_click(href, driver)
                        print(f"app_ids:{app_ids} num:{len(app_ids)}")
                        if app_ids:
                            GetCommon.save_add_json_file(appinfo_original_path, list(app_ids))

                    except TimeoutException:
                        print(f"❌ 访问 {href} 超时，跳过！")
                        logger.error(href)

        except TimeoutException:
            print(f"❌ 访问 {url} 超时，跳过！")
            logger.error(url)
            continue

        except Exception as e:
            # **其他异常打印错误并抛出**
            print("Error", e)
            logger.error(url)
            continue

def get_categories_method1(target_path):

    # 获取所有应用的URL列表
    for url in all_app_paths:
        driver.get(url)

        # **等待新页面加载完成**
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        GetCommon.scroll_and_click_show_more(driver) # 滚动并点击 'Show more'

        # **获取新页面的数据**
        new_page_content = driver.page_source
        soup = BeautifulSoup(new_page_content, "html.parser")

        # 查找所有 class="kcen6d" 的 div 标签
        divs = soup.find_all("div", class_="kcen6d")

        # ✅ 在这里添加调试信息，查看获取到的 div 标签个数
        print(f"Found {len(divs)} elements with class 'kcen6d' on {url}")

        # 提取文本内容
        for div in divs:
            category = div.get_text(strip=True)
            GetCommon.save_add_json_file(target_path,category)

def get_categories_method2(target_path):
    driver.get("https://support.google.com/googleplay/android-developer/answer/9859673?hl=en")
    # **等待新页面加载完成**
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    GetCommon.wait_span_highlights("//div[@class='zippy-overflow']",driver)

    # **获取新页面的数据**
    new_page_content = driver.page_source
    soup = BeautifulSoup(new_page_content, "html.parser")

    # 查找所有 class="kcen6d" 的 div 标签
    divs = soup.find_all("table", class_="nice-table")

    # 提取文本内容
    for div in divs:
        category = div.get_text(strip=True)
        GetCommon.save_add_json_file(target_path, category)

def get_categories_method3(target_path):
    print("enter get_categories_method3")

    base_url = "https://play.google.com/store/search?q={}&c=apps&hl=en&gl=US"

    for category in categories_new:
        url = base_url.format(category)
        try:
            driver.get(url)

            # 等待 input 元素出现
            input_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "HWAcU"))
            )

            # **模拟鼠标移动到元素上**
            actions = ActionChains(driver)
            actions.move_to_element(input_element).click().perform()
            time.sleep(1)

            # **获取新页面的数据**
            new_page_content = driver.page_source
            soup = BeautifulSoup(new_page_content, "html.parser")

            # 查找所有 class="kcen6d" 的 div 标签
            lis = soup.find_all("li", class_="YVhSle")

            # ✅ 在这里添加调试信息，查看获取到的 div 标签个数
            print(f"Found {len(lis)} elements on {url}")

            if len(lis) != 0:
                # 提取文本内容
                for li in lis:
                    category = li.get("data-display-text")
                    if category:  # 确保值不为空
                        GetCommon.save_add_json_file(target_path, category)


        except Exception as e:
            # **其他异常打印错误并抛出**
            print("Error", e)
            logger.error(url)
            continue

def filter_category(keywords1,keywords2):
    # 转换为大写
    keywords1 = {word.upper() for word in keywords1}
    keywords2 = {word.upper() for word in keywords2}

    # 去掉 keywords1 里已有的内容
    filtered_keywords = keywords2 - keywords1

    # 处理拆分 `_AND_` 和 `&`，但保留原始的未拆分版本
    final_categories = set(filtered_keywords)  # 先保留原始值
    for word in filtered_keywords:
        if "_AND_" in word:
            final_categories.update(word.split("_AND_"))
        if "&" in word:
            final_categories.update(word.split("&"))

    unique_keywords = list(set(final_categories))
    GetCommon.save_new_json_file(categories_new_path,unique_keywords)
    print(f"leave filter_category {len(unique_keywords)}")

def get_new_categories():
    # target_path = r"AppInfo_google\categories.json" #这个文件是用来存储新找到的类别的
    target_path = r"AppInfo_google\categories_new.json"
    get_categories_method1(target_path)
    get_categories_method2(target_path)
    get_categories_method3(target_path)

    file1 = GetCommon.get_app_info(r"AppInfo_google\categories_com.json")
    file2 = GetCommon.get_app_info(r"AppInfo_google\categories.json")
    filter_category(file1, file2) #在这里才会存储除去以前已经找到的类别新增的类别

    categories_new_data_tem = GetCommon.get_app_info(categories_new_path)
    categories_new_data = list(set(categories_new_data_tem))
    if len(categories_new_data_tem) != len(categories_new_data):
        print(f"任然有重复{categories_new_data_tem}--{categories_new_data}")
        GetCommon.save_new_json_file(categories_new_path,categories_new_data)

def get_new_app_ids():
    # get_app_id_method1()
    # get_app_id_method2()
    # get_app_id_method3()
    get_app_id_method4()

if __name__ == "__main__":
    print("enter main")

    MAX_CONCURRENT_THREADS = 20  # Limit concurrent threads
    BATCH_SIZE = 200  # Control how many items to load into memory at a time
    # Global driver instance (must be accessed in a thread-safe way)
    driver_lock = threading.Lock()
    driver = GetCommon.setup_driver()  # Or any other browser
    logger = GetCommon.getLogger("GooglePlayInfo")
    categories_new_path = r"AppInfo_google\categories_new.json"
    appinfo_new_path = r"AppInfo_google\appInfo_google_new.json"
    appinfo_original_path = r"AppInfo_google\appInfo_google_original.json"
    appinfo_all_path = r"AppInfo_google\appInfo_google_new_no_method4.json"
    all_app_path = r"AppInfo_google\all_app_paths.json"
    # categories_new = GetCommon.get_app_info(categories_new_path)
    categories_new = ""
    all_app_paths = GetCommon.get_app_info(all_app_path)
    appinfo_all = GetCommon.get_app_info(appinfo_all_path)
    # get categories
    # get_new_categories()
    get_new_app_ids()

    # filter app_id
    # GetCommon.remove_duplicates_json(appinfo_all_path, appinfo_original_path, appinfo_new_path)

    driver.quit()

    print("leave main")
