
class flexMessageManager:

    def getFlexMessage(str_title, str_statusMessage, str_content):
        return \
        """{
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": "總長度最多可到",
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
                "text": "1.AAA\n2.BBB",
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
        #         "text": "{str_title}", \
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
        #         "text": "{str_statusMessage}", \
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
        #         "text": "{str_content}", \
        #         "wrap": true, \
        #         "color": "#666666", \
        #         "size": "sm", \
        #         "flex": 5 \
        #     }} \
        #     ] \
        # }} \
        # }}"'