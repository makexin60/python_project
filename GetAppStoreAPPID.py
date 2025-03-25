import json
import os
import time

import requests

#"trackId":395979574,
#"trackViewUrl":"https://apps.apple.com/us/app/spider-solitaire-card-game/id395979574?uo=4",
#categoryUrl=https://apps.apple.com/ie/charts/iphone/sports-apps/6004

category_list = ["Books", "Business", "Developer Tools", "Education", "Entertainment", "Finance", "Food & Drink", "Graphics & Design", "Health & Fitness", "Kids", "Lifestyle", "Magazines & Newspapers", "Medical", "Music", "Navigation", "News", "Photo & Video", "Productivity", "Reference", "Shopping", "Social Networking", "Sports", "Travel", "Utilities", "Weather", "Action", "Adventure", "Board", "Card", "Casino", "Casual", "Family", "Music", "Puzzle", "Racing", "Role-Playing", "Simulation", "Sports", "Strategy", "Trivia", "Word"]

country = "ie"
time_limit = 10

if_test = False
if if_test :
    time_limit = "5"

authorization = "Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlU4UlRZVjVaRFMifQ.eyJpc3MiOiI3TktaMlZQNDhaIiwiaWF0IjoxNzM2OTkzNDAzLCJleHAiOjE3NDQyNTEwMDMsInJvb3RfaHR0cHNfb3JpZ2luIjpbImFwcGxlLmNvbSJdfQ.3q1pg8YB4oaPM5DuJEa_to2M9YyDstsIGiyeYsLryLwGXuaP4uL69JtyEP-QbeIJyLSH_k-Ws9GZC7zRPoGXtg"

def get_app_info_list():
    print("enter get_appInfo_list")
    category_info_data = []
    category_app_id = []

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Origin": "https://apps.apple.com",
        "Referer": "https://apps.apple.com/",
        "Authorization": authorization
    }

    base_url = "https://itunes.apple.com/search"

    for item in category_list:
        print(f"enter {item}")
        all_results = []
        max_results = 3000
        offset = 0  # 用于分页
        while len(all_results) < max_results:
            params = {
                "term": item,
                "country": country,
                "entity": "software",
                "limit": 210,  # 每次最多 200
                "offset": offset  # 分页
            }
            response = requests.get(base_url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                before_results = len(results)
                # print(f"results_{item}:{before_results}")
                if not results:
                    break  # 没有更多数据时停止
                all_results.extend(results)
                offset += len(results)  # 更新偏移量
            else:
                print(f"请求失败: {response.status_code}")
                break  # 终止循环
            time.sleep(time_limit)

        print(f"leave get_apps_list_{item}:{len(all_results)}")

        # 遍历 results
        for result in all_results:
            # 获取 `results` 字段
            track_view_url = result.get("trackViewUrl", [])  # 使用 .get() 避免 KeyError，如果不存在返回空列表
            track_id = result.get("trackId", [])  # 使用 .get() 避免 KeyError，如果不存在返回空列表
            track_name = result.get("trackName", [])  # 使用 .get() 避免 KeyError，如果不存在返回空列表

            if track_id not in category_app_id:
                category_app_id.append(track_id)
                tem_app_info_data = {
                    "id": track_id,
                    "name": track_name,
                    "url": track_view_url
                }
                category_info_data.append(tem_app_info_data)
        time.sleep(time_limit)
        print(f"{item}->app_info_data_len:{len(category_info_data)}")

    # 按 5000 条一批写入文件
    batch_size = 5000
    total_batches = (len(category_info_data) + batch_size - 1) // batch_size  # 计算需要多少个文件

    # 确保目录存在
    os.makedirs("AppInfo", exist_ok=True)

    for i in range(total_batches):
        batch = category_info_data[i * batch_size: (i + 1) * batch_size]  # 获取当前批次数据
        if if_test:
            filename = f"AppInfo_appstore/appInfo_data_test_{i + 1}.json"
        else:
            filename = f"AppInfo_appstore/appInfo_data_{i + 1}.json"

        # 写入 JSON 文件
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(batch, file, ensure_ascii=False, indent=4)

    print("leave get_appInfo_list 写入数据成功")

if __name__ == "__main__":

    print(f"enter main ")
    # 获取 APPID 数组并转换为 JSON 格式
    get_app_info_list()
    print(f"leave main")
