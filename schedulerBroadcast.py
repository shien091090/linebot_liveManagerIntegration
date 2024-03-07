from linebot import LineBotApi
from linebot.models import FlexSendMessage
from flexMessageManager import getFlexMessage
from lineActionInfo import RequestInfo, API_ACTION_DAILY_SCHEDULER
from manage import REQUEST_TYPE_GAS
import json
import settings

LINE_MAIN_GROUP_ID = 'Cd6af810de75bfc7bc6817373a1fd0562'
TITLE_DAILY_REMIND = '每日提醒'


def DailyBroadCast():
    line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

    send_param = {"action": API_ACTION_DAILY_SCHEDULER}
    req_info = RequestInfo(TITLE_DAILY_REMIND, REQUEST_TYPE_GAS, send_param, 'text')
    req_info.sendRequest()

    reply_flex_message = getFlexMessage(req_info.title, req_info.statusMsg, req_info.responseMsg)
    flex_message_json_dict = json.loads(reply_flex_message)

    push_text = FlexSendMessage(alt_text=req_info.title, contents=flex_message_json_dict)
    line_bot_api.push_message(LINE_MAIN_GROUP_ID, messages=push_text)


DailyBroadCast()
