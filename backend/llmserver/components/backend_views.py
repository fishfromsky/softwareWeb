from openai import OpenAI
import os
import json
from docx import Document
import re
import concurrent.futures
import sys
from pdf_views import main_pdf
from docx.shared import Pt
from docx.oxml.ns import qn
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend import settings

client = OpenAI(
    api_key=settings.BACKEND_LLM_KEY[0],
    base_url=settings.BACKEND_LLM_URL[0],
)

def get_model_response(user_message):
    message = [{"role": "user", "content": user_message}]
    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=message
        )
        return json.loads(completion.model_dump_json())["choices"][0]["message"]["content"]
    except Exception as e:
        raise e

# 定义调用大模型的函数，用于代码生成
def get_response(messages):
    try:
        completion = client.chat.completions.create(
            model="qwen2.5-coder-32b-instruct",
            messages=messages
        )
        return completion
    except Exception as e:
        raise e


# 保存模型输出内容到txt文件
def save_to_txt(content, filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"内容已保存到 {filename}")
    except Exception as e:
        print(f"保存到txt文件时出错: {e}")

# 保存模型输出内容到文档
def save_to_word(content, filename):
    try:
        doc = Document()
        doc.add_paragraph(content)
        doc.save(filename)
        print(f"内容已保存到 Word 文档: {filename}")
    except Exception as e:
        print(f"保存到Word文档时出错: {e}")

# 读取指定路径的 JSON 文件
def read_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None


# 读取 JSON 文件内容并调用大模型理解
def analyze_file(file_path, txt_file_path):
    file_data = read_json_file(file_path)

    if file_data is not None:
        # 将文件内容转换为字符串并传递给大模型
        file_content = json.dumps(file_data, ensure_ascii=False)
        question = f"请理解以下JSON文件内容并回答：{file_content}"

        # 调用大模型获取回答
        answer = get_model_response(question)

        # print("最终答案：")
        # print(answer)

        # 将思考过程和答案保存到txt文件
        save_to_txt(f"最终答案：\n{answer}", txt_file_path)

        # 返回答案以供后续使用
        return answer
    else:
        print("无法读取文件，无法继续分析。")
        return None


# 第一次提问：扩展软件信息
def first_prompt(software_name, programming_language, txt_file_path, final_path):
    messages = [{
        "role": "system",
        "content": "You are a helpful assistant that expands software descriptions based on input."
    }]
    # # 获取编程语言的输入
    # programming_language = input("请输入软件的编程语言：")
    # 扩展软件描述的模板
    user_input = f"请根据以下框架信息扩展对{software_name}这一软件著作权的软件描述\n"
    user_input += f"""
    扩展软件描述的模板如下：
    【软件全称】
    【版本号】
    【软件分类】
    【开发的硬件环境】
    【运行的硬件环境】
    【开发该软件的操作系统】
    【软件开发环境/开发工具】
    【该软件的运行平台/操作系统】
    【软件运行支撑环境/支持软件】
    【编程语言】{programming_language}  # 使用用户输入的编程语言
    【源程序量】
    【开发目的】
    【面向领域/行业】
    【软件的主要功能】
    【软件的技术特点】
    请注意:【源程序量】后面仅需要填行数,行数是生成的随机数，范围为20000-60000行。版本号写死为v1.0
    """

    messages.append({"role": "user", "content": user_input})

    # 获取模型返回的完整内容
    assistant_output = get_response(messages).choices[0].message.content

    # print(f"第一次提问的输出：\n{assistant_output}")

    # 保存到指定txt文件
    save_to_txt(assistant_output, txt_file_path)
    save_to_txt(assistant_output, final_path)

    return assistant_output


# 第二次提问：生成代码框架，包含模块分析
def second_prompt(programming_language, expanded_description, txt_file_path):
    messages = [{
        "role": "system",
        "content": f"You are a helpful assistant that generates {programming_language} code framework based on software descriptions, and includes detailed descriptions and comments for each module."
    }]
    user_input = f"根据以下软件描述，生成{programming_language}代码框架，并为每个模块加入详细描述和注释：\n{expanded_description}\n"
    user_input += """
    并请详细描述代码框架的各个部分：
    - 前端部分：包括用户界面设计、交互逻辑、状态管理、API调用等，每个模块需要有详细的注释和描述。
    - 后端部分：包括用户认证模块、数据存储模块、错误处理模块等，每个模块需要有详细的注释和描述。
    - 数据库部分：包括多个数据库表设计、存储过程、视图等，每个部分需要详细描述。
    - API部分：设计多个RESTful API接口，并加入权限控制、认证、限流等功能。
    - 业务部分：包括用户管理、订单处理等复杂业务逻辑模块，每个模块需要有详细的描述。
    - 安全部分：包括数据加密、认证与授权、日志记录等每个部分需要有详细说明。
    """
    messages.append({"role": "user", "content": user_input})

    assistant_output = get_response(messages).choices[0].message.content
    # print(f"第二次提问的输出：\n{assistant_output}")

    # 保存到指定txt文件
    save_to_txt(assistant_output, txt_file_path)

    return assistant_output


# 修改后的代码生成函数
def generate_code_with_details(programming_language, layer, code_framework):
    messages = [{
        "role": "system",
        "content": f"You are a helpful assistant that generates {programming_language} code with detailed comments and explanations for each module. Please only return the code and remove any extra explanations or descriptions."
    }]
    user_input = f"理解下面描述中关于{layer}的部分，并为每个模块生成详细注释的{programming_language}代码, 不包含任何额外的描述，且代码内容不应包含其他格式的解释或说明，不少于500行：\n{code_framework}\n"
    messages.append({"role": "user", "content": user_input})

    assistant_output = get_response(messages).choices[0].message.content

    # 过滤掉不需要的内容：删除以“Below is a detailed...”开头的描述性文字、代码块标记、注释等
    # 删除以 ``` 开头的行和其余内容
    code_only = re.sub(r"(?i)^(below is a detailed.*|python\s*|code follows.*|the code is).*", "", assistant_output)
    code_only = re.sub(r"^```.*", "", code_only)  # 删除以 ``` 开头的行

    # 删除空行，确保代码紧凑
    code_only = "\n".join([line for line in code_only.split("\n") if line.strip() != ""])

    # print(f"{layer}层生成的代码：\n{code_only}")
    return code_only


# 细化每个模块的代码生成，修改生成“用户表设计”模块的部分
def generate_submodules_for_layer(programming_language, layer_name, code_framework, json_answer=None):
    submodules = {
        "前端": ["页面布局", "组件开发", "状态管理", "API调用", "权限前端控制"],
        "后端": ["用户认证模块", "数据存储模块", "错误处理模块", "日志记录模块", "配置管理模块"],
        "数据库": ["用户表设计", "存储过程", "视图", "索引优化", "数据备份机制"],
        "API": ["用户API接口", "订单API接口", "认证接口", "限流接口", "第三方API对接"],
        "业务": ["用户管理", "订单处理", "支付处理", "库存管理", "通知系统"],
        "安全": ["数据加密", "权限验证", "访问控制", "输入输出校验", "登录日志追踪"],
    }

    all_code = []
    for submodule in submodules[layer_name]:
        submodule_description = f"{layer_name}层 - {submodule}"

        # 如果是“用户表设计”模块，将json_answer加入到输入
        if layer_name == "数据库" and submodule == "用户表设计" and json_answer:
            submodule_code = generate_code_with_details(programming_language, submodule_description, code_framework + "\n" + json_answer)
        else:
            submodule_code = generate_code_with_details(programming_language, submodule_description, code_framework)

        all_code.append(submodule_code)

    return "\n".join(all_code)


# 并发生成所有层代码
def generate_all_layers_concurrently(programming_language, code_framework, json_answer=None):
    layer_names = ["前端", "后端", "数据库", "API", "业务", "安全"]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_layer = {
            executor.submit(generate_submodules_for_layer, programming_language, layer, code_framework,
                            json_answer if layer == "数据库" else None): layer
            for layer in layer_names
        }

        results = {}
        for future in concurrent.futures.as_completed(future_to_layer):
            layer_name = future_to_layer[future]
            try:
                results[layer_name] = future.result()
                print(f"{layer_name} 代码生成完成！")
            except Exception as e:
                print(f" {layer_name} 代码生成失败: {e}")

    return results


# 合并多个Word文档为一个
def merge_word_documents(file_paths, output_path, software_name):
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    merged_doc = Document()

    # 添加页眉
    section = merged_doc.sections[0]
    header = section.header
    header_paragraph = header.paragraphs[0]
    header_paragraph.text = software_name
    header_paragraph.alignment = 1  # 居中

    run = header_paragraph.runs[0]
    run.font.name = "SimSun"
    run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
    run.font.size = Pt(10.5)

    # 遍历文件合并内容
    for file_path in file_paths:
        try:
            doc = Document(file_path)
            for para in doc.paragraphs:
                text = para.text

                # 依次去除代码块标识符
                text = text.replace("```\n", "").replace("```", "")

                # 依次去除各种编程语言名称（大小写都考虑）
                languages = [
                    "python", "Python", "java", "Java", "Php","php"
                ]

                for lang in languages:
                    text = text.replace(lang, "")

                new_para = merged_doc.add_paragraph(text)
                for run in new_para.runs:
                    run.font.name = "SimSun"
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
                    run.font.size = Pt(10.5)

            merged_doc.add_page_break()  # 添加分页符
            print(f"成功合并文档: {file_path}")
        except Exception as e:
            print(f"合并文档时出错: {file_path}, 错误: {e}")

    # 等待2秒并保存
    time.sleep(2)
    try:
        merged_doc.save(output_path)
        print(f"所有文档已合并并保存到: {output_path}")
    except Exception as e:
        print(f"保存合并文档时出错: {e}")


# 运行主要流程
if __name__ == "__main__":
    platform = sys.argv[1]
    language = sys.argv[2]
    username = sys.argv[3]
    datetime = sys.argv[4]

    medium_path = os.path.join(BASE_DIR, "medium", username, datetime)
    final_path = os.path.join(BASE_DIR, "static", username, datetime)
    if not os.path.exists(medium_path):
        os.makedirs(medium_path)
    if not os.path.exists(final_path):
        os.makedirs(final_path)
    # 定义保存代码的路径
    output_path_1 = medium_path  # 保存各层的代码文档
    output_path_2 = final_path  # 保存合并后的总代码文档

    # 第1次提问:扩充软著描述，第2次提问：软著实现整体框架
    expanded_description = first_prompt(platform, language, os.path.join(medium_path, "expanded_description.txt"),
                                        os.path.join(final_path, "expanded_description.txt"))  # 第一次提问，获得对软著名的扩充描述，并保存到txt
    code_framework = second_prompt(language, expanded_description,os.path.join(medium_path, "code_framework.txt"))  # 第二次提问，获得对软著实现的框架性语言，并保存到txt

    # 调用函数，传入文件路径
    file_path = os.path.join(medium_path, "menu.json")
    json_answer = analyze_file(file_path, os.path.join(medium_path, "json_analysis.txt"))  # 获得对后续数据库代码实现的补充提示词，并保存到txt

    # 并发生成代码
    layer_codes = generate_all_layers_concurrently(language, code_framework, json_answer)

    # 保存各层代码到 Word 文件
    file_paths = []  # 存储各层代码word文档的地址，方便后续合并
    for layer, code in layer_codes.items():  # 获取键值对，层名-代码
        file_path = os.path.join(output_path_1, f"{layer}_code.docx")
        save_to_word(code, file_path)
        file_paths.append(file_path)

    # 合并所有代码文件
    merged_file_path = os.path.join(output_path_2, "merged_code.docx")
    merge_word_documents(file_paths, merged_file_path, platform)
    main_pdf(username, datetime)
