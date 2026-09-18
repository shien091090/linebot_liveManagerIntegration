import requests
import settings
import json

STATUS_CODE_BACKEND_ERROR = 500


class RequestInfo:

    def __init__(self, str_title, str_request_type, request_param):
        self.title = str_title
        self.requestType = str_request_type
        self.requestParam = request_param

        self.statusCode = 0
        self.statusMsg = ''
        self.responseMsg = ''
        self.messageType = 'text'

    def parseResponseJsonDct(self, dct):
        self.statusCode = dct['statusCode']
        self.statusMsg = dct['statusMsg']
        self.responseMsg = dct['responseMsg']
        self.messageType = dct['messageType']

    def sendRequest(self):
        print(
            f'[SNTest] [Request Info] title = {self.title}, requestType = {self.requestType}, requestParam = {self.requestParam}')
        if self.requestType == 'request_type_gas':
            req = None
            try:
                req = requests.get(settings.URL_GAS_API, params=self.requestParam)
                json.loads(req.text, object_hook=self.parseResponseJsonDct)
            except Exception as err:
                # GAS 拋例外時會回 HTML 錯誤頁而非 JSON, 不能讓它炸穿整個 webhook,
                # 否則 LINE 完全收不到回覆(即使資料已經寫進試算表)
                self.setBackendError(err, req)
            self.PrintResponseLog()

    def setBackendError(self, err, req=None):
        raw_body = ''
        if req is not None:
            raw_body = (req.text or '')[:200]

        print(f'[SNTest] [Backend Error] {type(err).__name__}: {err}')
        print(f'[SNTest] [Backend Error] raw body = {raw_body!r}')

        self.statusCode = STATUS_CODE_BACKEND_ERROR
        self.statusMsg = '【後端異常】\n指令可能已經生效, 請到試算表確認'
        self.responseMsg = f'{type(err).__name__}: {err}'
        self.messageType = 'text'

    def PrintResponseLog(self):
        print(
            f'[SNTest] [Response Info] statusCode = {self.statusCode}, statusMsg = {self.statusMsg}, responseMsg = {self.responseMsg}')


API_ACTION_MEMO_ADD = 'action_memo_add'
API_ACTION_MEMO_REMOVE = 'action_memo_remove'
API_ACTION_MEMO_REMOVE_MULTIPLE = 'action_memo_remove_multiple'
API_ACTION_MEMO_MODIFY = 'action_memo_modify'
API_ACTION_MEMO_EXTEND = 'action_memo_extend'
API_ACTION_MEMO_GET = 'action_memo_get'
API_ACTION_SCHEDULE_ADD = 'action_schedule_add'
API_ACTION_SCHEDULE_REMOVE = 'action_schedule_remove'
API_ACTION_SCHEDULE_MODIFY = 'action_schedule_modify'
API_ACTION_SCHEDULE_GET = 'action_schedule_get'
API_ACTION_DAILY_SCHEDULER = 'action_daily_scheduler'
API_ACTION_BUY = 'action_buy'
API_ACTION_BUY_WITH_BUDGET_TYPE = 'action_buy_with_budget_type'
API_ACTION_GET_CHART = 'action_get_chart'
API_ACTION_PURCHASE_LIST_ADD = 'action_purchase_list_add'
API_ACTION_PURCHASE_LIST_GET = 'action_purchase_list_get'
API_ACTION_PURCHASE_LIST_DELETE = 'action_purchase_list_delete'
API_ACTION_PURCHASE_LIST_MARK_BOUGHT = 'action_purchase_list_mark_bought'
