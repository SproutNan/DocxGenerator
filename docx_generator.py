from objects import *
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from time import time
from base64_coder import *
from modify_act import *
from modify_item import *

# 创建新活动
def create_activity_record():
    activity_info = input_group("请输入活动信息：", [
        input("活动名称：", type="text", name="name", required=True),
        input("活动时间：", type="date", name="time", required=True),
        input("活动地点：", type="text", name="place", required=True)
    ])
    activity_director = input_group("请输入活动负责人：", [
        input("姓名：", type="text", name="name", required=True),
        # 学号以两个英文字母开头，后面跟着8位数字
        input("学号：", type="text", name="stuid", pattern=r"[a-zA-Z]{2}\d{8}", help_text="如：PB20000001", required=True),
        input("手机号：", type="text", name="phone", pattern=r"\d{11}", required=True),
        input("邮箱：", type="text", name="email", pattern=r".+@.+", required=True)
    ])
    activity_director = student(
        activity_director["name"], 
        activity_director["stuid"], 
        activity_director["phone"], 
        activity_director["email"]
    )
    activity_new = activity()
    activity_new.init(
        activity_info["name"],
        activity_director,
        activity_info["time"],
        activity_info["place"]
    )
    return activity_new

# 下载存档
def download(act: activity):
    # 下载activity的json版本
    serialized = act.to_json()
    # 提供文件下载
    put_file(f"{act.name}_{int(time())}.json", content=serialized.encode("utf-8"))
    # 退出
    return None

# 为活动添加策划书，物资等
def activity_operating(act: activity):
    if act is None:
        return
    while True:
        # 创建一个按钮菜单
        action = actions(label=f"对[{act.name}]的操作", buttons=[
            {'label': "管理活动概况", 'value': "modify_info"},
            {'label': "管理活动物资", 'value': "modify_item"},
            {'label': "下载存档", 'value': "download"},
            {'label': "退出对此活动的操作", 'value': "back"}
        ], help_text=f"详细信息：{act.info()}")
        # 根据选择的操作进行处理
        value_map = {
            "modify_info": modify_info,
            "modify_item": modify_item,
            "download": download,
            "back": None
        }
        if value_map[action] is None:
            break
        else:
            value_map[action](act)
 
def docx_generator_main():
    # 文字说明
    put_markdown("# 校芳草社活动报销处理系统")
    put_markdown("- 您只需要按照提示输入相关信息，系统会自动创建活动报销用的docx文件供打印。")
    put_markdown("- 注意，本系统是**脱机系统**，不保存您的任何信息，也不会上传到任何服务器。您在完成编辑之后，请下载文件并保存到本地。如果需要二次修改，请将之前保存的文件上传到浏览器打开。（你可以理解为需要手动存档读档，这是为了减轻服务器端的开销）")
    while True:
        put_markdown("---")
        # 选择创建还是读取
        action = actions(label="请选择操作", buttons=[
            {'label': "创建新活动", 'value': "create"},
            {'label': "读取已有活动", 'value': "read"},
            {'label': "将存档转换为docx供打印", 'value': "convert"}
        ])
        if action == "read" or action == "convert":
            # 读取已有活动
            activity_file = file_upload("请上传活动存档", accept=".json")
            try:
                activitys = activity()
                activitys.from_json(activity_file["content"].decode("utf-8"))
                if action == "convert":
                    # 转换为docx
                    # activitys.to_docx()
                    # 下载docx
                    # put_file(f"{activitys.name}_{int(time())}.docx", content=activitys.docx)
                    pass
            except:
                popup("错误提示", "读取活动存档失败，请检查文件格式是否正确。\n如果您是从本系统下载的文件，请检查是否曾经修改过文件内容。")
                continue
        elif action == "create":
            activitys = create_activity_record()
        # 为活动添加策划书，物资等(编辑模式)
        if action != "convert":
            activity_operating(activitys)
        # 是否退出
        if actions(label="你的工作都完成了吗？", buttons=[
            {'label': "是的，退出", 'value': "exit"},
            {'label': "不是的，我还有另一个活动要编辑", 'value': "continue"}
        ]) == "exit":
            break
    put_markdown("再见，祝您工作顺利！")