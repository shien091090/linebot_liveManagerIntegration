keyWordEnum = {
    'KEY_MEMO_ADD': '新增 ',
    'KEY_MEMO_REMOVE': '刪除 ',
    'KEY_MEMO_MODIFY': '修改 ',
    'KEY_MEMO_CHECK': '確認行事曆',
    'KEY_MONTHLY_MEMO_ADD': '新增每月待辦 ',
    'KEY_MONTHLY_MEMO_REMOVE': '刪除每月待辦 ',
    'KEY_MONTHLY_MEMO_MODIFY': '修改每月待辦 ',
    'KEY_MONTHLY_MEMO_CHECK': '確認每月待辦',
    'KEY_BUY': '買 '
}
KEY_MEMO_ADD = '新增 '
KEY_MEMO_REMOVE = '刪除 '
KEY_MEMO_MODIFY = '修改 '
KEY_MEMO_CHECK = '確認行事曆'
KEY_MONTHLY_MEMO_ADD = '新增每月待辦 '
KEY_MONTHLY_MEMO_REMOVE = '刪除每月待辦 '
KEY_MONTHLY_MEMO_MODIFY = '修改每月待辦 '
KEY_MONTHLY_MEMO_CHECK = '確認每月待辦'
KEY_BUY = '買 '

TITLE_COMMAND_LIST = '指令列表'
TITLE_MEMO_ADD = '新增每日待辦事項'
TITLE_MEMO_REMOVE = '刪除每日待辦事項'
TITLE_MEMO_MODIFY = '修改每日待辦事項'
TITLE_MEMO_CHECK = '確認每日待辦事項'
TITLE_MONTHLY_MEMO_ADD = '新增每月待辦事項'
TITLE_MONTHLY_MEMO_REMOVE = '刪除每月待辦事項'
TITLE_MONTHLY_MEMO_MODIFY = '修改每月待辦事項'
TITLE_MONTHLY_MEMO_CHECK = '確認每月待辦事項'
TITLE_BUY = '新增記帳項目'

def getCommandKeyList():
    keyWords = keyWordEnum.values()
    resultTxt = ''
    index = 1
    for key in keyWords:
        resultTxt += '{0}.{1}\n'.format(index, key)
        index += 1
    return resultTxt