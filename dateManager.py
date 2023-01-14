import datetime
from dateutil import parser


def getCurrentTimeText():
    tz_taiwan = datetime.timezone(datetime.timedelta(hours=+8))
    local_date = datetime.datetime.today().astimezone(tz_taiwan)
    date_str = local_date.strftime("%Y/%m/%d_%H:%M:%S")
    return date_str


def getTodayDayNumber():
    tz_taiwan = datetime.timezone(datetime.timedelta(hours=+8))
    local_date = datetime.datetime.today().astimezone(tz_taiwan)
    day_num = local_date.day
    return day_num


def parseHeaderDateString(content_str):
    content_length = len(content_str)
    if content_length <= 0 or content_str == '':
        return ''

    parse_success = False
    final_succeed_date = ''
    for i in range(0, content_length + 1):
        sub_str = content_str[0:i]
        try:
            d = datetime.datetime.strptime(sub_str, "%m/%d")
        except ValueError:
            d = None

        if parse_success and d is None:
            return final_succeed_date

        if d is not None:
            final_succeed_date = sub_str
            parse_success = True
    return ''


def CheckTextIsDateFormat(text_str):
    try:
        parse_date = parser.parse(text_str)
    except ValueError:
        parse_date = None

    return parse_date is not None
