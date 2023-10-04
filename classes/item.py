from hashlib import md5
from modules.base64_coder import *

# 物品
class item:
    """
    存储物品信息的类

    成员：
    - `name`: str, 物品名称
    - `count`: int, 物品数量
    - `price`: float, 物品单价
    - `total`: float, 物品总价
    - `use`: str, 物品用途
    - `group`: str, 物品分组
    - `invoice`: str, 物品发票（以str形式存储的base64）
    - `screenhot`: str, 物品购买截图（以str形式存储的base64）
    - `note`: str, 物品备注
    """
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
        # 购买截图
        self.screenshot: str = None
        # 相关说明
        self.note: str = None
    
    def to_dict(self) -> dict:
        """
        将对象转换成dict
        """
        return {
            "name": self.name,
            "count": self.count,
            "price": self.price,
            "total": self.total,
            "use": self.use,
            "group": self.group,
            "invoice": self.invoice,
            "screenshot": self.screenshot,
            "note": self.note
        }

    def from_dict(self, dict):
        """
        从dict中读取对象并赋值给自身
        """
        self.name = dict["name"]
        self.count = dict["count"]
        self.price = dict["price"]
        self.total = dict["total"]
        self.use = dict["use"]
        self.group = dict["group"]
        self.invoice = dict["invoice"]
        self.screenshot = dict["screenshot"]
        self.note = dict["note"]
        return self
    
    def md5(self) -> str:
        """
        返回物品信息（八个成员均包含）的md5值
        """
        return md5(self.name + str(self.count) + str(self.price) + str(self.total) + self.use + self.group + self.invoice + self.note + self.screenshot).hexdigest()