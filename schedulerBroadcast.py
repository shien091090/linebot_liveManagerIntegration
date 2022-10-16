from tkinter.tix import InputOnly
from linebot import LineBotApi
from linebot.models import FlexSendMessage
from flexMessageManager import flexMessageManager
from lineActionInfo import RequestInfo, API_ACTION_DAILY_SCHEDULER
from manage import REQUEST_TYPE_GAS
import json
import settings

LINE_MAIN_GROUP_ID = ''
TITLE_DAILY_REMIND = '�C�鴣��'
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

def SchedulerBroadcast():
    sendParam = {}
    sendParam["action"] = API_ACTION_DAILY_SCHEDULER
    reqInfo = RequestInfo(TITLE_DAILY_REMIND, REQUEST_TYPE_GAS, None)
    reqInfo.sendRequest()

    replyFlexMessage = flexMessageManager.getFlexMessage(reqInfo.title, reqInfo.statusMsg, reqInfo.resposeMsg)
    flexMessageJsonDict = json.loads(replyFlexMessage)

    pushText = FlexSendMessage(alt_text=reqInfo.title, contents=flexMessageJsonDict)
    line_bot_api.push_message(LINE_MAIN_GROUP_ID, messages = pushText)