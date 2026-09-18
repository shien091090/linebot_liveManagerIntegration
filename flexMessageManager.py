import json


def _escape_json(text):
    # GAS 字表分頁裡的換行是以「字面的反斜線 + n」兩個字元存放, 而不是真的換行字元,
    # 所以要先還原成真正的換行, 再交給 json.dumps 做跳脫。
    # (GAS 程式碼裡直接寫的 '\n' 本來就是真換行, 不受這一步影響)
    normalized = str(text).replace('\\n', '\n')

    # json.dumps 會一併處理反斜線、雙引號、換行與控制字元,
    # [1:-1] 去掉外層引號以便嵌進下面的字串模板。
    # 只 replace 換行的話, GAS 例外訊息裡的雙引號會讓整段 flex JSON 解析失敗,
    # 結果又變成 LINE 完全不回訊息
    return json.dumps(normalized, ensure_ascii=False)[1:-1]


def getFlexMessage(str_title, str_status_message, str_content):
    new_title = _escape_json(str_title)
    new_status_message = _escape_json(str_status_message)
    new_content = _escape_json(str_content)

    return f'{{ \
    "type": "bubble", \
    "header": {{ \
        "type": "box", \
        "layout": "vertical", \
        "contents": [ \
        {{ \
            "type": "text", \
            "text": "{new_title}", \
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


def getMemoFlexMessage(str_title, str_status_message, colored_items):
    new_status_message = _escape_json(str_status_message)

    if colored_items:
        elements = []
        for (text, color) in colored_items:
            elements.append(
                f'{{ "type": "text", "text": "{_escape_json(text)}", "wrap": true, "size": "xs", "color": "{color}" }}'
            )
        body_contents = ','.join(elements)
    else:
        body_contents = '{ "type": "text", "text": " ", "size": "xs" }'

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
        "contents": [{body_contents}], \
        "paddingStart": "18px" \
    }} \
    }}'


def getUrlButtonFlexMessage(str_title, str_status_message, url):
    new_status_message = _escape_json(str_status_message)
    escaped_url = _escape_json(url)
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
            "type": "button", \
            "action": {{ \
                "type": "uri", \
                "label": "開啟頁面", \
                "uri": "{escaped_url}" \
            }}, \
            "style": "primary", \
            "color": "#587cbe", \
            "height": "sm" \
        }} \
        ], \
        "paddingAll": "16px" \
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
        "spacing": "xs" \
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
                "color": "#D41B1B", \
                "wrap": true \
            }} \
            ], \
            "paddingAll": "3px", \
            "flex": 2, \
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
            "paddingAll": "3px", \
            "flex": 4, \
            "justifyContent": "center" \
        }} \
        ] \
    }}'
