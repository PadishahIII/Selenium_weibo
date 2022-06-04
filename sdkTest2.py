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

    req = models.KeywordsExtractionRequest()
    params = {
        "Text":
        "哈工大的兄弟们，你们有东北的么？集合点人，打哪个洋狗子一顿不行么？现在都带着口罩，你们联系一下集体穿校服，打完往学生队里一混，都找不着人。我以 前还笑话人山东广州的学校，说洋人在东北就不敢得瑟，结果你们这中国军工的脸面被洋人打了，真让我无话可说了。求你们去把脸面打回来吧，别指望那帮官老爷 和警察了，他们都是恨不得把洋人供起来的货d"
    }
    req.from_json_string(json.dumps(params))

    resp = client.KeywordsExtraction(req)
    print(resp.to_json_string())
    json_obj = json.loads(resp.to_json_string())

except TencentCloudSDKException as err:
    print(err)