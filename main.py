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

# Vue 项目路径
vue_project_path = r"E:\ui_generator"

TXT_PATH = 'backend/Introduction/'
IMAGE_PATH = 'screenshot'
if not os.path.exists(IMAGE_PATH):
    os.makedirs(IMAGE_PATH)

# 启动 Vue 项目
def start_vue_project():
    # 进入 Vue 项目目录并启动开发服务器
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


def take_screenshot(index, driver):
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


def main_process():
    chrome_driver_path = r"chromedriver-win64\chromedriver.exe"
    # 配置 Selenium 使用 Chrome 浏览器
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)  # 让 Chrome 保持打开，不会自动关闭
    options.add_argument("--start-maximized")  # 启动时窗口最大化
    options.add_argument("--disable-blink-features=AutomationControlled")  # 规避检测
    # options.add_argument("--headless")  # 无头模式
    # options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    # options.add_argument("--window-size=1280,800")  # 设置窗口大小

    # 启动浏览器
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

    # 访问 Vue 项目
    driver.get("http://localhost:8080/")

    take_screenshot('1-1', driver)

    try:
        sidebarItems = driver.find_element(By.ID, 'menu')
        parent_items = sidebarItems.find_elements(By.CLASS_NAME, 'parent-menu')
        for index, parent in enumerate(parent_items):
            try:
                sub_menu = parent.find_element(By.XPATH, ".//following-sibling::ul")  # 这里假设子菜单是 <ul> 标签
                if not sub_menu.is_displayed():
                    parent.click()  # **如果子目录未显示，则点击父目录展开**
                    time.sleep(1)  # 等待展开
            except:
                print("无法找到子菜单，可能结构不同")

            sub_menus = parent.find_elements(By.XPATH, ".//following-sibling::ul//li")
            for sub_index, sub_item in enumerate(sub_menus):
                sub_item.click()
                menu_index = str(index+1)+'-'+str(sub_index+1)
                if menu_index != '1-1':
                    take_screenshot(menu_index, driver)


    except Exception as e:
        print("无法找到侧边栏目录:", e)

    # 关闭浏览器
    driver.quit()

# 主函数
def main():
    # 启动 Vue 项目
    # vue_process = start_vue_project()

    # 等待 Vue 项目启动
    # time.sleep(10)

    # try:
        # 截图
    main_process()
    # finally:
    #     # 关闭 Vue 项目
    #     stop_vue_project(vue_process)


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


def generate_word_template():
    doc = Document('template.docx')

    main_info = {
        'title': '共享充电宝后台管理系统V1.0',
        'table': [
            {'version': 'v1.0', 'date': '2025-02-18', 'name': '张三', 'info': '初始版本'},
            {'version': 'v1.1', 'date': '2025-03-15', 'name': '张三', 'info': '增加数据统计页面'},
        ]
    }

    config = [
        {
            'name': '环境描述',
            'subsection': [
                {
                    'name': '开发的硬件环境',
                    'content': '开发的硬件环境：处理器AMD 7900X，内存32GB，硬盘2TB，显卡AMDRX 7900 XT'
                },
                {
                    'name': '运行的硬件环境',
                    'content': '运行的硬件环境：CPU32核以上，内存32G以上，硬盘空间不低于400G，带宽不低于30Mbps'
                }
            ]
        },
        {
            'name': '开发目的',
            'content': '该软件旨在解决电动车充电过程中的管理难题，提高充电桩的使用效率，提升用户体验，支持绿色出行。'
        },
        {
            'name': '功能描述',
            'content': '智能电动车充电桩控制程序主要功能包括充电管理、用户身份验证、实时监控和数据分析。用户可以通过手机应用或网页端查看充电桩的状态、剩余电量和充电时间，并进行远程启动和停止充电。此外，系统支持多用户管理，确保不同用户的充电记录和费用独立。充电桩管理模块可实现故障报警和维护提示，确保设备正常运行。数据分析模块对充电数据进行统计和分析，帮助运营方优化充电桩布局，提高使用效率。'
        }
    ]

    main_content = {
        'title': '使用说明',
        'subsection': []
    }

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

    doc.save('template_manual.docx')


if __name__ == "__main__":
    # main()
    generate_word_template()