import json
import os
import re

import GetCommon

def make_diff():
    # C:\Users\smile\PycharmProjects\pythonProject\AppInfo_google\appInfo_google_original.json
    a = GetCommon.get_app_info(r"AppInfo_google\appInfo_google_original.json")
    b = set(a)
    print(len(a))
    print(len(b))
    GetCommon.save_new_json_file(r"AppInfo_google\Untitled-2.json",list(b))

def make_file():
    for i in range(1,40):
        with open(f"AppInfo_google/appInfo_google_new_{i}.json", "w", encoding="utf-8") as f:
            pass  # 什么都不写，文件会被创建

def del_file():
    # 指定目录
    folder_path = r"C:\Users\smile\PycharmProjects\pythonProject\Label_google"

    # 读取文件内容，获取所有字符串
    with open(r"AppInfo_google/get_content_null_google_label.json", "r", encoding="utf-8") as f:
        target_names = [line.strip() for line in f.readlines()]  # 去除空格和引号
    print(target_names)

    # 遍历目录下的所有文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # 如果 name_part 在目标字符串列表中，则删除文件
        if filename in target_names:
            os.remove(file_path)
            print(f"已删除文件: {file_path}")

    print("文件删除完成。")

import os
import json


def split_file(input_file, output_prefix, lines_per_file=5000):
    with open(input_file, 'r', encoding='utf-8') as infile:
        file_count = 1
        lines = []

        for line_number, line in enumerate(infile, start=1):
            lines.append(line)

            # 每 5000 行写入一个新文件
            if line_number % lines_per_file == 0:
                output_file = f"{output_prefix}_{file_count}.json"
                with open(output_file, 'w', encoding='utf-8') as outfile:
                    outfile.writelines(lines)
                print(f"✅ 已写入: {output_file}")

                # 清空缓冲区
                lines = []
                file_count += 1

        # 处理剩余行
        if lines:
            output_file = f"{output_prefix}_{file_count}.json"
            with open(output_file, 'w', encoding='utf-8') as outfile:
                outfile.writelines(lines)
            print(f"✅ 已写入: {output_file}")


if __name__ == "__main__":
    # 指定目录（请替换成你的实际目录）
    directory_path = r"C:\Users\smile\PycharmProjects\pythonProject\Label_appstore"
    id_file_path = r"/AppInfo_appstore/handle_error_info/missing_ids.json"

    # del_file()
    # make_file

    split_file(r"AppInfo_google\diff_sub_privacy_url.json", r"AppInfo_google\diff_sub_privacy_url", 6000)

    # read_id()
    # make_diff()
    # C:\Users\smile\PycharmProjects\pythonProject\Label_google
    # C:\Users\smile\PycharmProjects\pythonProject\Policy_google
    # C:\Users\smile\PycharmProjects\pythonProject\Policy_appstore
    # GetCommon.get_file_name(r'C:\Users\smile\PycharmProjects\pythonProject\Policy_appstore',"Policy_appstore.json")
    # GetCommon.convert_upper(r"AppInfo_google\scategories_new.json",r"AppInfo_google\categories_target.json")

    # C:\Users\smile\PycharmProjects\pythonProject\AppInfo_appstore\appInfo_data_1.json
    # C:\Users\smile\PycharmProjects\pythonProject\AppInfo_google\Untitled-2.json
    #C:\Users\smile\PycharmProjects\pythonProject\AppInfo_google\appInfo_google_new.json
    #C:\Users\smile\PycharmProjects\pythonProject\AppInfo_google\appInfo_google.json
    # AppInfo_google\appInfo_google.json
    # GetCommon.filter_content(r"AppInfo_google\ids_successful.json",r"AppInfo_google\a.json",
    #                          r"AppInfo_google\diff.json")
    # GetCommon.filter_content(r"AppInfo_google\appInfo_google.json",r"AppInfo_google\appInfo_google_new.json",
    #                          r"AppInfo_google\diff.json")


