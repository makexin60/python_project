import json
import os
import re
import sqlite3

import GetCommon


def insert_data(original_path,table_name,reg_str,logger):
    with open(original_path, "r", encoding="utf-8") as file:
        if table_name == "appstore_label_privacy":
            data = json.load(file)

            for item in data:
                app_id = item["id"]
                try:
                    cursor.execute("""
                                    INSERT OR IGNORE INTO appstore_label_privacy (app_id, label_flag, label_flag_type, privacy_flag, privacy_flag_type, if_equal) 
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (
                        app_id,
                        1,
                        None,
                        1,
                        None,
                        None
                    ))

                except Exception as e:
                    # Catch all other exceptions (such as database errors)
                    print(f"❌ insert fail: {e}")
                    logger.error(f"insertion failed: {data}")
                    continue  # Skip this line and move to the next one

        elif table_name == "google_label_privacy":
            lines = file.readlines()
            lines = lines[1:-1]

            for line in lines:
                json_str = line.strip()
                app_id = json_str.strip('",')

                cursor.execute("""
                                    INSERT OR IGNORE INTO google_label_privacy (app_id, label_flag, label_flag_type, privacy_flag, privacy_flag_type, if_equal) 
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (
                    app_id,
                    1,
                    None,
                    1,
                    None,
                    None
                ))

        elif table_name == "appstore_appInfo":
            data = json.load(file)

            for item in data:
                app_id = item["id"]
                name = item["name"]
                url = item["url"]
                try:
                    cursor.execute("""
                                       INSERT OR IGNORE INTO appstore_appInfo (app_id, name, app_url, privacy_url, sub_privacy_url.json)
                                       VALUES (?, ?, ?, ?, ?)
                                   """, (
                        app_id,
                        name,
                        url,
                        None,
                        None,
                    ))

                except Exception as e:
                    # Catch all other exceptions (such as database errors)
                    print(f"❌ insert fail: {e}")
                    logger.error(f"insertion failed: {data}")
                    continue  # Skip this line and move to the next one

        else:
            lines = file.readlines()
            lines = lines[1:-1]

            for line in lines:
                json_str = line.strip()
                json_str = json_str.strip('",')
                try:
                    cursor.execute("""
                                    INSERT OR IGNORE INTO google_appInfo 
                                    (app_id, name, app_url, privacy_url, sub_privacy_url.json, installs, developerEmail, developerWebsite, score, ratings, reviews) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                        json_str,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None
                    ))

                    print("success")
                except Exception as e:
                    # Catch all other exceptions (such as database errors)
                    print(f"❌ insert fail: {e}")
                    logger.error(f"Data insertion failed: {json_str} | Error: {e}")
                    continue  # Skip this line and move to the next one

    print("finish")

def import_data(table_name):
    # 查询数据
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # 获取列名
    columns = [desc[0] for desc in cursor.description]

    # 创建导出目录（如果不存在）
    os.makedirs("data_csv", exist_ok=True)

    # 每个文件最多写入的行数
    chunk_size = 2000
    total_rows = len(rows)

    for i in range(0, total_rows, chunk_size):
        chunk = rows[i:i + chunk_size]
        file_index = i // chunk_size + 1
        filename = f"data_csv/{table_name}_{file_index}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(columns)  # 写入表头
            writer.writerows(chunk)  # 写入数据
        print(f"导出 {filename} 成功，包含 {len(chunk)} 条记录")

def delete_data(table_name):
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

def create_table(table_name):
    if table_name == "appstore_appInfo":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appstore_appInfo (
                app_id INTEGER UNIQUE,
                name TEXT,
                app_url TEXT,
                privacy_url TEXT,
                sub_privacy_url.json TEXT,
                PRIMARY KEY (app_id)  -- Make app_id the primary key
            )
        """)

    elif table_name == "google_appInfo":
        # 创建表（如果表不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS google_appInfo (
                app_id TEXT UNIQUE,  
                name TEXT,
                app_url TEXT,
                privacy_url TEXT,
                sub_privacy_url.json TEXT,
                installs TEXT,
                developerEmail TEXT,
                developerWebsite TEXT,
                score REAL,
                ratings INTEGER,
                reviews INTEGER,
                PRIMARY KEY (app_id)  -- Make app_id the primary key
            )
        """)

    elif table_name == "google_label_privacy":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS google_label_privacy (
                app_id TEXT UNIQUE, 
                label_flag INTEGER, -- Make 1=have label 0=no label
                label_flag_type TEXT, 
                privacy_flag INTEGER, -- Make 1=have privacy 0=no privacy
                privacy_flag_type TEXT,
                if_equal INTEGER, -- Make 1=equal 0=not equal
                PRIMARY KEY (app_id)  -- Make app_id the primary key
            )
        """)

    elif table_name == "appstore_label_privacy":
        # 创建表（如果表不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appstore_label_privacy (
                app_id TEXT UNIQUE, 
                label_flag INTEGER, -- Make 1=have label 0=no label
                label_flag_type TEXT, 
                privacy_flag INTEGER, -- Make 1=have privacy 0=no privacy
                privacy_flag_type TEXT,
                if_equal INTEGER, -- Make 1=equal 0=not equal
                PRIMARY KEY (app_id)  -- Make app_id the primary key
            )
        """)

    else:
        print("no table")

def alter_table(table_name):
    # cursor.execute("ALTER TABLE {} ADD COLUMN access INTEGER".format(table_name))
    # cursor.execute("UPDATE {} SET access = 1".format(table_name))
    # cursor.execute("ALTER TABLE {} ADD COLUMN new_sub_privacy_url TEXT".format(table_name))
    # cursor.execute("ALTER TABLE {} ADD COLUMN sub_privacy_url_if_equal INTEGER".format(table_name))
    cursor.execute("UPDATE {} SET sub_privacy_url_if_equal = 1".format(table_name))

def update_data(original_path,table_name,reg_str,logger):
    with open(original_path, "r", encoding="utf-8") as file:
        if table_name == "appstore_label_privacy":
            lines = file.readlines()
            lines = lines[1:-1]

            for line in lines:
                json_str = line.strip()
                app_id = json_str.strip('",')
                try:
                    if reg_str == "label":
                        cursor.execute("""
                                   UPDATE appstore_label_privacy
                                   SET
                                       label_flag = ?,
                                       label_flag_type = ?
                                   WHERE app_id = ?
                               """, (
                            0,
                            "empty_privacyType",
                            app_id
                        ))
                    else:
                        cursor.execute("""
                                   UPDATE appstore_label_privacy
                                   SET
                                       privacy_flag = ?,
                                       privacy_flag_type = ?
                                   WHERE app_id = ?
                               """, (
                            0,
                            "404",
                            app_id
                        ))
                except Exception as e:
                    print(f"❌ insert fail: {e}")
                    logger.error(f"insert failed: {json_str}")
                    continue  # Skip this line and move to the next one
        elif table_name == "google_label_privacy":
            for line in file:
                json_str = line.strip()
                match = re.search(reg_str, json_str)
                if match:
                    app_id = match.group(1)
                    cursor.execute("""
                           UPDATE google_label_privacy
                           SET
                               label_flag = ?,
                               label_flag_type = ?
                           WHERE app_id = ?
                       """, (
                        0,
                        "empty privacy block",
                        app_id
                    ))
                else:
                    logger.error(json_str)
                    print(f"❌ error:{json_str}")
        elif table_name == "appstore_appInfo":
            if reg_str == "sub_privacy_url":
                try:
                    data = json.load(file)
                    for item in data:
                        app_id = item.get('id')
                        sub_url = json.dumps(
                            item["sub-section_urls"]) if "sub-section_urls" in item else None  # 为空时存储 None

                        try:
                            cursor.execute("""
                                UPDATE appstore_appInfo
                                SET
                                    new_sub_privacy_url = ?
                                WHERE app_id = ?
                            """, (
                                sub_url,
                                app_id
                            ))
                        except Exception as e:
                            print(f"❌ insert fail: {e}")
                            logger.error(f"insert failed: {item}")
                            continue  # Skip this line and move to the next one
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse fail: {e}")
                    logger.error(item)

                except Exception as e:
                    print(f"❌ JSON fail: {e}")
                    logger.error(item)
            elif reg_str == "":
                lines = file.readlines()
                lines = lines[1:-1]

                for line in lines:
                    json_str = line.strip()
                    app_id = json_str.strip('",')
                    try:
                        cursor.execute("""
                                   UPDATE appstore_appInfo
                                   SET
                                       access = ?
                                   WHERE app_id = ?
                               """, (
                            0,
                            app_id
                        ))
                    except Exception as e:
                        print(f"❌ insert fail: {e}")
                        logger.error(f"insert failed: {json_str}")
                        continue  # Skip this line and move to the next one
            else:
                for line in file:
                    json_str = line.strip()
                    match = re.search(reg_str, json_str)

                    if not match:
                        print(f"❌ cant find json，jump: {json_str}")
                        logger.error(json_str)
                        continue

                    json_str = match.group()
                    try:
                        json_str = json_str.replace("None", "null")
                        data = json.loads(json_str)
                        try:
                            cursor.execute("""
                                UPDATE appstore_appInfo
                                SET
                                    name = ?,
                                    app_url = ?,
                                    privacy_url = ?,
                                    sub_privacy_url.json = ?
                                WHERE app_id = ?
                            """, (
                                data.get("name"),
                                data.get("app_url"),
                                data.get("privacy_url") if data.get("privacy_url") is not None else None,
                                json.dumps(data.get("sub-section_urls")) if data.get("sub-section_urls") is not None else None,
                                data.get("id")
                            ))
                        except Exception as e:
                            print(f"❌ insert fail: {e}")
                            logger.error(f"insert failed: {json_str}")
                            continue  # Skip this line and move to the next one
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON parse fail: {e}")
                        logger.error(json_str)
                        continue
                    except Exception as e:
                        print(f"❌ JSON fail: {e}")
                        logger.error(json_str)
                        continue  # Skip this line and move to the next one
        else:
            if reg_str == "sub_privacy_url":
                try:
                    data = json.load(file)

                    for item in data:
                        app_id = item.get('id')
                        sub_url = json.dumps(item["sub-section_urls"]) if "sub-section_urls" in item else None  # 为空时存储 None

                        try:
                            cursor.execute("""
                                UPDATE google_appInfo
                                SET
                                    new_sub_privacy_url = ?
                                WHERE app_id = ?
                            """, (
                                sub_url,
                                app_id
                            ))
                        except Exception as e:
                            print(f"❌ insert fail: {e}")
                            logger.error(f"insert failed: {item}")
                            continue  # Skip this line and move to the next one
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse fail: {e}")
                    logger.error(item)

                except Exception as e:
                    print(f"❌ JSON fail: {e}")
                    logger.error(item)
            else:
                for line in file:
                    json_str = line.strip()
                    match = re.search(reg_str, json_str)

                    if not match:
                        print(f"❌ cant find json，jump: {json_str}")
                        logger.error(json_str)
                        continue

                    json_str = match.group()
                    try:
                        json_str = json_str.replace("None", "null")
                        data = json.loads(json_str)
                        try:
                            cursor.execute("""
                                UPDATE google_appInfo
                                SET
                                    name = ?,
                                    app_url = ?,
                                    privacy_url = ?,
                                    sub_privacy_url.json = ?,
                                    installs = ?,
                                    developerEmail = ?,
                                    developerWebsite = ?,
                                    score = ?,
                                    ratings = ?,
                                    reviews = ?
                                WHERE app_id = ?
                            """, (
                                data.get("title"),
                                data.get("app_url"),
                                data.get("privacyPolicy") if data.get("privacyPolicy") is not None else None,
                                json.dumps(data.get("sub-section_urls")) if data.get(
                                    "sub-section_urls") is not None else None,
                                data.get("installs").replace(",", "").replace("+", "").strip() if data.get(
                                    "installs") is not None else None,  # 清理 installs
                                data.get("developerEmail") if data.get("developerEmail") is not None else None,
                                data.get("developerWebsite") if data.get("developerWebsite") is not None else None,
                                float(data.get("score")) if data.get("score") is not None else None,
                                int(data.get("ratings")) if data.get("ratings") is not None else None,
                                int(data.get("reviews")) if data.get("reviews") is not None else None,
                                str(data.get("app_id"))
                            ))
                        except Exception as e:
                            print(f"❌ insert fail: {e}")
                            logger.error(f"insert failed: {json_str}")
                            continue  # Skip this line and move to the next one
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON parse fail: {e}")
                        logger.error(json_str)
                        continue
                    except Exception as e:
                        print(f"❌ JSON fail: {e}")
                        logger.error(json_str)
                        continue  # Skip this line and move to the next one
    return

def handel_appstore_app_info():
    logger = GetCommon.getLogger("AppstoreData")
    table_name = "appstore_appInfo"
    reg_str = r"\{.*\}$"
    # delete_data(table_name)
    # create_table(table_name)
    # alter_table(table_name)
    # insert_data(r"AppInfo_appstore\appInfo_data.json", table_name, "",logger)
    # update_data(r"Logger\AppStorePrivacyLoop1_warning.log", table_name, reg_str,logger)
    # update_data(r"Logger\AppStorePrivacyLoop1_error.log", table_name, reg_str,logger)
    # update_data(r"Logger\AppstoreData_error.log", table_name, reg_str,logger)
    # update_data(r"AppInfo_appstore\loop2\cant_open_ids.json", table_name, "",logger)
    # update_data(r"AppInfo_appstore\loop3\cant_open_ids.json", table_name, "",logger)
    update_data(r"AppInfo_appstore\loop4\sub_privacy_url.json", table_name,"sub_privacy_url",logger)
    update_sub_privacy_url_if_equal(table_name)
    get_sub_privacy_url_if_equal_is_0(table_name,r"AppInfo_appstore\loop4\diff_sub_privacy_url.json")

    # import_data(table_name)


def update_sub_privacy_url_if_equal(table_name):
    cursor.execute("""
            UPDATE {}
            SET sub_privacy_url_if_equal = CASE
                WHEN COALESCE(sub_privacy_url, '') = COALESCE(new_sub_privacy_url, '') THEN 1                
                ELSE 0
            END
        """.format(table_name))


def get_sub_privacy_url_if_equal_is_0(table_name,target_path):
    try:
        sql = f"""
            SELECT app_id, privacy_url, sub_privacy_url, new_sub_privacy_url
            FROM {table_name}
            WHERE sub_privacy_url_if_equal = 0
        """
        cursor.execute(sql)

        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "privacy_url": row[1],
                "sub_privacy_url": row[2],
                "new_sub_privacy_url": row[3]
            })

        GetCommon.save_new_json_file(target_path, result)

    except Exception as e:
        print(f"fail: {e}")


def handel_google_app_info():
    logger = GetCommon.getLogger("GoogleData")
    table_name = "google_appInfo"
    # delete_data(table_name)
    # create_table(table_name)
    # alter_table(table_name)
    # insert_data(r"AppInfo_google\appInfo_google.json", table_name,"",logger)
    # update_data(r"Logger\GooglePlayPrivacyLoop1_warning.log", table_name,r"\{.*\}$",logger)
    # update_data(r"Logger\GooglePlayPrivacyLoop1_error.log", table_name,r"\{.*\}$",logger)
    # update_data(r"Logger\GoogleData_error.log", table_name,r"\{.*\}$",logger)
    # update_data(r"AppInfo_google\loop4\sub_privacy_url.json", table_name,"sub_privacy_url",logger)
    # update_sub_privacy_url_if_equal(table_name)
    get_sub_privacy_url_if_equal_is_0(table_name,r"AppInfo_google\loop4\diff_sub_privacy_url.json")
    # import_data(table_name)


def get_data_count_by_condition(table_name, query_column, query_text,flag):
    try:
        if flag == "count":
            query = f"SELECT COUNT(*) FROM {table_name} WHERE {query_column} = ?"

            cursor.execute(query, (query_text,))

            result = cursor.fetchone()

            return result[0] if result else 0
        else:
            query = f"SELECT * FROM {table_name} WHERE {query_column} = ?"
            cursor.execute(query, (query_text,))
            result = cursor.fetchone()
            return result

    except Exception as e:
        print(f"fail: {e}")
        return 0

def handel_google_label_privacy():
    logger = GetCommon.getLogger("GoogleData")
    # delete_data("google_label_privacy")
    # create_table("google_label_privacy")
    insert_data(r"AppInfo_google\appInfo_google.json", "google_label_privacy","",logger)
    update_data(r"Logger\GooglePlayLabel_error.log", "google_label_privacy",r"id=([^&]+)",logger)
    import_data("google_label_privacy")

def handel_appstore_label_privacy():
    table_name = "appstore_label_privacy"
    logger = GetCommon.getLogger("AppstoreData")
    # delete_data(table_name)
    # create_table(table_name)
    insert_data(r"AppInfo_appstore\appInfo_data.json", table_name,"",logger)
    update_data(r"AppInfo_appstore\loop2\error_appId_label.json",table_name,"label",logger)
    update_data(r"AppInfo_appstore\loop2\cant_open_ids.json",table_name,"privacy",logger)

    import_data(table_name)


if __name__ == "__main__":
    conn = sqlite3.connect("my_database.db")
    cursor = conn.cursor()

    # handel_google_app_info()
    handel_appstore_app_info()
    # handel_google_label_privacy()
    # handel_appstore_label_privacy()

    conn.commit()

    # table_name = "google_appInfo"
    # result = get_data_count_by_condition(table_name,"app_id","ru.yandex.translate","data")
    # if result:
    #     print("results:", result)
    # else:
    #     print("cant find id_info")

    conn.close()
