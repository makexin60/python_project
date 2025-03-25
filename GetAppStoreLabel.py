import time

import requests
from bs4 import BeautifulSoup

import GetCommon

country = "ie"  # Ireland, change as needed
time_limit = 2

def get_privacy():
    print(f"Start get_privacy")
    all_privacy_info = []
    # 遍历 data 数组中的每个字典对象
    for item in app_info_datas:
        get_label(item)
        time.sleep(1)
    print(f"End get_privacy")
    return all_privacy_info

def get_card(card_url):
    print(f"enter get_card")
    # 提取数据
    privacy_data = {}
    # Make the request
    response = requests.get(card_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 获取所有的隐私卡片
        cards = soup.find_all("div", class_="app-privacy__card")
        if cards:
            for card in cards:
                # 获取卡片的标题
                heading = card.find("h3", class_="privacy-type__heading").text.strip()
                # 获取卡片的描述
                description = card.find("p", class_="privacy-type__description").text.strip()

                # 获取卡片下的所有数据项
                items = []

                list_items = card.find_all("li", attrs={"classs": "privacy-type__item"})
                for item in list_items:
                    data_category = item.find("span", class_="privacy-type__data-category-heading").text.strip()
                    items.append(data_category)

                # 将每个卡片的标题、描述和数据项存储到字典中
                privacy_data[heading] = {
                    "description": description,
                    "data_categories": items
                }
        else:
            print("No privacy cards found.")
    else:
        print(f"Failed to retrieve the page: {response.status_code}")
    print(f"leave get_card")
    return privacy_data

def get_label(app_info):
    print(f"enter get_label")

    app_id = app_info["id"]

    detail_url = f"https://amp-api-edge.apps.apple.com/v1/catalog/{country}/apps/{app_id}?l=en-gb&platform=web&fields=privacyDetails"

    # Make the request
    response = requests.get(detail_url, headers=headers)

    # Check if request is successful
    if response.status_code == 200:
        data = response.json()
        print(f"Detail Privacy Policy: {data}")  # Print full privacy details
        GetCommon.save_new_json_file(f"Label_appstore/{app_id}_label.json",data)
    else:
        json_tem={
            "detail_url":detail_url,
            "response_code":response.status_code,
            "response_text":response.text
        }
        logger.error(json_tem)
    time.sleep(1)

    print(f"leave get_label")

if __name__ == "__main__":
    print(f"enter main")
    logger = GetCommon.getLogger("AppStoreLabel")
    app_info_datas = GetCommon.get_app_info(r"AppInfo_appstore\Label_appstore_isnull_appInfo.json")
    driver = GetCommon.setup_driver()
    headers = GetCommon.get_header()
    get_privacy()
    driver.quit()
    print(f"leave main ")