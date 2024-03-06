import manage
import requests
import settings
import json


class RequestInfo:

    def __init__(self, str_title, str_request_type, request_param, str_message_type):
        self.title = str_title
        self.requestType = str_request_type
        self.requestParam = request_param
        self.statusCode = 0
        self.statusMsg = ''
        self.responseMsg = ''
        self.messageType = ''

    def parseResponseJsonDct(self, dct):
        self.statusCode = dct['statusCode']
        self.statusMsg = dct['statusMsg']
        self.responseMsg = dct['responseMsg']

    def sendRequest(self):
        print(
            f'[SNTest] [Request Info] title = {self.title}, requestType = {self.requestType}, requestParam = {self.requestParam}')
        if self.requestType == manage.REQUEST_TYPE_GAS:
            req = requests.get(settings.URL_GAS_API, params=self.requestParam)
            json.loads(req.text, object_hook=self.parseResponseJsonDct)
            self.PrintResponseLog()

    def PrintResponseLog(self):
        print(
            f'[SNTest] [Response Info] statusCode = {self.statusCode}, statusMsg = {self.statusMsg}, responseMsg = {self.responseMsg}')


API_ACTION_MEMO_ADD = 'action_memo_add'
API_ACTION_MEMO_REMOVE = 'action_memo_remove'
API_ACTION_MEMO_MODIFY = 'action_memo_modify'
API_ACTION_MEMO_GET = 'action_memo_get'
API_ACTION_SCHEDULE_ADD = 'action_schedule_add'
API_ACTION_SCHEDULE_REMOVE = 'action_schedule_remove'
API_ACTION_SCHEDULE_MODIFY = 'action_schedule_modify'
API_ACTION_SCHEDULE_GET = 'action_schedule_get'
API_ACTION_DAILY_SCHEDULER = 'action_daily_scheduler'
API_ACTION_BUY = 'action_buy'
API_ACTION_BUY_WITH_BUDGET_TYPE = 'action_buy_with_budget_type'
API_ACTION_RECORD_BABY_DIAPER_CHANGING_TIME = 'action_record_baby_diaper_changing_time'
API_ACTION_RECORD_BABY_EAT_TIME = 'action_record_baby_eat_time'
API_ACTION_GET_CHART = 'action_get_chart'
