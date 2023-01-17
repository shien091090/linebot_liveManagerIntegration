import unittest
from parameterized import parameterized

import lineActionInfo
import manage

INPUT_FLAW_TYPE_PREFIX_BLANK = 'prefix_blank'
INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK = 'prefix_multi_blank'
INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN = 'multi_blank_between_command_part'
INPUT_FLAW_TYPE_SUFFIX_BLANK = 'suffix_blank'


# [How To Use]
# Terminal : python -m unittest LiveManagerIntegrationTest
def GetDecoratedCommand(input_flaw_type, origin_input_command):
    input_command = origin_input_command
    if input_flaw_type == INPUT_FLAW_TYPE_PREFIX_BLANK:
        input_command = ' ' + input_command
    elif input_flaw_type == INPUT_FLAW_TYPE_SUFFIX_BLANK:
        input_command = input_command + ' '
    elif input_flaw_type == INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK:
        input_command = '   ' + input_command
    elif input_flaw_type == INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN:
        input_command_parts = input_command.split(' ')
        if len(input_command_parts) > 0:
            input_command = '   '.join(input_command_parts)

    return input_command


class MyTestCase(unittest.TestCase):
    def test_send_empty_message(self):
        self.GivenCommand('')
        self.RequestShouldBeNone(True)

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_send_not_exist_command(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, 'ABC')
        self.RequestShouldBeNone(True)
        self.GivenCommandWithFlawType(input_flaw_type, 'ABC 123')
        self.RequestShouldBeNone(True)

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK
    ])
    def test_request_command_list(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '指令')
        self.RequestTitleShouldBe('指令列表')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_BYPASS)
        self.RequestShouldBeNone(False)

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK
    ])
    def test_request_add_memo_command_and_no_any_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增')
        self.RequestResultShouldBeFormatError('新增待辦事項')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_memo_command(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增 小7取貨')
        self.RequestTitleShouldBe('新增待辦事項')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_MEMO_ADD)
        self.RequestSubContentShouldBe('小7取貨')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_memo_command_and_input_extra_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增 5/1 1500 看電影')
        self.RequestTitleShouldBe('新增待辦事項')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_MEMO_ADD)
        self.RequestSubContentShouldBe('5/1 1500 看電影')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
    ])
    def test_request_remove_memo_command_and_no_any_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除')
        self.RequestResultShouldBeFormatError('刪除待辦事項')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_remove_memo_command_and_input_sub_content(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除 A')
        self.RequestResultShouldBeFormatError('刪除待辦事項')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_remove_memo_command(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除 9')
        self.RequestTitleShouldBe('刪除待辦事項')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_MEMO_REMOVE)
        self.RequestNumberShouldBe('9')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_remove_memo_command_and_input_extra_number(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除 3 4')
        self.RequestResultShouldBeFormatError('刪除待辦事項')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_remove_memo_command_and_input_extra_sub_content(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除 5 abc')
        self.RequestResultShouldBeFormatError('刪除待辦事項')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK
    ])
    def test_request_modify_memo_command_and_no_any_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改')
        self.RequestResultShouldBeFormatError('修改待辦事項')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_memo_command_and_input_deficient_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改 2')
        self.RequestResultShouldBeFormatError('修改待辦事項')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_memo_command_and_input_wrong_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改 abc')
        self.RequestResultShouldBeFormatError('修改待辦事項')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_memo_command_and_input_upside_down_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改 LearnEnglish 3')
        self.RequestResultShouldBeFormatError('修改待辦事項')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_memo_command_and_input_zero_index(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改 0 LearnEnglish')
        self.RequestResultShouldBeFormatError('修改待辦事項')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_memo_command(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改 3 LearnEnglish')
        self.RequestTitleShouldBe('修改待辦事項')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_MEMO_MODIFY)
        self.RequestNumberShouldBe('3')
        self.RequestSubContentShouldBe('LearnEnglish')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_memo_command_and_sub_content_with_blank(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改 5 LearnEnglish In Library')
        self.RequestTitleShouldBe('修改待辦事項')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_MEMO_MODIFY)
        self.RequestNumberShouldBe('5')
        self.RequestSubContentShouldBe('LearnEnglish In Library')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_memo_command_and_sub_content_is_digit(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改 1 176235')
        self.RequestTitleShouldBe('修改待辦事項')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_MEMO_MODIFY)
        self.RequestNumberShouldBe('1')
        self.RequestSubContentShouldBe('176235')

    def RequestSubContentShouldBe(self, expected_sub_content):
        self.assertEqual(expected_sub_content, self.req_info.requestParam['subContent'])

    def RequestActionShouldBe(self, expected_action):
        self.assertEqual(expected_action, self.req_info.requestParam['action'])

    def RequestNumberShouldBe(self, expected_number):
        self.assertEqual(expected_number, self.req_info.requestParam['number'])

    def RequestResultShouldBeFormatError(self, expected_request_title):
        self.RequestTitleShouldBe(expected_request_title)
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_BYPASS)
        self.assertTrue('格式錯誤' in self.req_info.statusMsg)
        self.RequestShouldBeNone(False)

    def RequestShouldBeNone(self, expected_is_none):
        if expected_is_none:
            self.assertIsNone(self.req_info)
        else:
            self.assertIsNotNone(self.req_info)

    def RequestTypeShouldBe(self, expected_request_type):
        self.assertEqual(expected_request_type, self.req_info.requestType)

    def RequestTitleShouldBe(self, expected_title):
        self.assertEqual(expected_title, self.req_info.title)

    def GivenCommand(self, input_command):
        input_command = GetDecoratedCommand('', input_command)
        self.reply_flex_message, self.req_info = manage.ParseRequestInfo(input_command)

    def GivenCommandWithFlawType(self, input_flaw_type, input_command):
        input_command = GetDecoratedCommand(input_flaw_type, input_command)
        print(f'[SNTest] input_command = {input_command}')
        self.reply_flex_message, self.req_info = manage.ParseRequestInfo(input_command)


if __name__ == '__main__':
    unittest.main()
