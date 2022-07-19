import imp
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, FlexSendMessage
from TextParserManager import TextParser
from dateManager import dateManager
from flexMessageManager import flexMessageManager
from lineActionInfo import LineActionInfo
from flask import Flask, request, abort
import KeyWordSetting
import lineActionInfo
import settings
import json
import TextParserManager

REQUEST_TYPE_BYPASS = 'request_type_bypass'
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
    actionInfo = None

    textParser = TextParser()
    textParseResult = textParser.GetParseTextResult(TextParserManager.DEFAULT_SPLIT_CHAR, receiveTxt)
    sendParam = {}

    textParseResult.PrintLog()

    #指令列表
    if textParseResult.IsKeyWordMatch(KeyWordSetting.keyWordEnum['KEY_COMMAND_LIST']):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_COMMAND_LIST,
            REQUEST_TYPE_BYPASS,
            None)
        actionInfo.statusMsg = '可使用的指令如下:'
        actionInfo.resposeMsg = KeyWordSetting.getCommandKeyList()

    #新增待辦事項
    if textParseResult.IsKeyWordMatch(KeyWordSetting.keyWordEnum['KEY_MEMO_ADD']):
        sendParam["action"] = lineActionInfo.API_ACTION_MEMO_ADD
        sendParam["subContent"] = textParseResult.GetSpecificTextTypeValue(TextParserManager.TextType_SubContent)
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_MEMO_ADD,
            REQUEST_TYPE_GAS,
            sendParam)
    
    #刪除待辦事項
    elif textParseResult.IsKeyWordMatch(KeyWordSetting.keyWordEnum['KEY_MEMO_REMOVE']):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_MEMO_REMOVE,
            REQUEST_TYPE_GAS,
            {'action':lineActionInfo.API_ACTION_MEMO_REMOVE,'content':TextParserManager.returnNumberAfterExtractKeyword(receiveTxt, KeyWordSetting.keyWordEnum['KEY_MEMO_REMOVE'])})

    #修改待辦事項
    elif textParseResult.IsKeyWordMatch(KeyWordSetting.keyWordEnum['KEY_MEMO_MODIFY']):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_MEMO_MODIFY,
            REQUEST_TYPE_GAS,
            {'action':lineActionInfo.API_ACTION_MEMO_MODIFY,'content':TextParserManager.returnNumberAndSubStringAfterExtractKeyword(receiveTxt, KeyWordSetting.keyWordEnum['KEY_MEMO_MODIFY'])})

    #確認待辦事項
    elif textParseResult.IsKeyWordMatch(KeyWordSetting.keyWordEnum['KEY_MEMO_GET']):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_MEMO_GET,
            REQUEST_TYPE_GAS,
            {'action':lineActionInfo.API_ACTION_MEMO_GET,'content':''})

    #新增週期行程
    elif textParseResult.IsKeyWordMatch(KeyWordSetting.keyWordEnum['KEY_SCHEDULE_ADD']):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_SCHEDULE_ADD,
            REQUEST_TYPE_GAS,
            {'action':lineActionInfo.API_ACTION_SCHEDULE_ADD,'content':TextParserManager.returnSubStringAfterExtractKeyword(receiveTxt, KeyWordSetting.keyWordEnum['KEY_SCHEDULE_ADD'])})

    #刪除週期行程
    elif textParseResult.IsKeyWordMatch(KeyWordSetting.keyWordEnum['KEY_SCHEDULE_REMOVE']):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_SCHEDULE_REMOVE,
            REQUEST_TYPE_GAS,
            {'action':lineActionInfo.API_ACTION_SCHEDULE_REMOVE,'content':TextParserManager.returnNumberAfterExtractKeyword(receiveTxt, KeyWordSetting.keyWordEnum['KEY_SCHEDULE_REMOVE'])})

    #修改週期行程
    elif textParseResult.IsKeyWordMatch(KeyWordSetting.keyWordEnum['KEY_SCHEDULE_MODIFY']):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_SCHEDULE_MODIFY,
            REQUEST_TYPE_GAS,
            {'action':lineActionInfo.API_ACTION_SCHEDULE_MODIFY,'content':TextParserManager.returnNumberAndSubStringAfterExtractKeyword(receiveTxt, KeyWordSetting.keyWordEnum['KEY_SCHEDULE_MODIFY'])})

    #確認週期行程
    elif textParseResult.IsKeyWordMatch(KeyWordSetting.keyWordEnum['KEY_SCHEDULE_GET']):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_SCHEDULE_GET,
            REQUEST_TYPE_GAS,
            {'action':lineActionInfo.API_ACTION_SCHEDULE_GET,'content':''})

    #記帳
    elif textParseResult.IsKeyWordMatch(KeyWordSetting.keyWordEnum['KEY_BUY']):
        actionInfo = LineActionInfo(
            KeyWordSetting.TITLE_BUY,
            REQUEST_TYPE_GAS,
            lineActionInfo.API_ACTION_BUY)

    if actionInfo is None:
        print('[SNTest] Invalid Command')
        quit()

    actionInfo.sendRequest()
    actionInfo.PrintLog()

    replyFlexMessage = flexMessageManager.getFlexMessage(actionInfo.title, actionInfo.statusMsg, actionInfo.resposeMsg)
    flexMessageJsonDict = json.loads(replyFlexMessage)

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text=actionInfo.title, contents=flexMessageJsonDict))

def printReceiverLog(event):
    eventType = str(event.source.type)
    if eventType == 'user':
        eventTypeLog = "[userId : {0}]".format(str(event.source.user_id))
    elif eventType == 'group':
        eventTypeLog = "[groupId : {0}]".format(str(event.source.group_id))
    print("[SNTest] [source.type = {0}] {1}".format(eventType, eventTypeLog))

if __name__ == "__main__":
    app.run()