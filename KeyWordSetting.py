keyWordEnum = {
    'KEY_COMMAND_LIST': '指令',
    'KEY_MEMO_ADD': '新增 ',
    'KEY_MEMO_REMOVE': '刪除 ',
    'KEY_MEMO_MODIFY': '修改 ',
    'KEY_MEMO_GET': '確認待辦',
    'KEY_SCHEDULE_ADD': '新增行程 ',
    'KEY_SCHEDULE_REMOVE': '刪除行程 ',
    'KEY_SCHEDULE_MODIFY': '修改行程 ',
    'KEY_SCHEDULE_GET': '確認行程',
    'KEY_BUY': '買 '
}

TITLE_COMMAND_LIST = '指令列表'
TITLE_MEMO_ADD = '新增待辦事項'
TITLE_MEMO_REMOVE = '刪除待辦事項'
TITLE_MEMO_MODIFY = '修改待辦事項'
TITLE_MEMO_GET = '確認待辦事項'
TITLE_SCHEDULE_ADD = '新增週期行程'
TITLE_SCHEDULE_REMOVE = '刪除週期行程'
TITLE_SCHEDULE_MODIFY = '修改週期行程'
TITLE_SCHEDULE_GET = '確認週期行程'
TITLE_BUY = '新增記帳項目'

def getCommandKeyList():
    keyWords = keyWordEnum.values()
    resultTxt = ''
    index = 1
    for key in keyWords:
        resultTxt += '{0}.{1}\n'.format(index, key)
        index += 1
    return resultTxt