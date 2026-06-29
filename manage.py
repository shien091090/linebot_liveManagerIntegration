from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage, ImageSendMessage
from textParserManager import TextParser, TextType_AdditionalContent, TextType_KeyWord, TextType_Number, \
    TextType_SubContent, TextStructureType_Content, TextStructureType_Number, TextType_SubNumber
from flexMessageManager import GetCommandExplanationFlexMessage, getFlexMessage, getMemoFlexMessage, getUrlButtonFlexMessage
from dateColorHelper import build_colored_memo_items, taiwan_today
from expenseDashboardHelper import fetch_expense_data, generate_expense_dashboard_html
from chartManager import createPieChartAndGetFileName

import keyWordSetting
import textParserManager
import lineActionInfo
import settings
import re
import uuid
import pyimgur
import json

REQUEST_TYPE_BYPASS = 'request_type_bypass'
REQUEST_TYPE_GAS = 'request_type_gas'

STATUS_CODE_SUCCESS = 200
STATUS_CODE_EMPTY_INPUT = 300
STATUS_CODE_INVALID = 301

IMGUR_CLIENT_ID = "cd9dac4885101cf"

MESSAGE_TYPE_TEXT = 'text'
MESSAGE_TYPE_CHART = 'chart'
MESSAGE_TYPE_URL = 'url'

MEMO_ACTIONS = {
    lineActionInfo.API_ACTION_MEMO_ADD,
    lineActionInfo.API_ACTION_MEMO_REMOVE,
    lineActionInfo.API_ACTION_MEMO_REMOVE_MULTIPLE,
    lineActionInfo.API_ACTION_MEMO_MODIFY,
    lineActionInfo.API_ACTION_MEMO_EXTEND,
    lineActionInfo.API_ACTION_MEMO_GET,
}

SCHEDULE_ACTIONS = {
    lineActionInfo.API_ACTION_SCHEDULE_ADD,
    lineActionInfo.API_ACTION_SCHEDULE_REMOVE,
    lineActionInfo.API_ACTION_SCHEDULE_MODIFY,
    lineActionInfo.API_ACTION_SCHEDULE_GET,
}

app = Flask(__name__)
mockup_store = {}

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


@app.route('/mockup/<token>')
def serve_mockup(token):
    html = mockup_store.get(token)
    if not html:
        return 'Not found', 404
    return html, 200, {'Content-Type': 'text/html; charset=utf-8'}


@app.route('/preparation-list')
def preparation_list():
    import requests as req_lib
    params = {'action': 'action_get_preparation_list', 'format': 'text'}
    attributes = request.args.get('attributes', '')
    condition = request.args.get('condition', '')
    if attributes:
        params['attributes'] = attributes
    if condition:
        params['condition'] = condition
    r = req_lib.get(settings.URL_GAS_API, params=params)
    return r.text, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/dashboard')
def dashboard():
    from dashboardHelper.dashboardBuilder import build_dashboard
    return build_dashboard(settings.URL_GAS_API), 200, {'Content-Type': 'text/html; charset=utf-8'}


@app.route('/record-daily-time')
def record_daily_time():
    import requests as req_lib
    event_type = request.args.get('eventType', '')
    params = {'action': 'action_record_daily_time', 'eventType': event_type}
    r = req_lib.get(settings.URL_GAS_API, params=params)
    return r.text, 200, {'Content-Type': 'application/json; charset=utf-8'}



@handler.add(MessageEvent, message=TextMessage)
def receiveMessage(event):
    printReceiverLog(event)
    receive_txt = event.message.text
    reply_flex_message, req_info = ParseRequestInfo(receive_txt)

    if req_info is None:
        print('[SNTest] Invalid Command')
        quit()

    req_info.sendRequest()

    if req_info.messageType == MESSAGE_TYPE_CHART:

        chart_info_dict = json.loads(req_info.responseMsg)
        print(f'responseMsg: {chart_info_dict}')
        
        file_name = createPieChartAndGetFileName(chart_info_dict['data'], chart_info_dict['chartTitle'])
        im = pyimgur.Imgur(IMGUR_CLIENT_ID)
        uploaded_image = im.upload_image(file_name, title='testChart')

        img_message = ImageSendMessage(
            original_content_url = uploaded_image.link,
            preview_image_url = uploaded_image.link)
        
        line_bot_api.reply_message(
            event.reply_token,
            img_message)
        
    elif req_info.messageType == MESSAGE_TYPE_URL:
        flex_dict = json.loads(getUrlButtonFlexMessage(req_info.title, req_info.statusMsg, req_info.responseMsg))
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text=req_info.title, contents=flex_dict))

    elif req_info.messageType == MESSAGE_TYPE_TEXT:
        if reply_flex_message == '':
            action = req_info.requestParam.get('action') if req_info.requestParam else None
            if action in MEMO_ACTIONS and req_info.statusCode == STATUS_CODE_SUCCESS:
                colored_items = build_colored_memo_items(req_info.responseMsg, taiwan_today())
                reply_flex_message = getMemoFlexMessage(req_info.title, req_info.statusMsg, colored_items)
            elif action in SCHEDULE_ACTIONS and req_info.statusCode == STATUS_CODE_SUCCESS:
                colored_items = build_colored_memo_items(req_info.responseMsg, taiwan_today())
                reply_flex_message = getMemoFlexMessage(req_info.title, req_info.statusMsg, colored_items)
            else:
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

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            text_parse_result.PrintLog()
            send_param["action"] = lineActionInfo.API_ACTION_MEMO_ADD
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param)
    # 刪除待辦事項
    temp_command_key = 'KEY_MEMO_REMOVE'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        raw_tokens = text_parser.rawContent.split(textParserManager.DEFAULT_SPLIT_CHAR)
        numbers_token = raw_tokens[1].strip() if len(raw_tokens) >= 2 else ''
        is_multiple = bool(re.match(r'^\d+~\d+$', numbers_token) or re.match(r'^\d+([/.,]\d+)+$', numbers_token))

        if is_multiple:
            send_param["action"] = lineActionInfo.API_ACTION_MEMO_REMOVE_MULTIPLE
            send_param["numbers"] = numbers_token
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle('KEY_MEMO_REMOVE_MULTIPLE'),
                                                  REQUEST_TYPE_GAS,
                                                  send_param)
        else:
            command_text_structure = [TextStructureType_Content, TextStructureType_Number]
            text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

            if text_parse_result is None or \
                    text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
                req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                      REQUEST_TYPE_BYPASS,
                                                      None)
                req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
                req_info.responseMsg = ' '
            else:
                text_parse_result.PrintLog()
                send_param["action"] = lineActionInfo.API_ACTION_MEMO_REMOVE
                send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
                req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                      REQUEST_TYPE_GAS,
                                                      send_param)
    # 修改待辦事項
    temp_command_key = 'KEY_MEMO_MODIFY'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Number, TextStructureType_Content]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
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
    # 延伸待辦事項
    temp_command_key = 'KEY_MEMO_EXTEND'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Number, TextStructureType_Content]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_MEMO_EXTEND
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param)
    # 確認待辦事項
    temp_command_key = 'KEY_MEMO_GET'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        send_param["action"] = lineActionInfo.API_ACTION_MEMO_GET
        req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                              REQUEST_TYPE_GAS,
                                              send_param)
    # 新增週期行程
    temp_command_key = 'KEY_SCHEDULE_ADD'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Content, TextStructureType_Number,
                                  TextStructureType_Content]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)
        is_daily_type = False

        if text_parse_result is None or \
                (text_parse_result is not None and text_parse_result.GetSpecificTextTypeValue(
                    TextType_SubContent) == '每天'):
            command_text_structure = [TextStructureType_Content, TextStructureType_Content, TextStructureType_Content]
            text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)
            is_daily_type = text_parse_result is not None and \
                            text_parse_result.GetSpecificTextTypeValue(TextType_SubContent) == '每天'

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False or \
                (not is_daily_type and text_parse_result.GetSpecificTextTypeValue(TextType_Number) == '') or \
                (not is_daily_type and int(text_parse_result.GetSpecificTextTypeValue(TextType_Number)) <= 0) or \
                keyWordSetting.VerifyPeriodKeyWord(
                    text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為\n『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_SCHEDULE_ADD
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            if is_daily_type:
                send_param["number"] = '0'
            else:
                send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            send_param["additionalContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_AdditionalContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param)
    # 刪除週期行程
    temp_command_key = 'KEY_SCHEDULE_REMOVE'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Number]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_SCHEDULE_REMOVE
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param)
    # 修改週期行程
    temp_command_key = 'KEY_SCHEDULE_MODIFY'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Number, TextStructureType_Content,
                                  TextStructureType_Number, TextStructureType_Content]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)
        is_daily_type = False

        if text_parse_result is None or \
                (text_parse_result is not None and text_parse_result.GetSpecificTextTypeValue(
                    TextType_SubContent) == '每天'):
            command_text_structure = [TextStructureType_Content, TextStructureType_Number, TextStructureType_Content,
                                      TextStructureType_Content]
            text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)
            is_daily_type = text_parse_result is not None and \
                            text_parse_result.GetSpecificTextTypeValue(TextType_SubContent) == '每天'

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False or \
                (not is_daily_type and text_parse_result.GetSpecificTextTypeValue(TextType_SubNumber) == '') or \
                keyWordSetting.VerifyPeriodKeyWord(
                    text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為\n『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_SCHEDULE_MODIFY
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            if is_daily_type:
                send_param["subNumber"] = '0'
            else:
                send_param["subNumber"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubNumber)
            send_param["additionalContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_AdditionalContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param)
    # 確認週期行程
    temp_command_key = 'KEY_SCHEDULE_GET'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        send_param["action"] = lineActionInfo.API_ACTION_SCHEDULE_GET
        req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                              REQUEST_TYPE_GAS,
                                              send_param)
    # 記帳
    temp_command_key = 'KEY_BUY'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Content, TextStructureType_Number]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_BUY
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param)

    # 記帳(預算種類)
    temp_command_key = 'KEY_BUY_WITH_BUDGET_TYPE'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Content, TextStructureType_Number,
                                  TextStructureType_Content]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_BUY_WITH_BUDGET_TYPE
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            send_param["additionalContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_AdditionalContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param)

    #分析圖表
    temp_command_key = 'KEY_GET_CHART'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Content, TextStructureType_Content]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None)
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_GET_CHART
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            send_param["additionalContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_AdditionalContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param)

    # 花費統計報表（不加入使用者指令列表）
    if command_key == '分析家庭收支':
        try:
            months, cats = fetch_expense_data()
            html = generate_expense_dashboard_html(months, cats)
        except Exception as e:
            html = f'<html><body><p>Error: {e}</p></body></html>'
        mockup_store['expense_dashboard'] = html
        url = 'https://linebot-livemanagerintegration.herokuapp.com/mockup/expense_dashboard'
        req_info = lineActionInfo.RequestInfo('分析家庭收支', REQUEST_TYPE_BYPASS, None)
        req_info.statusMsg = '已生成家庭收支分析報表'
        req_info.responseMsg = url
        req_info.messageType = MESSAGE_TYPE_URL

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
