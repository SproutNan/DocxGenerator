import json
import math
import base64
from PIL import Image
from io import BytesIO
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models

threshold = 2097152

secretId = ""
secretKey = ""

def handle_invoice(image: Image.Image) -> list:
    width, height = image.size
    if width >= height:
        newWidth = int(math.sqrt(threshold / 2))
        newHeight = int(newWidth * height * 1.0 / width)
    else:
        newHeight = int(math.sqrt(threshold / 2))
        newWidth = int(newHeight * width * 1.0 / height)
    resized = image.resize((newWidth, newHeight))
    buffer = BytesIO()
    resized.save(buffer, format="PNG")
    encodeImg = base64.b64encode(buffer.getvalue())
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
            elif name == "单价":
                record.update({"单价": float(value)})
            elif name == "金额":
                record.update({"总价": float(value)})
            elif name == "税额":
                # 识别到税额则单件物资结束
                record["总价"] += float(value) if value != "***" else 0
                items.append(record)
        return items
    except TencentCloudSDKException as err:
        print(err)