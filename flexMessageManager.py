
class flexMessageManager:

    def getFlexMessage(str_title, str_statusMessage, str_content):
        print("[SNTest] str_content = {0}".format(str_content))
        newContent = str_content.replace("\n", "\\n")
        print("[SNTest] newContent = {0}".format(newContent))
        return \
        f'"{{ \
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
            ] \
        }}, \
        "hero": {{ \
            "type": "box", \
            "layout": "vertical", \
            "contents": [ \
            {{ \
                "type": "text", \
                "text": "{str_statusMessage}", \
                "offsetStart": "xxl", \
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
                "color": "#666666", \
                "size": "sm", \
                "flex": 5 \
            }} \
            ] \
        }} \
        }}"'