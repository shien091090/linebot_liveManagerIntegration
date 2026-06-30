from linebot import LineBotApi
from linebot.models import FlexSendMessage
from flexMessageManager import getMemoFlexMessage, getFlexMessage, getUrlButtonFlexMessage
from dateColorHelper import build_colored_memo_items, taiwan_today
from lineActionInfo import RequestInfo, API_ACTION_DAILY_SCHEDULER, API_ACTION_PURCHASE_LIST_GET
from manage import REQUEST_TYPE_GAS
import json
import requests
import settings

LINE_MAIN_GROUP_ID = 'Cd6af810de75bfc7bc6817373a1fd0562'
TITLE_DAILY_REMIND = '每日提醒'
DASHBOARD_URL = 'https://linebot-livemanagerintegration.herokuapp.com/dashboard'


def DailyBroadCast():
    line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

    send_param = {"action": API_ACTION_DAILY_SCHEDULER}
    req_info = RequestInfo(TITLE_DAILY_REMIND, REQUEST_TYPE_GAS, send_param)
    req_info.sendRequest()

    colored_items = build_colored_memo_items(req_info.responseMsg, taiwan_today())
    reply_flex_message = getMemoFlexMessage(req_info.title, req_info.statusMsg, colored_items)
    push_daily = FlexSendMessage(alt_text=req_info.title, contents=json.loads(reply_flex_message))

    dashboard_flex = getUrlButtonFlexMessage('家庭總覽', '點擊查看家庭狀況', DASHBOARD_URL)
    push_dashboard = FlexSendMessage(alt_text='家庭總覽', contents=json.loads(dashboard_flex))

    messages = [push_daily, push_dashboard]

    try:
        r = requests.get(settings.URL_GAS_API, params={'action': API_ACTION_PURCHASE_LIST_GET}, timeout=10)
        purchase_resp = json.loads(r.text)
        if purchase_resp.get('statusCode') == 200:
            purchase_items = json.loads(purchase_resp.get('responseMsg', '[]'))
            if purchase_items:
                purchase_text = '\n'.join(f'{i+1}. {item["name"]}' for i, item in enumerate(purchase_items))
                purchase_flex = getFlexMessage('待購買清單', f'共 {len(purchase_items)} 筆', purchase_text)
                messages.append(FlexSendMessage(alt_text='待購買清單', contents=json.loads(purchase_flex)))
    except Exception:
        pass

    line_bot_api.push_message(LINE_MAIN_GROUP_ID, messages=messages)


DailyBroadCast()
