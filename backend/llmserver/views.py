from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from openai import OpenAI
import os
import json
import threading
from django.db.models.fields import DateTimeField
from django.db.models.fields.related import ManyToManyField
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.backend.settings")
from django.conf import settings
from .models import *
from tenacity import retry, stop_after_attempt, wait_exponential
import shutil

client = OpenAI(
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL
)

WEB_URL = "http://121.196.229.117:8000/static"

BASE_DIR = base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIUM_PATH = os.path.join(BASE_DIR, "medium")

from django.db.models.fields import DateTimeField
from django.db.models.fields.related import ManyToManyField


def read_json(username, datetime):
    with open(os.path.join(MEDIUM_PATH, username, datetime, "config.json"), "r", encoding="utf-8") as fr:
        data = json.load(fr)
        fr.close()

    return data


def delete_directory(folder_path):
    if os.path.exists(folder_path):
        # 删除文件夹及其所有内容
        shutil.rmtree(folder_path)

    else:
        raise "文件夹不存在"


def get_response(message):
    try:
        completion = client.chat.completions.create(
            model="qwen-coder-plus-latest",
            messages=message
        )
        return completion
    except Exception as e:
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

def run_another_script_webfront(arg1, arg2, arg3):
    # 使用 subprocess.run 运行另一个 Python 文件并传递参数
    import subprocess
    subprocess.run(["python3", os.path.join(BASE_DIR, "llmserver", "components", "webfront_screenshot.py"), arg1, arg2, arg3])


def run_another_script_backend(arg1, arg2, arg3, arg4):
    # 使用 subprocess.run 运行另一个 Python 文件并传递参数
    import subprocess
    subprocess.run(["python3", os.path.join(BASE_DIR, "llmserver", "components", "backend_views.py"), arg1, arg2, arg3, arg4])

@require_http_methods(["POST"])
def startProgram(request):
    response = {"code": 0, "message": "success"}
    data = json.loads(request.body)
    person_id = data.get("id")
    platform = data.get("platform")
    language = data.get("language")
    datetime = data.get("time")
    username = data.get("username")

    code_path = WEB_URL + "/" + username + "/" + datetime + "/merged_code.docx"
    word_file = WEB_URL + "/" + username + "/" + datetime + "/template_manual.docx"
    introduce_file = WEB_URL + "/" + username + "/" + datetime + "/expanded_description.txt"

    medium_url = os.path.join(MEDIUM_PATH, username, datetime)  # 用户存放某用户在某时间下创建的项目的具体信息
    if not os.path.exists(medium_url):
        os.makedirs(medium_url)
    user_dict = {
        "platform": platform,
        "username": username,
        "datetime": datetime,
        "language": language
    }
    with open(os.path.join(medium_url, "config.json"), "w", encoding="utf-8") as f:
        json.dump(user_dict, f, indent=4)
        f.close()

    record = UserRecord.objects.create(name=platform, time=datetime, language=language, user=UserProfile(id=person_id),
                                       pdf_download=word_file, code_download=code_path, introduce_download=introduce_file)
    record.save()
    thread1 = threading.Thread(target=run_another_script_webfront, args=(platform, username, datetime))
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
def getUserAllRecord(request):
    response = {"code": 0, "message": "success"}
    user_id = request.GET.get("user_id")
    record = UserRecord.objects.filter(user=UserProfile(id=user_id))
    response["data"] = []
    for r in record:
        dict_record = to_dict(r)
        record_id = dict_record["id"]
        record_item = UserRecord.objects.get(id=record_id)
        if dict_record["pdf_status"] == 0:
            relative_path = BASE_DIR+"/"+"/".join(dict_record["pdf_download"].split("/")[3:])
            if os.path.exists(relative_path):
                dict_record["pdf_status"] = 1
                record_item.pdf_status = 1
                record_item.save()
        if dict_record["code_status"] == 0:
            relative_path = BASE_DIR + "/" + "/".join(dict_record["code_download"].split("/")[3:])
            if os.path.exists(relative_path):
                dict_record["code_status"] = 1
                record_item.code_status = 1
                record_item.save()
        if dict_record["introduce_status"] == 0:
            relative_path = BASE_DIR + "/" + "/".join(dict_record["introduce_download"].split("/")[3:])
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
def getMenuConfig(request):  # 生成侧边栏信息
    username = request.GET.get("username")
    datetime = request.GET.get("datetime")
    data = read_json(username, datetime)
    platform = data["platform"]
    language = data["language"]
    response = {"code": 0, "message": "success"}
    MESSAGE = [{"role": "system", "content": "You are a helpful programmer and product manager"}]
    question = f"""
    设计一个{platform}的侧边栏, 有如下要求:
    1.包含至少6个目录以及相应的目录, 目录名称要与系统业务逻辑密切相关. 
    2.以Object的形式返回, 每个Object的key为父目录,每一个key下是一个List,包含所有子目录名称.
    3.回答的时候不需要做任何解释和说明，只需要返回Object即可, 回答开头以Object的"{{"开始")
    """
    query = {"role": "user", "content": question}
    MESSAGE.append(query)
    try:
        completion = api_call(MESSAGE)
    except Exception as e:
        print(f"所有尝试均失败 {e}")

    data_dict = json.loads(completion.model_dump_json())
    menu = data_dict["choices"][0]["message"]["content"]
    menu = json.loads(menu)
    MENU_CONFIG = menu

    json_file = os.path.join(MEDIUM_PATH, username, datetime, "menu.json")   # 保存侧边栏信息
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(MENU_CONFIG, f)
        f.close()

    response["menu"] = MENU_CONFIG
    thread2 = threading.Thread(target=run_another_script_backend, args=(platform, language, username, datetime))
    thread2.start()
    return JsonResponse(response)


@require_http_methods(["GET"])
def getPageInfo(request):  # 根据前段返回的当前点击的侧边栏id生成具体的页面代码
    username = request.GET.get("username")
    datetime = request.GET.get("datetime")
    data = read_json(username, datetime)
    platform = data["platform"]
    response = {"code": 0, "message": "success"}
    with open(os.path.join(MEDIUM_PATH, username, datetime, "menu.json"), "r", encoding="utf-8") as f:
        menu_info = json.load(f)
        f.close()

    menu_item = request.GET.get("index")
    parent_idx = int(menu_item.split("-")[0])
    child_idx = int(menu_item.split("-")[1])
    parent_name = list(menu_info.keys())[int(parent_idx-1)]
    child_name = menu_info[parent_name][int(child_idx-1)]

    MESSAGE = [{"role": "system", "content": "You are a helpful programmer and product manager"}]

    question = f"""
    现在有一个后台管理系统叫{platform}, 请为侧边栏父目录名称为{parent_name}下的{child_name}子目录所对应的页面设计Vue.js页面代码, 满足如下要求:
     1.代码基于element-ui框架, 若有数据展示, 可以编写5-6条示例数据.
     2.要求只返回页面代码部分, 代码只包含template部分和script部分, 不需要style部分. 以"<template>"开头, 以"<\/script>"结尾, 不需要其他任何解释说明内容.
     3.若使用el-table, 不需要固定列宽, 列宽自适应.
     4.页面的组件类型尽量多样化, 尽量包含可操作组件, 例如按钮, 输入框, 链接等.
    """
    query = {"role": "user", "content": question}
    MESSAGE.append(query)
    try:
        completion = api_call(MESSAGE)
    except Exception as e:
        print(f"所有尝试均失败 {e}")
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict["choices"][0]["message"]["content"]
    response["content"] = content
    #  生成具体的页面功能描述
    question = f"""
    请根据你所生成的页面代码, 详细介绍该页面的业务功能以及使用说明, 有如下要求:
    1.代码部分和文字说明部分的中间以"*****"严格分割.
    2.说明部分仅仅使用文字说明, 无需引用任何代码格式(包括markdown).
    3.说明部分格式为：
    {{ 侧边栏名称 }}
    {{ 说明部分文字 }}
    4.侧边栏名称仅为子菜单名称, 不用显示父菜单名称
    5.介绍说明文字至少300字.
    """
    query = {"role": "user", "content": question}
    MESSAGE.append(query)
    try:
        completion = api_call(MESSAGE)
    except Exception as e:
        print(f"所有尝试均失败 {e}")
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict["choices"][0]["message"]["content"]

    txt_path = os.path.join(BASE_DIR, "Introduction", username, datetime)
    if not os.path.exists(txt_path):
        os.makedirs(txt_path)

    with open(os.path.join(txt_path, menu_item+".txt"), "w", encoding="utf-8") as f:
        f.write(content)
        f.close()

    print(f"说明文档{menu_item}已保存")

    return JsonResponse(response)

@require_http_methods(["GET"])   # 生成登录界面信息
def getPageMain(request):
    username = request.GET.get("username")
    datetime = request.GET.get("datetime")
    data = read_json(username, datetime)
    platform = data["platform"]
    response = {"code": 0, "message": "success"}
    MESSAGE = [{"role": "system", "content": "You are a helpful programmer and product manager"}]
    question = f"""
        现在有一个后台管理系统叫{platform}, 请为其用户登录页面生成所对应的基于Vue.js的代码, 满足如下要求:
         1.要求符合日常用户登录界面业务逻辑. 
         2.组件基于element-ui框架.
         3.除了登录按钮之外,还需要额外添加注册按钮.
         4.内容包含标题,输入框以及按钮.
         5.标题在输入框上方,距离输入框5vh.按钮在输入框下方,距离输入框底部5vh.
         6.要求只返回页面代码部分, 代码只包含template部分和script部分, 不需要style部分. 以"<template>"开头, 以"<\/script>"结尾, 不需要其他任何解释说明内容.
        """
    query = {"role": "user", "content": question}
    MESSAGE.append(query)
    try:
        completion = api_call(MESSAGE)
    except Exception as e:
        print(f"所有尝试均失败 {e}")
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict["choices"][0]["message"]["content"]
    response["content"] = content

    question = f"""
       请根据你所生成的页面代码, 详细介绍该页面的业务功能以及使用说明, 有如下要求:
       1.代码部分和文字说明部分的中间以"*****"严格分割.
       2.说明部分仅仅使用文字说明, 无需引用任何代码格式(包括markdown).
       3.说明部分格式为:
       用户登录
       {{ 说明部分文字 }}
       4.介绍说明文字至少300字.
       """
    query = {"role": "user", "content": question}
    MESSAGE.append(query)
    try:
        completion = api_call(MESSAGE)
    except Exception as e:
        print(f"所有尝试均失败 {e}")
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict["choices"][0]["message"]["content"]

    txt_path = os.path.join(BASE_DIR, "Introduction", username, datetime)
    if not os.path.exists(txt_path):
        os.makedirs(txt_path)

    with open(os.path.join(txt_path, "0-0.txt"), "w", encoding="utf-8") as f:
        f.write(content)
        f.close()

    return JsonResponse(response)


@require_http_methods(["GET"])  # 生成注册页面信息
def getPageVice(request):
    username = request.GET.get("username")
    datetime = request.GET.get("datetime")
    data = read_json(username, datetime)
    platform = data["platform"]
    response = {"code": 0, "message": "success"}
    MESSAGE = [{"role": "system", "content": "You are a helpful programmer and product manager"}]
    question = f"""
            现在有一个后台管理系统叫{platform}, 请为其用户注册页面生成所对应的基于Vue.js的代码, 满足如下要求:
             1.要求符合日常用户注册界面业务逻辑. 
             2.组件基于element-ui框架.
             3.内容包含标题,输入框以及注册按钮.
             4.输入框至少包括姓名,电话号码,验证码,密码,确认密码,你也可以自由发挥再增添一下注册内容.
             5.电话号码输入框旁有一个获取验证码的按钮并排.
             5.标题在输入框上方,距离输入框5vh.按钮在输入框下方,距离输入框底部5vh.
             6.要求只返回页面代码部分, 代码只包含template部分和script部分, 不需要style部分. 以"<template>"开头, 以"<\/script>"结尾, 不需要其他任何解释说明内容.
            """
    query = {"role": "user", "content": question}
    MESSAGE.append(query)
    try:
        completion = api_call(MESSAGE)
    except Exception as e:
        print(f"所有尝试均失败 {e}")
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict["choices"][0]["message"]["content"]
    response["content"] = content

    question = f"""
           请根据你所生成的页面代码, 详细介绍该页面的业务功能以及使用说明, 有如下要求:
           1.代码部分和文字说明部分的中间以"*****"严格分割.
           2.说明部分仅仅使用文字说明, 无需引用任何代码格式(包括markdown).
           3.说明部分格式为:
           用户注册
           {{ 说明部分文字 }}
           4.介绍说明文字至少300字.
           """
    query = {"role": "user", "content": question}
    MESSAGE.append(query)
    try:
        completion = api_call(MESSAGE)
    except Exception as e:
        print(f"所有尝试均失败 {e}")
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict["choices"][0]["message"]["content"]

    txt_path = os.path.join(BASE_DIR, "Introduction", username, datetime)
    if not os.path.exists(txt_path):
        os.makedirs(txt_path)

    with open(os.path.join(txt_path, "0-1.txt"), "w", encoding="utf-8") as f:
        f.write(content)
        f.close()

    return JsonResponse(response)
