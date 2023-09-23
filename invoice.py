import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models
from PIL import Image
import math
import base64

threshold = 2097152

secretId = "AKIDpZHuMeiVeileAHF59EOF6Vxc8WigQwFL"
secretKey = "dxDmEVZROEAHRVPElGalnloV2Ngs21qT"
fileName = "./bill.png"
outputFileName = "./out_bill.png"

def handle_invoice(image: Image.Image) -> list:
    width, height = image.size
    if width >= height:
        newWidth = int(math.sqrt(threshold / 2))
        newHeight = int(newWidth * height * 1.0 / width)
    else:
        newHeight = int(math.sqrt(threshold / 2))
        newWidth = int(newHeight * width * 1.0 / height)
    resized = image.resize((newWidth, newHeight))
    resized.save(outputFileName)
    encodeImg = base64.b64encode(open(outputFileName, "rb").read())
    baseImg = str(encodeImg, 'utf-8')

    try:
        cred = credential.Credential(secretId, secretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "ocr.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = ocr_client.OcrClient(cred, "ap-beijing", clientProfile)

        req = models.VatInvoiceOCRRequest()
        params = '{\"ImageBase64\":\"%s\"} ' % baseImg
        req.from_json_string(params)

        response = client.VatInvoiceOCR(req)
        infos = json.loads(response.to_json_string())

        items = []
        for info in infos["VatInvoiceInfos"]:
            name, value = info['Name'], info['Value']
            if name == "货物或应税劳务、服务名称":
                record = {}
                record.update({"名称": value})
            elif name == "数量":
                record.update({"数量": int(value)})
            elif name == "金额":
                record.update({"单价": float(value)})
            elif name == "税额":
                # 识别到税额则单件物资结束
                record["单价"] += float(value) if value != "***" else 0
                record.update({"总价": record["单价"] * record["数量"]})
                items.append(record)
        return items
    except TencentCloudSDKException as err:
        print(err)

# usage
# image = Image.open(fileName)
# print(handle_invoice(image))

'''
销售方识别号: 91330106084551589L
销售方名称: 杭州木垛文化创意有限公司
购买方识别号: 12100000485001086E
购买方名称: 中国科学技术大学
发票代码: 033002200711
二维码: 1
发票名称: 浙江增值税电子普通发票
发票号码: No03211653
开票日期: 2023年04月20日
机器编号: 661022830599
校验码: 55330570684005455484
密码区1: >4273<7**0<2752-+5-3<03->6-
密码区2: 42744+83>4>3-04052*+5<6-930
购买方地址、电话: 安徽省合肥市金寨路96号
密码区3: --37802<6-<92><>6/2-<7+7+56
购买方开户行及账号: 中国银行合肥蜀山支行营业部184203468850
密码区4: -/6>/0544+*6/4>7-30>8464*>5
货物或应税劳务、服务名称: *印刷品*深度学习 √
单位: 件
数量: 1                             √
单价: 85.01                         √
金额: 85.01
税率: 免税                          金额 + 税额
税额: ***
货物或应税劳务、服务名称2: *印刷品*计算机体系结构.量化研究方法(第6版)
单位2: 件
数量2: 1
单价2: 102.08
金额2: 102.08
税额2: ***
合计金额: ¥187.99
合计税额: ***
价税合计(大写): 壹佰捌拾柒圆玖角玖分
小写金额: ¥187.99
备注: W00363376918
销售方地址、电话: 浙江省杭州市西湖区西溪街道文二路38号一楼102室0571-28052232
销售方开户行及账号: 中信银行杭州天水支行7331110182600132437
收款人: 博库
复核: 沈志峰
开票人: 孙玉荣
是否有公司印章: 1
是否有纸质全电票标记: 0
省: 浙江省
发票类型: 增值税电子普通发票
发票消费类型: 服务
是否代开:
打印发票代码:
打印发票号码:
规格型号:
联次:
成品油标志:
市:
服务类型:
通行费标志:
车船税:
车牌号:
类型:
通行日期起:
通行日期止:
发票联名:
全电号码:
'''