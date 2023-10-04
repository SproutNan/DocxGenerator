from modules.base64_coder import *
from classes.activity import activity
from classes.student import student
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from time import time

# 管理活动概况
def modify_info(act: activity):
    action = actions(label=f"管理活动[{act.name}]概况", buttons=[
        {'label': "修改活动信息", 'value': "modify_act_info"},
        {'label': "管理策划书", 'value': "modify_act_plan"},
        {'label': "管理新闻稿", 'value': "modify_act_news"},
        {'label': "返回上一级", 'value': "back"}
    ], help_text=f"详细信息：{act.info()}")

    if action == "modify_act_info":
        modify_act_info(act)
    elif action == "modify_act_plan":
        modify_act_plan(act)
    elif action == "modify_act_news":
        modify_act_news(act)
    else:
        return

# 修改活动信息
def modify_act_info(act: activity):
    old_act_info = {
        "name": act.name,
        "director": act.director,
        "time": act.time,
        "place": act.place
    }
    toast("已经为您自动填写了原来的信息，如果不需要修改请直接点击「提交」")
    new_act_info = input_group("请输入新的活动信息：", [
        input("活动名称：", type="text", name="name", value=old_act_info["name"], required=True),
        input("活动时间：", type="date", name="time", value=old_act_info["time"], required=True),
        input("活动地点：", type="text", name="place", value=old_act_info["place"], required=True)
    ])
    toast("已经为您自动填写了原来的信息，如果不需要修改请直接点击「提交」")
    new_act_director = input_group("请输入新的活动负责人：", [
        input("姓名：", type="text", name="name", value=old_act_info["director"].name, required=True),
        # 学号以两个英文字母开头，后面跟着8位数字
        input("学号：", type="text", name="stuid", value=old_act_info["director"].stuid, pattern=r"[a-zA-Z]{2}\d{8}", help_text="如：PB20000001", required=True),
        input("手机号：", type="text", name="phone", value=old_act_info["director"].phone, pattern=r"\d{11}", required=True),
        input("邮箱：", type="text", name="email", value=old_act_info["director"].email, pattern=r".+@.+", required=True)
    ])
    act.name = new_act_info["name"]
    act.time = new_act_info["time"]
    act.place = new_act_info["place"]
    act.director = student(
        new_act_director["name"],
        new_act_director["stuid"],
        new_act_director["phone"],
        new_act_director["email"]
    )
    toast("修改成功！")

# 修改策划书
def modify_act_plan(act: activity):
    action = actions(label=f"管理活动[{act.name}]的策划书", buttons=[
        {'label': "上传新的策划书", 'value': "modify_act_plan_upload"},
        {'label': "预览当前策划书", 'value': "modify_act_plan_preview"},
        {'label': "返回上一级", 'value': "back"}
    ], help_text=f"详细信息：{act.info()}")

    if action == "modify_act_plan_upload":
        modify_act_plan_upload(act)
    elif action == "modify_act_plan_preview":
        modify_act_plan_preview(act)

# 添加策划书
def modify_act_plan_upload(act: activity):
    upload = file_upload("请上传策划书", accept=".docx", max_size=1024*1024*5, help_text="请上传小于5MB的docx文件")
    if upload is not None:
        act.plan = upload

# 预览当前策划书
def modify_act_plan_preview(act: activity):
    if act.plan is None:
        toast("当前活动没有策划书，请先上传策划书")
        return
    else:
        content = act.plan["content"]
        put_file(f"{act.name}策划书_{int(time())}.docx", content=content)

# 修改新闻稿
def modify_act_news(act: activity):
    action = actions(label=f"管理活动[{act.name}]的新闻稿", buttons=[
        {'label': "上传新的新闻稿", 'value': "modify_act_news_upload"},
        {'label': "预览当前新闻稿", 'value': "modify_act_news_preview"},
        {'label': "返回上一级", 'value': "back"}
    ], help_text=f"详细信息：{act.info()}")

    if action == "modify_act_news_upload":
        modify_act_news_upload(act)
    elif action == "modify_act_news_preview":
        modify_act_news_preview(act)

# 添加新闻稿
def modify_act_news_upload(act: activity):
    upload = file_upload("请上传新闻稿", accept=".docx", max_size=1024*1024*5, help_text="请上传小于5MB的docx文件")
    if upload is not None:
        act.news = upload

# 预览当前新闻稿
def modify_act_news_preview(act: activity):
    if act.news is None:
        toast("当前活动没有新闻稿，请先上传新闻稿")
        return
    else:
        content = act.news["content"]
        put_file(f"{act.name}新闻稿_{int(time())}.docx", content=content)