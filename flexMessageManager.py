
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

    def GetCommandExplanationFlexMessage(str_title, strArray_commandKeys, strArray_formats):
        commandCount = len(strArray_commandKeys)

        if commandCount <= 0:
            return ''

        commandElements = []
        for index in range(0, commandCount):
            commandElements.append(flexMessageManager.GetCommandExplanationFlexMessageElement(strArray_commandKeys[index], strArray_formats[index]))

        commandJoinExplanation = ",".join(commandElements)

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
                    "type": "separator", \
                    "color": "#B3C2CD" \
                }}, \
                {{ \
                    "type": "box", \
                    "layout": "vertical", \
                    "contents": [ \
                     {{ \
                        "type": "text", \
                        "text": "格式", \
                        "align": "center", \
                        "size": "sm" \
                    }} \
                    ], \
                    "paddingAll": "5px", \
                    "flex": 3 \
                }} \
                ] \
            }}, \
            {commandJoinExplanation} \
            ], \
            "spacing": "10px" \
        }} \
        }}'

    def GetCommandExplanationFlexMessageElement(str_commandKey, strArray_format):
        return f'{{ \
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
                    "align": "center", \
                    "text": "{str_commandKey}", \
                    "size": "xs" \
                }} \
                ], \
                "paddingAll": "5px", \
                "flex": 1, \
                "justifyContent": "center" \
            }}, \
            {{ \
                "type": "separator", \
                "color": "#B3C2CD" \
            }}, \
            {{ \
                "type": "box", \
                "layout": "vertical", \
                "contents": [ \
                {{ \
                    "type": "text", \
                    "text": "{strArray_format}", \
                    "align": "center", \
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