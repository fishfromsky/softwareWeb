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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend import settings

# Vue 项目路径
vue_project_path = os.path.join(os.path.dirname(BASE_DIR), 'webfront')


client = OpenAI(
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL
)


def write_env_file(username, datetime):
    env_file_path = os.path.join(os.path.dirname(BASE_DIR), 'webfront', 'user.json')

    user_dict = {
        'username': username,
        'datetime': datetime
    }

    with open(env_file_path, 'w') as json_file:
        json.dump(user_dict, json_file)

# 启动 Vue 项目
def start_vue_project(username, datetime):
    env = os.environ.copy()
    # 进入 Vue 项目目录并启动开发服务器
    write_env_file(username, datetime)
    process = subprocess.Popen(
        ["npm", "run", "serve"],
        cwd=vue_project_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    print("Vue 项目已启动...")
    return process

# 关闭 Vue 项目
def stop_vue_project(process):
    process.terminate()
    print("Vue 项目已关闭。")

def generate_config(PLATFORM, username, datetime):
    with open(os.path.join(BASE_DIR, 'medium', username, datetime, 'menu.json'), 'r', encoding='utf-8') as f:
        menu = json.load(f)
        f.close()
    json_str = json.dumps(menu, ensure_ascii=False)
    MESSAGE = [{'role': 'system', 'content': 'You are a helpful programmer and product manager'}]
    question = f"""
    现在有一个名为{PLATFORM}的后台管理系统,其侧边栏为{json_str},请为其设计如下的一些配置信息:
    1.开发硬件环境,包括处理器,内存,硬盘,显卡等配置信息.
    2.运行硬件环境,包括处理器,内存,硬盘,带宽等配置信息.
    3.开发目的,说明文字不少于300字.
    4.功能描述,说明文字不少于600字.
    5.以Object形式返回，返回内容开始以'{{'开头，不需要额外任何解释说明.
    6.Object的Key也需要使用双引号引起来
    6.语言为中文
    7.配置信息为纯文字说明,不需要换行
    """
    query = {'role': 'user', 'content': question}
    MESSAGE.append(query)
    completion = client.chat.completions.create(
        model="qwen-coder-plus-latest",
        messages=MESSAGE
    )
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict['choices'][0]['message']['content']
    return content


def take_screenshot(index, driver, IMAGE_PATH):
    script = f"""
        window.dataLoaded = false;
        window.addEventListener('data-loaded_{index}', () => {{
            window.dataLoaded = true;
        }});
        """
    driver.execute_script(script)
    wait = WebDriverWait(driver, 500)
    wait.until(lambda d: d.execute_script("return window.dataLoaded;"))
    time.sleep(2)

    screenshot_path = os.path.join(IMAGE_PATH, index+'.png')
    driver.save_screenshot(screenshot_path)
    print(f"截图已保存为 {screenshot_path}")


def main_process(IMAGE_PATH):
    chrome_driver_path = os.path.join(os.path.dirname(BASE_DIR), "chromedriver-win64", "chromedriver.exe")
    # 配置 Selenium 使用 Chrome 浏览器
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)  # 让 Chrome 保持打开，不会自动关闭
    options.add_argument("--start-maximized")  # 启动时窗口最大化
    options.add_argument("--disable-blink-features=AutomationControlled")  # 规避检测
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    options.add_argument("--window-size=2880,1562")  # 设置窗口大小

    # 启动浏览器
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

    driver.get('http://localhost:8080/login')
    take_screenshot('0-0', driver, IMAGE_PATH)

    driver.get('http://localhost:8080/register')
    take_screenshot('0-1', driver, IMAGE_PATH)

    # 访问 Vue 项目
    driver.get("http://localhost:8080/")

    take_screenshot('1-1', driver, IMAGE_PATH)

    try:
        sidebarItems = driver.find_element(By.ID, 'menu')
        parent_items = sidebarItems.find_elements(By.CLASS_NAME, 'parent-menu')
        for index, parent in enumerate(parent_items):
            try:
                sub_menu = parent.find_element(By.XPATH, ".//following-sibling::ul")  # 这里假设子菜单是 <ul> 标签
                if not sub_menu.is_displayed():
                    # 折叠其他已经展开的父菜单
                    for other_parent in parent_items:
                        if other_parent != parent:  # 排除当前父菜单
                            try:
                                other_sub_menu = other_parent.find_element(By.XPATH, ".//following-sibling::ul")
                                if other_sub_menu.is_displayed():
                                    other_parent.click()  # 点击其他父菜单以折叠其子菜单
                                    time.sleep(1)  # 等待折叠动画完成
                            except:
                                print("无法折叠其他父菜单，可能结构不同")

                    # 展开当前父菜单
                    parent.click()  # 点击当前父菜单以展开子菜单
                    time.sleep(1)  # 等待展开动画完成
            except:
                print("无法找到子菜单，可能结构不同")

            sub_menus = parent.find_elements(By.XPATH, ".//following-sibling::ul//li")
            for sub_index, sub_item in enumerate(sub_menus):
                sub_item.click()
                menu_index = str(index+1)+'-'+str(sub_index+1)
                if menu_index != '1-1':
                    take_screenshot(menu_index, driver, IMAGE_PATH)

    except Exception as e:
        print("无法找到侧边栏目录:", e)

    # 关闭浏览器
    driver.quit()

# 主函数
def main(username, datetime, IMAGE_PATH):
    # 启动 Vue 项目
    vue_process = start_vue_project(username, datetime)

    # 等待 Vue 项目启动
    time.sleep(10)

    # try:
        # 截图
    main_process(IMAGE_PATH)
    # finally:
    #     # 关闭 Vue 项目
    stop_vue_project(vue_process)


def read_txt_file(filename):
    context = {}
    line_data = []
    flag = False
    index = 0
    with open(filename, 'r', encoding='utf-8') as fr:
        lines = fr.readlines()
        for line in lines:
            if line.__contains__('*****'):
                flag = True
                continue
            if flag:
                if index == 0:
                    context['name'] = line.replace('\n', '')+'页面'
                    index += 1
                else:
                    line_data.append(line)

    content = ''.join(line_data).replace('\n\n', '\n')
    context['content'] = content
    return context


def get_image_info(file):
    index = file.split('.')[0]
    for file in os.listdir(IMAGE_PATH):
        if file.split('.')[0] == index:
            return os.path.join(IMAGE_PATH, file)


def generate_word_template(title, user, time, TXT_PATH):
    doc = Document(os.path.join(BASE_DIR, 'medium', 'template.docx'))

    main_info = {
        'title': title,
        'table': [
            {'version': 'v1.0', 'date': time, 'name': user, 'info': '初始版本'},
        ]
    }

    config = [
        {
            'name': '环境描述',
            'subsection': []
        },
        {
            'name': '开发目的',
            'content': ''
        },
        {
            'name': '功能描述',
            'content': ''
        }
    ]

    main_content = {
        'title': '使用说明',
        'subsection': []
    }

    config_content = generate_config(title, user, time)
    config_content = json.loads(config_content, strict=False)

    for i, key in enumerate(config_content.keys()):
        if i < 2:
            config[0]['subsection'].append({
                'name': key,
                'content': config_content[key]
            })
        else:
            config[i-1]['content'] = config_content[key]

    for paragraph in doc.paragraphs:
        if '{{ title }}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{ title }}', main_info['title'])

    table = doc.tables[0]
    for i, row_data in enumerate(main_info['table']):
        table.cell(i + 1, 0).text = row_data['version']
        table.cell(i + 1, 1).text = str(row_data['date'])
        table.cell(i + 1, 2).text = row_data['name']
        table.cell(i + 1, 3).text = row_data['info']

    for section in config:
        doc.add_page_break()
        doc.add_heading(section['name'], level=1)
        if 'subsection' in section.keys():
            for subsection in section['subsection']:
                doc.add_heading(subsection['name'], level=2)
                doc.add_paragraph(subsection['content'])
        else:
            doc.add_paragraph(section['content'])

    for file in os.listdir(TXT_PATH):
        filename = os.path.join(TXT_PATH, file)
        context = read_txt_file(filename)
        image = get_image_info(file)
        context['image'] = image
        main_content['subsection'].append(context)

    doc.add_page_break()
    doc.add_heading(main_content['title'], level=1)
    for section in main_content['subsection']:
        doc.add_heading(section['name'], level=2)
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        paragraph.add_run().add_picture(section['image'], width=Inches(5.5))
        doc.add_paragraph(section['content'])

    doc_save_path = os.path.join(BASE_DIR, 'static', user, time, 'template_manual.docx')
    doc.save(doc_save_path)


if __name__ == '__main__':
    platform = sys.argv[1]
    username = sys.argv[2]
    datetime = sys.argv[3]

    final_path = os.path.join(BASE_DIR, 'static', username, datetime)
    if not os.path.exists(final_path):
        os.makedirs(final_path)

    TXT_PATH = os.path.join(BASE_DIR, 'Introduction', username, datetime)
    IMAGE_PATH = os.path.join(BASE_DIR, 'screenshot', username, datetime)
    if not os.path.exists(IMAGE_PATH):
        os.makedirs(IMAGE_PATH)
    if not os.path.exists(TXT_PATH):
        os.makedirs(TXT_PATH)

    main(username, datetime, IMAGE_PATH)
    generate_word_template(platform, username, datetime, TXT_PATH)
