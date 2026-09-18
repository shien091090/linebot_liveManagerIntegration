import json
import unittest

import flexMessageManager

# [How To Use]
# Terminal : python -m unittest test_flexMessageManager


class GetFlexMessageTestCase(unittest.TestCase):

    def _parse(self, title, status_message, content):
        return json.loads(flexMessageManager.getFlexMessage(title, status_message, content))

    def test_plain_text_is_valid_json(self):
        self._parse('新增記帳項目', '【記帳成功】', '飲料 (21$)')

    def test_newline_is_preserved(self):
        status = '【記帳成功】\n飲料 (21$)'
        result = self._parse('新增記帳項目', status, '　')
        self.assertEqual(status, result['hero']['contents'][1]['text'])

    def test_double_quote_in_content_does_not_break_json(self):
        # GAS 例外訊息常帶雙引號, 例如 Cannot read properties of null (reading "getColumn")
        self._parse('新增記帳項目', '【後端異常】', 'TypeError: cannot read "getColumn" of null')

    def test_backslash_in_content_does_not_break_json(self):
        self._parse('新增記帳項目', '【後端異常】',
                    'Exception: bad path C:' + '\\' + 'temp' + '\\' + 'x')

    def test_double_quote_in_title_does_not_break_json(self):
        self._parse('新增"記帳"項目', '【後端異常】', '　')


if __name__ == '__main__':
    unittest.main()
