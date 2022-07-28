import datetime
from dateutil import parser

class dateManager:

    def getCurrentTimeText():
        tz_taiwan = datetime.timezone(datetime.timedelta(hours=+8))
        localDate = datetime.datetime.today().astimezone(tz_taiwan)
        dateStr = localDate.strftime("%Y/%m/%d_%H:%M:%S")
        return dateStr

    def getTodayDayNumber():
        tz_taiwan = datetime.timezone(datetime.timedelta(hours=+8))
        localDate = datetime.datetime.today().astimezone(tz_taiwan)
        dayNum = localDate.day
        return dayNum

    def parseHeaderDateString(content_str):
        contentLength = len(content_str)
        if(contentLength <= 0 or content_str == ''):
            return ''

        parseSuccess = False
        finalSucceedDate = '' 
        for i in range(0,contentLength+1):
            subStr = content_str[0:i]
            try:
                d = datetime.datetime.strptime(subStr, "%m/%d")
            except ValueError:
                d = None
            
            if(parseSuccess and d == None):
                return finalSucceedDate
            
            if(d != None):
                finalSucceedDate = subStr
                parseSuccess = True
        return ''
    
    def CheckTextIsDateFormat(text_str):
        try:
            parseDate = parser.parse(text_str)
        except ValueError:
            parseDate = None
        
        return parseDate != None