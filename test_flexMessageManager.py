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

    def test_literal_backslash_n_becomes_real_newline(self):
        # GAS 字表分頁裡的換行是以字面的反斜線 + n 兩個字元存放,
        # 要還原成真正的換行, 否則卡片上會直接看到 \n
        status = '【記帳成功】' + '\\' + 'n掏水軒口糧餅*2包 (30$)'
        result = self._parse('新增記帳項目', status, '　')
        self.assertEqual('【記帳成功】\n掏水軒口糧餅*2包 (30$)',
                         result['hero']['contents'][1]['text'])

    def test_literal_backslash_n_in_content_becomes_real_newline(self):
        content = '第一行' + '\\' + 'n第二行'
        result = self._parse('新增記帳項目', '【記帳成功】', content)
        self.assertEqual('第一行\n第二行', result['body']['contents'][0]['text'])

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
