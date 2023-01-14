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

    def __init__(self, split_char_str, raw_content_str):
        self.splitChar = split_char_str
        self.rawContent = raw_content_str
        self.splitContents = []
        self.splitContentsParseTypeData = []
        self.parsedIndex = 0

    def ParseTextBySpecificStructure(self, text_structure_type_arr):
        if text_structure_type_arr.count(TextStructureType_Content) > 3:
            print(f"[SNTest] TextStructureType = {TextStructureType_Content} is Over Limit(3) !")
        elif text_structure_type_arr.count(TextStructureType_Number) > 2:
            print(f"[SNTest] TextStructureType = {TextStructureType_Number} is Over Limit(2) !")
        elif text_structure_type_arr.count(TextStructureType_Date) > 2:
            print(f"[SNTest] TextStructureType = {TextStructureType_Date} is Over Limit(1) !")

        self.splitContentsParseTypeData = []
        self.splitContents = self.rawContent.split(self.splitChar)
        self.parsedIndex = 0

        while self.splitContents.count(''):
            self.splitContents.remove('')

        split_contents_count = len(self.splitContents)
        self.splitContentsParseTypeData = [''] * split_contents_count
        specific_structure_count = len(text_structure_type_arr)

        if specific_structure_count <= 0 or split_contents_count < specific_structure_count:
            return None

        for textStructureType in text_structure_type_arr:
            is_parse_success = self.ParseContentToStructureType(textStructureType)
            if not is_parse_success:
                return None

        print(
            f"[SNTest] [Parse Structure] splitContents = {self.splitContents}, splitTypes = {self.splitContentsParseTypeData}")
        return self.RemoveRecordDataAndGetParseResult()

    def RemoveRecordDataAndGetParseResult(self):
        if len(self.splitContents) <= 0 or \
                len(self.splitContentsParseTypeData) <= 0 or \
                len(self.splitContents) != len(self.splitContentsParseTypeData):
            return None

        temp_index = -1
        temp_content_arr = []
        temp_text_structure_type_arr = []
        can_combine_text = False

        while len(self.splitContentsParseTypeData) > 0:
            parse_type_element = self.splitContentsParseTypeData.pop(0)
            split_content = self.splitContents.pop(0)

            if parse_type_element == TextStructureType_Number or \
                    parse_type_element == TextStructureType_Date or \
                    parse_type_element == TextStructureType_Content:
                temp_text_structure_type_arr.append(parse_type_element)
                temp_content_arr.append(split_content)
                temp_index += 1
                can_combine_text = parse_type_element == TextStructureType_Content
            else:
                if temp_index < 0:
                    return None
                else:
                    if can_combine_text:
                        temp_content_arr[temp_index] += f" {split_content}"
                    else:
                        return None

        text_type_arr = []
        number_type_num = 0
        content_type_num = 0
        date_type_num = 0
        for index in range(len(temp_text_structure_type_arr)):
            temp_text_structure_type = temp_text_structure_type_arr[index]
            if temp_text_structure_type == TextStructureType_Number:
                if number_type_num == 0:
                    text_type_arr.append(TextType_Number)
                elif number_type_num == 1:
                    text_type_arr.append(TextType_SubNumber)
                number_type_num += 1

            elif temp_text_structure_type == TextStructureType_Content:
                if content_type_num == 0:
                    text_type_arr.append(TextType_KeyWord)
                elif content_type_num == 1:
                    text_type_arr.append(TextType_SubContent)
                elif content_type_num == 2:
                    text_type_arr.append(TextType_AdditionalContent)
                content_type_num += 1

            elif temp_text_structure_type == TextStructureType_Date:
                if date_type_num == 0:
                    text_type_arr.append(TextType_Date)
                date_type_num += 1

        result = TextParseResult(temp_content_arr, text_type_arr)
        return result

    def ParseContentToStructureType(self, target_structure_type):
        is_result_success = False
        if len(self.splitContentsParseTypeData) <= 0 or len(self.splitContentsParseTypeData) != len(self.splitContents):
            return is_result_success

        if self.parsedIndex >= len(self.splitContents):
            return is_result_success

        for index in range(self.parsedIndex, len(self.splitContents)):
            content_element = self.splitContents[index]
            is_parse_success = \
                target_structure_type == TextStructureType_Content or \
                (target_structure_type == TextStructureType_Number and TextParser.CanValueConvertNumber(
                    content_element)) or \
                (target_structure_type == TextStructureType_Date and TextParser.CanValueConvertDate(content_element))

            if is_parse_success:
                is_result_success = True
                self.splitContentsParseTypeData[index] = target_structure_type
                self.parsedIndex = index
                break

        self.parsedIndex += 1
        return is_result_success

    def CanValueConvertNumber(value_var):
        if isinstance(value_var, int):
            return True
        elif isinstance(value_var, str) and value_var.isdigit():
            return True
        else:
            return False

    def CanValueConvertDate(value_var):
        if isinstance(value_var, str) and dateManager.CheckTextIsDateFormat(value_var):
            return True
        else:
            return False


class TextParseResult:

    def __init__(self, elements_arr, combine_types_arr):
        self.elements = elements_arr
        self.combineTypes = combine_types_arr

    def PrintLog(self):
        print(f'[SNTest] TextParserResult Elements = {self.elements}, CombineTypes = {self.combineTypes}')

    def GetSpecificTextTypeValue(self, text_type_text_combine_type_enum):
        if self.IsInvalid():
            return ''

        if text_type_text_combine_type_enum in self.combineTypes is False:
            return ''

        if text_type_text_combine_type_enum not in self.combineTypes:
            return ''

        index = self.combineTypes.index(text_type_text_combine_type_enum)

        if index >= len(self.elements):
            return ''

        return self.elements[index]

    def IsKeyWordMatch(self, key_word_str):
        own_key_word = self.GetSpecificTextTypeValue(TextType_KeyWord)
        if own_key_word is None:
            return False
        elif own_key_word == '':
            return False
        else:
            return key_word_str == own_key_word

    def IsStructureMatch(self, structure_arr):
        if self.IsInvalid():
            return False
        else:
            return self.combineTypes == structure_arr

    def IsStructureElementAllValid(self, text_types_arr):
        if len(text_types_arr) <= 0:
            return False

        is_all_element_valid = True
        for textType in text_types_arr:
            element_value = self.GetSpecificTextTypeValue(textType)
            is_all_element_valid &= element_value is not None and element_value != ''

        return is_all_element_valid

    def IsInvalid(self):
        if self.elements is None or self.combineTypes is None:
            return True
        elif len(self.elements) <= 0 or len(self.combineTypes) <= 0:
            return True
        else:
            return False
