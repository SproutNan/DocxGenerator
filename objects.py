import json
import hashlib
from hashlib import md5
from base64_coder import *

# 学生
class student:
    def __init__(self, name: str="None", stuid: str="None", phone: str="None", email: str="None") -> None:
        self.name: str = name
        self.stuid: str = stuid
        self.phone: str = phone
        self.email: str = email

    def to_dict(self) -> dict:
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

    def info(self) -> str:
        return f"{self.name}({self.stuid}), {self.phone}"
    
    def md5(self) -> str:
        return md5(self.name + self.stuid + self.phone + self.email).hexdigest()

    def __repr__(self) -> str:
        return self.name
    
# 物品
class item:
    def __init__(self, name: str="None", count: int=0, price: float=0) -> None:
        self.name: str = name
        self.count: int = count
        self.price: float = price
        # 按照默认，总价应该是count*price，但是涉及淘金币等，允许手动修改
        self.total: float = None
        # 用途，奖品/其他
        self.use: str = "奖品"
        # 组别，允许添加分组，不添加分组即为默认
        self.group: str = "默认"
        # 发票
        self.invoice: str = None
        # 相关说明
        self.note: str = None
    
    def to_dict(self) -> dict:
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
    
    def md5(self) -> str:
        return md5(self.name + str(self.count) + str(self.price) + str(self.total) + self.use + self.group + self.invoice + self.note).hexdigest()

    def __repr__(self) -> str:
        return self.name

# 活动
class activity:
    def __init__(self) -> None:
        self.name: str = None
        self.director: student = None
        self.time: str = None
        self.place: str = None
        # 策划书
        self.plan: str = None
        # 活动物资
        self.item: list[item] = []
        # 新闻稿
        self.news: str = None
        # 创建的物资分组
        self.groups: list[item] = ["默认"]

    def from_para(self, name: str, director: student, time: str, place: str):
        self.name = name
        self.director = director
        self.time = time
        self.place = place
        return self

    def to_json(self) -> str:
        # 因为要转成json，所以先转成dict
        dump_dict = self.__dict__.copy()
        # 处理不平凡结构
        dump_director = dump_dict["director"].to_dict()
        dump_item = [it.to_dict() for it in dump_dict["item"]]
        # 处理新闻稿，这个新闻稿是bytes格式的，需要转换成base64
        if dump_dict["news"] is not None:
            dump_dict["news"] = to_base64(dump_dict["news"])
        # 处理策划书
        if dump_dict["plan"] is not None:
            dump_dict["plan"] = to_base64(dump_dict["plan"])
        dump_dict["director"] = dump_director
        dump_dict["item"] = dump_item
        return json.dumps(dump_dict)
    
    def from_json(self, json_str) -> None:
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
            load_dict["news"] = from_base64(load_dict["news"])
        # 处理策划书
        if load_dict["plan"] is not None:
            load_dict["plan"] = from_base64(load_dict["plan"])
        self.name = load_dict["name"]
        self.director = load_dict["director"]
        self.time = load_dict["time"]
        self.place = load_dict["place"]
        self.plan = load_dict["plan"]
        self.item = load_dict["item"]
        self.news = load_dict["news"]
        self.groups = load_dict["groups"]
        return self

    def info(self) -> str:
        return f"【负责人】{self.director.info()}，【时间】{self.time}，【策划书】{'有' if self.plan is not None else '无'}，【新闻稿】{'有' if self.news is not None else '无'}"

    def md5(self) -> str:
        part1 = self.name + self.time + self.place
        part2 = self.director.md5().hexdigest()
        part3 = self.plan + self.news
        part4 = sum([i.md5().hexdigest() for i in self.item])
        part5 = ",".join(self.groups)
        return md5(part1 + part2 + part3 + part4 + part5).hexdigest()

    def __repr__(self) -> str:
        return self.name