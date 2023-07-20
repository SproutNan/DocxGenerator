from objects import *
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from time import time
from base64_coder import *

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

# 添加物资
def add_item(act: activity):
    no_forever = False
    while True:
        # 询问是否继续添加物资
        if not no_forever:
            result = actions("是否需要修改物资分组？", ["是", "否", "否，不要再问我"])
            if result == "否，不要再问我":
                no_forever = True
            elif result == "是":
                group_str = "，".join(act.groups)
                group_str = input("请修改下方的物资分组，组名与组名之间用「，」分割", type="text", value=group_str, required=True)
                group_str = group_str.replace(", ", ",")
                group_str = group_str.replace(",", "，")
                act.groups = group_str.split("，")            

        item_info = input_group("请输入物资信息：", [
            select("组别", options=act.groups, name="group", required=True),
            input("名称", type="text", name="name", validate=lambda name: "名称不能超过15个字" if len(name) > 15 else None, required=True),
            input("数量", type="number", name="count", validate=lambda count: "数量必须是正整数" if count <= 0 else None, required=True),
            input("单价", type="float", name="price", validate=lambda price: "单价必须是正数" if price <= 0 else None, required=True),
            input("总价", type="float", name="total", validate=lambda total: "总价必须是正数" if total is not None and total <= 0 else None, help_text="此空如果为空则自动计算为 数量*单价，如果用了优惠等可以手动输入"),
            # 选择题
            select("用途", options=["奖品", "物资", "其他"], name="use", required=True),
            file_upload("发票", name="invoice", accept=".jpg,.png,.pdf", max_size=1024*1024*2, help_text="请上传发票的扫描件或者照片，大小不得超过2M，如果不上传则默认使用纸质发票"),
            input("备注", type="text", name="note"),
        ])
        item_new = item(
            item_info["name"],
            item_info["count"],
            item_info["price"]
        )
        # 总价
        if item_info["total"] is not None:
            item_new.total = item_info["total"]
        else:
            item_new.total = item_new.count * item_new.price
        item_new.group = item_info["group"]
        item_new.use = item_info["use"]
        item_new.note = item_info["note"]
        if item_info["invoice"] is not None:
            item_info["invoice"]["content"] = to_base64(item_info["invoice"]["content"])
            item_new.invoice = item_info["invoice"]
        act.item.append(item_new)
        toast("添加成功！")
        
        if actions("是否继续添加物资？", ["是", "否"]) == "否":
            break


# 查看物资
def show_item(act: activity):
    put_table_items = [[span('组别', row=2), span('详情', col=7)],
                       ['名称', '数量', '单价', '总价', '用途', '发票', '备注']]
    put_items = []
    for it in act.item:
        put_items.append([
            it.group,
            it.name,
            it.count,
            it.price,
            it.total,
            it.use,
            "纸质发票" if it.invoice is None else "发票已上传",
            it.note,
        ])
    put_items.sort(key=lambda x: x[0])
    put_table_items.extend(put_items)
    # 加入组内合计和所有合计
    put_table_items.append([span("", col=8)])
    put_table_items.append([span("组内合计", col=8)])
    for group in act.groups:
        put_table_items.append([
            span(group, col=2),
            span(sum([it.total for it in act.item if it.group == group]), col=6)
        ])
    put_table_items.append([span("", col=8)])
    put_table_items.append([span("合计", col=7), span(sum([it.total for it in act.item]), col=1)])
    popup("物资清单", put_table(put_table_items), size=PopupSize.LARGE)

# 添加策划书
def add_plan(act: activity):
    upload = file_upload("请上传策划书", accept=".docx", max_size=1024*1024*5, help_text="请上传小于5MB的docx文件")
    if upload is not None:
        act.plan = upload

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
 
def docx_generator_main():
    # 文字说明
    put_markdown("# 校芳草社活动报销处理系统")
    put_markdown("- 您只需要按照提示输入相关信息，系统会自动创建活动报销用的docx文件供打印。")
    put_markdown("- 注意，本系统是**脱机系统**，不保存您的任何信息，也不会上传到任何服务器。您在完成编辑之后，请下载文件并保存到本地。如果需要二次修改，请将之前保存的文件上传到浏览器打开。（你可以理解为需要手动存档读档，这是为了减轻服务器端的开销）")
    while True:
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