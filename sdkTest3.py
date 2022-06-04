import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.nlp.v20190408 import nlp_client, models
try:
    cred = credential.Credential("AKIDc5kHYZJ9k47uQgfNozuZx5xZv5yZuymJ",
                                 "HH2WjgNnxqTqwmCQN3SbT4ORDiwGK7ds")
    httpProfile = HttpProfile()
    httpProfile.endpoint = "nlp.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile)

    req = models.SentimentAnalysisRequest()
    params = {"Text": "哈工大的文科到底如何，蹲一个真是文科生的感受？！！", "Mode": "2class"}
    req.from_json_string(json.dumps(params))

    resp = client.SentimentAnalysis(req)
    print(resp.to_json_string())
    obj = json.loads(resp.to_json_string())
    print(obj)

except TencentCloudSDKException as err:
    print(err)