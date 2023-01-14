def getFlexMessage(str_title, str_status_message, str_content):
    new_status_message = str_status_message.replace("\n", "\\n")
    new_content = str_content.replace("\n", "\\n")

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
            "text": "{new_status_message}", \
            "wrap": true, \
            "size": "xxs", \
            "color": "#5e637e", \
            "align": "start" \
        }} \
        ], \
        "spacing": "10px", \
        "paddingStart" : "18px", \
        "paddingEnd" : "18px" \
    }}, \
    "body": {{ \
        "type": "box", \
        "layout": "vertical", \
        "contents": [ \
        {{ \
            "type": "text", \
            "text": "{new_content}", \
            "wrap": true, \
            "size": "xs", \
            "color": "#5e637e", \
            "flex": 5 \
        }} \
        ], \
        "paddingStart": "18px" \
    }} \
    }}'


def GetCommandExplanationFlexMessage(str_title, str_array_command_keys, str_array_formats):
    command_count = len(str_array_command_keys)

    if command_count <= 0:
        return ''

    command_elements = []
    for index in range(0, command_count):
        command_elements.append(
            GetCommandExplanationFlexMessageElement(str_array_command_keys[index], str_array_formats[index]))
        
    command_join_explanation = ",".join(command_elements)

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
            "color": "#B3C2CD", \
            "margin": "none" \
        }}, \
        {{ \
            "type": "box", \
            "layout": "horizontal", \
            "contents": [ \
            {{ \
                "type": "box", \
                "layout": "vertical", \
                "contents": [ \
                {{ \
                    "type": "text", \
                    "text": "指令名稱", \
                    "align": "center", \
                    "size": "sm" \
                }} \
                ], \
                "paddingAll": "5px", \
                "flex": 1 \
            }}, \
            {{ \
                "type": "box", \
                "layout": "vertical", \
                "contents": [ \
                 {{ \
                    "type": "text", \
                    "text": "格式", \
                    "size": "sm" \
                }} \
                ], \
                "paddingAll": "5px", \
                "flex": 3 \
            }} \
            ] \
        }}, \
        {{ \
            "type": "separator", \
            "color": "#B3C2CD", \
            "margin": "none" \
        }}, \
        {command_join_explanation} \
        ], \
        "spacing": "10px" \
    }} \
    }}'


def GetCommandExplanationFlexMessageElement(str_command_key, str_array_format):
    return f'{{ \
        "type": "box", \
        "layout": "horizontal", \
        "contents": [ \
        {{ \
            "type": "box", \
            "layout": "vertical", \
            "contents": [ \
            {{ \
                "type": "text", \
                "align": "center", \
                "text": "{str_command_key}", \
                "size": "xs", \
                "color": "#D41B1B" \
            }} \
            ], \
            "paddingAll": "5px", \
            "flex": 1, \
            "justifyContent": "center" \
        }}, \
        {{ \
            "type": "box", \
            "layout": "vertical", \
            "contents": [ \
            {{ \
                "type": "text", \
                "text": "{str_array_format}", \
                "size": "xxs", \
                "wrap": true \
            }} \
            ], \
            "paddingAll": "5px", \
            "flex": 3, \
            "justifyContent": "center" \
        }} \
        ] \
    }}'
