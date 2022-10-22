commandDataEnum = {
    'KEY_COMMAND_LIST':     ['指令', '指令', '指令列表'],
    'KEY_MEMO_ADD':         ['新增', '新增 <內容文字>', '新增待辦事項'],
    'KEY_MEMO_REMOVE':      ['刪除', '刪除 <編號數字>', '刪除待辦事項'],
    'KEY_MEMO_MODIFY':      ['修改', '修改 <編號數字> <新內容文字>', '修改待辦事項'],
    'KEY_MEMO_GET':         ['確認待辦', '確認待辦', '確認待辦事項'],
    'KEY_SCHEDULE_ADD':     ['新增行程', '新增行程 <每月/每週/每天> <幾號/星期幾(數字)> <內容文字>', '新增週期行程'],
    'KEY_SCHEDULE_REMOVE':  ['刪除行程', '刪除行程 <編號數字>', '刪除週期行程'],
    'KEY_SCHEDULE_MODIFY':  ['修改行程', '修改行程 <編號數字> <每月/每週/每天> <幾號/星期幾(數字)> <新內容文字>', '修改週期行程'],
    'KEY_SCHEDULE_GET':     ['確認行程', '確認行程', '確認週期行程'],
    'KEY_BUY':              ['買', '買 <記帳項目> <價格>', '新增記帳項目']
}

# TITLE_COMMAND_LIST = '指令列表'
# TITLE_MEMO_ADD = '新增待辦事項'
# TITLE_MEMO_REMOVE = '刪除待辦事項'
# TITLE_MEMO_MODIFY = '修改待辦事項'
# TITLE_MEMO_GET = '確認待辦事項'
# TITLE_SCHEDULE_ADD = '新增週期行程'
# TITLE_SCHEDULE_REMOVE = '刪除週期行程'
# TITLE_SCHEDULE_MODIFY = '修改週期行程'
# TITLE_SCHEDULE_GET = '確認週期行程'
# TITLE_BUY = '新增記帳項目'

def GetCommandExplantion():
    commandDataArr = commandDataEnum.values()
    resultTxt = ''
    index = 1
    for commandData in commandDataArr:
        resultTxt += f'{index}. [{commandData[0]}] 格式: {commandData[1]}\n'
        index += 1
    return resultTxt

def GetCommandKey(enumKey_str):
    if commandDataEnum.__contains__(enumKey_str) == False:
        return ''
    else:
        commandDataArr = commandDataEnum[enumKey_str]
        return commandDataArr[0]

def GetCommandFormatHint(enumKey_str):
    if commandDataEnum.__contains__(enumKey_str) == False:
        return ''
    else:
        commandDataArr = commandDataEnum[enumKey_str]
        return commandDataArr[1]
    
def GetCommandTitle(enumKey_str):
    if commandDataEnum.__contains__(enumKey_str) == False:
        return ''
    else:
        commandDataArr = commandDataEnum[enumKey_str]
        return commandDataArr[2]

def GetCommandKeyArray():
    commandDataArr = commandDataEnum.values()
    resultKeyArr = []
    for commandData in commandDataArr:
        resultKeyArr.append(commandData[0])

    return resultKeyArr

def GetCommandFormatArray():
    commandDataArr = commandDataEnum.values()
    resultKeyArr = []
    for commandData in commandDataArr:
        resultKeyArr.append(commandData[1])

    return resultKeyArr