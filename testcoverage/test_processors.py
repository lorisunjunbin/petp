"""Unit tests for individual processors."""

import json
import os
from unittest.mock import patch
from email.message import EmailMessage

import pytest


class TestEncodeDecodeStr:

    def test_base64_encode(self, make_processor):
        chain = {"inbound": "hello", "type": "encode", "algorithms": "base64"}
        proc = make_processor(
            "ENCODE_DECODE_STR",
            '{"type":"encode", "inbound":"hello", "algorithms":"base64", "outbound_key":"result"}',
            chain,
        )
        proc.process()
        assert chain["result"] == "aGVsbG8="

    def test_base64_decode(self, make_processor):
        chain = {"inbound": "aGVsbG8=", "type": "decode", "algorithms": "base64"}
        proc = make_processor(
            "ENCODE_DECODE_STR",
            '{"type":"decode", "inbound":"aGVsbG8=", "algorithms":"base64", "outbound_key":"result"}',
            chain,
        )
        proc.process()
        assert chain["result"] == "hello"

    def test_hexlify_encode(self, make_processor):
        chain = {}
        proc = make_processor(
            "ENCODE_DECODE_STR",
            '{"type":"encode", "inbound":"AB", "algorithms":"hexlify", "outbound_key":"hex_out"}',
            chain,
        )
        proc.process()
        assert chain["hex_out"] == "4142"

    def test_hexlify_decode(self, make_processor):
        chain = {}
        proc = make_processor(
            "ENCODE_DECODE_STR",
            '{"type":"decode", "inbound":"4142", "algorithms":"hexlify", "outbound_key":"hex_out"}',
            chain,
        )
        proc.process()
        assert chain["hex_out"] == "AB"

    def test_base85_roundtrip(self, make_processor):
        chain = {}
        proc = make_processor(
            "ENCODE_DECODE_STR",
            '{"type":"encode", "inbound":"test", "algorithms":"base85", "outbound_key":"encoded"}',
            chain,
        )
        proc.process()
        encoded = chain["encoded"]

        chain2 = {}
        proc2 = make_processor(
            "ENCODE_DECODE_STR",
            json.dumps({"type": "decode", "inbound": encoded, "algorithms": "base85", "outbound_key": "decoded"}),
            chain2,
        )
        proc2.process()
        assert chain2["decoded"] == "test"


class TestWaitSeconds:

    @patch("time.sleep")
    def test_waits_specified_seconds(self, mock_sleep, make_processor):
        proc = make_processor("WAIT_SECONDS", '{"wait_seconds":"3"}', {})
        proc.process()
        mock_sleep.assert_called_once_with(3)

    @patch("time.sleep")
    def test_zero_seconds(self, mock_sleep, make_processor):
        proc = make_processor("WAIT_SECONDS", '{"wait_seconds":"0"}', {})
        proc.process()
        mock_sleep.assert_called_once_with(0)


class TestProcessorDynamicLoading:

    def test_load_valid_processor(self):
        from core.processor import Processor
        proc = Processor.get_processor_by_type("ENCODE_DECODE_STR")
        assert proc is not None
        assert proc.__class__.__name__ == "ENCODE_DECODE_STRProcessor"

    def test_load_wait_seconds(self):
        from core.processor import Processor
        proc = Processor.get_processor_by_type("WAIT_SECONDS")
        assert proc is not None

    def test_cached_loading(self):
        from core.processor import Processor
        proc1 = Processor.get_processor_by_type("ENCODE_DECODE_STR")
        proc2 = Processor.get_processor_by_type("ENCODE_DECODE_STR")
        assert type(proc1) == type(proc2)


class TestHasParam:

    def test_has_param_exists(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"encode", "inbound":"x"}', {})
        assert proc.has_param("type") is True
        assert proc.has_param("inbound") is True

    def test_has_param_missing(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"encode"}', {})
        assert proc.has_param("nonexistent") is False

    def test_has_param_empty_string(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"encode", "empty":""}', {})
        assert proc.has_param("empty") is False

    def test_has_param_non_string_value(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"encode", "count":5}', {})
        assert proc.has_param("count") is True


class _DummySMTP:
    last_instance = None

    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.logged_in = None
        self.sent = None
        _DummySMTP.last_instance = self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self):
        self.started_tls = True

    def login(self, user, pwd):
        self.logged_in = (user, pwd)

    def send_message(self, msg, to_addrs=None):
        self.sent = (msg, to_addrs)


class _BrokenSMTP:
    def __init__(self, host, port, timeout=None):
        raise RuntimeError('smtp down')


class _DummySMTPSSL(_DummySMTP):
    last_instance = None

    def __init__(self, host, port, timeout=None):
        super().__init__(host, port, timeout)
        _DummySMTPSSL.last_instance = self


class TestSendEmail:

    @patch('core.processors.SEND_EMAILProcessor.smtplib.SMTP', _DummySMTP)
    def test_send_email_supports_html_cc_bcc_and_tls(self, make_processor):
        proc = make_processor(
            'SEND_EMAIL',
            json.dumps({
                'smtp': 'smtp.example.com',
                'port': 587,
                'name': 'from@example.com',
                'pwd': 'pwd',
                'to': 'a@example.com,b@example.com',
                'cc': 'cc@example.com',
                'bcc': 'bcc@example.com',
                'subject': 'hello',
                'content': '<b>hi</b>',
                'content_type': 'html',
                'use_tls': 'yes',
                'timeout': '9'
            }),
            {},
        )

        proc.process()

        smtp = _DummySMTP.last_instance
        assert smtp is not None
        assert smtp.host == 'smtp.example.com'
        assert smtp.port == 587
        assert smtp.timeout == 9.0
        assert smtp.started_tls is True
        assert smtp.logged_in == ('from@example.com', 'pwd')

        msg, to_addrs = smtp.sent
        assert msg['To'] == 'a@example.com, b@example.com'
        assert msg['Cc'] == 'cc@example.com'
        assert 'Bcc' not in msg
        assert to_addrs == ['a@example.com', 'b@example.com', 'cc@example.com', 'bcc@example.com']

    @patch('core.processors.SEND_EMAILProcessor.smtplib.SMTP', _DummySMTP)
    def test_send_email_supports_multiple_attachments(self, make_processor, tmp_path):
        a1 = tmp_path / 'a.txt'
        a2 = tmp_path / 'b.txt'
        a1.write_text('A', encoding='utf-8')
        a2.write_text('B', encoding='utf-8')

        proc = make_processor(
            'SEND_EMAIL',
            json.dumps({
                'smtp': 'smtp.example.com',
                'to': 'a@example.com',
                'attachment': str(a1),
                'attachments': f'{str(a1)};{str(a2)}',
            }),
            {},
        )

        proc.process()
        msg, _ = _DummySMTP.last_instance.sent
        filenames = [part.get_filename() for part in msg.iter_attachments()]
        assert filenames == ['a.txt', 'b.txt']

    @patch('core.processors.SEND_EMAILProcessor.smtplib.SMTP_SSL', _DummySMTPSSL)
    @patch('core.processors.SEND_EMAILProcessor.smtplib.SMTP', _DummySMTP)
    def test_send_email_prefers_starttls_on_587_when_both_modes_enabled(self, make_processor):
        _DummySMTP.last_instance = None
        _DummySMTPSSL.last_instance = None

        proc = make_processor(
            'SEND_EMAIL',
            json.dumps({
                'smtp': 'smtp.example.com',
                'port': 587,
                'name': 'from@example.com',
                'pwd': 'pwd',
                'to': 'a@example.com',
                'use_tls': 'yes',
                'use_ssl': 'yes'
            }),
            {},
        )

        proc.process()
        assert _DummySMTP.last_instance is not None
        assert _DummySMTP.last_instance.started_tls is True
        assert _DummySMTPSSL.last_instance is None

    @patch('core.processors.SEND_EMAILProcessor.smtplib.SMTP_SSL', _DummySMTPSSL)
    @patch('core.processors.SEND_EMAILProcessor.smtplib.SMTP', _DummySMTP)
    def test_send_email_auto_switches_to_ssl_on_465_when_tls_only(self, make_processor):
        _DummySMTP.last_instance = None
        _DummySMTPSSL.last_instance = None

        proc = make_processor(
            'SEND_EMAIL',
            json.dumps({
                'smtp': 'smtp.example.com',
                'port': 465,
                'name': 'from@example.com',
                'pwd': 'pwd',
                'to': 'a@example.com',
                'use_tls': 'yes',
                'use_ssl': 'no'
            }),
            {},
        )

        proc.process()
        assert _DummySMTPSSL.last_instance is not None
        assert isinstance(_DummySMTP.last_instance, _DummySMTPSSL)
        assert _DummySMTPSSL.last_instance.started_tls is False

    @patch('core.processors.SEND_EMAILProcessor.smtplib.SMTP', _BrokenSMTP)
    def test_send_email_can_ignore_error_when_fail_on_error_no(self, make_processor):
        proc = make_processor(
            'SEND_EMAIL',
            json.dumps({
                'smtp': 'smtp.example.com',
                'to': 'a@example.com',
                'fail_on_error': 'no'
            }),
            {},
        )
        proc.process()

    @patch('core.processors.SEND_EMAILProcessor.smtplib.SMTP', _BrokenSMTP)
    def test_send_email_raises_error_by_default(self, make_processor):
        proc = make_processor(
            'SEND_EMAIL',
            json.dumps({
                'smtp': 'smtp.example.com',
                'to': 'a@example.com'
            }),
            {},
        )
        with pytest.raises(RuntimeError):
            proc.process()


class _DummyIMAP:
    last_instance = None

    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.logged_in = None
        self.selected = None
        self.search_args = None
        self.fetch_calls = []
        self.store_calls = []
        self.logged_out = False
        _DummyIMAP.last_instance = self

    def login(self, user, pwd):
        self.logged_in = (user, pwd)

    def select(self, mailbox):
        self.selected = mailbox
        return 'OK', [b'2']

    def search(self, _charset, *criteria):
        self.search_args = criteria
        return 'OK', [b'1 2']

    def fetch(self, msg_id, query):
        self.fetch_calls.append((msg_id, query))
        m = EmailMessage()
        idx = msg_id.decode() if isinstance(msg_id, (bytes, bytearray)) else str(msg_id)
        m['Subject'] = f'subject-{idx}'
        m['From'] = 'from@example.com'
        m['To'] = 'to@example.com'
        m['Message-ID'] = f'<m-{idx}@example.com>'
        m.set_content(f'text-{idx}')
        m.add_alternative(f'<p>html-{idx}</p>', subtype='html')
        return 'OK', [(b'RFC822', m.as_bytes())]

    def store(self, msg_id, op, flag):
        self.store_calls.append((msg_id, op, flag))
        return 'OK', [b'']

    def logout(self):
        self.logged_out = True
        return 'BYE', [b'']


class _BrokenIMAP:
    def __init__(self, host, port, timeout=None):
        raise RuntimeError('imap down')


class _DummyIMAPWithAttachment(_DummyIMAP):

    def fetch(self, msg_id, query):
        self.fetch_calls.append((msg_id, query))
        m = EmailMessage()
        idx = msg_id.decode() if isinstance(msg_id, (bytes, bytearray)) else str(msg_id)
        m['Subject'] = f'subject-{idx}'
        m['From'] = 'from@example.com'
        m['To'] = 'to@example.com'
        m['Message-ID'] = f'<m-{idx}@example.com>'
        m.set_content(f'text-{idx}')
        m.add_attachment(b'hello-attachment', maintype='application', subtype='octet-stream', filename='report.txt')
        return 'OK', [(b'RFC822', m.as_bytes())]


class TestReceiveEmail:

    @patch('core.processors.RECEIVE_EMAILProcessor.imaplib.IMAP4_SSL', _DummyIMAP)
    def test_receive_email_fetches_and_sets_data_chain(self, make_processor):
        chain = {}
        proc = make_processor(
            'RECEIVE_EMAIL',
            json.dumps({
                'host': 'imap.example.com',
                'port': 993,
                'name': 'user@example.com',
                'pwd': 'pwd',
                'criteria': 'UNSEEN',
                'limit': '1',
                'mark_seen': 'yes',
                'data_key': 'mail_rows',
            }),
            chain,
        )

        proc.process()

        imap = _DummyIMAP.last_instance
        assert imap.host == 'imap.example.com'
        assert imap.logged_in == ('user@example.com', 'pwd')
        assert imap.selected == 'INBOX'
        assert imap.search_args == ('UNSEEN',)
        assert len(imap.fetch_calls) == 1
        assert imap.fetch_calls[0][1] == '(RFC822)'
        assert len(imap.store_calls) == 1
        assert imap.logged_out is True

        assert 'mail_rows' in chain
        assert len(chain['mail_rows']) == 1
        row = chain['mail_rows'][0]
        assert row['subject'] == 'subject-2'
        assert row['text'] == 'text-2'
        assert 'html-2' in row['html']

    @patch('core.processors.RECEIVE_EMAILProcessor.imaplib.IMAP4_SSL', _BrokenIMAP)
    def test_receive_email_can_ignore_error_when_fail_on_error_no(self, make_processor):
        chain = {}
        proc = make_processor(
            'RECEIVE_EMAIL',
            json.dumps({
                'host': 'imap.example.com',
                'name': 'user@example.com',
                'pwd': 'pwd',
                'fail_on_error': 'no',
                'data_key': 'mail_rows',
            }),
            chain,
        )

        proc.process()
        assert chain['mail_rows'] == []

    @patch('core.processors.RECEIVE_EMAILProcessor.imaplib.IMAP4_SSL', _DummyIMAP)
    def test_receive_email_supports_sender_filter(self, make_processor):
        chain = {}
        proc = make_processor(
            'RECEIVE_EMAIL',
            json.dumps({
                'host': 'imap.example.com',
                'name': 'user@example.com',
                'pwd': 'pwd',
                'criteria': 'UNSEEN',
                'sender': 'junbin.sun@sap.com',
                'limit': '1',
                'data_key': 'mail_rows',
            }),
            chain,
        )

        proc.process()
        imap = _DummyIMAP.last_instance
        assert imap.search_args == ('UNSEEN', 'FROM', '"junbin.sun@sap.com"')

    @patch('core.processors.RECEIVE_EMAILProcessor.imaplib.IMAP4_SSL', _DummyIMAP)
    def test_receive_email_supports_subject_contains_filter(self, make_processor):
        chain = {}
        proc = make_processor(
            'RECEIVE_EMAIL',
            json.dumps({
                'host': 'imap.example.com',
                'name': 'user@example.com',
                'pwd': 'pwd',
                'criteria': 'UNSEEN',
                'subject_contains': 'PETP 报告',
                'limit': '1',
                'data_key': 'mail_rows',
            }),
            chain,
        )

        proc.process()
        imap = _DummyIMAP.last_instance
        assert imap.search_args == ('UNSEEN', 'SUBJECT', '"PETP 报告"')

    @patch('core.processors.RECEIVE_EMAILProcessor.imaplib.IMAP4_SSL', _DummyIMAP)
    def test_receive_email_supports_sender_and_subject_filters_together(self, make_processor):
        chain = {}
        proc = make_processor(
            'RECEIVE_EMAIL',
            json.dumps({
                'host': 'imap.example.com',
                'name': 'user@example.com',
                'pwd': 'pwd',
                'criteria': 'UNSEEN',
                'sender': 'junbin.sun@sap.com',
                'subject_contains': 'PETP',
                'limit': '1',
                'data_key': 'mail_rows',
            }),
            chain,
        )

        proc.process()
        imap = _DummyIMAP.last_instance
        assert imap.search_args == ('UNSEEN', 'FROM', '"junbin.sun@sap.com"', 'SUBJECT', '"PETP"')

    @patch('core.processors.RECEIVE_EMAILProcessor.imaplib.IMAP4_SSL', _DummyIMAPWithAttachment)
    def test_receive_email_can_save_attachments(self, make_processor, tmp_path):
        chain = {}
        proc = make_processor(
            'RECEIVE_EMAIL',
            json.dumps({
                'host': 'imap.example.com',
                'name': 'user@example.com',
                'pwd': 'pwd',
                'limit': '1',
                'save_attachments': 'yes',
                'attachments_dir': str(tmp_path),
                'data_key': 'mail_rows',
                'attachments_key': 'saved_attachment_paths',
            }),
            chain,
        )

        proc.process()
        row = chain['mail_rows'][0]
        assert len(row['attachments']) == 1
        att = row['attachments'][0]
        assert att['saved'] is True
        assert os.path.isfile(att['saved_path'])
        assert att['filename'].endswith('report.txt')
        assert chain['saved_attachment_paths'] == [att['saved_path']]

    @patch('core.processors.RECEIVE_EMAILProcessor.imaplib.IMAP4_SSL', _DummyIMAP)
    def test_receive_email_result_key_on_success(self, make_processor):
        chain = {}
        proc = make_processor(
            'RECEIVE_EMAIL',
            json.dumps({
                'host': 'imap.example.com',
                'name': 'user@example.com',
                'pwd': 'pwd',
                'limit': '2',
                'data_key': 'mail_rows',
                'result_key': 'recv_result',
            }),
            chain,
        )
        proc.process()
        assert chain['recv_result']['ok'] is True
        assert chain['recv_result']['error'] is None
        assert chain['recv_result']['count'] == len(chain['mail_rows'])

    @patch('core.processors.RECEIVE_EMAILProcessor.imaplib.IMAP4_SSL', _BrokenIMAP)
    def test_receive_email_result_key_on_failure(self, make_processor):
        chain = {}
        proc = make_processor(
            'RECEIVE_EMAIL',
            json.dumps({
                'host': 'imap.example.com',
                'name': 'user@example.com',
                'pwd': 'pwd',
                'fail_on_error': 'no',
                'data_key': 'mail_rows',
                'result_key': 'recv_result',
            }),
            chain,
        )
        proc.process()
        assert chain['recv_result']['ok'] is False
        assert chain['recv_result']['count'] == 0
        assert 'imap down' in chain['recv_result']['error']

    @patch('core.processors.RECEIVE_EMAILProcessor.imaplib.IMAP4_SSL', _DummyIMAP)
    def test_receive_email_no_result_key_writes_nothing(self, make_processor):
        chain = {}
        proc = make_processor(
            'RECEIVE_EMAIL',
            json.dumps({
                'host': 'imap.example.com',
                'name': 'user@example.com',
                'pwd': 'pwd',
                'data_key': 'mail_rows',
            }),
            chain,
        )
        proc.process()
        assert 'result_key' not in chain


class TestSendEmailResultKey:

    @patch('core.processors.SEND_EMAILProcessor.smtplib.SMTP', _DummySMTP)
    def test_send_email_result_key_on_success(self, make_processor):
        chain = {}
        proc = make_processor(
            'SEND_EMAIL',
            json.dumps({
                'smtp': 'smtp.example.com',
                'to': 'a@example.com',
                'result_key': 'send_result',
            }),
            chain,
        )
        proc.process()
        assert chain['send_result']['ok'] is True
        assert chain['send_result']['error'] is None

    @patch('core.processors.SEND_EMAILProcessor.smtplib.SMTP', _BrokenSMTP)
    def test_send_email_result_key_on_failure(self, make_processor):
        chain = {}
        proc = make_processor(
            'SEND_EMAIL',
            json.dumps({
                'smtp': 'smtp.example.com',
                'to': 'a@example.com',
                'fail_on_error': 'no',
                'result_key': 'send_result',
            }),
            chain,
        )
        proc.process()
        assert chain['send_result']['ok'] is False
        assert chain['send_result']['error'] is not None

    @patch('core.processors.SEND_EMAILProcessor.smtplib.SMTP', _DummySMTP)
    def test_send_email_no_result_key_writes_nothing(self, make_processor):
        chain = {}
        proc = make_processor(
            'SEND_EMAIL',
            json.dumps({
                'smtp': 'smtp.example.com',
                'to': 'a@example.com',
            }),
            chain,
        )
        proc.process()
        assert 'result_key' not in chain
