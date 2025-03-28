from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, FileResponse
from openai import OpenAI
import os
import json
import threading
import random
import shutil
from tenacity import retry, stop_after_attempt, wait_exponential
import shutil
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis
from urllib.parse import quote
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.backend.settings")
from django.conf import settings
from .models import *

from django.db.models.fields import DateTimeField
from django.db.models.fields.related import ManyToManyField

RANDOM_CHOICE = random.randint(1, 2)

# 初始化 OpenAI 客户端，增加 timeout 参数
client = OpenAI(
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    timeout=300
)
api_keynum = settings.LLM_API_KEY
MAX_THREADS = 1
WEB_URL = "http://121.196.229.117:8000/static"
IMG_URL = "http://121.196.229.117/static"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIUM_PATH = os.path.join(BASE_DIR, "medium")

# def build_static_url(username, datetime_str, filename):
#     return f"{settings.STATIC_URL}{quote(username)}/{quote(datetime_str)}/{filename}"


def read_json(username, datetime_str):
    config_path = os.path.join(MEDIUM_PATH, username, datetime_str, "config.json")
    with open(config_path, "r", encoding="utf-8") as fr:
        data = json.load(fr)
    return data


def delete_directory(folder_path):
    if os.path.exists(folder_path):
        # 删除文件夹及其所有内容
        shutil.rmtree(folder_path)
    else:
        raise Exception("文件夹不存在")


def get_response(message):
    """
    使用流式请求模型，并将分块返回的内容合并为完整回复
    """
    reasoning_content = ""  # 定义完整思考过程
    full_response = ""     # 修改这里，使用 content 而不是 answer_content
    is_answering = False
    try:
        print("[DEBUG] 模型请求发送中...")
        # 采用流式返回，model 使用 qwq-32b（可根据实际情况调整）
        completion = client.chat.completions.create(
            model="qwq-plus-latest",
            messages=message,
            stream=True
        )
        #print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
        for chunk in completion:
            if not chunk.choices:
                print("\nUsage:")
                #print(chunk.usage)
            else:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                    #print(delta.reasoning_content, end='', flush=True)
                    reasoning_content += delta.reasoning_content
                else:
                    if delta.content != "" and is_answering is False:
                        #print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                        is_answering = True
                    #print(delta.content, end='', flush=True)
                    full_response += delta.content
        return full_response
    except Exception as e:
        print(f"[ERROR] 模型调用失败: {e}")
        raise e


@retry(stop=stop_after_attempt(10), wait=wait_exponential(multiplier=1, min=2, max=20))
def api_call(message):
    return get_response(message)


def to_dict(self, fields=None, exclude=None):
    data = {}
    for f in self._meta.concrete_fields + self._meta.many_to_many:
        value = f.value_from_object(self)

        if fields and f.name not in fields:
            continue

        if exclude and f.name in exclude:
            continue

        if isinstance(f, ManyToManyField):
            value = [i.id for i in value] if self.pk else None

        if isinstance(f, DateTimeField):
            value = value.strftime("%Y-%m-%d %H:%M:%S") if value else None

        data[f.name] = value

    return data


def run_another_script_webfront(arg1, arg2, arg3, arg4):
    global MAX_THREADS
    import subprocess
    if isinstance(arg4, list):
        arg4 = ",".join(arg4)
    subprocess.run(
        ["python3", os.path.join(BASE_DIR, "llmserver", "components", "webfront_screenshot.py"), arg1, arg2, arg3, arg4]
    )
    MAX_THREADS += 1


def run_another_script_backend(arg1, arg2, arg3, arg4):
    # 使用 subprocess.run 运行另一个 Python 文件并传递参数
    import subprocess
    subprocess.run(
        ["python3", os.path.join(BASE_DIR, "llmserver", "components", "backend_views.py"), arg1, arg2, arg3, arg4]
    )


@require_http_methods(["GET"])
def check_thread_pool_available(request):
    response = {"code": 0, "message": "success"}
    response["status"] = 1 if MAX_THREADS > 0 else 0
    return JsonResponse(response)


@require_http_methods(["POST"])
def startProgram(request):
    global MAX_THREADS
    MAX_THREADS -= 1
    response = {"code": 0, "message": "success"}
    data = json.loads(request.body)
    person_id = data.get("id")
    platform = data.get("platform")
    language = data.get("language")
    datetime_str = data.get("time")
    username = data.get("username")
    colors = data.get("color")

    code_path = f"{WEB_URL}/{username}/{datetime_str}/ultimate_file.pdf"
    word_file = f"{WEB_URL}/{username}/{datetime_str}/template_manual.docx"
    introduce_file = f"{WEB_URL}/{username}/{datetime_str}/expanded_description.txt"

    # print("[DEBUG] 生成的文件访问路径：")
    # print("PDF下载地址：", code_path)
    # print("Word文档地址：", word_file)
    # print("介绍文档地址：", introduce_file)


    medium_url = os.path.join(MEDIUM_PATH, username, datetime_str) # 用户存放某用户在某时间下创建的项目的具体信息
    if not os.path.exists(medium_url):
        os.makedirs(medium_url)
    user_dict = {
        "platform": platform,
        "username": username,
        "datetime": datetime_str,
        "language": language
    }
    with open(os.path.join(medium_url, "config.json"), "w", encoding="utf-8") as f:
        json.dump(user_dict, f, indent=4)

    record = UserRecord.objects.create(
        name=platform,
        time=datetime_str,
        language=language,
        user=UserProfile(id=person_id),
        pdf_download=word_file,
        code_download=code_path,
        introduce_download=introduce_file
    )
    record.save()

    thread1 = threading.Thread(
        target=run_another_script_webfront,
        args=(platform, username, datetime_str, colors)
    )
    thread1.start()
    return JsonResponse(response)


@require_http_methods(["POST"])
def login(request):
    response = {"code": 2000, "message": "success"}
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")
    user_count = UserProfile.objects.filter(username=username).count()
    if user_count == 0:
        response["code"] = 1
        response["message"] = "User not found"
        return JsonResponse(response)
    else:
        if not UserProfile.objects.filter(username=username, password=password).count():
            response["code"] = 2
            response["message"] = "Password Wrong"
            return JsonResponse(response)
        else:
            user = UserProfile.objects.get(username=username, password=password)
            data = {
                "username": username,
                "roles": [user.role],
                "id": user.id
            }
            response["data"] = data
            response["code"] = 0
            return JsonResponse(response)


@require_http_methods(["GET"])
def getuserinfo(request):
    response = {"code": 2000, "message": "success"}
    user_id = request.GET.get("user_id")
    user = UserProfile.objects.get(id=user_id)
    response["data"] = to_dict(user)
    return JsonResponse(response)


@require_http_methods(["POST"])
def editUserInfo(request):
    response = {"code": 2000, "message": "success"}
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    phone = data.get("phone_number")
    user_id = data.get("id")
    user = UserProfile.objects.get(id=user_id)
    user.username = username
    user.email = email
    user.phone_number = phone
    user.password = password
    user.save()
    return JsonResponse(response)


def deleteUserRecord(request):
    response = {"code": 2000, "message": "success"}
    record_id = request.GET.get("record_id")
    record = UserRecord.objects.get(id=record_id)
    datetime = record.time
    username = record.user.username
    medium_file_path = os.path.join(MEDIUM_PATH, username, datetime)
    delete_directory(medium_file_path)
    introduction_path = os.path.join(BASE_DIR, "Introduction", username, datetime)
    delete_directory(introduction_path)
    screenshot_path = os.path.join(BASE_DIR, "screenshot", username, datetime)
    delete_directory(screenshot_path)
    static_path = os.path.join(BASE_DIR, "static", username, datetime)
    delete_directory(static_path)
    record.delete()
    return JsonResponse(response)


@require_http_methods(["GET"])
def pdfDownload(request):
    user_id = request.GET.get("user_id")
    time = request.GET.get("time")
    username = UserProfile.objects.get(id=user_id).username
    static_file_path = os.path.join(BASE_DIR, "static", username, time, "ultimate_file.pdf")
    file = open(static_file_path, "rb")
    response = FileResponse(file)
    response["Content-Disposition"] = f"attachment; filename='{username}'+'{time}'+'.pdf"
    return response


@require_http_methods(["GET"])
def txtDownload(request):
    user_id = request.GET.get("user_id")
    time = request.GET.get("time")
    username = UserProfile.objects.get(id=user_id).username
    static_file_path = os.path.join(BASE_DIR, "static", username, time, "expanded_description.txt")
    file = open(static_file_path, "rb")
    response = FileResponse(file)
    response["Content-Disposition"] = f"attachment; filename='{username}'+'{time}'+'.txt"
    return response


@require_http_methods(["GET"])
def wordDownload(request):
    user_id = request.GET.get("user_id")
    time = request.GET.get("time")
    username = UserProfile.objects.get(id=user_id).username
    static_file_path = os.path.join(BASE_DIR, "static", username, time, "template_manual.docx")
    file = open(static_file_path, "rb")
    response = FileResponse(file)
    response["Content-Disposition"] = f"attachment; filename='{username}'+'{time}'+'.docx"
    return response


@require_http_methods(["GET"])
def getUserAllRecord(request):
    response = {"code": 0, "message": "success"}
    user_id = request.GET.get("user_id")
    records = UserRecord.objects.filter(user=UserProfile(id=user_id))
    response["data"] = []
    for r in records:
        dict_record = to_dict(r)
        record_id = dict_record["id"]
        record_item = UserRecord.objects.get(id=record_id)
        if dict_record.get("pdf_status", 0) == 0:
            relative_path = os.path.join(BASE_DIR, *dict_record["pdf_download"].split("/")[3:])
            if os.path.exists(relative_path):
                dict_record["pdf_status"] = 1
                record_item.pdf_status = 1
                record_item.save()
        if dict_record.get("code_status", 0) == 0:
            relative_path = os.path.join(BASE_DIR, *dict_record["code_download"].split("/")[3:])
            if os.path.exists(relative_path):
                dict_record["code_status"] = 1
                record_item.code_status = 1
                record_item.save()
        if dict_record.get("introduce_status", 0) == 0:
            relative_path = os.path.join(BASE_DIR, *dict_record["introduce_download"].split("/")[3:])
            if os.path.exists(relative_path):
                dict_record["introduce_status"] = 1
                record_item.introduce_status = 1
                record_item.save()
        response["data"].append(dict_record)
    return JsonResponse(response)


@require_http_methods(["POST"])
def register(request):
    response = {"code": 0, "message": "success"}
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    phone = data.get("phone")
    user_count = UserProfile.objects.filter(username=username).filter().count()
    if user_count != 0:
        response["code"] = 1
        response["message"] = "Username has already existed"
        return JsonResponse(response)
    else:
        user = UserProfile(username=username, password=password, email=email, phone_number=phone)
        user.save()
        return JsonResponse(response)


@require_http_methods(["GET"])
def getNameConfig(request):
    username = request.GET.get("username")
    datetime = request.GET.get("datetime")
    data = read_json(username, datetime)
    platform = data["platform"]
    response = {"code": 0, "message": "success"}
    response["name"] = platform
    return JsonResponse(response)


@require_http_methods(["GET"])
def getMenuConfig(request): # 生成侧边栏信息
    username = request.GET.get("username")
    datetime = request.GET.get("datetime")
    data = read_json(username, datetime)
    platform = data["platform"]
    language = data["language"]
    response = {"code": 0, "message": "success"}
    MESSAGE = [{"role": "system", "content": "You are a helpful programmer and product manager"}]
    question = f"""
    设计一个{platform}的侧边栏, 有如下要求:
    1. 侧边栏需包含至少6个目录，每个目录名称应与系统业务逻辑密切相关。
    2. 返回结果应为一个Object，每个Object的key为父目录，对应的value为一个List，包含所有子目录名称。
    3. 回答时只需返回上述Object，无需任何解释说明，且返回内容必须以Object的"{{"开始。
    4. 侧边栏的第一个key必须为“主菜单”，且“主菜单”仅能包含数据统计和消息通知两个子目录，不需要别的子目录。
    """
    MESSAGE.append({"role": "user", "content": question})
    try:
        full_reply = api_call(MESSAGE)
        # print("[DEBUG] 大模型完整返回:", full_reply)
        menu = json.loads(full_reply)
    except Exception as e:
        print(f"所有尝试均失败: {e}")
        return JsonResponse({"code": 1, "message": "模型调用失败"})

    MENU_CONFIG = menu
    json_file = os.path.join(MEDIUM_PATH, username, datetime, "menu.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(MENU_CONFIG, f)
    response["menu"] = MENU_CONFIG
    # print(f"开始生成后端代码")
    thread2 = threading.Thread(target=run_another_script_backend, args=(platform, language, username, datetime))
    thread2.start()
    return JsonResponse(response)


@require_http_methods(["GET"])
def getPageInfo(request): # 根据前端返回的当前点击的侧边栏id生成具体的页面代码
    username = request.GET.get("username")
    datetime = request.GET.get("datetime")
    colors = request.GET.get("colors")
    content_save = ""
    # 若 colors 为空，则使用默认值
    if not colors:
        color_list = ["#40c9c6", "#40c9c6", "#40c9c6", "#40c9c6"]
    else:
        color_list = colors.split(',')

    data = read_json(username, datetime)
    platform = data["platform"]
    response = {"code": 0, "message": "success"}

    # 读取侧边栏信息
    menu_file = os.path.join(MEDIUM_PATH, username, datetime, "menu.json")
    with open(menu_file, "r", encoding="utf-8") as f:
        menu_info = json.load(f)

    menu_item = request.GET.get("index")
    parent_idx, child_idx = menu_item.split("-")
    parent_idx = int(parent_idx)
    child_idx = int(child_idx)
    parent_name = list(menu_info.keys())[parent_idx - 1]
    child_name = menu_info[parent_name][child_idx - 1]

    # 读取组件文件内容
    component_files = [
        "SearchForm.vue",
        "BaseTable.vue",
        "EChartLine.vue",
        "EChartBar.vue",
        "EChartPie.vue",
        "Card.vue",
        "Leaderboard.vue",
    ]
    base_dir = os.path.join(os.path.dirname(__file__), "templates_components")
    components_code_list = []
    for filename in component_files:
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            components_code_list.append(content)
        else:
            print(f"[WARNING] File not found: {file_path}")
    all_components_code = "\n".join(components_code_list)

    # 第一次调用：生成页面代码
    MESSAGE = [{"role": "system", "content": "You are a helpful programmer and product manager"}]
    question = f"""
    现在有一个后台管理系统叫 {platform}，请为侧边栏父目录名称为 {parent_name} 下的 {child_name} 子目录所对应的页面设计 Vue2 版本的 Vue.js 页面代码，满足如下要求：

    【基本要求，必须遵守】
    1. 回复必须只包含 Vue 代码，必须以 "<template>" 开头，以 "</script>" 结尾，不要包含任何解释说明。
    2. 项目基于 Vue2 + Element-UI，禁止出现 Vue3 语法（如 setup、v-slot、#slot、Composition API 等），仅使用 Vue2 标准写法。
   . 图表部分必须使用全局挂载的 echarts，通过 const chart = this.$echarts.init() 方式直接调用，不允许使用 import 语法，也不允许注册组件。
    4. 所有组件内部均应包含完整虚拟数据，且每个数据列表需包含 6-8 条真实业务场景示例数据，不从父组件传递 props。
    5. 表单字段必须分别使用单独变量进行 v-model 绑定，不要使用统一 formData 对象。
    6. Vue2 要求 template 中只能有一个根节点，请将页面所有内容统一包裹在一个根容器（如 <div>
    7.页面中的所有按钮中涉及到了新增数据的按钮设置class为add,其余按钮不需要设置class
    8.设置了class为add的按钮必须绑定一个新增表单

    【UI设计与样式要求】
    1. 页面整体风格需以 {color_list} 作为主题色，包括但不限于按钮背景色、标签颜色、表头颜色、进度条颜色、Tabs 激活色、分隔符颜色等，尽可能多体现主题色，按钮颜色不得使用 element-ui 默认色。
    2. 所有模块（如表格、图表、搜索栏、统计卡片、Tabs 等）必须包裹在 el-card 组件内，el-card 需设置 shadow="always"，并合理设置 margin 和 padding，卡片边界清晰，阴影突出。
    3. 页面布局采用 el-row + el-col 组合，统计卡片和图表均需一行放两个，el-col 设置 span=12，保证左右对齐，避免单列堆叠，每个模块宽度统一。
    4. 表格部分使用 el-table，表头背景色为 {color_list[0]}，不设置固定列宽。表格最后一列包含“编辑”、“删除”、“详情”三个操作按钮，按钮需同行排列，删除按钮带确认提示框，按钮颜色符合主题色 {color_list}。
    5. 分页使用 el-pagination，右对齐，整体风格统一。
    6. 顶部搜索栏放置在一个 el-card 内，包含 el-input 输入框、el-select 筛选框、新增按钮，新增按钮 class="add"，样式采用主题色。

    【图表特别要求】
    1. 图表必须通过 this.$echarts.init() 直接调用，不得 import 或注册组件。
    2. 每个图表的 option 配置，需完整手动设置 `type`、`data`、`radius` 等属性，**确保不会出现 series 被覆盖或数据丢失问题**。
    3. 图表内容用真实业务数据构造，禁止空数据，且务必放置在 el-card 中展示，保持美观。

    【组件丰富性要求】
    每个页面需合理引入至少 4 种以上 Element-UI 组件，提升页面交互性与美观性，颜色均符合主题色 {color_list}，组件包括但不限于：
    - el-tabs 选项卡
    - el-tag 标签
    - el-switch 开关
    - el-progress 进度条
    - el-divider 分隔符
    - el-avatar 头像
    - el-tooltip 提示
    - el-breadcrumb 面包屑
    - el-collapse 折叠面板
    - el-alert 提示信息

    【差异化要求】
    1. 主页页面必须包含至少一张 ECharts 图表，且布局与其他页面不同。
    2. 其他页面根据 {child_name} 业务内容，自行合理布局，禁止与主页完全相同，确保结构和数据内容有差异。
    3. 所有示例数据必须体现真实业务场景，如用户管理应包含姓名、角色、手机号、状态等字段，订单管理应体现订单编号、金额、时间、状态等。

    【表单要求】
    可以打开新增表单的按钮设置class为add，其余按钮不需要设置class。
    1. 新增或编辑数据弹窗表单需包含至少三个字段，字段类型覆盖文本输入、数字输入、下拉选择等，字段分别绑定到单独变量。
    2. 弹窗内必须包含“取消”和“确定”两个按钮，取消按钮 class="cancel"，点击取消关闭弹窗，按钮样式采用主题色。
    3. 弹窗需出现在屏幕正中央，水平垂直居中显示，弹窗宽度为屏幕宽度的 30%。

    【已有模板提示】
    此外，我们已有以下组件模板：{all_components_code}，你可以直接复制模板中的代码来复用，但禁止使用 import 语法，也不要直接注册组件调用。
    """

    MESSAGE.append({"role": "user", "content": question})


    try:
        page_code = api_call(MESSAGE)
    except Exception as e:
        print(f"所有尝试均失败: {e}")
        return JsonResponse({"code": 1, "message": "模型调用失败"})
    response["content"] = page_code
    content_save+=page_code
    MESSAGE.append({"role": "assistant", "content": page_code})
    # 第二次调用：生成说明文档
    question = f"""
    请根据你所生成的页面代码，详细介绍该页面的业务功能与使用说明，要求如下：

    1. 回复必须以 ***** 开头；
    2. 页面代码与说明文字之间必须严格使用 ***** 分隔；
    3. 说明部分仅使用文字描述，不得包含任何代码格式（包括 markdown）；
    4. 说明内容格式如下：
    {{ {child_name} }}
    {{ 说明文字 }}
    5. 请用一段流畅自然的语言说明页面用途、用户操作流程及数据交互，不要分条、不使用编号；
    6. 字数不少于300字；
    7. 请重点描述该页面能实现哪些核心功能，用户在页面中可以完成哪些任务，表单与表格如何交互，是否包含弹窗及弹窗的用途；
    8. 不要出现与主题色、颜色代码、样式细节、像素占比等相关的描述；
    9. 避免使用“页面整体视觉风格”、“界面美观性”、“卡片边框阴影”等表述；
    10. 若页面代码中包含弹窗，请将弹窗相关功能作为说明的最后一段单独说明。
    """
    MESSAGE.append({"role": "user", "content": question})
    try:
        description = api_call(MESSAGE)
    except Exception as e:
        print(f"所有尝试均失败: {e}")
        return JsonResponse({"code": 1, "message": "模型调用失败"})
    content_save+=description
    # 保存说明文档
    txt_path = os.path.join(BASE_DIR, "Introduction", username, datetime)
    if not os.path.exists(txt_path):
        os.makedirs(txt_path)
    with open(os.path.join(txt_path, menu_item + ".txt"), "w", encoding="utf-8") as f:
        f.write(content_save)
    print(f"说明文档 {menu_item} 已保存")
    return JsonResponse(response)


@require_http_methods(["GET"])   # 生成登录界面信息
def getPageMain(request):
    import codecs  # 兼容不同编码

    username = request.GET.get("username")
    datetime = request.GET.get("datetime")
    colors = request.GET.get("colors")
    safe_datetime = quote(datetime)

    #background_url = build_static_url(username, datetime, "background.jpg")

    # 若 colors 为空，则使用默认值
    if not colors:
        color_list = ["#40c9c6", "#40c9c6", "#40c9c6", "#40c9c6"]
    else:
        color_list = colors.split(',')
    data = read_json(username, datetime)
    platform = data["platform"]
    response = {"code": 0, "message": "success"}
    reasoning_content = ""  # 定义完整思考过程
    content = ""     # 修改这里，使用 content 而不是 answer_content
    is_answering = False   # 判断是否结束思考过程并开始回复
    messages = []

    template_path = os.path.join(BASE_DIR, "llmserver", "templates_components", "tempLogin.vue")
    try:
        with codecs.open(template_path, 'r', encoding='utf-8') as f:
            vue_template_code = f.read()
    except Exception as e:
        vue_template_code = ""
        print(f"读取模板失败: {e}")

    # 定义登录的两种 Prompt
    question1_option1 = f"""
            现在有一个后台管理系统叫{platform}, 请为其用户登录页面生成所对应的基于Vue.js的代码, 满足如下要求:
            回复只需要以"<template>"开头, 以"<\/script>"结尾, 不需要其他任何解释说明内容.
            1.要求符合日常用户登录界面业务逻辑.
            2.组件基于element-ui框架.
            3.根容器背景使用指定图片URL：{IMG_URL}/{username}/{safe_datetime}/background.jpg，请确保图片可以显示,正确保留url中的空格，使用行内式background-image: url('{IMG_URL}/{username}/{safe_datetime}/background.jpg')
            确保图片可以完整显示，正好铺满（解决图片过大或者过小显示不全的问题）。
            4.卡片容器需要始终居中,样式要求如下width: 20%;position: absolute;top: 50%;left: 50%;transform: translate(-50%, -50%);
            5.登录卡片内部划分为标题区、输入区、操作按钮区三个纵向模块，各模块间距比例为1:2:1。
            6.标题区域固定于卡片顶部，显示欢迎登录等字样，使用大字号粗体文本居中显示，下方保留与输入区的动态间距。
            7.输入区域包含三个组件：
            ▸ 用户名输入框：标签+输入框
            ▸ 密码输入框：标签+输入框
            ▸ 验证码区，
            三个区域之间有些许间隔。
            8.操作按钮区包含一个按钮，按钮文本为"登录"，按钮颜色为蓝色，按钮宽度占满容器宽度，按钮下靠右有注册账号的灰色字样。
            9.要求只返回页面代码部分, 代码只包含template部分和script部分, 不需要style部分. 最重要的是以"<template>"开头, 以"<\/script>"结尾, 不需要其他任何解释说明内容。
        """

    question1_option2 = f"""
        现在有一个后台管理系统叫 {platform}，请为其用户登录页面生成对应的基于 Vue.js 的代码，满足如下要求：
        1. 只返回页面代码部分，代码只包含 <template> 到 </script>，不需要任何解释说明，也不需要 style 块。
        2. 所有样式均使用行内式写在元素的 style 属性中，不能使用 <style> 或 scoped 样式。
        3. 整个页面作为背景，宽高 100%（width: 100%; height: 100vh;），使用 background-size: cover 显示图片：url('{IMG_URL}/{username}/{safe_datetime}/background.jpg')，居中对齐但在右侧留出一块区域放置登录卡片（margin-right: 80px）。
        4. 登录卡片宽度 360px，白色背景，圆角，box-shadow，内部使用 Element-UI 的 <el-form>、<el-form-item>、<el-input>、<el-button> 组件，包含用户名、密码两个输入框，均带 prefix-icon。
        5. 登录按钮使用动态行内样式实现鼠标悬停时的背景渐变方向切换、轻微上移等效果。点击后在 onSubmit 中以 alert() 方式演示获取到的用户名、密码。
        6. 登录卡片内的标题需显示“欢迎登录 {platform}”等字样，请在 <h2> 标签中动态拼接 {platform}。
        7. 代码需符合常规登录业务逻辑示例：onSubmit 中可以先用 alert() 演示用户名、密码获取。
        8. 最终输出必须从 <template> 开始，到 </script> 结束，中间不能有额外文字或说明。
        9. 参考以下已有 Vue 模板结构，你只能直接复制其中的代码使用，不允许使用 import 语句：
        {vue_template_code}

        请严格遵循以上要求，仅返回符合条件的 Vue2 代码。
        """

    # 2. 根据全局随机值决定最终要用哪个 Prompt
    if RANDOM_CHOICE == 1:
        question1 = question1_option1
    else:
        question1 = question1_option2

    question2 = f"""
       请根据你所生成的页面代码，撰写一段流畅自然的文字，详细介绍该页面的核心业务功能和用户使用流程，要求如下：

       1. 回复必须以 ***** 开头；
       2. 说明部分仅使用文字描述，不得包含任何代码格式（包括 markdown、代码片段等）；
       3. 说明内容格式如下：
       用户登录
       {{ 说明文字 }}
       4. 说明必须以一整段连贯文字进行撰写，避免使用编号、条列、分点描述等风格；
       5. 内容不少于 300 字；
       6. 请重点描述该页面实现了哪些功能、用户在页面中如何完成具体任务，前后端之间如何协同完成登录流程；
       7. 请避免出现页面配色、字体、大小、渐变、边框阴影等 UI 外观描述；
       8. 请勿撰写任何开发建议、技术扩展、接口设计说明或代码结构的说明；
       """
    prompt = f"""现在有一个网页系统叫{platform},请帮其生成一张可以在登陆页面使用的背景图片,图片颜色符合{color_list[0]}的色系，图片内容和{platform}相关，不包含文字"""


    #print('----sync call, please wait a moment----')
    rsp = ImageSynthesis.call(
        api_key=api_keynum,
        model="wanx2.0-t2i-turbo",  # 使用较轻量的模型
        prompt=prompt,
        n=1,
        size='1024*512'  # 降低分辨率到 512*512
    )
    #print('response: %s' % rsp)
    if rsp.status_code == HTTPStatus.OK:
        for result in rsp.output.results:
            # 创建目录
            dir_path = os.path.join(BASE_DIR, "static", username, datetime)
            os.makedirs(dir_path, exist_ok=True)

            # 添加文件名
            file_name = os.path.join(dir_path, "background.jpg")  # 添加具体的文件名

            print(f"保存图片到: {file_name}")
            with open(file_name, 'wb+') as f:
                f.write(requests.get(result.url).content)
    else:
        print('sync_call Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))

    user_msg = {"role": "user", "content": question1}
    messages.append(user_msg)
    completion = client.chat.completions.create(
        model="qwq-plus-latest",  # 此处以 qwq-32b 为例，可按需更换模型名称
        messages=messages,
        # QwQ 模型仅支持流式输出方式调用
        stream=True
    )
    #print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
    for chunk in completion:
        if not chunk.choices:
            print("\nUsage:")
            #print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                #print(delta.reasoning_content, end='', flush=True)
                reasoning_content += delta.reasoning_content
            else:
                if delta.content != "" and is_answering is False:
                    #print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    is_answering = True
                #print(delta.content, end='', flush=True)
                content += delta.content
    response["content"] = content
    messages.append({"role": "assistant", "content": content})
    user_msg = {"role": "user", "content": question2}
    messages.append(user_msg)
    completion = client.chat.completions.create(
        model="qwq-plus-latest",  # 此处以 qwq-32b 为例，可按需更换模型名称
        messages=messages,
        # QwQ 模型仅支持流式输出方式调用
        stream=True
    )
    #print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
    for chunk in completion:
        if not chunk.choices:
            print("\nUsage:")
            #print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                #print(delta.reasoning_content, end='', flush=True)
                reasoning_content += delta.reasoning_content
            else:
                if delta.content != "" and is_answering is False:
                    #print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    is_answering = True
                #print(delta.content, end='', flush=True)
                content += delta.content
    txt_path = os.path.join(BASE_DIR, "Introduction", username, datetime)
    if not os.path.exists(txt_path):
        os.makedirs(txt_path)

    with open(os.path.join(txt_path, "0-0.txt"), "w", encoding="utf-8") as f:
        f.write(content)
        f.close()
    return JsonResponse(response)

@require_http_methods(["GET"])  # 生成注册页面信息
def getPageVice(request):
    import codecs  # 兼容不同编码

    username = request.GET.get("username")
    datetime = request.GET.get("datetime")
    safe_datetime = quote(datetime)
    data = read_json(username, datetime)
    platform = data["platform"]
    response = {"code": 0, "message": "success"}

    #background_url = build_static_url(username, datetime, "background.jpg")

    reasoning_content = ""  # 定义完整思考过程
    content = ""     # 修改这里，使用 content 而不是 answer_content
    is_answering = False   # 判断是否结束思考过程并开始回复
    messages = []

    template_path = os.path.join(BASE_DIR, "llmserver", "templates_components", "tempRes.vue")
    try:
        with codecs.open(template_path, 'r', encoding='utf-8') as f:
            vue_template_code = f.read()
    except Exception as e:
        vue_template_code = ""
        print(f"读取模板失败: {e}")

    # 定义注册的两种 Prompt
    question1_option1 = f"""
        现在有一个后台管理系统叫{platform}, 请为其用户注册页面生成所对应的基于Vue.js的代码, 满足如下要求:
        回复只需要以"<template>"开头, 以"<\/script>"结尾, 不需要其他任何解释说明内容.
        1.要求符合日常用户注册界面业务逻辑.
        2.组件基于element-ui框架.
        3.根容器背景使用指定图片URL：{IMG_URL}/{username}/{safe_datetime}/background.jpg，请确保图片可以显示,正确保留url中的空格，注意图片需要完整显示background-size: cover，使用行内式background-image: url('{IMG_URL}/{username}/{safe_datetime}/background.jpg')
        4.卡片容器需要始终居中,样式要求如下width: 20%;position: absolute;top: 50%;left: 50%;transform: translate(-50%, -50%);
        5.登录卡片内部划分为标题区、输入区、操作按钮区三个纵向模块，各模块间距比例为1:2:1。
        6.标题区域固定于卡片顶部，显示欢迎登录等字样，使用大字号粗体文本居中显示，下方保留与输入区的动态间距。
        7.输入区域项目自定义（例如：用户名，密码，邮箱，电话号码，确认密码。尽量大于五项），但需要标签+输入框的格式，可在下面加小字提示输入格式
        8.要求只返回页面代码部分, 代码只包含template部分和script部分, 不需要style部分. 最重要的是以"<template>"开头, 以"<\/script>"结尾, 不需要其他任何解释说明内容.
    """

    question1_option2 = f"""
    现在有一个后台管理系统叫 {platform}，请为其用户注册页面生成对应的基于 Vue.js 的代码，满足如下要求：
    1. 只返回页面代码部分，代码只包含 <template> 到 </script>，不需要任何解释说明内容，也不需要 style 块。
    2. 所有样式均使用行内式写在元素的 style 属性中，不能使用 <style> 或 scoped 样式。
    3. 页面背景使用图片：url('{IMG_URL}/{username}/{safe_datetime}/background.jpg')，要求覆盖全屏 (width: 100%; height: 100vh; background-size: cover;)，且在右侧留出一块区域放置注册卡片 (margin-right: 80px)。
    4. 注册卡片宽度 360px、白色背景、圆角、阴影、padding: 40px，内部包含用户名、密码、确认密码、邮箱、电话 5 个输入项，使用 label+input 行内样式加上小字提示 (small 标签)。最后有一个 <el-button> type="primary" 作为“注册”按钮，点击触发 onRegister 方法，方法内通过 alert() 显示表单内容。
    5. 代码需符合常规注册业务逻辑示例：onRegister 中可以先用 alert() 演示获取到的表单信息。
    6. 最终输出必须从 <template> 开始，到 </script> 结束，中间不能有任何额外文字或说明。
    7. 参考以下已有 Vue 模板结构，你只能直接复制其中的代码使用，不允许使用 import 语句：
    {vue_template_code}

    请严格遵循以上要求，仅返回符合条件的 Vue2 代码。
    """

    question2 = f"""
        请根据你所生成的页面代码，撰写一段自然流畅的文字，介绍该页面的核心业务功能和用户使用流程，要求如下：

        1. 回复必须以 ***** 开头；
        2. 说明部分仅使用文字描述，不得包含任何代码格式（包括 markdown、代码片段等）；
        3. 说明内容格式如下：
        用户注册
        {{ 说明文字 }}
        4. 整体说明需以一段完整、连贯的叙述形式呈现，禁止使用编号、条列或分点描述；
        5. 内容不少于 300 字；
        6. 请围绕注册页面的核心功能展开描述，包括用户填写哪些信息、表单如何提交、验证机制如何、交互流程如何进行等；
        7. 请避免描述与页面外观有关的内容（如颜色、渐变、字体、布局样式等）；
        8. 不要写开发建议、接口说明、组件调用方式等技术实现细节；
        """

    # 3. 根据同一个全局随机值来决定使用哪一个注册 Prompt
    if RANDOM_CHOICE == 1:
        question1 = question1_option1
    else:
        question1 = question1_option2

    user_msg = {"role": "user", "content": question1}
    messages.append(user_msg)
    completion = client.chat.completions.create(
        model="qwq-plus-latest",  # 此处以 qwq-32b 为例，可按需更换模型名称
        messages=messages,
        # QwQ 模型仅支持流式输出方式调用
        stream=True
    )
    #print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
    for chunk in completion:
        if not chunk.choices:
            print("\nUsage:")
            #print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                #print(delta.reasoning_content, end='', flush=True)
                reasoning_content += delta.reasoning_content
            else:
                if delta.content != "" and is_answering is False:
                    #print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    is_answering = True
                #print(delta.content, end='', flush=True)
                content += delta.content
    response["content"] = content
    messages.append({"role": "assistant", "content": content})
    user_msg = {"role": "user", "content": question2}
    messages.append(user_msg)
    completion = client.chat.completions.create(
        model="qwq-plus-latest",  # 此处以 qwq-32b 为例，可按需更换模型名称
        messages=messages,
        # QwQ 模型仅支持流式输出方式调用
        stream=True
    )
    #print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
    for chunk in completion:
        if not chunk.choices:
            print("\nUsage:")
            #print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                #print(delta.reasoning_content, end='', flush=True)
                reasoning_content += delta.reasoning_content
            else:
                if delta.content != "" and is_answering is False:
                    #print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    is_answering = True
                #print(delta.content, end='', flush=True)
                content += delta.content
    txt_path = os.path.join(BASE_DIR, "Introduction", username, datetime)
    if not os.path.exists(txt_path):
        os.makedirs(txt_path)

    with open(os.path.join(txt_path, "0-1.txt"), "w", encoding="utf-8") as f:
        f.write(content)
        f.close()
    return JsonResponse(response)
