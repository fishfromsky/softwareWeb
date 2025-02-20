from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from openai import OpenAI
import os
import json


LLM_BASE_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
LLM_API_KEY = 'sk-8fafb7bba6d04e45a989191a8820f7a1'

client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL
)

PLATFORM = '共享充电宝后台管理系统'

BASE_DIR = base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXT_PATH = os.path.join(BASE_DIR, 'Introduction')
if not os.path.exists(TXT_PATH):
    os.makedirs(TXT_PATH)

MENU_CONFIG = {}


@require_http_methods(['GET'])
def getNameConfig(request):
    global PLATFORM
    response = {'code': 0, 'message': 'success'}
    response['name'] = PLATFORM
    return JsonResponse(response)

@require_http_methods(['GET'])
def getMenuConfig(request):
    global PLATFORM
    global MENU_CONFIG
    response = {'code': 0, 'message': 'success'}
    MESSAGE = [{'role': 'system', 'content': 'You are a helpful programmer and product manager'}]
    question = f"""
    设计一个'{PLATFORM}的侧边栏, 有如下要求:
    1.包含至少6个目录以及相应的目录, 目录名称要与系统业务逻辑密切相关. 
    2.以Object的形式返回, 每个Object的key为父目录,每一个key下是一个List,包含所有子目录名称.
    3.回答的时候不需要做任何解释和说明，只需要返回Object即可, 回答开头以Object的"{{"开始')
    """
    query = {'role': 'user', 'content': question}
    MESSAGE.append(query)
    completion = client.chat.completions.create(
        model="qwen-coder-plus-latest",
        messages=MESSAGE
    )
    data_dict = json.loads(completion.model_dump_json())
    menu = data_dict['choices'][0]['message']['content']
    menu = json.loads(menu)
    MENU_CONFIG = menu
    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(MENU_CONFIG, f)
        f.close()
    response['menu'] = MENU_CONFIG
    return JsonResponse(response)


@require_http_methods(['GET'])
def getPageInfo(request):
    global PLATFORM
    global MENU_CONFIG
    response = {'code': 0, 'message': 'success'}
    menu_item = request.GET.get('index')
    parent_idx = int(menu_item.split('-')[0])
    child_idx = int(menu_item.split('-')[1])
    parent_name = list(MENU_CONFIG.keys())[int(parent_idx-1)]
    child_name = MENU_CONFIG[parent_name][int(child_idx-1)]

    MESSAGE = [{'role': 'system', 'content': 'You are a helpful programmer and product manager'}]

    question = f"""
    现在有一个后台管理系统叫{PLATFORM}, 请为侧边栏父目录名称为{parent_name}下的{child_name}子目录所对应的页面设计Vue.js页面代码, 满足如下要求:
     1.要求符合相关目录主题名称与业务逻辑. 
     2.代码基于element-ui框架, 若有数据展示, 可以编写5-6条示例数据.
     3.要求只返回页面代码部分, 代码只包含template部分和script部分, 不需要style部分. 以"<template>"开头, 以"<\/script>"结尾, 不需要其他任何解释说明内容.
     4.若使用el-table, 不需要固定列宽, 列宽自适应.
     5.页面的组件类型尽量多样化, 尽量包含可操作组件, 例如按钮, 输入框, 链接等.
    """
    query = {'role': 'user', 'content': question}
    MESSAGE.append(query)
    completion = client.chat.completions.create(
        model="qwen-coder-plus-latest",
        messages=MESSAGE
    )
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict['choices'][0]['message']['content']
    response['content'] = content

    question = f"""
    请根据你所生成的页面代码, 详细介绍该页面的业务功能以及使用说明, 有如下要求:
    1.代码部分和文字说明部分的中间以'*****'严格分割.
    2.说明部分仅仅使用文字说明, 无需引用任何代码格式(包括markdown).
    3.说明部分第一行为当前侧边栏的名字, 随后下一行紧接着是具体的介绍文字, 中间无需再插入额外符号(如换行符)
    4.介绍说明文字至少300字.
    """
    query = {'role': 'user', 'content': question}
    MESSAGE.append(query)
    completion = client.chat.completions.create(
        model="qwen-coder-plus-latest",
        messages=MESSAGE
    )
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict['choices'][0]['message']['content']
    with open(os.path.join(TXT_PATH, 'test'+menu_item+'.txt'), 'w', encoding='utf-8') as f:
        f.write(content)
        f.close()

    return JsonResponse(response)

@require_http_methods(['GET'])
def getLoginInfo(request):
    global PLATFORM
    response = {'code': 0, 'message': 'success'}
    MESSAGE = [{'role': 'system', 'content': 'You are a helpful programmer and product manager'}]
    question = f"""
        现在有一个后台管理系统叫{PLATFORM}, 请为其用户登录页面生成所对应的基于Vue.js的代码, 满足如下要求:
         1.要求符合日常用户登录界面业务逻辑. 
         2.组件基于element-ui框架.
         3.除了登录按钮之外,还需要额外添加注册按钮.
         4.内容包含标题,输入框以及按钮.
         5.标题在输入框上方,距离输入框5vh.按钮在输入框下方,距离输入框底部5vh.
         6.要求只返回页面代码部分, 代码只包含template部分和script部分, 不需要style部分. 以"<template>"开头, 以"<\/script>"结尾, 不需要其他任何解释说明内容.
        """
    query = {'role': 'user', 'content': question}
    MESSAGE.append(query)
    completion = client.chat.completions.create(
        model="qwen-coder-plus-latest",
        messages=MESSAGE
    )
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict['choices'][0]['message']['content']
    response['content'] = content

    question = f"""
       请根据你所生成的页面代码, 详细介绍该页面的业务功能以及使用说明, 有如下要求:
       1.代码部分和文字说明部分的中间以'*****'严格分割.
       2.说明部分仅仅使用文字说明, 无需引用任何代码格式(包括markdown).
       3.说明部分第一行为'用户登录', 随后下一行紧接着是具体的介绍文字, 中间无需再插入额外符号(如换行符)
       4.介绍说明文字至少300字.
       """
    query = {'role': 'user', 'content': question}
    MESSAGE.append(query)
    completion = client.chat.completions.create(
        model="qwen-coder-plus-latest",
        messages=MESSAGE
    )
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict['choices'][0]['message']['content']
    with open(os.path.join(TXT_PATH, '0-0.txt'), 'w', encoding='utf-8') as f:
        f.write(content)
        f.close()

    return JsonResponse(response)


@require_http_methods(['GET'])
def getRegisterInfo(request):
    global PLATFORM
    response = {'code': 0, 'message': 'success'}
    MESSAGE = [{'role': 'system', 'content': 'You are a helpful programmer and product manager'}]
    question = f"""
            现在有一个后台管理系统叫{PLATFORM}, 请为其用户注册页面生成所对应的基于Vue.js的代码, 满足如下要求:
             1.要求符合日常用户注册界面业务逻辑. 
             2.组件基于element-ui框架.
             3.内容包含标题,输入框以及注册按钮.
             4.输入框至少包括姓名,电话号码,验证码,密码,确认密码,你也可以自由发挥再增添一下注册内容.
             5.电话号码输入框旁有一个获取验证码的按钮并排.
             5.标题在输入框上方,距离输入框5vh.按钮在输入框下方,距离输入框底部5vh.
             6.要求只返回页面代码部分, 代码只包含template部分和script部分, 不需要style部分. 以"<template>"开头, 以"<\/script>"结尾, 不需要其他任何解释说明内容.
            """
    query = {'role': 'user', 'content': question}
    MESSAGE.append(query)
    completion = client.chat.completions.create(
        model="qwen-coder-plus-latest",
        messages=MESSAGE
    )
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict['choices'][0]['message']['content']
    response['content'] = content

    question = f"""
           请根据你所生成的页面代码, 详细介绍该页面的业务功能以及使用说明, 有如下要求:
           1.代码部分和文字说明部分的中间以'*****'严格分割.
           2.说明部分仅仅使用文字说明, 无需引用任何代码格式(包括markdown).
           3.说明部分第一行为'用户注册', 随后下一行紧接着是具体的介绍文字, 中间无需再插入额外符号(如换行符)
           4.介绍说明文字至少300字.
           """
    query = {'role': 'user', 'content': question}
    MESSAGE.append(query)
    completion = client.chat.completions.create(
        model="qwen-coder-plus-latest",
        messages=MESSAGE
    )
    data_dict = json.loads(completion.model_dump_json())
    content = data_dict['choices'][0]['message']['content']
    with open(os.path.join(TXT_PATH, '0-1.txt'), 'w', encoding='utf-8') as f:
        f.write(content)
        f.close()

    return JsonResponse(response)