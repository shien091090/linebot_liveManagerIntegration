import unittest
from unittest import mock

import manage

# [How To Use]
# Terminal : python -m unittest test_receiveMessage


class FakeSource:
    type = 'user'
    user_id = 'U_test'


class FakeMessage:
    def __init__(self, text):
        self.text = text


class FakeEvent:
    def __init__(self, text):
        self.message = FakeMessage(text)
        self.source = FakeSource()
        self.reply_token = 'token_test'


class ReceiveMessageTestCase(unittest.TestCase):

    def test_invalid_command_returns_without_killing_worker(self):
        # 舊版用 quit(), 會丟 SystemExit 打死 gunicorn worker,
        # 讓 LINE 收到 H13 Connection closed without response
        with mock.patch.object(manage, 'line_bot_api'):
            manage.receiveMessage(FakeEvent('這不是任何指令'))

    def test_backend_error_still_replies_to_line(self):
        event = FakeEvent('記帳 飲料 21 外食餐費')

        def fake_send(self):
            self.setBackendError(ValueError('Expecting value: line 1 column 1 (char 0)'))

        with mock.patch.object(manage, 'line_bot_api') as fake_api, \
                mock.patch.object(manage.lineActionInfo.RequestInfo, 'sendRequest', fake_send):
            manage.receiveMessage(event)

        fake_api.reply_message.assert_called_once()
        self.assertEqual('token_test', fake_api.reply_message.call_args[0][0])


if __name__ == '__main__':
    unittest.main()
