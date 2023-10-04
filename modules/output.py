import os
import io
import random
from classes.activity import activity
from classes.placeholder import placeholder
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from time import time
from modules.base64_coder import *
from docx import Document
from docx.shared import Pt
from docx.oxml import parse_xml

def _replace(placeholder: str, paragraph, text: str):
    if placeholder in paragraph.text:
        paragraph.text = paragraph.text.replace(placeholder, text)

# 将活动输出为docx
def to_docx(act: activity):
    if len(act.items) == 0:
        toast("活动物资为空，无法生成申请表")
        return

    # 计算act预算，按照用途
    budget = {}
    for item in act.items:
        if item.use not in budget.keys():
            budget[item.use] = 0.0
        budget[item.use] += item.total
    # 按照预算排序
    budget = sorted(budget.items(), key=lambda item: item[1], reverse=True)
    # 如果预算超过了6个，只取前5个，剩下的归类为其他
    if len(budget) > 6:
        other_sum = sum([item[1] for item in budget[6:]])
        budget = budget[:6]
        budget.append(("其他", other_sum))
    # 生成保存文件
    time_stamp = int(time())
    random_num = random.randint(1000,9999)
    template_name = "./templates/template_applicant_form.docx"
    form_name = f"./temp_form_{time_stamp}_{random_num}.docx"
    # fill the template file
    doc = Document(template_name)
    for table in doc.tables:
        for row in table.rows:
            for cell in set(row.cells):
                for paragraph in cell.paragraphs:
                    _replace(placeholder.act_name, paragraph, act.name)
                    _replace(placeholder.act_time, paragraph, act.time)
                    _replace(placeholder.act_place, paragraph, act.place)
                    _replace(placeholder.act_plan, paragraph, "见后附页" if act.plan else "暂无")
                    _replace(placeholder.act_date, paragraph, act.time.replace("-", "年", 1).replace("-", "月", 1))
                    _replace(placeholder.dir_name, paragraph, act.director.name)
                    _replace(placeholder.dir_phone, paragraph, act.director.phone)
                    _replace(placeholder.dir_mail, paragraph, act.director.email)
                    _replace(placeholder.itm_cnt, paragraph, str(len(budget)))
                    _replace(placeholder.itm_sum, paragraph, str(sum([item[1] for item in budget])))
                    for i in range(1, 7):
                        if i <= len(budget):
                            _replace(f"{placeholder.itm_grp}{i}", paragraph, budget[i-1][0])
                            _replace(f"{placeholder.itm_bgt}{i}", paragraph, str(budget[i-1][1]))
                        else:
                            _replace(f"{placeholder.itm_grp}{i}", paragraph, "")
                            _replace(f"{placeholder.itm_bgt}{i}", paragraph, "")

    doc.add_page_break()
    title = doc.add_paragraph()
    title.alignment = 1  # 设置为居中对齐（1表示居中）
    run = title.add_run("活动物资清单")
    run.font.size = Pt(18)

    table = doc.add_table(rows=1, cols=8)
    # set the table header
    headers = ['组别', '名称', '数量', '单价', '总价', '用途', '发票', '备注']
    for idx, header in enumerate(headers):
        table.cell(0, idx).text = header

    for it in act.items:
        cells = table.add_row().cells
        values = [it.group, it.name, it.count, it.price, it.total, it.use,
            "纸质发票" if it.invoice is None else "发票已上传", it.note]
        for idx, value in enumerate(values):
            cells[idx].text = str(value)

    # 组内合计
    rowIndex = len(table.rows)
    table.add_row()
    table.cell(rowIndex, 0).merge(table.cell(rowIndex, len(headers)-1))
    table.cell(rowIndex, 0).text = "组内合计"

    # 各组总计
    for group in act.groups:
        rowIndex = len(table.rows)
        table.add_row()
        table.cell(rowIndex, 0).merge(table.cell(rowIndex, 1))
        table.cell(rowIndex, 2).merge(table.cell(rowIndex, len(headers)-1))
        table.cell(rowIndex, 0).text = group
        table.cell(rowIndex, 2).text = str(sum(it.total if it.total else 0 for it in act.items if it.group == group))

    # 合计
    rowIndex = len(table.rows)
    table.add_row()
    table.cell(rowIndex, 0).merge(table.cell(rowIndex, 6))
    table.cell(rowIndex, 0).text = "合计"
    table.cell(rowIndex, 7).text = str(sum(it.total if it.total else 0 for it in act.items))

    # 增加边框
    for row in table.rows:
        for cell in row.cells:
            # 获取单元格的tcPr对象
            tcPr = cell._tc.get_or_add_tcPr()

            # 创建边框元素
            borders = parse_xml(r'<w:tcBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                                r'<w:top w:val="single" w:color="000000" w:sz="8"/>'
                                r'<w:bottom w:val="single" w:color="000000" w:sz="8"/>'
                                r'<w:left w:val="single" w:color="000000" w:sz="8"/>'
                                r'<w:right w:val="single" w:color="000000" w:sz="8"/>'
                                r'</w:tcBorders>')

            # 将边框样式应用到单元格
            tcPr.append(borders)

    # 组别合并
    index = [-1]
    for i in range(len(act.items) - 1):
        if act.items[i].group != act.items[i + 1].group:
            index.append(i)
    index.append(len(act.items) - 1)
    for i in range(len(index) - 1):
        start, end = index[i] + 1, index[i + 1]
        table.cell(start + 1, 0).merge(table.cell(end + 1, 0))
        table.cell(start + 1, 0).text = act.items[start].group

    # 策划书
    doc.add_page_break()
    plan = Document(io.BytesIO(act.plan))
    plan.add_page_break()
    for element in plan.element.body:
        doc.element.body.append(element)

    # 新闻稿
    news = Document(io.BytesIO(act.news))
    for element in news.element.body:
        doc.element.body.append(element)


    # save the file
    doc.save(form_name)
    # provide download
    put_file(f"{act.name}_{int(time())}.docx", content=open(form_name, "rb").read())
    # remove the file
    os.remove(form_name)