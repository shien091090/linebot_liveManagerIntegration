class TextParser:

    def isContainKeyWord(parent_str, find_str):
        index = parent_str.find(find_str)
        isContain = index != 0
        return isContain

    def returnSubStringAfterExtractKeyword(parent_str, find_str):
        index = parent_str.find(find_str)
        if index != 0:
            return ''
        else:
            subStr = parent_str.replace(find_str, '')
            return subStr

    def returnSubStringAfterExtractKeywordAndNumber(parent_str, find_str):
        index = parent_str.find(find_str)
        if index != 0:
            return ''
        newContent = parent_str.replace(find_str, '')
        spaceIndex = newContent.find(' ')
        if spaceIndex < 0:
            return ''
        subStr = newContent[0:spaceIndex]
        isNum = subStr.isdigit()
        if isNum == False:
            return ''
        resultSubStr = newContent.replace(subStr + ' ', '')
        return resultSubStr

    def returnNumberAfterExtractKeyword(parent_str, find_str):
        index = parent_str.find(find_str)
        if index != 0:
            return -1
        newContent = parent_str.replace(find_str, '')
        spaceIndex = newContent.find(' ')
        if spaceIndex < 0:
            spaceIndex = len(newContent)
        subStr = newContent[0:spaceIndex]
        isNum = subStr.isdigit()
        if isNum == False:
            return -1
        parseNum = int(subStr)
        return parseNum

    def returnNumberAndSubStringAfterExtractKeyword(parent_str, find_str):
        index = parent_str.find(find_str)
        if index != 0:
            return ''
        newContent = parent_str.replace(find_str, '')
        spaceIndex = newContent.find(' ')
        if spaceIndex < 0:
            return ''
        subStr = newContent[0:spaceIndex]
        isNum = subStr.isdigit()
        if isNum == False:
            return ''
        return newContent

    def checkTextBeginIsKeyWord(parent_str, find_str):
        index = parent_str.find(find_str)
        if index != 0:
            return False
        else:
            return True
