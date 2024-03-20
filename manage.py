import json

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage, ImageSendMessage

import keyWordSetting
import textParserManager
import lineActionInfo
import settings
from textParserManager import TextParser, TextType_AdditionalContent, TextType_KeyWord, TextType_Number, \
    TextType_SubContent, TextStructureType_Content, TextStructureType_Number, TextType_SubNumber
from flexMessageManager import GetCommandExplanationFlexMessage, getFlexMessage

from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties
import pandas as pd
from datetime import datetime
import numpy as np
import os
import pyimgur

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

    if req_info.messageType == 'image':

        data = {
            "日期": ["2024-03-01", "2024-03-02", "2024-03-03", "2024-03-04", "2024-03-05",
                    "2024-03-01", "2024-03-02", "2024-03-03", "2024-03-04", "2024-03-05"],
            "款項": ["午餐", "公交", "晚餐", "書籍", "電影",
                    "午餐", "咖啡", "晚餐", "電影", "衣服"],
            "金額": [120, 25, 150, 200, 90,
                    130, 45, 160, 85, 300],
            "類別": ["餐飲", "交通", "餐飲", "學習", "娛樂",
                    "餐飲", "飲品", "餐飲", "娛樂", "服裝"]
        }

        df = pd.DataFrame(data)
        df["日期"] = pd.to_datetime(df["日期"])

        this_month = df[(df["日期"] >= "2024-03-01") & (df["日期"] <= "2024-03-31")]
        category_sums = this_month.groupby("類別")["金額"].sum()

        font_path = "fonts/meiryo.ttc"
        font_prop = FontProperties(fname=font_path, size=14)

        plt.figure(figsize=(10, 7))
        plt.pie(category_sums, labels=category_sums.index, autopct='%1.1f%%', startangle=140)
        plt.title('2024年3月各類別消費總金額', fontproperties=font_prop)
        plt.axis('equal')

        file_name = 'expense_pie_chart.jpg'
        plt.savefig(file_name)
        plt.close()

        CLIENT_ID = "cd9dac4885101cf"
        im = pyimgur.Imgur(CLIENT_ID)

        uploaded_image = im.upload_image(file_name, title='testChart')
        print(uploaded_image.link)

        img_message = ImageSendMessage(
            original_content_url = uploaded_image.link,
            preview_image_url = uploaded_image.link)
        
        line_bot_api.reply_message(
            event.reply_token,
            img_message)
        
    elif req_info.messageType == 'text':
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
            None,
            'text')

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
                                                  None,
                                                  'text')
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            text_parse_result.PrintLog()
            send_param["action"] = lineActionInfo.API_ACTION_MEMO_ADD
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param,
                                                  'text')
    # 刪除待辦事項
    temp_command_key = 'KEY_MEMO_REMOVE'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Number]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None,
                                                  'text')
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            text_parse_result.PrintLog()
            send_param["action"] = lineActionInfo.API_ACTION_MEMO_REMOVE
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param,
                                                  'text')
    # 修改待辦事項
    temp_command_key = 'KEY_MEMO_MODIFY'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Number, TextStructureType_Content]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None,
                                                  'text')
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_MEMO_MODIFY
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param,
                                                  'text')
    # 確認待辦事項
    temp_command_key = 'KEY_MEMO_GET'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        send_param["action"] = lineActionInfo.API_ACTION_MEMO_GET
        req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                              REQUEST_TYPE_GAS,
                                              send_param,
                                              'text')
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
                                                  None,
                                                  'text')
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
                                                  send_param,
                                                  'text')
    # 刪除週期行程
    temp_command_key = 'KEY_SCHEDULE_REMOVE'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Number]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None,
                                                  'text')
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_SCHEDULE_REMOVE
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param,
                                                  'text')
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
                                                  None,
                                                  'text')
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
                                                  send_param,
                                                  'text')
    # 確認週期行程
    temp_command_key = 'KEY_SCHEDULE_GET'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        send_param["action"] = lineActionInfo.API_ACTION_SCHEDULE_GET
        req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                              REQUEST_TYPE_GAS,
                                              send_param,
                                              'text')
    # 記帳
    temp_command_key = 'KEY_BUY'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Content, TextStructureType_Number]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_BYPASS,
                                                  None,
                                                  'text')
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_BUY
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param,
                                                  'text')

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
                                                  None,
                                                  'text')
            req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
            req_info.responseMsg = ' '
        else:
            send_param["action"] = lineActionInfo.API_ACTION_BUY_WITH_BUDGET_TYPE
            send_param["subContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_SubContent)
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            send_param["additionalContent"] = text_parse_result.GetSpecificTextTypeValue(TextType_AdditionalContent)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param,
                                                  'text')

    # 紀錄寶寶換尿布時間
    temp_command_key = 'KEY_BABY_DIAPER'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        send_param["action"] = lineActionInfo.API_ACTION_RECORD_BABY_DIAPER_CHANGING_TIME
        req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                              REQUEST_TYPE_GAS,
                                              send_param,
                                              'text')

    # 紀錄寶寶吃飯時間
    temp_command_key = 'KEY_BABY_EAT'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        command_text_structure = [TextStructureType_Content, TextStructureType_Number]
        text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

        if text_parse_result is None or \
                text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:

            command_text_structure = [TextStructureType_Content]
            text_parse_result = text_parser.ParseTextBySpecificStructure(command_text_structure)

            if text_parse_result is None or \
                    text_parse_result.IsKeyWordMatch(keyWordSetting.GetCommandKey(temp_command_key)) is False:
                req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                      REQUEST_TYPE_BYPASS,
                                                      None,
                                                      'text')
                req_info.statusMsg = f"【格式錯誤】\n正確格式為 『{keyWordSetting.GetCommandFormatHint(temp_command_key)}』"
                req_info.responseMsg = ' '

            else:
                send_param["action"] = lineActionInfo.API_ACTION_RECORD_BABY_EAT_TIME
                req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                      REQUEST_TYPE_GAS,
                                                      send_param,
                                                      'text')
        else:
            send_param["action"] = lineActionInfo.API_ACTION_RECORD_BABY_EAT_TIME
            send_param["number"] = text_parse_result.GetSpecificTextTypeValue(TextType_Number)
            req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                                  REQUEST_TYPE_GAS,
                                                  send_param,
                                                  'text')
    #圖表測試
    temp_command_key = 'KEY_GET_CHART'
    if command_key == keyWordSetting.GetCommandKey(temp_command_key):
        send_param["action"] = lineActionInfo.API_ACTION_GET_CHART
        req_info = lineActionInfo.RequestInfo(keyWordSetting.GetCommandTitle(temp_command_key),
                                              REQUEST_TYPE_GAS,
                                              send_param,
                                              'image')

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
