from linebot import LineBotApi
from linebot.models import FlexSendMessage
from flexMessageManager import getMemoFlexMessage
from dateColorHelper import build_colored_memo_items
from lineActionInfo import RequestInfo, API_ACTION_DAILY_SCHEDULER
from manage import REQUEST_TYPE_GAS
from datetime import date as date_today
import json
import settings

LINE_MAIN_GROUP_ID = 'Cd6af810de75bfc7bc6817373a1fd0562'
TITLE_DAILY_REMIND = '每日提醒'


def DailyBroadCast():
    line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

    send_param = {"action": API_ACTION_DAILY_SCHEDULER}
    req_info = RequestInfo(TITLE_DAILY_REMIND, REQUEST_TYPE_GAS, send_param)
    req_info.sendRequest()

    colored_items = build_colored_memo_items(req_info.responseMsg, date_today.today())
    reply_flex_message = getMemoFlexMessage(req_info.title, req_info.statusMsg, colored_items)
    flex_message_json_dict = json.loads(reply_flex_message)

    push_text = FlexSendMessage(alt_text=req_info.title, contents=flex_message_json_dict)
    line_bot_api.push_message(LINE_MAIN_GROUP_ID, messages=push_text)


DailyBroadCast()
