
class flexMessageManager:

    def getFlexMessage(str_title, str_statusMessage, str_content):
        print("[SNTest] str_content = {0}".format(str_content))
        newContent = str_content.replace("\n", "\\\n")
        print("[SNTest] newContent = {0}".format(newContent))
        return """{
  "type": "bubble",
  "header": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "總長度最多可到十一個字",
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
        "text": "[StatusMassage]",
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
        "text": "1.AAA2.BBB",
        "wrap": true,
        "color": "#666666",
        "size": "sm",
        "flex": 5
      }
    ]
  }
}"""
        # return \
        # f'"{{ \
        # "type": "bubble", \
        # "header": {{ \
        #     "type": "box", \
        #     "layout": "vertical", \
        #     "contents": [ \
        #     {{ \
        #         "type": "text", \
        #         "text": "A", \
        #         "size": "xl", \
        #         "weight": "bold", \
        #         "color": "#587cbe" \
        #     }} \
        #     ] \
        # }}, \
        # "hero": {{ \
        #     "type": "box", \
        #     "layout": "vertical", \
        #     "contents": [ \
        #     {{ \
        #         "type": "text", \
        #         "text": "AAA", \
        #         "offsetStart": "xxl", \
        #         "color": "#5e637e" \
        #     }} \
        #     ] \
        # }}, \
        # "body": {{ \
        #     "type": "box", \
        #     "layout": "vertical", \
        #     "contents": [ \
        #     {{ \
        #         "type": "text", \
        #         "text": "BBB", \
        #         "wrap": true, \
        #         "color": "#666666", \
        #         "size": "sm", \
        #         "flex": 5 \
        #     }} \
        #     ] \
        # }} \
        # }}"'