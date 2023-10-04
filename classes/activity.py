import json
from hashlib import md5
from modules.base64_coder import *
from classes.student import student
from classes.item import item

# 活动
class activity:
    """
    存储活动信息的类

    成员：
    - `name`: str, 活动名称
    - `director`: student, 活动负责人
    - `time`: str, 活动时间
    - `place`: str, 活动地点
    - `plan`: str, 活动策划书（以str形式存储的base64）
    - `items`: list[item], 活动物资
    - `news`: str, 活动新闻稿（以str形式存储的base64）
    - `groups`: list[str], 活动物资分组
    """
    def __init__(self) -> None:
        self.name: str = None
        self.director: student = None
        self.time: str = None
        self.place: str = None
        # 策划书
        self.plan: str = None
        # 活动物资
        self.items: list[item] = []
        # 新闻稿
        self.news: str = None
        # 创建的物资分组
        self.groups: list[str] = ["默认"]

    def from_para(self, name: str, director: student, time: str, place: str):
        """
        从参数中读取对象并赋值给自身，只包含 名称、负责人、时间、地点 四个成员
        """
        self.name = name
        self.director = director
        self.time = time
        self.place = place
        return self

    def to_json(self) -> str:
        """
        将活动对象转换成json
        """
        # 因为要转成json，所以先转成dict
        dump_dict = self.__dict__.copy()
        # 处理不平凡结构
        dump_director = dump_dict["director"].to_dict()
        dump_item = [it.to_dict() for it in dump_dict["items"]]
        # 处理新闻稿，这个新闻稿是bytes格式的，需要转换成base64
        if dump_dict["news"] is not None:
            dump_dict["news"] = to_base64(dump_dict["news"])
        # 处理策划书
        if dump_dict["plan"] is not None:
            dump_dict["plan"] = to_base64(dump_dict["plan"])
        dump_dict["director"] = dump_director
        dump_dict["items"] = dump_item
        return json.dumps(dump_dict)

    def from_json(self, json_str) -> None:
        """
        从json中读取对象并赋值给自身
        """
        load_dict: dict = json.loads(json_str)
        load_student = student().from_dict(load_dict["director"])
        load_dict["director"] = load_student
        load_items = []
        for it in load_dict["items"]:
            load_item = item().from_dict(it)
            load_items.append(load_item)
        load_dict["items"] = load_items
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
        self.items = load_dict["items"]
        self.news = load_dict["news"]
        self.groups = load_dict["groups"]
        return self

    def info(self) -> str:
        """
        返回活动信息的str，格式为`【负责人】姓名(学号)，手机号，【时间】yyyy-mm-dd，【策划书】有/无，【新闻稿】有/无`
        """
        return f"【负责人】{self.director.info()}，【时间】{self.time}，【策划书】{'有' if self.plan is not None else '无'}，【新闻稿】{'有' if self.news is not None else '无'}"

    def md5(self) -> str:
        """
        返回活动信息（所有成员均包含）的md5值
        """
        part1 = self.name + self.time + self.place
        part2 = self.director.md5().hexdigest()
        part3 = self.plan + self.news
        part4 = sum([i.md5().hexdigest() for i in self.items])
        part5 = ",".join(self.groups)
        return md5(part1 + part2 + part3 + part4 + part5).hexdigest()
    
    def lmd5(self) -> str:
        """
        返回活动信息（仅包含基本信息）的md5值
        """
        part1 = self.name + self.time + self.place
        part2 = self.director.md5().hexdigest()
        part3 = ("有" if self.plan is not None else "无") + ("有" if self.news is not None else "无")
        part4 = ",".join(self.groups)
        return md5(part1 + part2 + part3 + part4).hexdigest()