import dateManager

DEFAULT_SPLIT_CHAR = ' '

TextStructureType_Content = 'ContentType'
TextStructureType_Number = 'NumberType'
TextStructureType_Date = 'DateType'

TextType_KeyWord = 'KeyWord'
TextType_Number = 'Number'
TextType_SubContent = 'SubContent'
TextType_AdditionalContent = 'AdditionalContent'
TextType_SubNumber = 'SubNumber'
TextType_Date = 'Date'

class TextParser:

    def __init__(self, splitChar_str, rawContent_str):
        self.splitChar = splitChar_str
        self.rawContent = rawContent_str
        self.splitContents = []
        self.splitContentsParseTypeData = []
        self.parsedIndex = 0
    
    def ParseTextBySpecificStructure(self, textStructureType_arr):
        if textStructureType_arr.count(TextStructureType_Content) > 3:
            print(f"[SNTest] TextStructureType = {TextStructureType_Content} is Over Limit(3) !")
        elif textStructureType_arr.count(TextStructureType_Number) > 2:
            print(f"[SNTest] TextStructureType = {TextStructureType_Number} is Over Limit(2) !")
        elif textStructureType_arr.count(TextStructureType_Date) > 2:
            print(f"[SNTest] TextStructureType = {TextStructureType_Date} is Over Limit(1) !")

        self.splitContentsParseTypeData = []
        self.splitContents = self.rawContent.split(self.splitChar)
        self.parsedIndex = 0

        while self.splitContents.count(''):
            self.splitContents.remove('')

        splitContentsCount = len(self.splitContents)
        self.splitContentsParseTypeData = ['']*splitContentsCount
        specificStructureCount = len(textStructureType_arr)

        if specificStructureCount <= 0 or splitContentsCount < specificStructureCount:
            return None
        
        for textStructureType in textStructureType_arr:
            isParseSuccess = self.ParseContentToStructureType(textStructureType)
            if isParseSuccess == False:
                return None
        
        print(f"[SNTest] [Parse Structure] splitContents = {self.splitContents}, splitTypes = {self.splitContentsParseTypeData}")
        return self.RemoveRecordDataAndGetParseResult()

    def RemoveRecordDataAndGetParseResult(self):
        if  len(self.splitContents) <= 0 or \
            len(self.splitContentsParseTypeData) <= 0 or\
            len(self.splitContents) != len(self.splitContentsParseTypeData):
            return None
        
        tempIndex = -1
        tempContentArr = []
        tempTextStructureTypeArr = []
        canCombineText = False

        while len(self.splitContentsParseTypeData) > 0:
            parseTypeElement = self.splitContentsParseTypeData.pop(0)
            splitContent = self.splitContents.pop(0)

            if  parseTypeElement == TextStructureType_Number or \
                parseTypeElement == TextStructureType_Date or \
                parseTypeElement == TextStructureType_Content:
                tempTextStructureTypeArr.append(parseTypeElement)
                tempContentArr.append(splitContent)
                tempIndex += 1
                canCombineText = parseTypeElement == TextStructureType_Content
            else:
                if tempIndex < 0:
                    return None
                else:
                    if canCombineText:
                        tempContentArr[tempIndex] += f" {splitContent}"
                    else:
                        return None
                    
        
        textTypeArr = []
        numberTypeNum = 0
        contentTypeNum = 0
        dateTypeNum = 0
        for index in range(len(tempTextStructureTypeArr)):
            tempTextStructureType = tempTextStructureTypeArr[index]
            if tempTextStructureType == TextStructureType_Number:
                if numberTypeNum == 0:
                    textTypeArr.append(TextType_Number)
                elif numberTypeNum == 1:
                    textTypeArr.append(TextType_SubNumber)
                numberTypeNum += 1

            elif tempTextStructureType == TextStructureType_Content:
                if contentTypeNum == 0:
                    textTypeArr.append(TextType_KeyWord)
                elif contentTypeNum == 1:
                    textTypeArr.append(TextType_SubContent)
                elif contentTypeNum == 2:
                    textTypeArr.append(TextType_AdditionalContent)
                contentTypeNum += 1

            elif tempTextStructureType == TextStructureType_Date:
                if dateTypeNum == 0:
                    textTypeArr.append(TextType_Date)
                dateTypeNum += 1
        
        result = TextParseResult(tempContentArr, textTypeArr)
        return result
    
    def ParseContentToStructureType(self, targetStructureType):
        isResultSuccess = False
        if len(self.splitContentsParseTypeData) <= 0 or len(self.splitContentsParseTypeData) != len(self.splitContents):
            return isResultSuccess

        if self.parsedIndex >= len(self.splitContents):
            return isResultSuccess

        for index in range(self.parsedIndex, len(self.splitContents)):
            contentElement = self.splitContents[index]
            isParseSuccess = \
                targetStructureType == TextStructureType_Content or\
                (targetStructureType == TextStructureType_Number and TextParser.CanValueConvertNumber(contentElement)) or\
                (targetStructureType == TextStructureType_Date and TextParser.CanValueConvertDate(contentElement))

            if isParseSuccess:
                isResultSuccess = True
                self.splitContentsParseTypeData[index] = targetStructureType
                self.parsedIndex = index
                break
        
        self.parsedIndex += 1
        return isResultSuccess
    
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
        
        isDigitMatchArr = [index for index,value in enumerate(splitContents) if TextParser.CanValueConvertNumberOrDate(value)]
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
    
    def CanValueConvertNumber(value_var):
        if isinstance(value_var, int):
            return True
        elif isinstance(value_var, str) and value_var.isdigit():
            return True
        else:
            return False
    
    def CanValueConvertDate(value_var):
        if isinstance(value_var, str) and dateManager.dateManager.CheckTextIsDateFormat(value_var):
            return True
        else:
            return False

class TextParseResult:

    def __init__(self, elements_arr, combineTypes_arr):
        self.elements = elements_arr
        self.combineTypes = combineTypes_arr
    
    def PrintLog(self):
        print(f'[SNTest] TextParserResult Elements = {self.elements}, CombineTypes = {self.combineTypes}')

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

    def IsStructureElementAllValid(self, textTypes_arr):
        if len(textTypes_arr) <= 0:
            return False

        isAllElementValid = True
        for textType in textTypes_arr:
            elementValue = self.GetSpecificTextTypeValue(textType)
            isAllElementValid &= elementValue is not None and elementValue != ''
        
        return isAllElementValid
    
    def IsInvalid(self):
        if self.elements is None or self.combineTypes is None:
            return True
        elif len(self.elements) <= 0 or len(self.combineTypes) <= 0:
            return True
        else:
            return False

# inputRawContent = '修改 123 a  11aawqw 1'
# textParser = TextParser(' ', inputRawContent)
# parseTypeArr = [TextStructureType_Content, TextStructureType_Number, TextStructureType_Content]

# print(f'[SNTest] input rawContent = {inputRawContent}')
# print(f'[SNTest] input ParseTypeArr = {parseTypeArr}')

# result = textParser.ParseTextBySpecificStructure(parseTypeArr)

# if result is None:
#     print('result = None')
# else:
#     result.PrintLog()

# parseTypeArr = [TextStructureType_Content, TextStructureType_Number, TextStructureType_Content, TextStructureType_Content]

# print(f'[SNTest] input rawContent = {inputRawContent}')
# print(f'[SNTest] input ParseTypeArr = {parseTypeArr}')

# result = textParser.ParseTextBySpecificStructure(parseTypeArr)

# if result is None:
#     print('result = None')
# else:
#     result.PrintLog()