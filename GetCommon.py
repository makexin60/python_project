import json
import logging
import os
import re
import time
from collections import OrderedDict
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

limit_time = 0.8

def getLogger(address):
    # 创建日志记录器
    logger = logging.getLogger("my_logger")
    logger.setLevel(logging.DEBUG)  # 允许所有级别的日志进入处理器

    # 定义日志格式（包含毫秒）
    log_format = logging.Formatter(
        "%(asctime)s,%(msecs)03d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 创建 ERROR 级别日志文件处理器
    error_handler = logging.FileHandler(f"Logger/{address}_error.log",encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)

    # 创建 WARNING 级别日志文件处理器
    warning_handler = logging.FileHandler(f"Logger/{address}_warning.log",encoding="utf-8")
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(log_format)

    # 添加过滤器，确保 warning_handler 只处理 WARNING 级别日志
    warning_handler.addFilter(lambda record: record.levelno == logging.WARNING)

    # 添加过滤器，确保 error_handler 只处理 ERROR 及以上日志
    error_handler.addFilter(lambda record: record.levelno >= logging.ERROR)

    # 添加处理器到日志记录器
    logger.addHandler(error_handler)
    logger.addHandler(warning_handler)

    return logger

def get_app_info(target_path):
    with open(target_path, "r", encoding="utf-8") as file:
        content = json.load(file, object_pairs_hook=lambda pairs: OrderedDict(pairs))
    print(f"open {target_path} file length: {len(content)}")
    return content

def save_new_txt_file(target_path,data):
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(data)

def save_new_json_file(target_path, data):
    with open(target_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def save_add_json_file(target_path, data):
    with open(target_path, "a+", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4) + ",\n")


def scroll_to_load_apps(driver, max_scrolls=10):
    """滚动到底部加载更多应用"""
    print("🔽 开始滚动以加载更多应用...")

    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempt = 0

    while scroll_attempt < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            # **等待新内容加载**（最多 5 秒）
            WebDriverWait(driver, 2).until(
                lambda d: driver.execute_script("return document.body.scrollHeight") > last_height
            )
        except Exception:
            print("⚠️ 未检测到新内容，可能已加载完所有应用")

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:  # 没有新内容了，停止滚动
            print("✅ 滚动结束，所有应用已加载")
            break

        last_height = new_height
        scroll_attempt += 1

    print("🔼 结束滚动")

# def scroll_to_load_apps(driver):
#     """滚动到底部加载更多应用"""
#     last_height = driver.execute_script("return document.body.scrollHeight")
#
#     while True:
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(limit_time)  # 等待加载
#
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:  # 没有新内容了，停止滚动
#             print("leave scroll_to_load_apps")
#             break
#         last_height = new_height

def extract_app_ids(driver):
    """提取当前页面的所有 app_id"""
    app_ids = set()
    app_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/store/apps/details?id=')]")
    for link in app_links:
        match = re.search(r"id=([^&]+)", link.get_attribute("href"))
        if match:
            app_ids.add(match.group(1))
    return app_ids

def scrape_category_no_click(url,driver):
    print(f"enter scrape_category_no_click")
    driver.set_page_load_timeout(15)
    driver.get(url)

    try:
        # **等待新页面加载完成**
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception:
        print("⚠️ 页面主要元素未找到，可能需要调整 XPATH！")
        return None

    scroll_to_load_apps(driver)  # 只滚动到底部，不点击按钮
    app_ids = extract_app_ids(driver)

    print(f"leave {url} get {len(app_ids)} applications")
    return app_ids

def scrape_category_no_click_no_url(driver):
    time.sleep(limit_time)
    scroll_to_load_apps(driver)  # 只滚动到底部，不点击按钮
    app_ids = extract_app_ids(driver)

    print(f"leave scrape_category_no_click_no_url get {len(app_ids)} applications")
    return app_ids

def scroll_and_click_show_more(driver):
    print("enter scroll_and_click_show_more")
    while True:
        # 先滚动到底部，确保所有内容加载出来
        scroll_to_load_apps(driver)
        time.sleep(limit_time)
        # 尝试点击 'Show more' 按钮
        try:
            show_more_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Show More')]")
            ActionChains(driver).move_to_element(show_more_button).click().perform()
            print("✅ click 'Show more' button")
            time.sleep(limit_time)  # 等待新内容加载

            # **点击按钮后，再次滚动到底部，确保新内容加载**
            scroll_to_load_apps(driver)

        except Exception as e:
            print(f"leave scroll_and_click_show_more  ❌ not find 'Show more' button{e}")
            break

        # **检查页面是否继续增长**
        last_height = driver.execute_script("return document.documentElement.scrollHeight")
        time.sleep(limit_time)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")

        if new_height == last_height:
            print("leave scroll_and_click_show_more")
            break

#scroll page and click button
def scrape_category_click(url,driver):
    driver.get(url)
    time.sleep(limit_time)

    scroll_and_click_show_more(driver)
    app_ids = extract_app_ids(driver)

    print(f"leave scrape_category_click {url} get {len(app_ids)} applications")
    return app_ids

#remove_duplicates_json in two files
def remove_duplicates_json(file1,target_file,output_file):
    try:
        with open(file1, "r", encoding="utf-8") as f1:
            data1 = set(json.load(f1))  # 解析 JSON，转换为集合
        with open(target_file, "r", encoding="utf-8") as f2:
            data2 = set(json.load(f2))
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        return
    except FileNotFoundError as e:
        print(f"❌ file not find: {e}")
        return

    # 计算差集（只保留 file2 中不在 file1 里的内容）
    new_app_ids = list(data2 - data1)

    # 写入新的 JSON 文件
    save_new_json_file(output_file,new_app_ids)

    print(f"✅ success，data1:{len(data1)}, data2:{len(data2)}, new_app_ids:{len(new_app_ids)}, resule file path{output_file}")

# 只下载 chromedriver 一次，避免重复安装
CHROMEDRIVER_PATH = ChromeDriverManager().install()

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--lang=en-US")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    )
    prefs = {"profile.managed_default_content_settings.images": 2,
             "profile.managed_default_content_settings.javascript": 1}
    options.add_experimental_option("prefs", prefs)
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    return driver

def wait_span_highlights(click_path,driver):
    print("enter wait_span_highlights")

    try:
        # 等待所有包含 "Highlights" 文字的 <span> 出现
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, click_path))
        )

        if element:
            print("Found 'Highlights', performing actions...")

            # 查找所有 <span> 标签，文本内容为 "Highlights"
            highlights_spans = driver.find_elements(By.XPATH, click_path)

            # 依次点击
            for span in highlights_spans:
                # 确保元素可见并可点击
                driver.execute_script("arguments[0].scrollIntoView();", span)  # 滚动到元素
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(span)).click()

    except TimeoutException:
        print("TimeoutException wait_span_highlights:")

    except Exception as e:
        # **其他异常打印错误并抛出**
        print("Error wait_span_highlights:", e)

    print("leave wait_span_highlights")

def get_privacy_original(page_source):
    print(f"enter get_privacy_original")
    soup = BeautifulSoup(page_source, "html.parser")

    # **定义可能的内容区域**
    possible_selectors = [
        "main#brx-content",  # Justalk
        "div[class*='xg6iff7']",  # Facebook 右半部分
        "article",
        "main",
        "body"  # 兜底策略
    ]

    privacy_text = ""

    for selector in possible_selectors:
        content = soup.select_one(selector)
        if content:
            # **删除所有 <header> 和 <footer> 标签**
            for tag in content.find_all(["header", "footer"]):
                tag.decompose()

            # **删除所有 class 包含 'header' 或 'footer' 的元素**
            for tag in content.find_all(class_=lambda c: c and ("header" in c.lower() or "footer" in c.lower())):
                tag.decompose()

            time.sleep(limit_time)
            # **获取清理后的文本**
            privacy_text = content.get_text(separator="\n", strip=True)
            print("okay get_privacy_original")
            return privacy_text

    print(f"cant find content get_privacy_original")
    return privacy_text

def get_visible_privacy_links(driver):
    script = """
    return Array.from(document.querySelectorAll('a')).filter(a => {
        let rect = a.getBoundingClientRect();
        if (!a.textContent.toLowerCase().includes('privacy')) return false;
        if (document.head.contains(a)) return false;  // 🚫 <head> 里面的 <a> 不要

        let elem = a;
        while (elem) {
            let style = window.getComputedStyle(elem);
            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                return false;  // 🚫 祖先隐藏
            }
            if (elem.tagName.toLowerCase() === 'footer' || elem.tagName.toLowerCase() === 'header') {
                return false;  // 🚫 <footer> 和 <header> 里的 <a> 不要
            }
            elem = elem.parentElement;
        }

        return true;  // ✅ 符合条件的 <a> 
    }).map(a => a.href);
    """
    return driver.execute_script(script)

def filter_urls(urls,original_url):
    print(f"enter filter_urls original_urls:{urls}")

    seen_paths = set()  # 记录已经出现过的路径（忽略语言/地区代码、fragment 和结尾 `/`）
    seen_urls = set()  # 记录已出现过的完整 URL

    normalized_url = normalize_url(original_url)
    seen_paths.add(normalized_url)

    filtered_urls = []

    for url in urls:
        # **直接丢弃 `mailto:` URL**
        if url.startswith("mailto:"):
            continue

        # **去掉不是 http 或 https 开头的 URL**
        if not (url.startswith("http://") or url.startswith("https://")):
            continue  # 丢弃该 URL

        # **标准化 URL**
        normalized_url = normalize_url(url)

        # **检查 `seen_paths`（是否已经访问过相似的路径）**
        if normalized_url in seen_paths:
            continue  # 丢弃

        seen_paths.add(normalized_url)  # 记录路径（忽略 fragment 和 `/`）

        # **检查 `seen_urls`（完整 URL 去重）**
        if url in seen_urls:
            continue  # 丢弃

        seen_urls.add(url)  # 记录完整 URL

        # **保留 URL**
        filtered_urls.append(url)

    print(f"leave filter_urls: {filtered_urls}")
    return filtered_urls

def normalize_url(url):
    parsed = urlparse(url)

    # **去掉 fragment**
    parsed = parsed._replace(fragment="")

    # **去掉结尾 `/`**
    path = parsed.path.rstrip("/")

    # **忽略 www.**
    netloc = parsed.netloc.lower().replace("www.", "")

    # **忽略 http 和 https**
    scheme = "https"  # 统一成 https

    # **重新构造 URL**
    normalized = urlunparse((scheme, netloc, path, "", "", ""))

    return normalized

def read_id(original_path,target_path,express):
    with open(original_path, "r", encoding="utf-8") as file:
        for line in file:
            json_str = line.strip()
            match = re.search(express, json_str)
            if match:
                app_id = match.group(1)
                save_add_json_file(target_path, app_id)
                print(f"📌 extract App ID: {app_id}")
            else:
                print("❌ cant find App ID")

    print(f"save file path: {target_path}")

def delete_matching_files(directory, id_file):
    # 读取 JSON 文件，获取要删除的文件名列表
    with open(id_file, "r", encoding="utf-8") as f:
        id_list = json.load(f)  # 读取 ["1477079218", "1203185844", ...]

    # 遍历目标目录下的所有文件
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # 去掉文件扩展名
        file_name_without_ext, _ = os.path.splitext(filename)
        # 去掉最后一个 "_" 及其后面的内容
        new_name = file_name_without_ext.rsplit("_", 1)[0]  # 不加扩展名

        # 如果文件名在 ID 列表中，则删除
        if new_name in id_list:
            try:
                os.remove(file_path)
                print(f"✅ 已删除: {file_path}")
            except Exception as e:
                print(f"❌ 删除失败: {file_path}, 错误: {e}")

def wait_extra_privacy_only_sub(results,filtered_urls,driver,logger):
    print(f"enter wait_extra_privacy")

    sub_privacy_data = "Sub-section Policy: "
    results.update({
        "sub-section_urls": filtered_urls
    })

    for index, href in enumerate(filtered_urls):
        try:
            driver.set_page_load_timeout(10)  # 最多等待 10 秒
            # **跳转到该链接**
            driver.get(href)
            driver.execute_script("window.stop();")  # Stop unnecessary loading

            # **等待新页面加载完成**
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # **获取新页面的数据**
            new_page_content = driver.page_source

            soup = BeautifulSoup(new_page_content, "html.parser")

            # 获取 id="ph-body" 的 div
            body_content = soup.find(id="ph-body")

            # 如果找不到，则回退到 body
            if not body_content:
                body_content = soup.select_one("body")

            if body_content:
                # **删除 header 和 footer 以及 class 名称包含 'header' 或 'footer' 的元素**
                for tag in body_content.find_all(["header", "footer"]):  # 删除 <header> 和 <footer> 直接标签
                    tag.decompose()

                for tag in body_content.find_all(
                        class_=lambda c: c and ("header" in c.lower() or "footer" in c.lower())):
                    tag.decompose()  # 删除 class 包含 'header' 或 'footer' 的元素

                time.sleep(limit_time)
                sub_data = body_content.get_text(separator="\n", strip=True)
                sub_privacy_data += "\n" + "Sub-policy " + str(index) + "-" + href + ":\n" + sub_data  # 每次拼接后加真实换行符

        except TimeoutException:
            sub_privacy_data += "\n" + "Sub-policy " + str(index) + "-" + href + ":\n"
            logger.error(f"wait_extra_privacy TimeoutException: {(json.dumps(results, ensure_ascii=False))}")
            continue

        except Exception:
            sub_privacy_data += "\n" + "Sub-policy " + str(index) + "-" + href + ":\n"
            logger.error(f"Error more links:{href}---{(json.dumps(results, ensure_ascii=False))}")
            continue

    print("leave wait_extra_privacy")
    return sub_privacy_data,results

def wait_extra_privacy(results, privacy_data,filtered_urls,driver,logger):
    print(f"enter wait_extra_privacy")

    privacy_data += privacy_data + "\n" + "Sub-section Policy: "
    results.update({
        "sub-section_urls": filtered_urls
    })

    for index, href in enumerate(filtered_urls):
        try:
            driver.set_page_load_timeout(10)  # 最多等待 10 秒
            # **跳转到该链接**
            driver.get(href)

            # **等待新页面加载完成**
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # **获取新页面的数据**
            new_page_content = driver.page_source

            soup = BeautifulSoup(new_page_content, "html.parser")

            # 获取 id="ph-body" 的 div
            body_content = soup.find(id="ph-body")

            # 如果找不到，则回退到 body
            if not body_content:
                body_content = soup.select_one("body")

            if body_content:
                # **删除 header 和 footer 以及 class 名称包含 'header' 或 'footer' 的元素**
                for tag in body_content.find_all(["header", "footer"]):  # 删除 <header> 和 <footer> 直接标签
                    tag.decompose()

                for tag in body_content.find_all(
                        class_=lambda c: c and ("header" in c.lower() or "footer" in c.lower())):
                    tag.decompose()  # 删除 class 包含 'header' 或 'footer' 的元素

                time.sleep(limit_time)
                privacy_text = body_content.get_text(separator="\n", strip=True)
                privacy_data += "\n" + "Sub-policy " + str(index) + "\n" + href + ":\n" + privacy_text  # 每次拼接后加真实换行符

        except TimeoutException:
            privacy_data += "\n" + "Sub-policy " + str(index) + "\n" + href + ":\n"
            logger.error(f"wait_extra_privacy TimeoutException: {(json.dumps(results, ensure_ascii=False))}")
            continue

        except Exception:
            privacy_data += "\n" + "Sub-policy " + str(index) + "\n" + href + ":\n"
            logger.error(f"Error more links:{href}---{(json.dumps(results, ensure_ascii=False))}")
            continue


    print("leave wait_extra_privacy")
    return privacy_data,results

# calculate content file2 have but file1 not have
def filter_content(file1,file2,output_file):

    # 读取 A.json
    with open(file1, "r", encoding="utf-8") as file_A:
        original = set(json.load(file_A))  # 转换为集合，方便去重对比

    # 读取 A_bac.json
    with open(file2, "r", encoding="utf-8") as file_A_bac:
        bac = set(json.load(file_A_bac))

    diff = list(bac - original)

    # 写入最终文件
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(diff, output, ensure_ascii=False, indent=4)

    print("处理完成，生成文件：", output_file)

def convert_upper(path,output_path):
    data = get_app_info(path)
    data = [str(item).upper() for item in data]
    save_new_json_file(output_path,data)

def get_file_name(directory,target_path,size,flag,non_200_app_id_path):
    files = [
        f for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and os.path.getsize(os.path.join(directory, f)) < size
    ]
    print(f"Number of files in '{directory}': {len(files)}")

    if flag == "size":
        # extract the content before the last `_`
        for file in files:
            file_prefix = file.rsplit("_", 1)[0]
            save_add_json_file(target_path, file_prefix)
    else:
        error_codes = {"301", "302", "303", "307", "400", "403", "404", "408",  "410", "429", "500", "502", "503", "504"}

        for file in files:
            file_path = os.path.join(directory, file)
            file_prefix = file.rsplit("_", 1)[0]

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                if len(lines) < 4:
                    print(lines)
                    file_content = " ".join(lines)
                    if any(code in file_content for code in error_codes):
                        save_add_json_file(non_200_app_id_path, file_prefix)
                    else:
                        save_add_json_file(target_path, file_prefix)
            except Exception as e:
                print(f"❌ handel {file_path} fail: {e}")

def filter_data(file_a, file_b, output_file):
    # 读取 A 文件（列表）
    with open(file_a, "r", encoding="utf-8") as f:
        id_list = json.load(f)  # A 文件存的是 ["1000385101", "1000551625", ...]

    # 读取 B 文件（包含字典的列表）
    with open(file_b, "r", encoding="utf-8") as f:
        data_list = json.load(f)  # B 文件存的是 [{"id": 1214208722, "name": "...", "url": "..."}, ...]

    # 过滤 B 文件中的数据
    filtered_data = [item for item in data_list if str(item["id"]) in id_list]

    # 将匹配的结果写入新文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, indent=4, ensure_ascii=False)

    print(f"✅ 结果已保存到 {output_file}")


def get_header():
    authorization = "Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlU4UlRZVjVaRFMifQ.eyJpc3MiOiI3TktaMlZQNDhaIiwiaWF0IjoxNzM5MTkyNzIzLCJleHAiOjE3NDY0NTAzMjMsInJvb3RfaHR0cHNfb3JpZ2luIjpbImFwcGxlLmNvbSJdfQ.wuLUSBq_qWD4MAkmwbxoaJDQTRyUBZzEqDMuvT-nAJNarxda8F5TLXpRy_OjonWBuUcnD-eyWb86qn4w6xfang"

    # Headers (Apple may require authorization tokens, these are standard ones)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Origin": "https://apps.apple.com",
        "Referer": "https://apps.apple.com/",
        "Authorization": authorization
    }

    return headers