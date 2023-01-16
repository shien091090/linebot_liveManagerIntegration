import json

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage

import keyWordSetting
import textParserManager
import lineActionInfo
import settings
from textParserManager import TextParser, TextType_AdditionalContent, TextType_KeyWord, TextType_Number, \
    TextType_SubContent, TextStructureType_Content, TextStructureType_Number, TextType_SubNumber
from flexMessageManager import GetCommandExplanationFlexMessage, getFlexMessage

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
    receive_txt = event.message.text
    reply_flex_message, req_info = ParseRequestInfo(receive_txt)

    if req_info is None:
        print('[SNTest] Invalid Command')
        quit()

    req_info.sendRequest()

    if reply_flex_message == '':
        reply_flex_message = getFlexMessage(req_info.title, req_info.statusMsg, req_info.responseMsg)

    flex_message_json_dict = json.loads(reply_flex_message)

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text=req_info.title, contents=flex_message_json_dict))


def ParseRequestInfo(receive_txt):
    req_info = None
    text_parser = TextParser(textParserManager.DEFAULT_SPLIT_CHAR, receive_txt)
    send_param = {}
    reply_flex_message = ''
    command_key_parse_result = text_parser.ParseTextBySpecificStructure(
        [TextStructureType_Content, TextStructureType_Content])
    command_key_type_log = "'Key + Content'"

    if command_key_parse_result is None:
        command_key_parse_result = text_parser.ParseTextBySpecificStructure([TextStructureType_Content])
        command_key_type_log = "'One Key'"
    if command_key_parse_result is None:
        print('[SNTest] Invalid Command')
        return reply_flex_message, req_info

    command_key = command_key_parse_result.GetSpecificTextTypeValue(TextType_KeyWord)
    print(f'[SNTest] Command Key = {command_key}, Command Key type is {command_key_type_log}')
    print('---------------------------------')
    # 指令列表
    temp_command_key = 'KEY_COMMAND_LIST'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        req_info = lineActionInfo.RequestInfo(
            keyWordSetting.GetCommandTitle(temp_command_key),
            REQUEST_TYPE_BYPASS,
            None)

        reply_flex_message = GetCommandExplanationFlexMessage(
            req_info.title,
            keyWordSetting.GetCommandKeyArray(),
            keyWordSetting.GetCommandFormatArray())

    # 新增待辦事項
    temp_command_key = 'KEY_MEMO_ADD'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Content]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or text_parse_result.IsKeyWordMatch(
                keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            text_parse_result.PrintLog()
            send_param["action"] = lineActionInfo.API_ACTION_MEMO_ADD
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_GAS,
                                                  send_param)
    # 刪除待辦事項
    temp_command_key = 'KEY_MEMO_REMOVE'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Number]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or text_parse_result.IsKeyWordMatch(
                keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            text_parse_result.PrintLog()
            send_param["action"] = lineActionInfo.API_ACTION_MEMO_REMOVE
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_GAS,
                                                  send_param)
    # 修改待辦事項
    temp_command_key = 'KEY_MEMO_MODIFY'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Number, TextStructureType_Content]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False or \
                int(text_parse_result.GetSpecificTextTypeValue(TextType_Number)) <= 0:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_MEMO_MODIFY
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param)
    # 確認待辦事項
    temp_command_key = 'KEY_MEMO_GET'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        send_param["action"] = lineActionInfo.API_ACTION_MEMO_GET
        req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_GAS,
                                              send_param)
    # 新增週期行程
    temp_command_key = 'KEY_SCHEDULE_ADD'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Content, TextStructureType_Number,
                                  TextStructureType_Content]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or text_parse_result.IsKeyWordMatch(
                keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為\n『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_SCHEDULE_ADD
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            send_param["additionalContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_AdditionalContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_GAS,
                                                  send_param)
    # 刪除週期行程
    temp_command_key = 'KEY_SCHEDULE_REMOVE'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Number]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or text_parse_result.IsKeyWordMatch(
                keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_SCHEDULE_REMOVE
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_GAS,
                                                  send_param)
    # 修改週期行程
    temp_command_key = 'KEY_SCHEDULE_MODIFY'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Number, TextStructureType_Content,
                                  TextStructureType_Number, TextStructureType_Content]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or text_parse_result.IsKeyWordMatch(
                keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為\n『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_SCHEDULE_MODIFY
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            send_param["subNumber"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubNumber)
            send_param["additionalContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_AdditionalContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_GAS,
                                                  send_param)
    # 確認週期行程
    temp_command_key = 'KEY_SCHEDULE_GET'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        send_param["action"] = lineActionInfo.API_ACTION_SCHEDULE_GET
        req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_GAS,
                                              send_param)
    # 記帳
    temp_command_key = 'KEY_BUY'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Content, TextStructureType_Number]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or text_parse_result.IsKeyWordMatch(
                keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_BUY
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key), REQUEST_TYPE_GAS,
                                                  send_param)
    return reply_flex_message, req_info


def printReceiverLog(event):
    event_type = str(event.source.type)
    event_type_log = ''
    if event_type == 'user':
        event_type_log = "[userId : {0}]".format(str(event.source.user_id))
    elif event_type == 'group':
        event_type_log = "[groupId : {0}]".format(str(event.source.group_id))
    print("[SNTest] [source.type = {0}] {1}".format(event_type, event_type_log))


if __name__ == "__main__":
    app.run()
