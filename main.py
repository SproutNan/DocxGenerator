from objects import *
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio import start_server
from time import time

test_activity = activity()
test_activity.init(
    "测试活动",
    student("测试负责人", "PB20000000", "12345678901", "sprout@mail.ustc.edu.cn"),
    "2020-01-01",
    "中国科学技术大学"
)

# 创建新活动
def create_activity_record():
    activity_name = input("请输入活动名称：", type="text", required=True)
    activity_director = input_group("请输入活动负责人：", [
        input("姓名：", type="text", name="name", required=True),
        # 学号以两个英文字母开头，后面跟着8位数字
        input("学号：", type="text", name="stuid", pattern=r"[a-zA-Z]{2}\d{8}", help_text="如：PB20000001", required=True),
        input("手机号：", type="text", name="phone", pattern=r"\d{11}", required=True),
        input("邮箱：", type="text", name="email", pattern=r".+@.+", required=True)
    ])
    activity_time = input("请输入活动时间：", type="date", required=True)
    activity_place = input("请输入活动地点：", type="text", required=True)
    activity_director = student(
        activity_director["name"], 
        activity_director["stuid"], 
        activity_director["phone"], 
        activity_director["email"]
    )
    return activity(activity_name, activity_director, activity_time, activity_place)

# 添加物资
def add_item(act: activity):
    pass

# 查看物资
def show_item(act: activity):
    pass

# 添加策划书
def add_plan(act: activity):
    pass

# 添加新闻稿
def add_news(act: activity):
    upload = file_upload("请上传新闻稿", accept=".docx", max_size=1024*1024*5, help_text="请上传小于5MB的docx文件")
    if upload is not None:
        act.news = upload

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
            {'label': "添加物资", 'value': "add_item"},
            {'label': "查看物资", 'value': "show_item"},
            {'label': "添加策划书", 'value': "add_plan"},
            {'label': "添加新闻稿", 'value': "add_news"},
            {'label': "下载存档", 'value': "download"},
            {'label': "退出对此活动的操作", 'value': "back"}
        ], help_text=f"详细信息：{act.info()}")
        # 根据选择的操作进行处理
        value_map = {
            "add_item": add_item,
            "show_item": show_item,
            "add_plan": add_plan,
            "add_news": add_news,
            "download": download,
            "back": None
        }
        if value_map[action] is None:
            break
        else:
            value_map[action](act)
 
def main():
    # 文字说明
    put_markdown("# 校芳草社活动报销处理系统")
    put_markdown("- 您只需要按照提示输入相关信息，系统会自动创建活动报销用的docx文件供打印。")
    put_markdown("- 注意，本系统是**脱机系统**，不保存您的任何信息，也不会上传到任何服务器。您在完成编辑之后，请下载文件并保存到本地。如果需要二次修改，请将之前保存的文件上传到浏览器打开。（你可以理解为需要手动存档读档，这是为了减轻服务器端的开销）")
    while True:
        # 选择创建还是读取
        action = actions(label="请选择操作", buttons=[
            {'label': "创建新活动", 'value': "create"},
            {'label': "读取已有活动", 'value': "read"}
        ])
        if action == "read":
            # 读取已有活动
            activity_file = file_upload("请上传活动存档", accept=".json")
            try:
                activitys = activity()
                activitys.from_json(activity_file["content"].decode("utf-8"))
            except:
                popup("错误提示", "读取活动存档失败，请检查文件格式是否正确。\n如果您是从本系统下载的文件，请检查是否曾经修改过文件内容。")
                continue
        else:
            activitys = create_activity_record()
        # 为活动添加策划书，物资等
        activity_operating(activitys)
        # 是否退出
        if actions(label="你的工作都完成了吗？", buttons=[
            {'label': "是的，退出", 'value': "exit"},
            {'label': "不是的，我还有另一个活动要编辑", 'value': "continue"}
        ]) == "exit":
            break
    put_markdown("再见，祝您工作顺利！")
    
 
if __name__ == '__main__':
    start_server(
        applications=[main,],
        debug=True,
        # 最大并发数
        # max_payload_size=1024 * 1024 * 1024,？
        # auto_open_webbrowser=True,
        remote_access=True,
        port=8080
    )