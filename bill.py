import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models
import os
from PIL import Image
import math
import base64

threshold = 2097152

secretId = "AKIDpZHuMeiVeileAHF59EOF6Vxc8WigQwFL"
secretKey = "dxDmEVZROEAHRVPElGalnloV2Ngs21qT"
fileName = "./bill.png"
outputFileName = "./out_bill.png"
filesize = os.path.getsize(fileName)
record = {}

with Image.open(fileName) as im:
    width, height = im.size
    if width >= height:
        newWidth = int(math.sqrt(threshold / 2))
        newHeight = int(newWidth * height * 1.0 / width)
    else:
        newHeight = int(math.sqrt(threshold / 2))
        newWidth = int(newHeight * width * 1.0 / height)
    resized = im.resize((newWidth, newHeight))
    resized.save(outputFileName)

# img -> base64
with open(outputFileName, "rb") as f:
    data = f.read()
    encodeImg = base64.b64encode(data)
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
        for info in infos["VatInvoiceInfos"]:
            count = 1
            name = info['Name']
            value = info['Value']
            if str(name) in record:
                while str(name) in record:
                    count = count + 1
                    name = info['Name'] + str(count)
            record.update({name: value})
            print(name, ": ", value, sep='')
    except TencentCloudSDKException as err:
        print(err)