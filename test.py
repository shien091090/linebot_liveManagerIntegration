import unittest
from parameterized import parameterized

import keyWordSetting
import lineActionInfo
import manage

INPUT_FLAW_TYPE_PREFIX_BLANK = 'prefix_blank'
INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK = 'prefix_multi_blank'
INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN = 'multi_blank_between_command_part'
INPUT_FLAW_TYPE_SUFFIX_BLANK = 'suffix_blank'


# [How To Use]
# Terminal : python -m unittest test
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
    def test_request_remove_memo_command_and_input_number_is_zero(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除 0')
        self.RequestTitleShouldBe('刪除待辦事項')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_MEMO_REMOVE)
        self.RequestNumberShouldBe('0')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_remove_memo_command_and_input_number_is_smaller_then_zero(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除 -6')
        self.RequestResultShouldBeFormatError('刪除待辦事項')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_remove_memo_command_and_input_formatted_number(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除 07')
        self.RequestTitleShouldBe('刪除待辦事項')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_MEMO_REMOVE)
        self.RequestNumberShouldBe('7')

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
        self.RequestTitleShouldBe('修改待辦事項')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_MEMO_MODIFY)
        self.RequestNumberShouldBe('0')
        self.RequestSubContentShouldBe('LearnEnglish')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_memo_command_and_input_smaller_then_zero_index(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改 -1 LearnEnglish')
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
    def test_request_modify_memo_command_and_input_formatted_number_index(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改 08 LearnEnglish')
        self.RequestTitleShouldBe('修改待辦事項')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_MEMO_MODIFY)
        self.RequestNumberShouldBe('8')
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

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK
    ])
    def test_request_get_memo_command(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '確認待辦')
        self.RequestTitleShouldBe('確認待辦事項')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_MEMO_GET)

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_get_memo_command_and_input_unnecessary_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '確認待辦 A')
        self.RequestTitleShouldBe('確認待辦事項')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_MEMO_GET)

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK
    ])
    def test_request_add_schedule_command_and_no_any_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程')
        self.RequestResultShouldBeFormatError('新增週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command_and_only_input_period(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每月')
        self.RequestResultShouldBeFormatError('新增週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command_and_only_input_period_and_number(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每週 1')
        self.RequestResultShouldBeFormatError('新增週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每月 15 打掃家裡')
        self.RequestTitleShouldBe('新增週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_ADD)
        self.RequestSubContentShouldBe('每月')
        self.RequestNumberShouldBe('15')
        self.RequestAdditionalContentShouldBe('打掃家裡')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command_and_input_number_is_zero(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每月 0 打掃家裡')
        self.RequestResultShouldBeFormatError('新增週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command_and_no_input_number(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每月 利卡驅蟲藥')
        self.RequestResultShouldBeFormatError('新增週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command_and_no_input_wrong_period(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每年 5 清理濾網')
        self.RequestResultShouldBeFormatError('新增週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command_and_no_input_wrong_period_and_deficient_number(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每年 清理濾網')
        self.RequestResultShouldBeFormatError('新增週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command_and_period_is_daily_with_unnecessary_number(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每天 1 吃藥')
        self.RequestTitleShouldBe('新增週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_ADD)
        self.RequestSubContentShouldBe('每天')
        self.RequestNumberShouldBe('0')
        self.RequestAdditionalContentShouldBe('1 吃藥')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command_and_period_is_daily(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每天 吃藥')
        self.RequestTitleShouldBe('新增週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_ADD)
        self.RequestSubContentShouldBe('每天')
        self.RequestNumberShouldBe('0')
        self.RequestAdditionalContentShouldBe('吃藥')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command_and_additional_content_with_blank(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每月 3 1300 打掃家裡')
        self.RequestTitleShouldBe('新增週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_ADD)
        self.RequestSubContentShouldBe('每月')
        self.RequestNumberShouldBe('3')
        self.RequestAdditionalContentShouldBe('1300 打掃家裡')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command_and_input_multiple_period_key(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每月 每週 5 拖地')
        self.RequestResultShouldBeFormatError('新增週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command_and_period_is_daily_and_additional_content_with_blank(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每天 0030 波比工作 睡覺')
        self.RequestTitleShouldBe('新增週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_ADD)
        self.RequestSubContentShouldBe('每天')
        self.RequestNumberShouldBe('0')
        self.RequestAdditionalContentShouldBe('0030 波比工作 睡覺')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_add_schedule_command_and_additional_content_is_digits_with_blank(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '新增行程 每週 3 10001 404')
        self.RequestTitleShouldBe('新增週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_ADD)
        self.RequestSubContentShouldBe('每週')
        self.RequestNumberShouldBe('3')
        self.RequestAdditionalContentShouldBe('10001 404')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK
    ])
    def test_request_remove_schedule_command_and_no_any_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除行程')
        self.RequestResultShouldBeFormatError('刪除週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_remove_schedule_command_and_input_number_is_zero(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除行程 0')
        self.RequestTitleShouldBe('刪除週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_REMOVE)
        self.RequestNumberShouldBe('0')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_remove_schedule_command_and_input_number_is_smaller_than_zero(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除行程 -1')
        self.RequestResultShouldBeFormatError('刪除週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_remove_schedule_command_and_input_number_is_smaller_than_zero(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除行程 3')
        self.RequestTitleShouldBe('刪除週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_REMOVE)
        self.RequestNumberShouldBe('3')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_remove_schedule_command_and_input_is_not_number(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除行程 a')
        self.RequestResultShouldBeFormatError('刪除週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_remove_schedule_command_and_input_multiple_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除行程 1 a')
        self.RequestResultShouldBeFormatError('刪除週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_remove_schedule_command_and_input_formatted_number(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '刪除行程 05')
        self.RequestTitleShouldBe('刪除週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_REMOVE)
        self.RequestNumberShouldBe('5')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK
    ])
    def test_request_modify_schedule_command_and_no_any_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程')
        self.RequestResultShouldBeFormatError('修改週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_input_number_only(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 0')
        self.RequestResultShouldBeFormatError('修改週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_input_number_and_additional_content_only(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 1 繳網路費')
        self.RequestResultShouldBeFormatError('修改週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_not_input_additional_content(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 1 每月 1')
        self.RequestResultShouldBeFormatError('修改週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_period_key_is_monthly(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 1 每月 1 打醬油')
        self.RequestTitleShouldBe('修改週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_MODIFY)
        self.RequestNumberShouldBe('1')
        self.RequestSubContentShouldBe("每月")
        self.RequestSubNumberShouldBe("1")
        self.RequestAdditionalContentShouldBe("打醬油")

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_period_key_is_monthly_and_input_number_is_zero(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 0 每月 2 打醬油')
        self.RequestTitleShouldBe('修改週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_MODIFY)
        self.RequestNumberShouldBe('0')
        self.RequestSubContentShouldBe("每月")
        self.RequestSubNumberShouldBe("2")
        self.RequestAdditionalContentShouldBe("打醬油")

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_period_key_is_monthly_and_input_formatted_number(self,
                                                                                                  input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 03 每月 3 打醬油')
        self.RequestTitleShouldBe('修改週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_MODIFY)
        self.RequestNumberShouldBe('3')
        self.RequestSubContentShouldBe("每月")
        self.RequestSubNumberShouldBe("3")
        self.RequestAdditionalContentShouldBe("打醬油")

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_not_input_sub_number(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 1 每月 打醬油')
        self.RequestResultShouldBeFormatError('修改週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_period_key_is_monthly_and_input_sub_number_is_zero(self,
                                                                                                    input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 7 每月 0 打醬油')
        self.RequestTitleShouldBe('修改週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_MODIFY)
        self.RequestNumberShouldBe('7')
        self.RequestSubContentShouldBe("每月")
        self.RequestSubNumberShouldBe("0")
        self.RequestAdditionalContentShouldBe("打醬油")

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_input_multiple_additional_content(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 2 每月 1 買生鮮 買點心')
        self.RequestTitleShouldBe('修改週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_MODIFY)
        self.RequestNumberShouldBe('2')
        self.RequestSubContentShouldBe("每月")
        self.RequestSubNumberShouldBe("1")
        self.RequestAdditionalContentShouldBe("買生鮮 買點心")

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_input_additional_content_with_number(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 5 每月 1 1100 洗廁所')
        self.RequestTitleShouldBe('修改週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_MODIFY)
        self.RequestNumberShouldBe('5')
        self.RequestSubContentShouldBe("每月")
        self.RequestSubNumberShouldBe("1")
        self.RequestAdditionalContentShouldBe("1100 洗廁所")

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_period_key_is_weekly(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 3 每週 7 洗小狗')
        self.RequestTitleShouldBe('修改週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_MODIFY)
        self.RequestNumberShouldBe('3')
        self.RequestSubContentShouldBe("每週")
        self.RequestSubNumberShouldBe("7")
        self.RequestAdditionalContentShouldBe("洗小狗")

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_period_key_is_weekly_and_input_formatted_number_and_multiple_additional_content(
            self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 010 每週 5 洗小狗 洗車 打蠟')
        self.RequestTitleShouldBe('修改週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_MODIFY)
        self.RequestNumberShouldBe('10')
        self.RequestSubContentShouldBe("每週")
        self.RequestSubNumberShouldBe("5")
        self.RequestAdditionalContentShouldBe("洗小狗 洗車 打蠟")

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_period_key_is_daily_and_input_sub_number(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 8 每天 2 擦藥')
        self.RequestTitleShouldBe('修改週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_MODIFY)
        self.RequestNumberShouldBe('8')
        self.RequestSubContentShouldBe("每天")
        self.RequestSubNumberShouldBe("0")
        self.RequestAdditionalContentShouldBe("2 擦藥")

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_period_key_is_daily(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 6 每天 擦藥')
        self.RequestTitleShouldBe('修改週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_MODIFY)
        self.RequestNumberShouldBe('6')
        self.RequestSubContentShouldBe("每天")
        self.RequestSubNumberShouldBe("0")
        self.RequestAdditionalContentShouldBe("擦藥")

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_period_key_is_daily_and_input_multiple_additional_content(self,
                                                                                                           input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 12 每天 跑步 舉重')
        self.RequestTitleShouldBe('修改週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_MODIFY)
        self.RequestNumberShouldBe('12')
        self.RequestSubContentShouldBe("每天")
        self.RequestSubNumberShouldBe("0")
        self.RequestAdditionalContentShouldBe("跑步 舉重")

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_modify_schedule_command_and_input_invalid_period_key(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '修改行程 1 每年 6 繳燃料稅')
        self.RequestResultShouldBeFormatError('修改週期行程')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK
    ])
    def test_request_get_schedule_command(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '確認行程')
        self.RequestTitleShouldBe('確認週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_GET)

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_get_schedule_command_with_unnecessary_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '確認行程 A')
        self.RequestTitleShouldBe('確認週期行程')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_SCHEDULE_GET)

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK
    ])
    def test_request_buy_command_and_no_any_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '買')
        self.RequestResultShouldBeFormatError('新增記帳項目')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_buy_command_and_no_input_prize(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '買 鍋子')
        self.RequestResultShouldBeFormatError('新增記帳項目')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_buy_command(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '買 鍋子 150')
        self.RequestTitleShouldBe('新增記帳項目')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_BUY)
        self.RequestSubContentShouldBe("鍋子")
        self.RequestNumberShouldBe('150')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_buy_command_and_input_multiple_sub_content(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '買 鍋 碗 瓢 盆 1000')
        self.RequestTitleShouldBe('新增記帳項目')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_BUY)
        self.RequestSubContentShouldBe("鍋 碗 瓢 盆")
        self.RequestNumberShouldBe('1000')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_buy_command_and_input_multiple_sub_content(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '買 鉛筆 1 5')
        self.RequestResultShouldBeFormatError('新增記帳項目')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK,
        INPUT_FLAW_TYPE_MULTI_BLANK_BETWEEN
    ])
    def test_request_buy_command_and_input_formatted_prize(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '買 滑鼠 01500')
        self.RequestTitleShouldBe('新增記帳項目')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_BUY)
        self.RequestSubContentShouldBe("滑鼠")
        self.RequestNumberShouldBe('1500')

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK
    ])
    def test_request_record_baby_diaper_changing_time_command(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '紀錄寶寶換尿布時間')
        self.RequestTitleShouldBe('紀錄寶寶換尿布時間')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_RECORD_BABY_DIAPER_CHANGING_TIME)

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK
    ])
    def test_request_record_baby_eat_time_command_and_no_any_param(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '紀錄寶寶吃飯時間')
        self.RequestTitleShouldBe('紀錄寶寶吃飯時間')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_RECORD_BABY_EAT_TIME)

    @parameterized.expand([
        '',
        INPUT_FLAW_TYPE_PREFIX_BLANK,
        INPUT_FLAW_TYPE_SUFFIX_BLANK,
        INPUT_FLAW_TYPE_PREFIX_MULTI_BLANK
    ])
    def test_request_record_baby_eat_time_command_and_input_feeding_amount(self, input_flaw_type):
        self.GivenCommandWithFlawType(input_flaw_type, '紀錄寶寶吃飯時間 125')
        self.RequestTitleShouldBe('紀錄寶寶吃飯時間')
        self.RequestNumberShouldBe('125')
        self.RequestTypeShouldBe(manage.REQUEST_TYPE_GAS)
        self.RequestActionShouldBe(lineActionInfo.API_ACTION_RECORD_BABY_EAT_TIME)

    def RequestSubContentShouldBe(self, expected_sub_content):
        self.assertEqual(expected_sub_content, self.req_info.requestParam['subContent'])

    def RequestActionShouldBe(self, expected_action):
        self.assertEqual(expected_action, self.req_info.requestParam['action'])

    def RequestNumberShouldBe(self, expected_number):
        self.assertEqual(expected_number, self.req_info.requestParam['number'])

    def RequestAdditionalContentShouldBe(self, expected_additional_content):
        self.assertEqual(expected_additional_content, self.req_info.requestParam['additionalContent'])

    def RequestSubNumberShouldBe(self, expected_sub_number):
        self.assertEqual(expected_sub_number, self.req_info.requestParam['subNumber'])

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
