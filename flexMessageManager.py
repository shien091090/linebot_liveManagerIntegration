
class flexMessageManager:

    def getFlexMessage(str_title, str_statusMessage, str_content):
        newStatusMessage = str_statusMessage.replace("\n", "\\n")
        newContent = str_content.replace("\n", "\\n")

        return f'{{ \
        "type": "bubble", \
        "header": {{ \
            "type": "box", \
            "layout": "vertical", \
            "contents": [ \
            {{ \
                "type": "text", \
                "text": "{str_title}", \
                "size": "xl", \
                "weight": "bold", \
                "color": "#587cbe" \
            }} \
            ], \
            "paddingTop": "15px", \
            "paddingBottom": "13px" \
        }}, \
        "hero": {{ \
            "type": "box", \
            "layout": "vertical", \
            "contents": [ \
            {{ \
                "type": "separator", \
                "color": "#B3C2CD" \
            }}, \
            {{ \
                "type": "text", \
                "text": "{newStatusMessage}", \
                "wrap": true, \
                "offsetStart": "18px", \
                "size": "xxs", \
                "color": "#5e637e", \
                "align": "start" \
            }} \
            ], \
            "spacing": "10px" \
        }}, \
        "body": {{ \
            "type": "box", \
            "layout": "vertical", \
            "contents": [ \
            {{ \
                "type": "text", \
                "text": "{newContent}", \
                "wrap": true, \
                "size": "xs", \
                "color": "#5e637e", \
                "flex": 5 \
            }} \
            ], \
            "paddingStart": "18px" \
        }} \
        }}'