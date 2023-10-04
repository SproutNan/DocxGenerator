from hashlib import md5
from modules.base64_coder import *

# 学生
class student:
    """
    存储学生信息的类
    
    成员：
    - `name`: str, 姓名
    - `stuid`: str, 学号
    - `phone`: str, 手机号
    - `email`: str, 邮箱
    """
    def __init__(self, name: str="None", stuid: str="None", phone: str="None", email: str="None") -> None:
        self.name: str = name
        self.stuid: str = stuid
        self.phone: str = phone
        self.email: str = email

    def to_dict(self) -> dict:
        """
        将对象转换成dict
        """
        return {
            "name": self.name,
            "stuid": self.stuid,
            "phone": self.phone,
            "email": self.email
        }
    
    def from_dict(self, dict):
        """
        从dict中读取对象并赋值给自身
        """
        self.name = dict["name"]
        self.stuid = dict["stuid"]
        self.phone = dict["phone"]
        self.email = dict["email"]
        return self

    def info(self) -> str:
        """
        返回学生信息的str，格式为`姓名(学号)，手机号`
        """
        return f"{self.name}({self.stuid}), {self.phone}"
    
    def md5(self) -> str:
        """
        返回学生信息（四个成员均包含）的md5值
        """
        return md5(self.name + self.stuid + self.phone + self.email).hexdigest()