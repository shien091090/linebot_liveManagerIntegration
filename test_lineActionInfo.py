import json
import unittest
from unittest import mock

import lineActionInfo

# [How To Use]
# Terminal : python -m unittest test_lineActionInfo


class FakeResponse:
    def __init__(self, text):
        self.text = text


def _buildRequestInfo():
    return lineActionInfo.RequestInfo('新增記帳項目',
                                      'request_type_gas',
                                      {'action': lineActionInfo.API_ACTION_BUY_WITH_BUDGET_TYPE,
                                       'subContent': '飲料',
                                       'number': '21',
                                       'additionalContent': '外食餐費'})


class SendRequestTestCase(unittest.TestCase):

    def test_normal_json_response_is_parsed(self):
        body = json.dumps({'statusCode': 200,
                           'statusMsg': '【記帳成功】\n飲料 (21$)',
                           'responseMsg': '　',
                           'messageType': 'text'})
        req_info = _buildRequestInfo()

        with mock.patch.object(lineActionInfo.requests, 'get', return_value=FakeResponse(body)):
            req_info.sendRequest()

        self.assertEqual(200, req_info.statusCode)
        self.assertEqual('【記帳成功】\n飲料 (21$)', req_info.statusMsg)
        self.assertEqual('text', req_info.messageType)

    def test_html_error_page_does_not_raise(self):
        req_info = _buildRequestInfo()

        with mock.patch.object(lineActionInfo.requests, 'get',
                               return_value=FakeResponse('<!DOCTYPE html><html>error</html>')):
            req_info.sendRequest()

        self.assertEqual(lineActionInfo.STATUS_CODE_BACKEND_ERROR, req_info.statusCode)
        self.assertEqual('text', req_info.messageType)
        self.assertNotEqual('', req_info.statusMsg)

    def test_empty_body_does_not_raise(self):
        req_info = _buildRequestInfo()

        with mock.patch.object(lineActionInfo.requests, 'get', return_value=FakeResponse('')):
            req_info.sendRequest()

        self.assertEqual(lineActionInfo.STATUS_CODE_BACKEND_ERROR, req_info.statusCode)

    def test_network_failure_does_not_raise(self):
        req_info = _buildRequestInfo()

        with mock.patch.object(lineActionInfo.requests, 'get', side_effect=OSError('connection reset')):
            req_info.sendRequest()

        self.assertEqual(lineActionInfo.STATUS_CODE_BACKEND_ERROR, req_info.statusCode)

    def test_bypass_request_is_untouched(self):
        req_info = lineActionInfo.RequestInfo('新增記帳項目', 'request_type_bypass', None)
        req_info.statusMsg = '【格式錯誤】'
        req_info.responseMsg = ' '

        req_info.sendRequest()

        self.assertEqual(0, req_info.statusCode)
        self.assertEqual('【格式錯誤】', req_info.statusMsg)


if __name__ == '__main__':
    unittest.main()
