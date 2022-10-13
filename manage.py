import imp
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, FlexSendMessage
from TextParserManager import TextParser, TextType_AdditionalContent, TextType_KeyWord, TextType_Number, TextType_SubContent, TextStructureType_Content, TextStructureType_Number, TextStructureType_Date
from dateManager import dateManager
from flexMessageManager import flexMessageManager
from lineActionInfo import RequestInfo
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
    reqInfo = None

    textParser = TextParser(TextParserManager.DEFAULT_SPLIT_CHAR, receiveTxt)
    sendParam = {}
    commandTextStructure = []

    commandKeyParseResult = textParser.ParseTextBySpecificStructure([TextStructureType_Content, TextStructureType_Content])
    commandKeyTypeLog = "'Key + Content'"
    if commandKeyParseResult is None:
        commandKeyParseResult = textParser.ParseTextBySpecificStructure([TextStructureType_Content])
        commandKeyTypeLog = "'One Key'"
    if commandKeyParseResult is None:
        print('[SNTest] Invalid Command')
        quit()
    
    commandKey = commandKeyParseResult.GetSpecificTextTypeValue(TextType_KeyWord)
    print(f'[SNTest] Command Key = {commandKey}, Command Key type is {commandKeyTypeLog}')
    print('---------------------------------')

    tempCommandKey = ""

    #指令列表
    tempCommandKey = 'KEY_COMMAND_LIST'
    if commandKey == KeyWordSetting.GetCommandKey(tempCommandKey):
        reqInfo = RequestInfo(
            KeyWordSetting.GetCommandTitle(tempCommandKey),
            REQUEST_TYPE_BYPASS,
            None)
        reqInfo.statusMsg = '可使用的指令如下:'
        reqInfo.resposeMsg = KeyWordSetting.GetCommandExplantion()

    #新增待辦事項
    tempCommandKey = 'KEY_MEMO_ADD'
    if commandKey == KeyWordSetting.GetCommandKey(tempCommandKey):
        commandTextStructure = [TextStructureType_Content, TextStructureType_Content]
        textParseResult = textParser.ParseTextBySpecificStructure(commandTextStructure)

        if textParseResult is None or textParseResult.IsKeyWordMatch(KeyWordSetting.GetCommandKey(tempCommandKey)) == False:
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_BYPASS, None)
            reqInfo.statusMsg = f"[格式錯誤] 正確格式為:\n'{KeyWordSetting.GetCommandFormatHint(tempCommandKey)}'"
            reqInfo.resposeMsg = ' '
        else:
            textParseResult.PrintLog()
            sendParam["action"] = lineActionInfo.API_ACTION_MEMO_ADD
            sendParam["subContent"] = textParseResult.GetSpecificTextTypeValue(TextType_SubContent)
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_GAS, sendParam)
    
    #刪除待辦事項
    tempCommandKey = 'KEY_MEMO_REMOVE'
    if commandKey == KeyWordSetting.GetCommandKey(tempCommandKey):
        commandTextStructure = [TextStructureType_Content, TextStructureType_Number]
        textParseResult = textParser.ParseTextBySpecificStructure(commandTextStructure)

        if textParseResult is None or textParseResult.IsKeyWordMatch(KeyWordSetting.GetCommandKey(tempCommandKey)) == False:
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_BYPASS, None)
            reqInfo.statusMsg = f"[格式錯誤] 正確格式為:\n'{KeyWordSetting.GetCommandFormatHint(tempCommandKey)}'"
            reqInfo.resposeMsg = ' '
        else:
            textParseResult.PrintLog()
            sendParam["action"] = lineActionInfo.API_ACTION_MEMO_REMOVE
            sendParam["number"] = textParseResult.GetSpecificTextTypeValue(TextType_Number)
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_GAS, sendParam)

    #修改待辦事項
    tempCommandKey = 'KEY_MEMO_MODIFY'
    if commandKey == KeyWordSetting.GetCommandKey(tempCommandKey):
        commandTextStructure = [TextStructureType_Content, TextStructureType_Number, TextStructureType_Content]
        textParseResult = textParser.ParseTextBySpecificStructure(commandTextStructure)

        if textParseResult is None or textParseResult.IsKeyWordMatch(KeyWordSetting.GetCommandKey(tempCommandKey)) == False:
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_BYPASS, None)
            reqInfo.statusMsg = f"[格式錯誤] 正確格式為:\n'{KeyWordSetting.GetCommandFormatHint(tempCommandKey)}'"
            reqInfo.resposeMsg = ' '
        else:
            sendParam["action"] = lineActionInfo.API_ACTION_MEMO_MODIFY
            sendParam["number"] = textParseResult.GetSpecificTextTypeValue(TextType_Number)
            sendParam["subContent"] = textParseResult.GetSpecificTextTypeValue(TextType_SubContent)
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_GAS, sendParam)

    #確認待辦事項
    tempCommandKey = 'KEY_MEMO_GET'
    if commandKey == KeyWordSetting.GetCommandKey(tempCommandKey):
        sendParam["action"] = lineActionInfo.API_ACTION_MEMO_GET
        reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_GAS, sendParam)

    #新增週期行程
    tempCommandKey = 'KEY_SCHEDULE_ADD'
    if commandKey == KeyWordSetting.GetCommandKey(tempCommandKey):
        commandTextStructure = [TextStructureType_Content, TextStructureType_Content, TextStructureType_Number, TextStructureType_Content]
        textParseResult = textParser.ParseTextBySpecificStructure(commandTextStructure)

        if textParseResult is None or textParseResult.IsKeyWordMatch(KeyWordSetting.GetCommandKey(tempCommandKey)) == False:
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_BYPASS, None)
            reqInfo.statusMsg = f"[格式錯誤] 正確格式為:\n'{KeyWordSetting.GetCommandFormatHint(tempCommandKey)}'"
            reqInfo.resposeMsg = ' '
        else:
            sendParam["action"] = lineActionInfo.API_ACTION_SCHEDULE_ADD
            sendParam["subContent"] = textParseResult.GetSpecificTextTypeValue(TextParserManager.TextType_SubContent)
            sendParam["number"] = textParseResult.GetSpecificTextTypeValue(TextParserManager.TextType_Number)
            sendParam["additionalContent"] = textParseResult.GetSpecificTextTypeValue(TextParserManager.TextType_AdditionalContent)
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_GAS, sendParam)

    #刪除週期行程
    tempCommandKey = 'KEY_SCHEDULE_REMOVE'
    if commandKey == KeyWordSetting.GetCommandKey(tempCommandKey):
        checkTextTypeStructure = [TextType_KeyWord, TextType_Number]

        if textParseResult.IsStructureMatch(checkTextTypeStructure) == False:
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_BYPASS, None)
            reqInfo.statusMsg = f"[格式錯誤] 正確格式為:\n'{KeyWordSetting.GetCommandFormatHint(tempCommandKey)}'"
            reqInfo.resposeMsg = ' '
        else:
            sendParam["action"] = lineActionInfo.API_ACTION_SCHEDULE_REMOVE
            sendParam["number"] = textParseResult.GetSpecificTextTypeValue(TextParserManager.TextType_Number)
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_GAS, sendParam)

    #修改週期行程
    tempCommandKey = 'KEY_SCHEDULE_MODIFY'
    if commandKey == KeyWordSetting.GetCommandKey(tempCommandKey):
        checkTextTypeStructure = [TextType_KeyWord, TextType_Number, TextType_SubContent]

        if textParseResult.IsStructureMatch(checkTextTypeStructure) == False:
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_BYPASS, None)
            reqInfo.statusMsg = f"[格式錯誤] 正確格式為:\n'{KeyWordSetting.GetCommandFormatHint(tempCommandKey)}'"
            reqInfo.resposeMsg = ' '
        else:
            sendParam["action"] = lineActionInfo.API_ACTION_SCHEDULE_MODIFY
            sendParam["number"] = textParseResult.GetSpecificTextTypeValue(TextParserManager.TextType_Number)
            sendParam["subContent"] = textParseResult.GetSpecificTextTypeValue(TextParserManager.TextType_SubContent)
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_GAS, sendParam)

    #確認週期行程
    tempCommandKey = 'KEY_SCHEDULE_GET'
    if commandKey == KeyWordSetting.GetCommandKey(tempCommandKey):
        checkTextTypeStructure = [TextType_KeyWord]

        if textParseResult.IsStructureMatch(checkTextTypeStructure) == False:
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_BYPASS, None)
            reqInfo.statusMsg = f"[格式錯誤] 正確格式為:\n'{KeyWordSetting.GetCommandFormatHint(tempCommandKey)}'"
            reqInfo.resposeMsg = ' '
        else:
            sendParam["action"] = lineActionInfo.API_ACTION_SCHEDULE_GET
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_GAS, sendParam)

    #記帳
    tempCommandKey = 'KEY_BUY'
    if commandKey == KeyWordSetting.GetCommandKey(tempCommandKey):
        checkTextTypeStructure = [TextType_KeyWord, TextType_SubContent, TextType_Number]

        if textParseResult.IsStructureMatch(checkTextTypeStructure) == False:
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_BYPASS, None)
            reqInfo.statusMsg = f"[格式錯誤] 正確格式為:\n'{KeyWordSetting.GetCommandFormatHint(tempCommandKey)}'"
            reqInfo.resposeMsg = ' '
        else:
            sendParam["action"] = lineActionInfo.API_ACTION_BUY
            sendParam["subContent"] = textParseResult.GetSpecificTextTypeValue(TextParserManager.TextType_SubContent)
            sendParam["number"] = textParseResult.GetSpecificTextTypeValue(TextParserManager.TextType_Number)
            reqInfo = RequestInfo(KeyWordSetting.GetCommandTitle(tempCommandKey), REQUEST_TYPE_GAS, sendParam)

    if reqInfo is None:
        print('[SNTest] Invalid Command')
        quit()

    reqInfo.sendRequest()

    replyFlexMessage = flexMessageManager.getFlexMessage(reqInfo.title, reqInfo.statusMsg, reqInfo.resposeMsg)
    flexMessageJsonDict = json.loads(replyFlexMessage)

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text=reqInfo.title, contents=flexMessageJsonDict))

def printReceiverLog(event):
    eventType = str(event.source.type)
    if eventType == 'user':
        eventTypeLog = "[userId : {0}]".format(str(event.source.user_id))
    elif eventType == 'group':
        eventTypeLog = "[groupId : {0}]".format(str(event.source.group_id))
    print("[SNTest] [source.type = {0}] {1}".format(eventType, eventTypeLog))

if __name__ == "__main__":
    app.run()