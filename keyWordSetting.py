commandDataEnum = {
    'KEY_COMMAND_LIST': ['指令', '指令', '指令列表'],
    'KEY_MEMO_ADD': ['新增', '新增 <內容文字>', '新增待辦事項'],
    'KEY_MEMO_REMOVE': ['刪除', '刪除 <編號數字>', '刪除待辦事項'],
    'KEY_MEMO_MODIFY': ['修改', '修改 <編號數字> <新內容文字>', '修改待辦事項'],
    'KEY_MEMO_GET': ['確認待辦', '確認待辦', '確認待辦事項'],
    'KEY_SCHEDULE_ADD': ['新增行程', '新增行程 <每月/每週/每天> <數字> <內容文字>', '新增週期行程'],
    'KEY_SCHEDULE_REMOVE': ['刪除行程', '刪除行程 <編號數字>', '刪除週期行程'],
    'KEY_SCHEDULE_MODIFY': ['修改行程', '修改行程 <編號數字> <每月/每週/每天> <數字> <新內容文字>', '修改週期行程'],
    'KEY_SCHEDULE_GET': ['確認行程', '確認行程', '確認週期行程'],
    'KEY_BUY': ['買', '買 <記帳項目> <價格>', '新增記帳項目']
}

period_key_word_arr = ['每月', '每週', '每天']


def GetCommandExplanation():
    command_data_arr = commandDataEnum.values()
    result_txt = ''
    index = 1
    for commandData in command_data_arr:
        result_txt += f'{index}. [{commandData[0]}] 格式: {commandData[1]}\n'
        index += 1
    return result_txt


def GetCommandKey(enum_key_str):
    if not commandDataEnum.__contains__(enum_key_str):
        return ''
    else:
        command_data_arr = commandDataEnum[enum_key_str]
        return command_data_arr[0]


def GetCommandFormatHint(enum_key_str):
    if not commandDataEnum.__contains__(enum_key_str):
        return ''
    else:
        command_data_arr = commandDataEnum[enum_key_str]
        return command_data_arr[1]


def GetCommandTitle(enum_key_str):
    if not commandDataEnum.__contains__(enum_key_str):
        return ''
    else:
        command_data_arr = commandDataEnum[enum_key_str]
        return command_data_arr[2]


def GetCommandKeyArray():
    command_data_arr = commandDataEnum.values()
    result_key_arr = []
    for commandData in command_data_arr:
        result_key_arr.append(commandData[0])

    return result_key_arr


def GetCommandFormatArray():
    command_data_arr = commandDataEnum.values()
    result_key_arr = []
    for commandData in command_data_arr:
        result_key_arr.append(commandData[1])

    return result_key_arr


def VerifyPeriodKeyWord(period_key_word):
    return period_key_word in period_key_word_arr
