from errbot import BotPlugin, webhook
import requests
import json

TEKTON_URL = "http://el-tbcd:8080"


class Gitlab(BotPlugin):
    @webhook("/ci/ping")
    def trigger(self, request):
        return "pong"

    @webhook("/ci/<action>/", raw=True)
    def trigger(self, request, action):
        body = json.loads(request.data)

        if action == "trigger":
            self.trim_checkout_sha(body)
            self.lower_repository_name(body)
            resp = self.post_tekton(body)

            return {"code": 0, "msg": "success", "data": resp}
        return {"code": -1, "msg": "error action"}

    def lower_repository_name(self, body):
        body['project']['name'] = body['project']['name'].lower()

    def trim_checkout_sha(self, body):
        body['checkout_sha'] = body['checkout_sha'][0:7]

    def post_tekton(self, body):
        headers = {
            "Content-Type": "application/json",
            "X-Gitlab-Event": "Push Hook",
        }
        r = requests.post(TEKTON_URL, headers=headers, data=json.dumps(body))
        return r.text
