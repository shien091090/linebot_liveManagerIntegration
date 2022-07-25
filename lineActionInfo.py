import manage
import requests
import settings
import json

class RequestInfo:

    def __init__(self, str_title, str_requestType, requestParam):
        print("[SNTest] [LineActionInfo Init] str_title = {0}, str_requestType = {1}, requestParam = {2}".format(str_title, str_requestType, requestParam))
        self.title = str_title
        self.requestType = str_requestType
        self.requestParam = requestParam
        self.statusCode = 0
        self.statusMsg = ''
        self.resposeMsg = ''

    def parseResponseJsonDct(self, dct):
        self.statusCode = dct['statusCode']
        self.statusMsg = dct['statusMsg']
        self.resposeMsg = dct['responseMsg']

    def sendRequest(self):
        if self.requestType == manage.REQUEST_TYPE_GAS:
            req = requests.get(settings.URL_GAS_API, params=self.requestParam)
            print("[SNTest] req.text = {0}".format(req.text))
            jsonDct = json.loads(req.text, object_hook=self.parseResponseJsonDct)

    def PrintLog(self):
        print("[SNTest] [LineActionInfo PrintLog] title = {0}, requestType = {1}, requestParam = {2}, statusCode = {3}, statusMsg = {4}, resposeMsg = {5}"
        .format(self.title, self.requestType, self.requestParam, self.statusCode, self.statusMsg, self.resposeMsg))

API_ACTION_MEMO_ADD = 'action_memo_add'
API_ACTION_MEMO_REMOVE = 'action_memo_remove'
API_ACTION_MEMO_MODIFY = 'action_memo_modify'
API_ACTION_MEMO_GET = 'action_memo_get'
API_ACTION_SCHEDULE_ADD = 'action_schedule_add'
API_ACTION_SCHEDULE_REMOVE = 'action_schedule_remove'
API_ACTION_SCHEDULE_MODIFY = 'action_schedule_modify'
API_ACTION_SCHEDULE_GET = 'action_schedule_get'
API_ACTION_BUY = 'action_buy'