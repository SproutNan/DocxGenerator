import json
from base64_coder import *

# 学生
class student:
    def __init__(self, name: str=None, stuid: str=None, phone: str=None, email: str=None):
        self.name = name
        self.stuid = stuid
        self.phone = phone
        self.email = email

    def to_dict(self):
        return {
            "name": self.name,
            "stuid": self.stuid,
            "phone": self.phone,
            "email": self.email
        }
    
    def from_dict(self, dict):
        self.name = dict["name"]
        self.stuid = dict["stuid"]
        self.phone = dict["phone"]
        self.email = dict["email"]
        return self

    def info(self):
        return f"{self.name}({self.stuid}), {self.phone}"

    def __repr__(self):
        return self.name
    
# 物品
class item:
    def __init__(self, name: str=None, count: int=None, price: float=None):
        self.name = name
        self.count = count
        self.price = price
        # 按照默认，总价应该是count*price，但是涉及淘金币等，允许手动修改
        self.total = None
        # 用途，奖品/其他
        self.use = "奖品"
        # 组别，允许添加分组，不添加分组即为默认
        self.group = "默认"
        # 发票
        self.invoice = None
        # 相关说明
        self.note = None
    
    def to_dict(self):
        return {
            "name": self.name,
            "count": self.count,
            "price": self.price,
            "total": self.total,
            "use": self.use,
            "group": self.group,
            "invoice": self.invoice,
            "note": self.note
        }

    def from_dict(self, dict):
        self.name = dict["name"]
        self.count = dict["count"]
        self.price = dict["price"]
        self.total = dict["total"]
        self.use = dict["use"]
        self.group = dict["group"]
        self.invoice = dict["invoice"]
        self.note = dict["note"]
        return self
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

# 活动
class activity:
    def __init__(self):
        self.name = None
        self.director = None
        self.time = None
        self.place = None
        # 策划书
        self.plan = None
        # 活动物资
        self.item = []
        # 新闻稿
        self.news = None
        # 创建的物资分组
        self.groups = ["默认"]

    def init(self, name: str, director: student, time: str, place: str):
        self.name = name
        self.director = director
        self.time = time
        self.place = place

    def to_json(self):
        dump_dict = self.__dict__.copy()
        # 处理不平凡结构
        dump_director = dump_dict["director"].to_dict()
        dump_item = [it.to_dict() for it in dump_dict["item"]]
        # 处理新闻稿，这个新闻稿是bytes格式的，需要转换成base64
        if dump_dict["news"] is not None:
            dump_dict["news"]["content"] = to_base64(dump_dict["news"]["content"])
        # 处理策划书
        if dump_dict["plan"] is not None:
            dump_dict["plan"]["content"] = to_base64(dump_dict["plan"]["content"])
        dump_dict["director"] = dump_director
        dump_dict["item"] = dump_item
        return json.dumps(dump_dict)
    
    def from_json(self, json_str):
        load_dict = json.loads(json_str)
        load_student = student().from_dict(load_dict["director"])
        load_dict["director"] = load_student
        load_items = []
        for it in load_dict["item"]:
            load_item = item().from_dict(it)
            load_items.append(load_item)
        load_dict["item"] = load_items
        # 处理新闻稿，这个新闻稿是base64格式的，需要转换成bytes
        if load_dict["news"] is not None:
            load_dict["news"]["content"] = from_base64(load_dict["news"]["content"])
        # 处理策划书
        if load_dict["plan"] is not None:
            load_dict["plan"]["content"] = from_base64(load_dict["plan"]["content"])
        self.name = load_dict["name"]
        self.director = load_dict["director"]
        self.time = load_dict["time"]
        self.place = load_dict["place"]
        self.plan = load_dict["plan"]
        self.item = load_dict["item"]
        self.news = load_dict["news"]
        self.groups = load_dict["groups"]
        return self

    def info(self):
        return f"【负责人】{self.director.info()}，【时间】{self.time}，【策划书】{'有' if self.plan is not None else '无'}，【新闻稿】{'有' if self.news is not None else '无'}"

    def __repr__(self):
        return self.name