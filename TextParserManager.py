DEFAULT_SPLIT_CHAR = ' '

TextType_KeyWord = 'KeyWord'
TextType_Number = 'Number'
TextType_SubContent = 'SubContent'
TextType_AdditionalContent = 'AdditionalContent'

class TextParser:

    def GetParseTextResult(self, splitChar_str, rawContent_str):
        self.splitChar = splitChar_str
        self.rawContent = rawContent_str

        splitContents = self.rawContent.split(self.splitChar)

        while splitContents.count(''):
            splitContents.remove('')

        contentLength = len(splitContents)
        if contentLength <= 0 or all(splitContents) == False:
            emptyResult = TextParseResult([], [])
            return emptyResult

        if contentLength == 1:
            result = TextParseResult(splitContents, [TextType_KeyWord])
            return result
        
        isDigitMatchArr = [index for index,value in enumerate(splitContents) if isinstance(value, int) or (isinstance(value, str) and value.isdigit())]
        firstDigitIndex = -1

        if len(isDigitMatchArr) > 0:
            firstDigitIndex = isDigitMatchArr[0]
        
        isContainDigit = firstDigitIndex > 0
        if isContainDigit:
            if contentLength == 2:
                result = TextParseResult(splitContents, [TextType_KeyWord, TextType_Number])
                return result

            isDigitInSecondIndex = firstDigitIndex == 1
            if isDigitInSecondIndex:
                subStr = ' '.join(splitContents[2:contentLength])
                newContents = [splitContents[0], splitContents[1], subStr]
                textTypes = [TextType_KeyWord, TextType_Number, TextType_SubContent]
                result = TextParseResult(newContents, textTypes)
                return result
            else:
                lastIndex = contentLength - 1
                subStr = ' '.join(splitContents[1:firstDigitIndex])

                if lastIndex == firstDigitIndex:
                    newContents = [splitContents[0], subStr, splitContents[firstDigitIndex]]
                    textTypes = [TextType_KeyWord, TextType_SubContent, TextType_Number]
                    result = TextParseResult(newContents, textTypes)
                    return result
                else:
                    additionStr = ' '.join(splitContents[firstDigitIndex + 1:lastIndex + 1])
                    newContents = [splitContents[0], subStr, splitContents[firstDigitIndex], additionStr]
                    textTypes = [TextType_KeyWord, TextType_SubContent, TextType_Number, TextType_AdditionalContent]
                    result = TextParseResult(newContents, textTypes)
                    return result

        else:
            subStr = ' '.join(splitContents[1:contentLength])
            newContents = [splitContents[0], subStr]
            textTypes = [TextType_KeyWord, TextType_SubContent]
            result = TextParseResult(newContents, textTypes)
            return result

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


class TextParseResult:

    def __init__(self, elements_arr, CombineType_arr):
        self.elements = elements_arr
        self.combineTypes = CombineType_arr
    
    def PrintLog(self):
        print(f'Elements = {self.elements}, CombineTypes = {self.combineTypes}')

    def GetElementLength(self):
        return len(self.elements)

    def GetSpecificTextTypeValue(self, textType_TextCombineTypeEnum):
        if self.IsInvalid():
            return ''
        
        if textType_TextCombineTypeEnum in self.combineTypes == False:
            return ''

        if textType_TextCombineTypeEnum not in self.combineTypes:
            return ''

        index = self.combineTypes.index(textType_TextCombineTypeEnum)

        if index >= len(self.elements):
            return ''
        
        return self.elements[index]

    def GetCombineContentByTypeArray(self, textTypes_arr):
        if len(textTypes_arr) <= 0:
            return ''
        
        contentElements = []

        for t in textTypes_arr:
            matchText = self.GetSpecificTextTypeValue(t)
            contentElements.append(matchText)

        while contentElements.count(''):
            contentElements.remove('')

        while contentElements.count(None):
            contentElements.remove(None)

        combineContent = ' '.join(contentElements)
        return combineContent

    def IsKeyWordMatch(self, keyWord_str):
        ownKeyWord = self.GetSpecificTextTypeValue(TextType_KeyWord)
        if ownKeyWord is None:
            return False
        elif ownKeyWord == '':
            return False
        else:
            return keyWord_str == ownKeyWord

    def IsStructureMatch(self, structure_arr):
        if self.IsInvalid():
            return False
        else:
            return self.combineTypes == structure_arr
    
    def IsInvalid(self):
        if self.elements is None or self.combineTypes is None:
            return True
        elif len(self.elements) <= 0 or len(self.combineTypes) <= 0:
            return True
        else:
            return False

# rawContentArr = [
#     ' ',
#     '指令',
#     '指令 ',
#     '指令 1',
#     '指令 A',
#     '指令 A ',
#     ' 指令 A ',
#     '1 abc',
#     '1 abc aa',
#     '1 abc aa 5 aaw',
#     ' 1 abc',
#     ' 1 abasd 1',
#     '1 atttt 5',
#     '指令 1 A',
#     ' 指令 1 A',
#     '指令 A 1',
#     '指令 A 1 B',
#     '指令  A 1 B',
#     '指令 Aqweq 15 Baa',
#     '指令 Aqweq 15 Baa yyy',
#     '指令 88 15 Baa yyy',
#     '指令 A 1 ',
#     '指令 AA BB CC 2',
#     '5 AA BB CC 2']

# findArr = [TextType_SubContent, TextType_Number]

# for c in rawContentArr:
#     print(f'input : "{c}"')

#     textParser = TextParser()
#     result = textParser.GetParseTextResult(DEFAULT_SPLIT_CHAR, c)
#     result.PrintLog()
#     print(result.GetCombineContentByTypeArray(findArr))