class TextParser:

    def isContainKeyWord(parent_str, find_str):
        index = parent_str.find(find_str)
        isContain = index != 0
        return isContain

    def getSubStringByKeyWord(parent_str, find_str):
        index = parent_str.find(find_str)
        if index != 0:
            return ''
        else:
            subStr = parent_str.replace(find_str, '')
            return subStr

    def getSubStringByKeyWordAndNumber(parent_str, find_str):
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

    def getNumberByKeyWordAndNumber(parent_str, find_str):
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
            return -3
        parseNum = int(subStr)
        return parseNum

    def checkHeaderByKeyWord(parent_str, find_str):
        index = parent_str.find(find_str)
        if index != 0:
            return False
        else:
            return True
