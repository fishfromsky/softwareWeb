import subprocess
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from openai import OpenAI
import json
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend import settings

# Vue 项目路径
vue_project_path = os.path.join(os.path.dirname(BASE_DIR), "webfront")

chrome_user_path = os.path.join(BASE_DIR, "chrome_user_data")


client = OpenAI(
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL
)


def exponential_search(json_data):
    # 随机选择一个起始点
    keys = json_data.keys()
    for key in keys:
        next_key = key
        if json_data[key] == False:
            return next_key
    return -1


def write_env_file(path):
    env_file_path = os.path.join(path, "user.json")

    user_dict = {
        "username": username,
        "datetime": datetime
    }

    with open(env_file_path, "w") as json_file:
        json.dump(user_dict, json_file)
        json_file.close()


def modify_port_file_start(path):  # 将对应端口改为True
    with open(path, "r", encoding="utf-8") as fr:
        json_data = json.load(fr)
        fr.close()

    port = exponential_search(json_data)
    json_data[port] = True

    with open(path, "w", encoding="utf-8") as fw:
        json.dump(json_data, fw)
        fw.close()

    return port


def modify_port_file_end(path, port):
    with open(path, "r", encoding="utf-8") as fr:
        json_data = json.load(fr)
        fr.close()

    json_data[port] = False

    with open(path, "w", encoding="utf-8") as fw:
        json.dump(json_data, fw)
        fw.close()


def copy_file(file_path1, file_path2):
    shutil.copytree(file_path1, file_path2)


# 启动 Vue 项目
def start_vue_project(username, datetime):

    virtual_vue_path = os.path.join(BASE_DIR, "virtual_vue_project", username, datetime, "webfront")
    copy_file(vue_project_path, virtual_vue_path)

    # 进入 Vue 项目目录并启动开发服务器
    write_env_file(virtual_vue_path)
    json_path = os.path.join(BASE_DIR, "llmserver", "port.json")

    port = modify_port_file_start(json_path)

    print("正在编译")
    process = subprocess.Popen(
        ["npm", "install"],
        cwd=virtual_vue_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())

    print("编译完成")

    process = subprocess.Popen(
        ["npm", "run", "serve", "--", "--port", str(port)],
        cwd=virtual_vue_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    success = False
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())
            if "App running at:" in output or "Local:   http://localhost:" in output:
                success = True
                print("Vue 项目已成功启动！")
                break

    if not success:
        print("Vue 项目启动失败！")

    return process, port, virtual_vue_path

# 关闭 Vue 项目
def stop_vue_project(process, port, virtual_vue_path):
    process.terminate()

    json_path = os.path.join(BASE_DIR, "llmserver", "port.json")

    modify_port_file_end(json_path, port)

    virtual_vue_path = os.path.dirname(virtual_vue_path)
    shutil.rmtree(virtual_vue_path)
    print("Vue 项目已关闭。")

def generate_config(PLATFORM, username, datetime):
    with open(os.path.join(BASE_DIR, "medium", username, datetime, "menu.json"), "r", encoding="utf-8") as f:
        menu = json.load(f)
        f.close()
    json_str = json.dumps(menu, ensure_ascii=False)
    MESSAGE = [{"role": "system", "content": "You are a helpful programmer and product manager"}]
    question = f"""
    现在有一个名为{PLATFORM}的后台管理系统,其侧边栏为{json_str},请为其设计如下的一些配置信息:
    1.开发硬件环境,包括处理器,内存,硬盘,显卡等配置信息.
    2.运行硬件环境,包括处理器,内存,硬盘,带宽等配置信息.
    3.开发目的,说明文字不少于300字.
    4.功能描述,说明文字不少于600字.
    5.以Object形式返回，返回内容开始以"{{"开头，不需要额外任何解释说明.
    6.Object的Key也需要使用双引号引起来
    6.语言为中文
    7.配置信息为纯文字说明,不需要换行
    """
    query = {"role": "user", "content": question}
    MESSAGE.append(query)
    completion = client.chat.completions.create(
        model="qwen-coder-plus-latest",
        messages=MESSAGE
    )
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict["choices"][0]["message"]["content"]
    return content


def take_screenshot(index, driver, IMAGE_PATH):
    script = f"""
        window.dataLoaded = false;
        window.addEventListener("data-loaded_{index}", () => {{
            window.dataLoaded = true;
        }});
        """
    driver.execute_script(script)
    wait = WebDriverWait(driver, 500)
    wait.until(lambda d: d.execute_script("return window.dataLoaded;"))
    time.sleep(2)

    screenshot_path = os.path.join(IMAGE_PATH, index+".png")
    driver.save_screenshot(screenshot_path)
    print(f"截图已保存为 {screenshot_path}")


def main_process(IMAGE_PATH, port, username, datetime):
    user_path = os.path.join(chrome_user_path, username, datetime)
    if not os.path.exists(user_path):
        os.makedirs(user_path)

    chrome_driver_path = os.path.join(os.path.dirname(BASE_DIR), "chromedriver", "chromedriver")
    # 配置 Selenium 使用 Chrome 浏览器
    options = webdriver.ChromeOptions()
    options.binary_location = os.path.join(os.path.dirname(BASE_DIR), "chrome", "chrome")
    options.add_argument("--disable-application-cache")
    options.add_argument("--no-sandbox")  # 禁用Linux沙箱机制
    options.add_argument(f"--user-data-dir={user_path}")  # 配置独立的用户数据目录
    options.add_argument("--disable-blink-features=AutomationControlled")  # 规避检测
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    options.add_argument("--window-size=2580,1562")  # 设置窗口大小

    # 设置字体
    options.add_argument('--font-cache-shared-handle=0')
    options.add_argument('--lang=zh-CN')

    # 启动浏览器
    driver = webdriver.Chrome(service=Service(chrome_driver_path, port=0), options=options)

    driver.get(f"http://localhost:{port}/login")
    take_screenshot("0-0", driver, IMAGE_PATH)

    driver.get(f"http://localhost:{port}/register")
    take_screenshot("0-1", driver, IMAGE_PATH)

    # 访问 Vue 项目
    driver.get(f"http://localhost:{port}/")
    take_screenshot("1-1", driver, IMAGE_PATH)

    try:
        sidebarItems = driver.find_element(By.ID, "menu")
        parent_items = sidebarItems.find_elements(By.CLASS_NAME, "parent-menu")
        for index, parent in enumerate(parent_items):

            parent.click()
            time.sleep(1)  # 等待

            sub_menus = parent.find_elements(By.XPATH, ".//following-sibling::ul//li")
            for sub_index, sub_item in enumerate(sub_menus):
                sub_item.click()
                menu_index = str(index+1)+"-"+str(sub_index+1)
                if menu_index != "1-1":
                    take_screenshot(menu_index, driver, IMAGE_PATH)

    except Exception as e:
        print("无法找到侧边栏目录:", e)

    # 关闭浏览器
    driver.quit()

    shutil.rmtree(user_path)

# 主函数
def main(username, datetime, IMAGE_PATH):
    # 启动 Vue 项目
    vue_process, port, virtual_vue_path = start_vue_project(username, datetime)
    # try:
        # 截图
    main_process(IMAGE_PATH, port, username, datetime)
    # finally:
    #     # 关闭 Vue 项目
    stop_vue_project(vue_process, port, virtual_vue_path)


def read_txt_file(filename):
    context = {}
    line_data = []
    flag = False
    index = 0
    with open(filename, "r", encoding="utf-8") as fr:
        lines = fr.readlines()
        for line in lines:
            if line.__contains__("*****"):
                flag = True
                continue
            if flag:
                if index == 0:
                    context["name"] = line.replace("\n", "")+"页面"
                    index += 1
                else:
                    line_data.append(line)

    content = "".join(line_data).replace("\n\n", "\n")
    context["content"] = content
    return context


def get_image_info(file):
    index = file.split(".")[0]
    for file in os.listdir(IMAGE_PATH):
        if file.split(".")[0] == index:
            return os.path.join(IMAGE_PATH, file)


def generate_word_template(title, user, time, TXT_PATH):
    doc = Document(os.path.join(BASE_DIR, "medium", "template.docx"))

    main_info = {
        "title": title,
        "table": [
            {"version": "v1.0", "date": time, "name": user, "info": "初始版本"},
        ]
    }

    config = [
        {
            "name": "环境描述",
            "subsection": []
        },
        {
            "name": "开发目的",
            "content": ""
        },
        {
            "name": "功能描述",
            "content": ""
        }
    ]

    main_content = {
        "title": "使用说明",
        "subsection": []
    }

    config_content = generate_config(title, user, time)
    config_content = json.loads(config_content, strict=False)

    for i, key in enumerate(config_content.keys()):
        if i < 2:
            config[0]["subsection"].append({
                "name": key,
                "content": config_content[key]
            })
        else:
            config[i-1]["content"] = config_content[key]

    for paragraph in doc.paragraphs:
        if "{{ title }}" in paragraph.text:
            paragraph.text = paragraph.text.replace("{{ title }}", main_info["title"])

    table = doc.tables[0]
    for i, row_data in enumerate(main_info["table"]):
        table.cell(i + 1, 0).text = row_data["version"]
        table.cell(i + 1, 1).text = str(row_data["date"])
        table.cell(i + 1, 2).text = row_data["name"]
        table.cell(i + 1, 3).text = row_data["info"]

    for section in config:
        doc.add_page_break()
        doc.add_heading(section["name"], level=1)
        if "subsection" in section.keys():
            for subsection in section["subsection"]:
                doc.add_heading(subsection["name"], level=2)
                doc.add_paragraph(subsection["content"])
        else:
            doc.add_paragraph(section["content"])

    for file in os.listdir(TXT_PATH):
        filename = os.path.join(TXT_PATH, file)
        context = read_txt_file(filename)
        image = get_image_info(file)
        context["image"] = image
        main_content["subsection"].append(context)

    doc.add_page_break()
    doc.add_heading(main_content["title"], level=1)
    for section in main_content["subsection"]:
        doc.add_heading(section["name"], level=2)
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        paragraph.add_run().add_picture(section["image"], width=Inches(5.5))
        doc.add_paragraph(section["content"])

    doc_save_path = os.path.join(BASE_DIR, "static", user, time, "template_manual.docx")
    doc.save(doc_save_path)
    print('Word 文档生成完毕')


if __name__ == "__main__":
    platform = sys.argv[1]
    username = sys.argv[2]
    datetime = sys.argv[3]

    final_path = os.path.join(BASE_DIR, "static", username, datetime)
    if not os.path.exists(final_path):
        os.makedirs(final_path)

    TXT_PATH = os.path.join(BASE_DIR, "Introduction", username, datetime)
    IMAGE_PATH = os.path.join(BASE_DIR, "screenshot", username, datetime)
    if not os.path.exists(IMAGE_PATH):
        os.makedirs(IMAGE_PATH)
    if not os.path.exists(TXT_PATH):
        os.makedirs(TXT_PATH)

    main(username, datetime, IMAGE_PATH)
    generate_word_template(platform, username, datetime, TXT_PATH)
