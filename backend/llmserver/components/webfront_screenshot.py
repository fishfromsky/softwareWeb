import subprocess
import os
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from docx import Document
from docx.shared import Pt
from docx.shared import RGBColor
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import json
import sys
import shutil
import re
from utils import add_multi_level, add_manual, add_pager_header
import threading
from natsort import natsorted


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


def write_env_file(path, username, datetime, colors):
    env_file_path = os.path.join(path, "user.json")

    if isinstance(colors, str):
        colors_list = colors.split(',')
    else:
        colors_list = colors

    user_dict = {
        "username": username,
        "datetime": datetime,
        "colors": colors_list
    }

    with open(env_file_path, "w", encoding="utf-8") as json_file:
        json.dump(user_dict, json_file, ensure_ascii=False, indent=2)


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


def kill_process_by_port(port):  # 强制终止进程 (限于Linux系统)
    try:
        # 查找占用指定端口的进程ID
        command = f"lsof -i :{port} -t"
        pid = subprocess.check_output(command, shell=True)
        pid = int(pid.strip())

        # 尝试终止进程
        os.kill(pid, 15)  # 先尝试发送SIGTERM信号请求正常终止
        print(f"已向PID {pid}发送终止信号，等待进程正常结束...")

        # 确认进程是否已经结束，如果没有，则强制终止
        try:
            os.kill(pid, 0)  # 这个操作会抛出异常如果进程不存在
            os.kill(pid, 9)  # 如果进程还在运行，发送SIGKILL信号强制结束
            print(f"已强制终止PID {pid}")
        except OSError:
            print(f"PID {pid} 已正常结束")

    except subprocess.CalledProcessError:
        print(f"找不到端口号为 {port} 的进程")
    except ValueError:
        print("解析PID时出现错误")
    except OSError as e:
        print(f"无法终止进程: {e}")


# 启动 Vue 项目
def start_vue_project(username, datetime, colors):

    virtual_vue_path = os.path.join(BASE_DIR, "virtual_vue_project", username, datetime, "webfront")
    copy_file(vue_project_path, virtual_vue_path)

    # 进入 Vue 项目目录并启动开发服务器
    write_env_file(virtual_vue_path, username, datetime, colors)
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
    process.kill()

    json_path = os.path.join(BASE_DIR, "llmserver", "port.json")

    modify_port_file_end(json_path, port)

    kill_process_by_port(port)

    virtual_vue_path = os.path.dirname(virtual_vue_path)
    shutil.rmtree(virtual_vue_path)
    print("Vue 项目已关闭。")


@retry(stop=stop_after_attempt(10), wait=wait_exponential(multiplier=1, min=2, max=20))
def generate_config(PLATFORM, username, datetime):
    try:
        with open(os.path.join(BASE_DIR, "medium", username, datetime, "menu.json"), "r", encoding="utf-8") as f:
            menu = json.load(f)
            f.close()
        json_str = json.dumps(menu, ensure_ascii=False)
        MESSAGE = [{"role": "system", "content": "You are a helpful programmer and product manager"}]
        question = f"""
        现在有一个名为{PLATFORM}的后台管理系统，其侧边栏为{json_str}，请为其设计如下的一些配置信息：

        1. "开发硬件环境"：包括处理器、内存、硬盘、显卡等配置信息，不同配置信息之间通过分号标点隔开，以句号结束。
        2. "运行硬件环境"：包括处理器、内存、硬盘、带宽等配置信息，不同配置信息之间通过分号标点隔开，以句号结束。
        3. "开发目的"：确保生成“开发目的”的文字信息不少于300字。
        4. "功能描述"：对侧边栏每个父目录及其子目录进行一句话功能描述。
        5. "功能描述"内容以嵌套Object形式返回，第一层的每一个Key是父目录名称，Value是一个子Object，它的每一个Key是子目录名称，value是对应的功能描述。
        6. "功能描述"的Object中的每一个子Object的每一个键值对之间必须以英文逗号“,”分隔，禁止使用分号。
        7. 所有Object的Key必须使用双引号引起来。
        8. 生成的所有配置信息为纯文字说明，不需要换行。
        9. 返回内容为一个JSON格式的Object，以“{{”开头，“}}”结尾，中间不要插入任何解释或说明。

        ### 请从这里开始生成配置内容 ###
        """
        query = {"role": "user", "content": question}
        MESSAGE.append(query)
        completion = client.chat.completions.create(
            model="qwen-coder-plus-latest",
            messages=MESSAGE
        )
        data_dict = json.loads(completion.model_dump_json())
        content = data_dict["choices"][0]["message"]["content"]
        content = json.loads(content, strict=False)
        return content
    except Exception as e:
        raise e


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
    time.sleep(10)

    colors_data = driver.execute_script("return window.myColors || null;")
    username_data = driver.execute_script("return window.userName || null;")

    try:
        # 先保存主页面截图
        screenshot_path = os.path.join(IMAGE_PATH, f"{index}.png")
        driver.save_screenshot(screenshot_path)
        print(f"截图已保存为 {screenshot_path}")

        # 查找所有新增按钮
        add_buttons = driver.find_elements(By.CLASS_NAME, "add")
        print(f"找到 {len(add_buttons)} 个新增按钮")

        # 遍历每个新增按钮
        for btn_index, add_button in enumerate(add_buttons, 1):
            try:
                # 检查按钮是否可见和可点击
                if not add_button.is_displayed() or not add_button.is_enabled():
                    print(f"[{index}] 按钮 {btn_index} 不可见或不可点击，跳过")
                    continue

                # 滚动到按钮位置
                driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
                time.sleep(1)

                # 使用 JavaScript 点击按钮
                driver.execute_script("arguments[0].click();", add_button)
                print(f"[{index}] 点击新增按钮 {btn_index}")
                time.sleep(1)

                try:
                    # 等待对话框出现
                    dialog = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "el-dialog"))
                    )

                    if dialog.is_displayed():
                        # 保存对话框截图
                        dialog_screenshot_path = os.path.join(IMAGE_PATH, f"{index}-{btn_index}.png")
                        driver.save_screenshot(dialog_screenshot_path)
                        print(f"[{index}] 对话框截图已保存")

                        # 查找并点击取消按钮
                        cancel_button = dialog.find_element(By.CLASS_NAME, "cancel")
                        if cancel_button.is_displayed() and cancel_button.is_enabled():
                            driver.execute_script("arguments[0].click();", cancel_button)
                            print(f"[{index}] 关闭对话框")
                            time.sleep(1)
                    else:
                        print(f"[{index}] 对话框未显示")

                except Exception as e:
                    print(f"[{index}] 等待对话框超时或处理对话框时出错:")
                    print(f"  - 错误类型: {type(e).__name__}")
                    print(f"  - 错误信息: {str(e)}")
                    # 继续处理下一个按钮
                    continue

            except Exception as e:
                print(f"[{index}] 处理按钮 {btn_index} 时出错:")
                print(f"  - 错误类型: {type(e).__name__}")
                print(f"  - 错误信息: {str(e)}")
                continue

    except Exception as e:
        print(f"[{index}] 截图过程出错:")
        print(f"  - 错误类型: {type(e).__name__}")
        print(f"  - 错误信息: {str(e)}")


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
def main(username, datetime, IMAGE_PATH, colors):
    # 启动 Vue 项目
    vue_process, port, virtual_vue_path = start_vue_project(username, datetime, colors)
    # 截图
    main_process(IMAGE_PATH, port, username, datetime)
    # 关闭 Vue 项目
    stop_vue_project(vue_process, port, virtual_vue_path)


def read_txt_file(filename):
    """读取txt文件内容"""
    context = {}
    line_data = []
    flag = False
    index_local = 0
    with open(filename, "r", encoding="utf-8") as fr:
        lines = fr.readlines()
        for line in lines:
            if "*****" in line:
                flag = True
                continue
            if flag:
                if index_local == 0:
                    # 使用正则表达式清理文本
                    cleaned_line = re.sub(r'[^\w\u4e00-\u9fff]+', '', line)
                    context["name"] = cleaned_line + "页面"
                    index_local += 1
                else:
                    line_data.append(line)
    # 合并所有内容行
    content = "".join(line_data)

    # 使用正则表达式清理文本
    # 移除所有特殊字符，但保留中文、英文、数字、基本标点
    content = re.sub(r'[*{}\\/<>|]', '', content)

    # 处理多余的空白和换行
    content = re.sub(r'\n\s*\n', '\n', content)
    content = content.strip()

    context["content"] = content
    return context


def get_image_info(file):
    index = file.split(".")[0]
    try:
        image_files = os.listdir(IMAGE_PATH)
        for file_name in image_files:
            current_index = file_name.split(".")[0]
            if current_index == index:
                image_path = os.path.join(IMAGE_PATH, file_name)
                if os.path.exists(image_path):
                    return image_path
                else:
                    print(f"文件路径存在问题: {image_path}")

        print(f"警告: 未找到图片文件 {index}.*")
        return None
    except Exception as e:
        print(f"查找图片时出错: {str(e)}")
        return None


def get_sub_images(file):
    base_index = file.split(".")[0]  # 获取基础索引，如 "2-1"
    sub_images = []

    try:
        image_files = os.listdir(IMAGE_PATH)

        for image_file in image_files:
            if image_file.startswith(f"{base_index}-"):  # 匹配前缀
                image_path = os.path.join(IMAGE_PATH, image_file)
                if os.path.exists(image_path):
                    sub_images.append(image_path)

        if not sub_images:
            print(f"未找到 {base_index}-* 的子图片")

        return sorted(sub_images)  # 按文件名排序返回

    except Exception as e:
        print(f"查找子图片时出错: {str(e)}")
        return []

def generate_word_template(title, user, time, TXT_PATH):
    doc = Document(os.path.join(BASE_DIR, "medium", "template.docx"))
    version_str = "V1.0"
    main_info = {
        "title": title,
        "table": [{"version": version_str, "date": time, "name": user, "info": "初始版本"}]
    }
    config = [
        {"name": "环境描述", "subsection": []},
        {"name": "开发目的", "content": ""},
        {"name": "功能描述", "content": ""}
    ]
    main_content = {"title": "使用说明", "subsection": []}

    # 设置页眉
    section = doc.sections[0]
    header = section.header
    header_paragraph = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    header_paragraph.clear()
    run = header_paragraph.add_run(f"{title} {version_str}")
    run.font.name = "宋体"
    header_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

    # 替换 {{ title }} 为标题 + 操作手册
    for paragraph in doc.paragraphs:
        if "{{ title }}" in paragraph.text:
            paragraph.clear()
            run1 = paragraph.add_run(f"{title} {version_str}")
            run1.bold = True
            run1.font.name = "黑体"
            run1.font.size = Pt(45)

            run2 = paragraph.add_run("\n操作手册")
            run2.bold = True
            run2.font.name = "黑体"
            run2.font.size = Pt(40)
            run2.font.color.rgb = RGBColor(255, 0, 0)

            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            break

    # 生成配置信息
    config_content = generate_config(title, user, time)

    for i, key in enumerate(config_content.keys()):
        if i < 2:
            config[0]["subsection"].append({
                "name": key,
                "content": config_content[key]
            })
        else:
            config[i-1]["content"] = config_content[key]

    # 作者信息写入表格
    table = doc.tables[0]
    for i, row_data in enumerate(main_info["table"]):
        table.cell(i + 1, 0).text = row_data["version"]
        table.cell(i + 1, 1).text = str(row_data["date"])
        table.cell(i + 1, 2).text = row_data["name"]
        table.cell(i + 1, 3).text = row_data["info"]

    # 平台配置信息
    for section in config:
        doc.add_page_break()
        doc.add_heading(section["name"], level=1)
        if "subsection" in section.keys():
            for subsection in section["subsection"]:
                doc.add_heading(subsection["name"], level=2)
                doc.add_paragraph(subsection["content"])
        else:
            if type(section["content"]) == str:
                doc.add_paragraph(section["content"])
            else:
                # 添加带序号的段落
                doc = add_multi_level(doc, section["content"])

    # 添加第五部分：系统设计（架构图）
    doc.add_page_break()
    doc.add_heading("系统设计", level=1)
    doc.add_heading("系统架构图", level=2)
    try:
        system_img_path = os.path.join(BASE_DIR, "static", user, time, "system_architecture.png")
        if os.path.exists(system_img_path):
            para = doc.add_paragraph()
            para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            para.add_run().add_picture(system_img_path, width=Inches(5.5))
        else:
            print("⚠️ 未找到系统架构图:", system_img_path)
    except Exception as e:
        print(f"插入系统架构图失败: {e}")

        # 读取 TXT 并插入对应图片
    files = natsorted(os.listdir(TXT_PATH))
    for file in files:
        filename = os.path.join(TXT_PATH, file)
        context = read_txt_file(filename)

            # 获取主图片
        image = get_image_info(file)
        if image:
            context["image"] = image

             # 获取子图片
            sub_images = get_sub_images(file)
            if sub_images:
                 context["sub_images"] = sub_images

            main_content["subsection"].append(context)
        else:
             print(f"跳过 {file} 的处理，因为没有找到对应的图片")

   
    doc.add_page_break()
    doc.add_heading(main_content["title"], level=1)
    # image_number = len(main_content["subsection"])
    # for i, section in enumerate(main_content["subsection"]):
    #     image_dict[str(i)] = section["image"]
    #     title_dict[str(i)] = section["name"]
    #     thread = threading.Thread(target=add_manual, args=(section, platform, i, content_dict))
    #     thread_pool.append(thread)
    #
    # for thr in thread_pool:
    #     thr.start()
    #
    # for thr in thread_pool:
    #     thr.join()
    #
    # for key in range(image_number):
    #     doc.add_heading(title_dict[str(key)], level=2)
    #     paragraph = doc.add_paragraph()
    #     paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    #     paragraph.add_run().add_picture(image_dict[str(key)], width=Inches(5.5))
    #     doc.add_paragraph(content_dict[str(key)])

    for section in main_content["subsection"]:
        # 添加标题
        doc.add_heading(section["name"], level=2)

        # 1. 添加主图片
        if "image" in section and section["image"]:
            paragraph = doc.add_paragraph()
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            try:
                paragraph.add_run().add_picture(section["image"], width=Inches(5.5))
            except Exception as e:
                print(f"添加主图片时出错 {section['image']}: {str(e)}")

        # 2. 添加内容描述
        doc.add_paragraph(section["content"])

        # 3. 添加子图片
        if "sub_images" in section:
            for sub_image in section["sub_images"]:
                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                try:
                    paragraph.add_run().add_picture(sub_image, width=Inches(5.5))
                except Exception as e:
                    print(f"添加子图片时出错 {sub_image}: {str(e)}")


    add_pager_header(doc, platform)

    doc_save_path = os.path.join(BASE_DIR, "static", user, time, "template_manual.docx")
    doc.save(doc_save_path)
    print('Word 文档生成完毕')


if __name__ == "__main__":
    platform = sys.argv[1]
    username = sys.argv[2]
    datetime = sys.argv[3]
    colors = sys.argv[4]

    final_path = os.path.join(BASE_DIR, "static", username, datetime)
    if not os.path.exists(final_path):
        os.makedirs(final_path)

    TXT_PATH = os.path.join(BASE_DIR, "Introduction", username, datetime)
    IMAGE_PATH = os.path.join(BASE_DIR, "screenshot", username, datetime)
    if not os.path.exists(IMAGE_PATH):
        os.makedirs(IMAGE_PATH)
    if not os.path.exists(TXT_PATH):
        os.makedirs(TXT_PATH)

    main(username, datetime, IMAGE_PATH, colors)
    generate_word_template(platform, username, datetime, TXT_PATH)
