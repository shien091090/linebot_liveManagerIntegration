import imp
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, FlexSendMessage
from TextParser import TextParser
from dateManager import dateManager
from flexMessageManager import flexMessageManager
from lineActionInfo import LineActionInfo

from flask import Flask, request, abort
import KeyWordSetting
import lineActionInfo
import settings
import json

REQUEST_TYPE_GAS = 'request_type_gas'

STATUS_CODE_SUCCESS = 200
STATUS_CODE_EMPTY_INPUT = 300
STATUS_CODE_INVALID = 301

app = Flask(__name__)

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():

    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def receiveMessage(event):

    printReceiverLog(event)
    receiveTxt = event.message.text

    #新增待辦事項
    if TextParser.checkHeaderByKeyWord(receiveTxt, KeyWordSetting.KEY_MEMO_ADD):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_MEMO_ADD,
            REQUEST_TYPE_GAS,
            {'action':lineActionInfo.API_ACTION_MEMO_ADD,'content':TextParser.getSubStringByKeyWord(receiveTxt, KeyWordSetting.KEY_MEMO_ADD)})
    
    #刪除待辦事項
    elif TextParser.checkHeaderByKeyWord(receiveTxt, KeyWordSetting.KEY_MEMO_REMOVE):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_MEMO_REMOVE,
            REQUEST_TYPE_GAS,
            {'action':lineActionInfo.API_ACTION_MEMO_REMOVE,'content':TextParser.getNumberByKeyWordAndNumber(receiveTxt, KeyWordSetting.KEY_MEMO_REMOVE)})

    #修改待辦事項
    elif TextParser.checkHeaderByKeyWord(receiveTxt, KeyWordSetting.KEY_MEMO_MODIFY):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_MEMO_MODIFY,
            REQUEST_TYPE_GAS,
            {'action':lineActionInfo.API_ACTION_MEMO_MODIFY,'content':TextParser.getNumberByKeyWordAndNumber(receiveTxt, KeyWordSetting.KEY_MEMO_MODIFY)})

    #確認待辦事項
    elif TextParser.checkHeaderByKeyWord(receiveTxt, KeyWordSetting.KEY_MEMO_CHECK):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_MEMO_CHECK,
            REQUEST_TYPE_GAS,
            {'action':lineActionInfo.API_ACTION_MEMO_CHECK,'content':''})

    elif TextParser.checkHeaderByKeyWord(receiveTxt, KeyWordSetting.KEY_MONTHLY_MEMO_ADD):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_MONTHLY_MEMO_ADD,
            REQUEST_TYPE_GAS,
            lineActionInfo.API_ACTION_MONTHLY_MEMO_ADD)

    elif TextParser.checkHeaderByKeyWord(receiveTxt, KeyWordSetting.KEY_MONTHLY_MEMO_REMOVE):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_MONTHLY_MEMO_REMOVE,
            REQUEST_TYPE_GAS,
            lineActionInfo.API_ACTION_MONTHLY_MEMO_REMOVE)

    elif TextParser.checkHeaderByKeyWord(receiveTxt, KeyWordSetting.KEY_MONTHLY_MEMO_MODIFY):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_MONTHLY_MEMO_MODIFY,
            REQUEST_TYPE_GAS,
            lineActionInfo.API_ACTION_MONTHLY_MEMO_MODIFY)

    elif TextParser.checkHeaderByKeyWord(receiveTxt, KeyWordSetting.KEY_MONTHLY_MEMO_CHECK):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_MONTHLY_MEMO_CHECK,
            REQUEST_TYPE_GAS,
            lineActionInfo.API_ACTION_MONTHLY_MEMO_CHECK)

    elif TextParser.checkHeaderByKeyWord(receiveTxt, KeyWordSetting.KEY_BUY):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_BUY,
            REQUEST_TYPE_GAS,
            lineActionInfo.API_ACTION_BUY)

    actionInfo.sendRequest()

    replyFlexMessage = flexMessageManager.getFlexMessage(actionInfo.title, actionInfo.statusMsg, actionInfo.resposeMsg)
    print(f"[SNTest] replyFlexMessage = {replyFlexMessage}")
    flexMessageJsonDict = json.loads(replyFlexMessage)

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text=actionInfo.title, contents=flexMessageJsonDict))

    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=replyTxt)
    #)

def printReceiverLog(event):
    eventType = str(event.source.type)
    if eventType == 'user':
        eventTypeLog = "[userId : {0}]".format(str(event.source.user_id))
    elif eventType == 'group':
        eventTypeLog = "[groupId : {0}]".format(str(event.source.group_id))
    print("[SNTest] [source.type = {0}] {1}".format(eventType, eventTypeLog))

if __name__ == "__main__":
    app.run()