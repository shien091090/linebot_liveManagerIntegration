import manage
import requests
import settings
import json

class LineActionInfo:

    def __init__(self, str_requestType, requestParam):
        print("[SNTest] str_requestType = {0}, requestParam = {1}".format(str_requestType, requestParam))
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

API_ACTION_BUY = 'action_buy'
API_ACTION_MEMO_GET_DATA = 'action_memo_get_data'
API_ACTION_MEMO_ADD = 'action_memo_add'
API_ACTION_MEMO_REMOVE = 'action_memo_remove'
API_ACTION_MEMO_MODIFY = 'action_memo_modify'
API_ACTION_MEMO_CHECK = 'action_memo_get'
API_ACTION_MONTHLY_MEMO_GET_DATA = 'action_monthly_memo_get_data'
API_ACTION_MONTHLY_MEMO_ADD = 'action_monthly_memo_add'
API_ACTION_MONTHLY_MEMO_REMOVE = 'action_monthly_memo_remove'
API_ACTION_MONTHLY_MEMO_MODIFY = 'action_monthly_memo_modify'
API_ACTION_MONTHLY_MEMO_CHECK = 'action_monthly_memo_check'