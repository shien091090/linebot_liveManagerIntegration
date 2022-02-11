
class flexMessageManager:

    FLEX_MESSAGE_FORMAT = \
    """{
    "type": "bubble",
    "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "text",
            "text": "{0}",
            "size": "xl",
            "weight": "bold",
            "color": "#587cbe"
        }
        ]
    },
    "hero": {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "text",
            "text": "{1}",
            "offsetStart": "xxl",
            "color": "#5e637e"
        }
        ]
    },
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "text",
            "text": "{2}",
            "wrap": true,
            "color": "#666666",
            "size": "sm",
            "flex": 5
        }
        ]
    }
    }"""

    def getFlexMessage(str_title, str_statusMessage, str_content):
        print("[SNTest] str_title = {0}, str_statusMessage = {1}, str_content = {2}".format(str_title, str_statusMessage, str_content))
        txt = flexMessageManager.FLEX_MESSAGE_FORMAT.format(str(str_title), str(str_statusMessage), str(str_content))
        print("[SNTest] result Message = {0}".format(txt))
        
        return txt