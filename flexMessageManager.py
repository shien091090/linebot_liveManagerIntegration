
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
                "size": "lg", \
                "weight": "bold", \
                "color": "#587cbe" \
            }} \
            ] \
        }}, \
        "hero": {{ \
            "type": "box", \
            "layout": "vertical", \
            "contents": [ \
            {{ \
                "type": "text", \
                "text": "{newStatusMessage}", \
                "wrap": true, \
                "offsetStart": "20px", \
                "size": "xs", \
                "color": "#5e637e" \
            }} \
            ] \
        }}, \
        "body": {{ \
            "type": "box", \
            "layout": "vertical", \
            "contents": [ \
            {{ \
                "type": "text", \
                "text": "{newContent}", \
                "wrap": true, \
                "size": "md", \
                "color": "#666666", \
                "flex": 5 \
            }} \
            ] \
        }} \
        }}'