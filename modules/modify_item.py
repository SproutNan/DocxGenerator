import io
from PIL import Image
from classes.activity import activity
from classes.item import item
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from modules.base64_coder import *
from modules.invoice import *
import traceback
import fitz
import tempfile
import os


# 管理活动物资
def modify_item(act: activity) -> bool:
    while True:
        action = actions(label=f"管理活动[{act.name}]的物资", buttons=[
            {'label': "管理物资标签", 'value': "modify_item_label"},
            {'label': "添加物资", 'value': "modify_item_add"},
            {'label': "查看物资", 'value': "modify_item_show"},
            {'label': "删除物资", 'value': "modify_item_delete"},
            {'label': "返回上一级", 'value': "back"}
        ], help_text=f"详细信息：{act.info()}")
        value_map = {
            "modify_item_label": modify_item_label,
            "modify_item_add": modify_item_add,
            "modify_item_show": modify_item_show,
            "modify_item_delete": modify_item_delete,
            "back": None
        }
        if value_map[action] is None:
            break
        else:
            value_map[action](act)


# 管理物资标签
def modify_item_label(act: activity):
    group_str = "，".join(act.groups)
    group_str = input("请修改下方的物资分组，组名与组名之间用「，」分割", type="text",
                      value=group_str, required=True, help_text="每个组名不能超过6个字，最多不超过30个组")
    group_str = group_str.replace(", ", ",")
    group_str = group_str.replace(",", "，")
    groups = group_str.split("，")
    if len(groups) > 30:
        groups = groups[:30]
        put_markdown("- 最多只能有30个组，已经为您截断")
    for i in range(len(groups)):
        if len(groups[i]) > 6:
            put_markdown(f"- 组名**{groups[i]}**超过6个字，将被截断为**{groups[i][:6]}**")
            groups[i] = groups[i][:6]
    act.groups = groups
    put_markdown("- 修改物资标签成功！")


# 添加物资
def modify_item_add(act: activity):
    while True:
        action = actions(label=f"添加物资方式", buttons=[
            {'label': "手动输入信息", 'value': "modify_item_add_manual"},
            {'label': "发票自动识别", 'value': "modify_item_add_ocrinv"},
        ])
        if action == "modify_item_add_manual":
            try:
                if not modify_item_add_manual(act):
                    continue
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                popup("错误提示", f"应用内部错误，请联系管理员\n{e}")
                continue
        elif action == "modify_item_add_ocrinv":
            try:
                modify_item_add_ocrinv(act)
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                popup("错误提示", f"应用内部错误，请联系管理员\n{e}")
                continue
        else:
            return

        if actions("是否继续添加物资？", ["是", "否"]) == "否":
            break

# 手动输入信息 item 是一个 list 的迭代器
def modify_item_add_manual(act: activity, iterator=None, invoice: bytes = None):
    # 遍历下一个
    curItem = next(iterator, "nothing") if iterator is not None else None
    if curItem == "nothing":
        return

    inputs = [
        select("组别", options=act.groups, name="group", required=True),
        input("名称", type="text", name="name", validate=lambda name: "名称不能超过15个字" if len(
            name) > 15 else None, required=True, value=curItem["名称"] if curItem is not None else None),
        input("数量", type="number", name="count", validate=lambda count: "数量必须是正整数" if count <=
              0 else None, required=True, value=curItem["数量"] if curItem is not None else None),
        input("单价", type="float", name="price", validate=lambda price: "单价必须是正数" if price <=
              0 else None, required=True, value=curItem["单价"] if curItem is not None else None),
        input("总价", type="float", name="total", validate=lambda total: "总价必须是正数" if total is not None and total <=
              0 else None, help_text="此空如果为空则自动计算为 数量*单价，如果用了优惠等可以手动输入", value=curItem["总价"] if curItem is not None else None),
        # 选择题
        select("用途", options=["奖品", "物资", "其他"], name="use", required=True),
        input("备注", type="text", name="note"),
        file_upload("网购购买截图", name="screenshot", accept=".jpg", max_size=1024 * 1024 * 2,
                    help_text="请上传JPG格式的网购购买截图，大小不得超过2M，如果不上传则认为是线下购买")
    ]

    if iterator is None:
        inputs.insert(-1, file_upload("发票", name="invoice", accept=".jpg,.pdf", max_size=1024 * 1024 * 2,
                                      help_text="请上传发票的扫描件或者JPG格式图片，大小不得超过2M，如果不上传则默认使用纸质发票"), )

    item_info = input_group("请输入物资信息：", inputs)
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
    # 发票
    if iterator is None and item_info["invoice"] is not None:
        item_info["invoice"]["content"] = to_base64(
            item_info["invoice"]["content"])
        item_new.invoice = item_info["invoice"]
    elif iterator is not None and invoice is not None:
        item_new.invoice = to_base64(invoice)
    # 购买截图
    if item_info["screenshot"] is not None:
        item_info["screenshot"]["content"] = to_base64(
            item_info["screenshot"]["content"])
        item_new.screenshot = item_info["screenshot"]
    # 添加到活动物资中
    act.items.append(item_new)
    toast("添加成功！")
    if iterator is not None:
        modify_item_add_manual(act, iterator, invoice)


# 发票自动识别
def modify_item_add_ocrinv(act: activity):
    file = file_upload("请上传发票", accept=".jpg,.pdf",
                       max_size=1024*1024*2, help_text="请上传发票的扫描件或者照片，大小不得超过2M")
    print(file['mime_type'], file['filename'])
    if file['mime_type'] == 'application/pdf':
        pdf_bytes = file['content']
        # 创建临时文件
        temp_pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_pdf_file.write(pdf_bytes)
        temp_pdf_file.close()
        pdf_document = fitz.open(temp_pdf_file.name)
        if (pdf_document.page_count > 1):
            put_markdown("PDF文件有多页，只识别第一页")
        pdf_page = pdf_document.load_page(0)
        pixmap = pdf_page.get_pixmap()
        image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        content = buffer.getvalue()
        pdf_document.close()
        os.remove(temp_pdf_file.name)
    else:
        try:
            image = Image.open(io.BytesIO(file["content"]))
            content = file["content"]
        except Exception as e:
            print(e)
            popup("错误提示", "图片格式错误，请上传JPG格式的图片")
            return
    put_markdown("正在识别中，请稍等...")
    items = handle_invoice(image)
    if items is not None and len(items) > 0:
        put_markdown("识别成功！")
        modify_item_add_manual(act, iter(items), content)
    else:
        put_markdown("识别失败，请检查发票是否清晰")

# 查看物资
def modify_item_show(act: activity):
    if len(act.items) == 0:
        toast("当前活动没有物资，请先添加物资")
        return
    
    put_table_items = [[span('组别', row=2), span('详情', col=7)],
                       ['名称', '数量', '单价', '总价', '用途', '发票', '备注']]
    put_items = []
    for it in act.items:
        put_items.append([
            it.group,
            it.name,
            it.count,
            it.price,
            it.total,
            it.use,
            "纸质发票" if it.invoice is None else "发票已上传",
            f"{it.note}, 有购买截图" if it.screenshot is not None else it.note,
        ])
    put_items.sort(key=lambda x: x[0])
    put_table_items.extend(put_items)
    # 加入组内合计和所有合计
    put_table_items.append([span("", col=8)])
    put_table_items.append([span("组内合计", col=8)])
    for group in act.groups:
        put_table_items.append([
            span(group, col=2),
            span(
                sum([it.total if it.total else 0 for it in act.items if it.group == group]), col=6)
        ])
    put_table_items.append([span("", col=8)])
    put_table_items.append([span("合计", col=7), span(
        sum([it.total if it.total else 0 for it in act.items]), col=1)])
    popup("物资清单", put_table(put_table_items), size=PopupSize.LARGE)

# 删除物资
def modify_item_delete(act: activity):
    if len(act.items) == 0:
        toast("当前活动没有物资，请先添加物资")
        return
    # 选择要删除的物资
    items = [f"{it.group} - {it.name}" for it in act.items]
    items_md5 = [it.md5() for it in act.items]
    # 多选题
    tobe_deleted_item = checkbox("请选择要删除的物资", options=items, required=True)
    tobe_deleted_index = [items.index(it) for it in tobe_deleted_item]
    tobe_deleted_md5 = [items_md5[i] for i in tobe_deleted_index]
    # 删除物资
    act.items = [it for it in act.items if it.md5() not in tobe_deleted_md5]
    toast("删除成功！")

# 合并存档
def merge(act: activity) -> bool:
    file = file_upload("请上传要合并的活动存档", accept=".json", max_size=1024 *
                          1024 * 2, required=True, help_text="请上传要合并的活动存档，大小不得超过2M")
    try:
        act_merge = activity()
        act_merge.from_json(file["content"].decode("utf-8"))
        names = [it.name for it in act.items]
        for it in act_merge.items:
            if it.name not in names:
                act.items.append(it)
        toast("合并成功！")
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        popup("错误提示", "合并失败，请检查文件格式是否正确。\n如果您是从本系统下载的文件，请检查是否曾经修改过文件内容。")
