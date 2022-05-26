import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.nlp.v20190408 import nlp_client, models
try:
    # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey,此处还需注意密钥对的保密
    cred = credential.Credential("AKIDc5kHYZJ9k47uQgfNozuZx5xZv5yZuymJ",
                                 "HH2WjgNnxqTqwmCQN3SbT4ORDiwGK7ds")

    httpProfile = HttpProfile()
    httpProfile.endpoint = "nlp.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile)

    req = models.LexicalAnalysisRequest()
    params = {"Text": "哈尔滨工业大学哈尔滨工业大学超话蹲一位电气的研究生学长或学姐"}
    req.from_json_string(json.dumps(params))

    resp = client.LexicalAnalysis(req)
    #print(resp.to_json_string())
    json_obj = json.loads(resp.to_json_string())
    print(json_obj)
except TencentCloudSDKException as err:
    print(err)