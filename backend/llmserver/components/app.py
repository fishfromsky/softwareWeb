from openai import OpenAI
import random
import os
import sys
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend import settings
# === 固定输入参数 ===

software_name = ""
programming_language = ""
technical_features = ""

# === 初始化大模型客户端 ===
client = OpenAI(
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    timeout=300  # 添加超时设置
)

# === 使用重试机制封装模型调用 ===
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=20))
def get_model_response(messages, model="qwq-plus-latest"):
    try:
        print(f"[DEBUG] 发送请求到模型: {model}")
        # 使用流式模式调用模型
        response_stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True  # 启用流式响应
        )
        
        # 从流中收集完整响应
        full_response = ""
        for chunk in response_stream:
            if chunk.choices and hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content is not None:
                    full_response += content
        
        print(f"[DEBUG] 模型响应完成，长度: {len(full_response)}")
        return full_response.strip()
    except Exception as e:
        print(f"[ERROR] 模型调用失败: {e}")
        raise e

# === 从文件中提取技术特点 ===
def extract_technical_features_from_file(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 查找技术特点部分
                tech_start = content.find("【软件的技术特点】")
                if tech_start != -1:
                    # 查找下一个【】标记或文件结尾
                    next_section = content.find("【", tech_start + 9)
                    if next_section != -1:
                        tech_features = content[tech_start:next_section].strip()
                    else:
                        tech_features = content[tech_start:].strip()
                    
                    # 移除标题，只保留内容
                    tech_features = tech_features.replace("【软件的技术特点】", "").strip()
                    return tech_features
                else:
                    print("未找到技术特点部分")
                    return ""
        else:
            print(f"文件不存在: {file_path}")
            return ""
    except Exception as e:
        print(f"读取文件出错: {e}")
        return ""

# === 生成不含"0"的随机行数 ===
def generate_source_lines():
    while True:
        num = random.randint(20000, 25000)
        if '0' not in str(num):
            return num

# === 独立生成主要功能描述（100~200字）
def generate_main_function():
    prompt =  """
请生成一段中文描述，用于表示一款“管理系统”的软件主要功能。
要求：
1. 内容为完整书面句子，不允许使用列点或“、”；
2. 描述应包括用户注册、职业测评、报告生成、权限控制、数据分析等核心功能；
3. 内容长度在100至200个汉字之间；
4. 只输出内容本身，不附带任何解释。
"""

    messages = [{'role': 'user', 'content': prompt}]
    content = get_model_response(messages)
   
    return content

# === 总结技术特点（20~100字）
def summarize_technical_features(raw_features):
    prompt = f"""
请将以下技术特点内容压缩为20到100个汉字之间的简明描述，保持主要含义，风格专业：
{raw_features}
只返回压缩后的内容。
回复内容中除了压缩的内容，不要包括任何其余解释
"""
    messages = [{'role': 'user', 'content': prompt}]
    return get_model_response(messages)

# === 根据技术特点内容判断最合适的选项
def choose_tech_option(summary):
    options = ["APP", "游戏软件", "人工智能软件", "金融软件", "大数据软件", "云计算软件", "信息安全软件", "小程序", "物联网", "智慧城市软件"]
    prompt = f"""
根据以下软件技术特点内容，判断最适合归类的类型，并从以下选项中选择一个最匹配的：
{options}

技术特点描述如下：
{summary}

请返回最合适的一个类别名称（仅输出选项本身，不加任何解释）。
"""
    messages = [{'role': 'user', 'content': prompt}]
    return get_model_response(messages)

# === 生成标准字段（通用字段9项）
def generate_fields_via_model():
    prompt = f"""
    请根据以下框架信息扩展对{software_name}这一软件著作权的软件描述\n
请为以下软件字段生成内容。要求：
1. 每项内容直接接在字段标签后（同一行）；
2. 内容风格为简洁罗列；
3. 每项独占一行，示例如下：

【开发的硬件环境】CPU: Intel i7-10700K 主频:3.8GHz 内存:32GB SSD:512GB
【运行的硬件环境】CPU: Xeon E5-2640 内存:16GB 存储:1.2T*24块(SAS)
【开发该软件的操作系统】Windows Server 2016、Ubuntu 20.04
【软件开发环境或者开发工具】PyCharm、VS Code、Git、MySQL Workbench
【软件的运行平台或操作系统】Windows 10、Android 11、Linux CentOS
【软件运行支撑环境或支持软件】Python 3.10、Redis、MySQL、Chrome
【开发目的】
【面向领域/行业】

⚠️只生成以上字段，禁止生成多余字段。
"""
    messages = [{'role': 'user', 'content': prompt}]
    return get_model_response(messages)

# === 拼接最终内容并保存
def generate_and_save_txt(output_path):
    global software_name, programming_language, technical_features
    
    version = "V1.0"
    category = "应用软件"
    code_lines = generate_source_lines()

    # 生成所有部分
    model_fields = generate_fields_via_model().splitlines()
    main_function = generate_main_function()
    summarized_tech = summarize_technical_features(technical_features)
    tech_option = choose_tech_option(summarized_tech)

    # 插入语言/行数
    insert_after = "【软件运行支撑环境或支持软件】"
    insert_index = next((i for i, line in enumerate(model_fields) if line.startswith(insert_after)), -1)
    if insert_index != -1:
        model_fields.insert(insert_index + 1, f"【编程语言】{programming_language}")
        model_fields.insert(insert_index + 2, f"【源程序量】{code_lines}")
    else:
        model_fields.append(f"【编程语言】{programming_language}")
        model_fields.append(f"【源程序量】{code_lines}")

    # 拼接尾部字段
    model_fields.append(f"【软件的主要功能】{main_function}")
    model_fields.append(f"【技术特点】{summarized_tech}")
    model_fields.append(f"【软件的技术特点选项】{tech_option}")

    # 最终合成
    final_text = f"""【软件名称】{software_name}
【版本号】{version}
【软件分类】{category}
""" + "\n".join(model_fields)

    try:
        # 始终保存为TXT格式文件
        txt_output_path = output_path
        if output_path.endswith('.docx'):
            txt_output_path = output_path.replace('.docx', '.txt')
        
        # 保存为文本文件
        with open(txt_output_path, "w", encoding="utf-8") as f:
            f.write(final_text)
        print(f"✅ 成功保存文本文件至：{txt_output_path}")
    except Exception as e:
        print(f"❌ 写入失败：{e}")

# === 主执行 ===
if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) >= 4:
        software_name = sys.argv[1]
        programming_language = sys.argv[2]
        output_path = sys.argv[3]
        # 确保输出路径使用.txt扩展名
        if output_path.endswith('.docx'):
            output_path = output_path.replace('.docx', '.txt')
        output_dir = sys.argv[4]
        
        # 尝试从expanded_description.txt文件中读取技术特点
        description_file = os.path.join(output_dir, "expanded_description.txt")
        technical_features = extract_technical_features_from_file(description_file)
        
        # 如果没有找到技术特点，则使用默认生成的简单描述
        if not technical_features:
            technical_features = "使用现代编程技术开发，具有高效性、易用性、跨平台兼容性和安全性。"
            print(f"未找到技术特点，使用默认描述")
    else:
        # 默认路径
        software_name = "默认软件名称"
        programming_language = "Java"
        output_path = r"C:\Users\hwh13\Desktop\LLM\软件描述信息.txt"
        technical_features = "使用现代编程技术开发，具有高效性、易用性、跨平台兼容性和安全性。"
    print(f"技术特点: {technical_features}")
    print(f"生成软著注册表: 软件名称={software_name}, 编程语言={programming_language}")
    generate_and_save_txt(output_path)
