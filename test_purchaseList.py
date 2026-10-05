import json
import unittest
from unittest import mock

import requests

import manage

# [How To Use]
# Terminal : python -m unittest test_purchaseList


class FakeResponse:
    def __init__(self, payload):
        self.text = json.dumps(payload)


def purchase_list_response(items):
    return FakeResponse({'statusCode': 200, 'statusMsg': '取得待購買清單成功',
                         'responseMsg': json.dumps(items), 'messageType': 'text'})


TWO_ITEMS = [{'name': '滑步車', 'category': '短期', 'addTime': ''},
             {'name': '洗碗機', 'category': '長期', 'addTime': ''}]


class FetchPurchaseItemsTestCase(unittest.TestCase):

    def test_success_returns_items_with_short_term_first(self):
        items = [TWO_ITEMS[1], TWO_ITEMS[0]]
        with mock.patch.object(manage.requests, 'get', return_value=purchase_list_response(items)):
            result = manage._fetch_purchase_items()
        self.assertEqual(['滑步車', '洗碗機'], [item['name'] for item in result])

    def test_real_empty_list_returns_empty(self):
        with mock.patch.object(manage.requests, 'get', return_value=purchase_list_response([])):
            self.assertEqual([], manage._fetch_purchase_items())

    def test_timeout_returns_none_instead_of_empty(self):
        with mock.patch.object(manage.requests, 'get', side_effect=requests.exceptions.Timeout()):
            self.assertIsNone(manage._fetch_purchase_items())

    def test_non_json_response_returns_none(self):
        fake = mock.Mock(text='<!DOCTYPE html><html>error</html>')
        with mock.patch.object(manage.requests, 'get', return_value=fake):
            self.assertIsNone(manage._fetch_purchase_items())

    def test_non_success_status_returns_none(self):
        fake = FakeResponse({'statusCode': 301, 'statusMsg': '找不到購買清單分頁', 'responseMsg': ''})
        with mock.patch.object(manage.requests, 'get', return_value=fake):
            self.assertIsNone(manage._fetch_purchase_items())

    def test_uses_relaxed_timeout(self):
        with mock.patch.object(manage.requests, 'get', return_value=purchase_list_response([])) as fake_get:
            manage._fetch_purchase_items()
        self.assertGreaterEqual(fake_get.call_args.kwargs['timeout'], 25)


class PurchaseCommandTestCase(unittest.TestCase):

    def test_get_command_shows_failure_message_when_fetch_fails(self):
        with mock.patch.object(manage.requests, 'get', side_effect=requests.exceptions.Timeout()):
            _, req_info = manage.ParseRequestInfo('確認待買')
        self.assertEqual(manage.PURCHASE_FETCH_FAILED_TEXT, req_info.responseMsg)
        self.assertNotIn('(空)', req_info.responseMsg)

    def test_get_command_shows_empty_when_list_really_empty(self):
        with mock.patch.object(manage.requests, 'get', return_value=purchase_list_response([])):
            _, req_info = manage.ParseRequestInfo('確認待買')
        self.assertEqual('(空)', req_info.responseMsg)

    def test_delete_does_not_report_missing_number_when_fetch_fails(self):
        with mock.patch.object(manage.requests, 'get', side_effect=requests.exceptions.Timeout()) as fake_get:
            _, req_info = manage.ParseRequestInfo('刪除待買 1')
        self.assertEqual(manage.PURCHASE_FETCH_FAILED_TEXT, req_info.responseMsg)
        self.assertEqual(1, fake_get.call_count)

    def test_mark_bought_does_not_report_missing_number_when_fetch_fails(self):
        with mock.patch.object(manage.requests, 'get', side_effect=requests.exceptions.Timeout()) as fake_get:
            _, req_info = manage.ParseRequestInfo('已購買 1')
        self.assertEqual(manage.PURCHASE_FETCH_FAILED_TEXT, req_info.responseMsg)
        self.assertEqual(1, fake_get.call_count)

    def test_add_keeps_add_result_but_shows_failure_when_list_fetch_fails(self):
        add_resp = FakeResponse({'statusCode': 200, 'statusMsg': '已新增：束線帶', 'responseMsg': '束線帶'})
        with mock.patch.object(manage.requests, 'get',
                               side_effect=[add_resp, requests.exceptions.Timeout()]):
            _, req_info = manage.ParseRequestInfo('新增待買 束線帶')
        self.assertEqual('已新增：束線帶', req_info.statusMsg)
        self.assertEqual(manage.PURCHASE_FETCH_FAILED_TEXT, req_info.responseMsg)

    def test_all_purchase_gas_calls_use_relaxed_timeout(self):
        add_resp = FakeResponse({'statusCode': 200, 'statusMsg': '已新增：束線帶', 'responseMsg': '束線帶'})
        with mock.patch.object(manage.requests, 'get',
                               side_effect=[add_resp, purchase_list_response(TWO_ITEMS)]) as fake_get:
            manage.ParseRequestInfo('新增待買 束線帶')
        for call in fake_get.call_args_list:
            self.assertGreaterEqual(call.kwargs['timeout'], 25)


if __name__ == '__main__':
    unittest.main()
