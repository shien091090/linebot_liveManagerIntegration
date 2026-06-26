from linebot import LineBotApi
from linebot.models import FlexSendMessage
from flexMessageManager import getMemoFlexMessage, getUrlButtonFlexMessage
from dateColorHelper import build_colored_memo_items, taiwan_today
from lineActionInfo import RequestInfo, API_ACTION_DAILY_SCHEDULER
from manage import REQUEST_TYPE_GAS
import json
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

    line_bot_api.push_message(LINE_MAIN_GROUP_ID, messages=[push_daily, push_dashboard])


DailyBroadCast()
