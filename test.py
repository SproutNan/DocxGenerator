from objects import *

test_activity = activity()
test_activity.init(
    name="测试活动",
    director=student(
        name="测试负责人",
        stuid="PB20000000",
        phone="12345678901",
        email="sprout@mail.ustc.edu.cn"
    ),
    time="2020-01-01",
    place="中国科学技术大学"
)

test_item1 = item(
    name="测试物品1",
    count=1,
    price=1.0
)

test_item2 = item(
    name="测试物品2",
    count=2,
    price=2.0
)

test_activity.item.append(test_item1)
test_activity.item.append(test_item2)

print(test_activity.__dict__)

