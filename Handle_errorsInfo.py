import json
import re
import GetCommon
import os
import requests

def get_error_logs_json(original_path,logger,target_path):
    with open(original_path, "r", encoding="utf-8") as file:
        for line in file:
            json_str = line.strip()

            # remove timestamp and level
            json_match = re.search(r"\{.*\}$", json_str)
            if not json_match:
                print(f"❌ 未找到 JSON，跳过: {json_str}")
                logger.error(json_str)
                continue

            json_str = json_match.group()  # get the part of JSON

            try:
                json_str = json_str.replace(": None", ": null")
                data = json.loads(json_str)
                GetCommon.save_add_json_file(target_path,data)

            except json.JSONDecodeError as e:
                print(f"❌ JSON parse fail: {json_str},{e}")
                logger.error(json_str)
                continue

def get_errors_none_json_app_id(directory2_path, logger, target_path):
    pattern = r"app_id:([\w\.]+)"
    with open(directory2_path, "r", encoding="utf-8") as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                app_id = match.group(1)
                with open(target_path, "a+", encoding="utf-8") as f:
                    f.write(json.dumps(app_id, ensure_ascii=False, indent=4) + ",\n")

def save_add_txt_file(target_path, data):
    with open(target_path, "a+", encoding="utf-8") as f:
        f.write(data)

def split_logs(log_file_path, end,loop):
    with open(log_file_path, 'r', encoding='utf-8') as log_file:
        for line in log_file:
            # remove the header info
            cleaned_line = re.sub(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - ERROR - ', '', line)

            if end == "google":
                if "Error more links" in cleaned_line:
                    save_add_txt_file(r"Logger\split_log\google\Loop3\error_more_links.log", cleaned_line)
                    print("error_more_links")
                elif "wait_extra_privacy" in cleaned_line:
                    save_add_txt_file(r"Logger\split_log\google\Loop3\wait_extra_privacy.log", cleaned_line)
                    print("wait_extra_privacy")
                elif "enter wrong privacy_url" in cleaned_line:
                    save_add_txt_file(r"Logger\split_log\google\Loop3\enter_wrong_privacy_url.log", cleaned_line)
                    print("enter_wrong_privacy_url")
                elif "privacy_data is null" in cleaned_line:
                    save_add_txt_file(r"Logger\split_log\google\Loop3\privacy_data_is_null.log", cleaned_line)
                    print("privacy_data_is_null")
                else:
                    save_add_txt_file(r"Logger\split_log\google\Loop3\other_types_errors.log", cleaned_line)
            else:
                if loop == "loop2":
                    if "error find_privacy_cards" in cleaned_line:
                        save_add_txt_file(r"Logger\split_log\appstore\Loop2\find_privacy_cards.log", cleaned_line)
                        print("error find_privacy_cards")
                    else:
                        save_add_txt_file(r"Logger\AppStorePrivacyLoop2_afterHandel_error", cleaned_line)
                else:
                    if "error find_privacy_cards" in cleaned_line:
                        save_add_txt_file(r"Logger\split_log\appstore\Loop3\find_privacy_cards.log", cleaned_line)
                        print("error find_privacy_cards")
                    else:
                        save_add_txt_file(r"Logger\AppStorePrivacyLoop3_afterHandel_error", cleaned_line)

    print("finish")

def read_logs_status_code(original_path,target_fail_path,target_success_path,reg_str):
    with open(original_path, 'r', encoding='utf-8') as log_file:
        for line in log_file:
            match = re.search(reg_str, line)

            if match:
                app_url = match.group(1)
                try:
                    response = requests.get(app_url, timeout=5)  # Set a timeout to avoid long waits
                    if response.status_code != 200:
                        save_add_txt_file(target_fail_path,f"{response.status_code}: {line}")  # Store the original log line
                        print(f"❌ Error {response.status_code}: {app_url} (Stored in log)")
                    else:
                        save_add_txt_file(target_success_path,line)  # Store the original log line
                except requests.RequestException as e:
                    save_add_txt_file(target_fail_path,line)
                    print(f"⚠️ Connection error: {app_url} (Stored in log)")
            else:
                print(f"app_url not found{line}")

# def get_app_id_error_file(original_path,target_path,reg_str,flag,logger):
#     with open(original_path, "r", encoding="utf-8") as file:
#         for line in file:
#             json_str = line.strip()
#             match = re.search(reg_str, json_str)
#
#             if not match:
#                 print(f"❌ 未找到 JSON，跳过: {json_str}")
#                 logger.error(json_str)
#                 continue  # 跳过错误行
#
#             json_str = match.group()  # 取 JSON 部分
#
#             # **2. 处理 JSON 格式，确保使用双引号**
#             try:
#                 data = json.loads(json_str)  # 解析 JSON
#                 if flag == 2:
#                     app_id = str(data.get("app_id"))
#                 else:
#                     app_id = str(data.get("id"))
#                 GetCommon.save_add_json_file(target_path,app_id)
#
#             except json.JSONDecodeError as e:
#                 print(f"❌ JSON 解析失败: {e} -{target_path}")
#                 logger.error(json_str)
#                 continue  # 跳过错误行，防止程序崩溃
#             except Exception as e:
#                 # Catch all other exceptions (such as database errors)
#                 print(f"❌ JSON 失败: {e}")
#                 logger.error(f"Data insertion failed: {json_str} | Error: {e}")
#                 continue  # Skip this line and move to the next one

def get_wrong_app_id(original_path,target_path,end,reg_str,logger):
    if not os.path.exists(original_path) or os.path.getsize(original_path) == 0:
        print("🚨 Error: The log file is empty or does not exist.")
        return

    if end == "google":
        with open(original_path, "r", encoding="utf-8") as file:
            for line in file:
                json_str = line.strip()
                match = re.search(reg_str, json_str)
                if match:
                    app_id = match.group(1)
                    GetCommon.save_add_json_file(target_path, app_id)
                else:
                    logger.warning(f"cant find app_id: {json_str}")
                    continue  # Skip this line and move to the next one
    else:
        with open(original_path, "r", encoding="utf-8") as file:
            for line in file:
                json_str = line.strip()
                match = re.search(reg_str, json_str)  # Handles both quoted and unquoted ID values
                if match:
                    app_id = match.group(1)
                    GetCommon.save_add_json_file(target_path, app_id)
                else:
                    logger.warning(f"cant find id: {json_str}")
                    continue  # Skip this line and move to the next one

    print("finish")

def handel_wrong_file(end,flag,reg_str,logger):
    if end == "google":
        directory_path = r"Policy_google"

        if flag == "loop1":
            target_path = r"AppInfo_google\loop1\error_appId_privacy.json"
            original_path = r"Logger\GooglePlayPrivacyLoop1_error.log"
            GetCommon.get_file_name(directory_path, target_path, 1, "size", "")
            get_wrong_app_id(original_path, target_path, end, reg_str, logger)
            app_id = GetCommon.get_app_info(target_path)
            unique_app_ids = set(app_id)
            print(f"before:{len(app_id)} after:{len(unique_app_ids)}")
            GetCommon.save_new_json_file(target_path, list(unique_app_ids))
        elif flag == "loop2":
            target_path = r"AppInfo_google\loop2\error_appId_privacy.json"
            original_path = r"Logger\GooglePlayPrivacyLoop2_error.log"
            GetCommon.get_file_name(directory_path, target_path, 1, "size", "")
            get_wrong_app_id(original_path, target_path, end, reg_str, logger)
            app_id = GetCommon.get_app_info(target_path)
            unique_app_ids = set(app_id)
            print(f"before:{len(app_id)} after:{len(unique_app_ids)}")
            GetCommon.save_new_json_file(target_path, list(unique_app_ids))
        elif flag == "loop3":
            target_path = r"AppInfo_google\loop3\error_appId_privacy.json"
            original_path = r"Logger\GooglePlayPrivacyLoop3_error.log"
            GetCommon.get_file_name(directory_path, target_path, 1, "size", "")
            get_wrong_app_id(original_path, target_path, end, reg_str, logger)
            app_id = GetCommon.get_app_info(target_path)
            unique_app_ids = set(app_id)
            print(f"before:{len(app_id)} after:{len(unique_app_ids)}")
            GetCommon.save_new_json_file(target_path, list(unique_app_ids))
        elif flag == "loop4":
            target_path = r"AppInfo_google\loop4\error_appId_privacy_error_more_links.json"
            original_path = r"Logger\split_log\google\Loop3\error_more_links.log"
            get_error_logs_json(r"Logger\GooglePlayPrivacyLoop4_warning.log", logger,
                            r"AppInfo_google\loop4\sub_privacy_url.json")
            # get_wrong_app_id(original_path, target_path, end, reg_str, logger)
            # app_id = GetCommon.get_app_info(target_path)
            # unique_app_ids = set(app_id)
            # print(f"before:{len(app_id)} after:{len(unique_app_ids)}")
            # GetCommon.save_new_json_file(target_path, list(unique_app_ids))
        else:
            print("b")

    else:
        directory_path = r"Policy_appstore"
        all_app_info_path = r"AppInfo_appstore\appInfo_data.json"
        tem_log_path_error = r"Logger\AppstoreData_error.log"

        if flag == "loop1":
            original_path = r"Logger\AppStorePrivacyLoop1_error.log"
            target_path = r"AppInfo_appstore\loop1\error_appId_privacy.json"
            output_file = r"AppInfo_appstore\loop1\error_appInfo_privacy.json"
            missing_ids_file = r"AppInfo_appstore\loop1\missing_ids.json"
            GetCommon.get_file_name(directory_path, target_path, 1025, "size", "")
            get_wrong_app_id(original_path, target_path, end, reg_str, logger)
            get_wrong_app_id(tem_log_path_error, target_path, end, reg_str, logger)

            app_id = GetCommon.get_app_info(target_path)
            unique_app_ids = set(app_id)
            print(f"before:{len(app_id)} after:{len(unique_app_ids)}")
            GetCommon.save_new_json_file(target_path, list(unique_app_ids))
            filter_data_appstore_label(target_path, all_app_info_path, output_file, missing_ids_file)
        elif flag == "loop2":
            original_path = r"Logger\AppStorePrivacyLoop2_afterHandel_error.log"
            target_path = r"AppInfo_appstore\loop2\error_appId_privacy.json"
            output_file = r"AppInfo_appstore\loop2\error_appInfo_privacy.json"
            missing_ids_file = r"AppInfo_appstore\loop2\missing_ids.json"
            split_log_error_path = r"Logger\split_log\appstore\Loop2\handel_find_privacy_cards_success.log"
            split_logs(original_path, end,"loop2")
            read_logs_status_code(r"Logger\split_log\appstore\Loop2\find_privacy_cards.log",
                                  r"Logger\split_log\appstore\Loop2\handel_find_privacy_cards_errorCode.log", split_log_error_path, r'"app_url":\s*"([^"]+)"')
            GetCommon.read_id(r"Logger\split_log\appstore\Loop2\handel_find_privacy_cards_errorCode.log",
                              r"AppInfo_appstore\loop2\cant_open_ids.json", r'"id":\s*(\d+)')

            get_wrong_app_id(split_log_error_path, target_path, end, reg_str, logger)
            GetCommon.get_file_name(directory_path, target_path, 1025, "size", "")
            get_wrong_app_id(original_path, target_path, end, reg_str, logger)
            get_wrong_app_id(tem_log_path_error, target_path, end, reg_str, logger)

            app_id = GetCommon.get_app_info(target_path)
            unique_app_ids = set(app_id)
            print(f"before:{len(app_id)} after:{len(unique_app_ids)}")
            GetCommon.save_new_json_file(target_path, list(unique_app_ids))
            filter_data_appstore_label(target_path, all_app_info_path, output_file, missing_ids_file)
        elif flag == "loop3":
            original_path = r"Logger\AppStorePrivacyLoop3_error.log"
            target_path = r"AppInfo_appstore\loop3\error_appId_privacy.json"
            output_file = r"AppInfo_appstore\loop3\error_appInfo_privacy.json"
            missing_ids_file = r"AppInfo_appstore\loop3\missing_ids.json"
            split_log_error_path = r"Logger\split_log\appstore\Loop3\handel_find_privacy_cards_success.log"

            read_logs_status_code(r"Logger\split_log\appstore\Loop3\find_privacy_cards.log",
                                  r"Logger\split_log\appstore\Loop3\handel_find_privacy_cards_errorCode.log",
                                  split_log_error_path, r'"app_url":\s*"([^"]+)"')
            GetCommon.read_id(r"Logger\split_log\appstore\Loop3\handel_find_privacy_cards_errorCode.log",
                              r"AppInfo_appstore\loop3\cant_open_ids.json", r'"id":\s*(\d+)')
            get_wrong_app_id(split_log_error_path, target_path, end, reg_str, logger)
            GetCommon.get_file_name(directory_path, target_path, 1025, "size", "")
            get_wrong_app_id(original_path, target_path, end, reg_str, logger)
            get_wrong_app_id(tem_log_path_error, target_path, end, reg_str, logger)

            app_id = GetCommon.get_app_info(target_path)
            unique_app_ids = set(app_id)
            print(f"before:{len(app_id)} after:{len(unique_app_ids)}")
            GetCommon.save_new_json_file(target_path, list(unique_app_ids))
            filter_data_appstore_label(target_path, all_app_info_path, output_file, missing_ids_file)
        elif flag == "loop4":
            target_path = r"AppInfo_appstore\loop4\error_appId_privacy_error_more_links.json"
            original_path = r"Logger\split_log\google\Loop3\error_more_links.log"
            get_error_logs_json(r"Logger\AppStorePrivacyLoop4_warning.log", logger,
                            r"AppInfo_appstore\loop4\sub_privacy_url.json")
        else:
            print("okay")


def filter_data_appstore_label(file_a,file_b,output_file,missing_ids_file):
    # read id list
    with open(file_a, "r", encoding="utf-8") as f:
        id_list = set(json.load(f))  # 转为 set 以提高查找效率

    # read id dict
    with open(file_b, "r", encoding="utf-8") as f:
        data_list = json.load(f)

    b_ids = {str(item["id"]) for item in data_list}

    filtered_data = [item for item in data_list if str(item["id"]) in id_list]

    missing_ids = list(id_list - b_ids)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, indent=4, ensure_ascii=False)

    with open(missing_ids_file, "w", encoding="utf-8") as f:
        json.dump(missing_ids, f, indent=4, ensure_ascii=False)

    print(f"✅ result path {output_file}")
    print(f"⚠️ Missing ID path {missing_ids_file}")

def get_error_appstore_privacy():
    logger = GetCommon.getLogger("AppstoreData")
    end = "appstore"
    reg_str = r'"id":\s*(\d+)'

    # # loop1 error log
    # handel_wrong_file(end, "loop1", reg_str,logger)
    # # loop2 error log
    # handel_wrong_file(end, "loop2", reg_str,logger)
    # # loop3 error log
    # handel_wrong_file(end, "loop3", reg_str,logger)
    # loop4 error log (find wrong sub_privacy_url)
    handel_wrong_file(end, "loop4", reg_str, logger)

def get_error_google_privacy():
    logger = GetCommon.getLogger("GoogleData")
    end = "google"
    reg_str = r'"app_id":\s*"([^"]+)"'

    # loop1 error log
    handel_wrong_file(end, "loop1",  reg_str,logger)
    # loop2 error log
    handel_wrong_file(end, "loop2",  reg_str,logger)
    # loop3 error log
    handel_wrong_file(end, "loop3",  reg_str,logger)
    # loop4 error log (find wrong sub_privacy_url)
    handel_wrong_file(end, "loop4",  reg_str,logger)

    # split_logs
    split_logs(r"Logger\GooglePlayPrivacyLoop3_error.log", end,"loop3")

def get_error_appstore_label():
    logger = GetCommon.getLogger("AppstoreData")
    end = "appstore"
    all_app_info_path = r"AppInfo_appstore\appInfo_data.json"

    # loop1 empty privacyType from file
    target_path = r"AppInfo_appstore\loop1\error_appId_label.json"
    output_file = r"AppInfo_appstore\loop1\error_appInfo_label.json"
    missing_ids_file = r"AppInfo_appstore\loop1\missing_ids_label.json"
    empty_label(r"Label_appstore",target_path,logger)
    filter_data_appstore_label(target_path, all_app_info_path, output_file, missing_ids_file)

    # loop2 empty privacyType from file
    target_path = r"AppInfo_appstore\loop2\error_appId_label.json"
    output_file = r"AppInfo_appstore\loop2\error_appInfo_label.json"
    missing_ids_file = r"AppInfo_appstore\loop2\missing_ids_label.json"
    empty_label(r"Label_appstore", target_path, logger)
    filter_data_appstore_label(target_path, all_app_info_path, output_file, missing_ids_file)

def empty_label(directory,target_path,logger):
    files = [
        f for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and os.path.getsize(os.path.join(directory, f)) < 2048
    ]
    print(f"Number of matching files in '{directory}': {len(files)}")

    for file in files:
        file_prefix = file.rsplit("_", 1)[0]
        file_path = os.path.join(directory, file)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for app in data["data"]:
                app_id = app.get("id")
                privacy_details = app.get("attributes", {}).get("privacyDetails", {})
                privacy_types = privacy_details.get("privacyTypes", [])

                if not privacy_types:
                    print(app_id)
                    GetCommon.save_add_json_file(target_path, app_id)

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ Error processing file {file_prefix}")
            print(f"❌ Error processing file {file_prefix}: {e}")

    print(f"finish: {target_path}")

if __name__ == "__main__":
    # processing error log for privacy
    get_error_appstore_privacy()
    # get_error_google_privacy()

    # processing error log for label
    # get_error_appstore_label()

