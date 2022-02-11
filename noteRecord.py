import json
import datetime
from textParser import checkHeaderByKeyWord
from dateManager import parseHeaderDateString

HEADER_MONTHLY = '(每月)'

class NoteRecordItem:
    def __init__(self, content_str, sender_str, memoTime_str):
        self.content = content_str
        self.sender = sender_str
        self.memoTime = memoTime_str
    
    def printInfo(self):
        print('content:{0}, sender:{1}, memoTime:{2}'.format(self.content, self.sender, self.memoTime))

class NoteRecordManager:

    def parseRecordDict(dct):
        return NoteRecordItem(dct['content'], dct['sender'], dct['memoTime'])

    def parseJsonDataToRecordList(json_str):
        recordList = []
        if json_str == '':
            return recordList
    
        jsonDictList = json.loads(json_str)
        for jData in jsonDictList:
            record = json.loads(jData, object_hook=NoteRecordManager.parseRecordDict)
            recordList.append(record)
        return recordList

    def parseRecordListToJsonData(record_list):
        sortedRecordList = NoteRecordManager.getSortedRecordList(record_list)
        dctList = []
        for r in sortedRecordList:
            jRecord = json.dumps(r.__dict__)
            dctList.append(jRecord)
        jsonContent = json.dumps(dctList)
        return jsonContent

    def getSortedRecordList(record_list):
        monthlyItemList = []
        datePrefixList = []
        noDatePrefixList = []

        for r in record_list:
            isMonthlyItem = checkHeaderByKeyWord(r.content, HEADER_MONTHLY)
            parseDateStr = parseHeaderDateString(r.content)
            if isMonthlyItem:
                monthlyItemList.append(r)
            elif parseDateStr != '':
                datePrefixList.append(r)
            else:
                noDatePrefixList.append(r)

        ouputRecordList = []

        if len(monthlyItemList) > 0:
            for r_monthly in monthlyItemList:
                ouputRecordList.append(r_monthly)

        if len(datePrefixList) > 0:
            datePrefixList = sorted(datePrefixList, key = lambda r: datetime.datetime.strptime(parseHeaderDateString(r.content), "%m/%d"))
            for r_sort in datePrefixList:
                ouputRecordList.append(r_sort)

        if len(noDatePrefixList) > 0:
            for r_normal in noDatePrefixList:
                ouputRecordList.append(r_normal)
        
        return ouputRecordList

    def getCurrentMemoShowText_daily(record_list):
        return NoteRecordManager.getCurrentMemoShowText(record_list, '目前行事曆項目:\n')

    def getCurrentMemoShowText_monthly(record_list):
        return NoteRecordManager.getCurrentMemoShowText(record_list, '目前每月待辦項目:\n')

    def getCurrentMemoShowText(record_list, caption_str):
        sortedRecordList = NoteRecordManager.getSortedRecordList(record_list)
        showTxt = caption_str
        idx = 0
        for r in sortedRecordList:
            idx += 1
            showTxt += '{0}. {1}\n'.format(str(idx), r.content)
        return showTxt