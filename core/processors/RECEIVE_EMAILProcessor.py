import email
import imaplib
import logging
import os
import re
from email import policy

from core.processor import Processor


class RECEIVE_EMAILProcessor(Processor):
    TPL: str = '{"host":"","port":993,"name":"","pwd":"","mailbox":"INBOX","criteria":"UNSEEN","sender":"","subject_contains":"","limit":"10","use_ssl":"yes","mark_seen":"yes","save_attachments":"no","attachments_dir":"{p.get_ddir()}/email_attachments","detail_level":"detail","data_key":"emails","attachments_key":"","timeout":"30","fail_on_error":"yes","result_key":""}'

    DESC: str = '''
        Receive emails from an IMAP mailbox and store parsed results into data_chain.

        - host: IMAP server hostname or IP (supports expression, default: "")
        - port: IMAP server port (default: 993)
        - name: IMAP login username/email (supports expression, default: "")
        - pwd: IMAP login password or app password (supports expression, default: "")
        - mailbox: Mailbox folder to read, e.g. "INBOX" (supports expression, default: "INBOX")
        - criteria: IMAP search criteria, e.g. "UNSEEN", "ALL", "FROM \"x@x.com\"" (supports expression, default: "UNSEEN")
        - sender: Optional sender email filter; supports multiple addresses separated by ";" or "," (supports expression, default: "")
        - subject_contains: Optional subject keyword/phrase filter (supports expression, default: "")
        - limit: Max number of latest matched messages to fetch; <=0 means all (supports expression, default: "10")
        - use_ssl: "yes" to use IMAP SSL, otherwise plain IMAP (default: "yes")
        - mark_seen: "yes" to mark fetched messages as read (default: "yes")
        - save_attachments: "yes" to save email attachments to local folder (default: "no")
        - attachments_dir: Folder path used when save_attachments="yes" (supports expression, default: "{p.get_ddir()}/email_attachments")
        - detail_level: "detail" returns all fields; "summary" returns subject/from/to/date/attachments(filenames only)/text(first 50 chars) (default: "detail")
        - data_key: data_chain key to store result list (default: "emails")
        - attachments_key: Optional data_chain key to store all saved attachment file paths (default: "")
        - timeout: IMAP connection timeout seconds (supports expression, default: "30")
        - fail_on_error: "yes" to raise error; "no" to log and continue (default: "yes")
        - result_key: data_chain key to store fetch result {"ok": bool, "count": int, "error": str|None}; only written when set (default: "")
    '''

    def get_category(self) -> str:
        return super().CATE_EMAIL

    @staticmethod
    def _as_yes(value: str) -> bool:
        return str(value).strip().lower() == 'yes'

    @staticmethod
    def _extract_bodies(msg) -> tuple[str, str]:
        text_parts: list[str] = []
        html_parts: list[str] = []

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get_filename():
                    continue
                ctype = part.get_content_type()
                try:
                    payload = part.get_content()
                except Exception:
                    payload = ''
                if not isinstance(payload, str):
                    payload = str(payload)
                if ctype == 'text/plain':
                    text_parts.append(payload)
                elif ctype == 'text/html':
                    html_parts.append(payload)
        else:
            try:
                payload = msg.get_content()
            except Exception:
                payload = ''
            if not isinstance(payload, str):
                payload = str(payload)
            if msg.get_content_type() == 'text/html':
                html_parts.append(payload)
            else:
                text_parts.append(payload)

        return '\n'.join(text_parts).strip(), '\n'.join(html_parts).strip()

    @staticmethod
    def _parse_criteria(criteria: str) -> list[str]:
        c = (criteria or '').strip()
        if not c:
            return ['UNSEEN']
        # Keep simple for v1: space split supports common terms like UNSEEN/ALL/FROM.
        return c.split()

    def _build_search_args(self, criteria: str, sender: str, subject_contains: str) -> list[str]:
        args = self._parse_criteria(criteria)
        sender = (sender or '').strip()
        if sender:
            senders = [s.strip() for s in re.split(r'[;,]', sender) if s.strip()]
            if len(senders) == 1:
                args.extend(['FROM', f'"{senders[0]}"'])
            else:
                # Multiple senders handled via _search_multi_sender, skip FROM here
                pass
        subject_contains = (subject_contains or '').strip()
        if subject_contains:
            args.extend(['SUBJECT', f'"{subject_contains}"'])
        return args

    def _search_messages(self, client, criteria: str, sender: str, subject_contains: str) -> list[bytes]:
        senders = [s.strip() for s in re.split(r'[;,]', sender) if s.strip()] if sender else []
        if len(senders) <= 1:
            search_args = self._build_search_args(criteria, sender, subject_contains)
            status, found = client.search(None, *search_args)
            if status != 'OK':
                raise RuntimeError(f'Failed to search mailbox with criteria: {criteria}')
            return found[0].split() if found and found[0] else []
        else:
            # Multiple senders: search each individually, merge and deduplicate preserving order
            seen = set()
            all_ids = []
            for s in senders:
                search_args = self._build_search_args(criteria, s, subject_contains)
                status, found = client.search(None, *search_args)
                if status != 'OK':
                    continue
                ids = found[0].split() if found and found[0] else []
                for mid in ids:
                    if mid not in seen:
                        seen.add(mid)
                        all_ids.append(mid)
            return all_ids

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        base = os.path.basename(str(filename or '').strip())
        if not base:
            return 'attachment.bin'
        # Avoid unsafe path characters while keeping names readable.
        return re.sub(r'[^A-Za-z0-9._-]+', '_', base)

    @staticmethod
    def _next_available_path(path: str) -> str:
        if not os.path.exists(path):
            return path
        root, ext = os.path.splitext(path)
        idx = 1
        while True:
            candidate = f'{root}_{idx}{ext}'
            if not os.path.exists(candidate):
                return candidate
            idx += 1

    def _extract_attachments(self, msg, uid: str, save_attachments: bool, attachments_dir: str) -> list[dict]:
        rows = []
        if save_attachments:
            os.makedirs(attachments_dir, exist_ok=True)

        seq = 1
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            filename = part.get_filename()
            if not filename:
                continue

            payload = part.get_payload(decode=True)
            if payload is None:
                try:
                    content = part.get_content()
                    payload = content.encode('utf-8') if isinstance(content, str) else bytes(content)
                except Exception:
                    payload = b''

            safe_name = self._sanitize_filename(filename)
            attachment_meta = {
                'filename': safe_name,
                'content_type': str(part.get_content_type() or ''),
                'size': len(payload),
                'saved': False,
                'saved_path': '',
            }

            if save_attachments:
                prefixed_name = f'{uid}_{seq}_{safe_name}'
                target = self._next_available_path(os.path.join(attachments_dir, prefixed_name))
                with open(target, 'wb') as fp:
                    fp.write(payload)
                attachment_meta['saved'] = True
                attachment_meta['saved_path'] = target

            rows.append(attachment_meta)
            seq += 1

        return rows

    def process(self):
        fail_on_error = self._as_yes(self.explain_param_or_default('fail_on_error', 'yes'))
        data_key = self.explain_param_or_default('data_key', 'emails')
        attachments_key = self.explain_param_or_default('attachments_key', '').strip()
        result_key = self.explain_param_or_default('result_key', '').strip()
        detail_level = self.explain_param_or_default('detail_level', 'detail').strip().lower()

        client = None
        try:
            host = self.explain_param_or_default('host', '').strip()
            port = self.explain_param_as_int('port', 993)
            name = self.explain_param_or_default('name', '').strip()
            pwd = self.explain_param_or_default('pwd', '').strip()
            mailbox = self.explain_param_or_default('mailbox', 'INBOX').strip() or 'INBOX'
            criteria = self.explain_param_or_default('criteria', 'UNSEEN')
            sender = self.explain_param_or_default('sender', '').strip()
            subject_contains = self.explain_param_or_default('subject_contains', '').strip()
            limit = self.explain_param_as_int('limit', 10)
            use_ssl = self._as_yes(self.explain_param_or_default('use_ssl', 'yes'))
            mark_seen = self._as_yes(self.explain_param_or_default('mark_seen', 'yes'))
            save_attachments = self._as_yes(self.explain_param_or_default('save_attachments', 'no'))
            attachments_dir = self.explain_param_or_default('attachments_dir', f'{self.get_ddir()}{os.sep}email_attachments').strip()
            timeout = float(self.explain_param_or_default('timeout', '30'))

            if not host:
                raise ValueError('host is required for RECEIVE_EMAIL')
            if not name:
                raise ValueError('name is required for RECEIVE_EMAIL')

            imap_cls = imaplib.IMAP4_SSL if use_ssl else imaplib.IMAP4
            client = imap_cls(host=host, port=port, timeout=timeout)
            client.login(name, pwd)
            try:
                client._encoding = 'utf-8'
            except Exception:
                pass

            status, _ = client.select(mailbox)
            if status != 'OK':
                raise RuntimeError(f'Failed to select mailbox: {mailbox}')

            msg_ids = self._search_messages(client, criteria, sender, subject_contains)
            if limit > 0:
                msg_ids = msg_ids[-limit:]

            fetch_query = '(RFC822)' if mark_seen else '(BODY.PEEK[])'
            result = []
            all_saved_paths = []
            for msg_id in msg_ids:
                uid = msg_id.decode(errors='ignore') if isinstance(msg_id, (bytes, bytearray)) else str(msg_id)
                status, payload = client.fetch(uid, fetch_query)
                if status != 'OK' or not payload:
                    continue

                raw_bytes = b''
                for item in payload:
                    if isinstance(item, tuple) and len(item) > 1 and isinstance(item[1], (bytes, bytearray)):
                        raw_bytes = bytes(item[1])
                        break
                if not raw_bytes:
                    continue

                msg = email.message_from_bytes(raw_bytes, policy=policy.default)
                text_body, html_body = self._extract_bodies(msg)
                attachments = self._extract_attachments(msg, uid, save_attachments, attachments_dir)
                for att in attachments:
                    saved_path = str(att.get('saved_path', '')).strip()
                    if saved_path:
                        all_saved_paths.append(saved_path)

                if detail_level == 'summary':
                    result.append({
                        'subject': str(msg.get('Subject', '')),
                        'from': str(msg.get('From', '')),
                        'to': str(msg.get('To', '')),
                        'date': str(msg.get('Date', '')),
                        'attachments': [a['filename'] for a in attachments],
                        'text_first_50': text_body[:50] + '...',
                    })
                else:
                    result.append({
                        'uid': uid,
                        'subject': str(msg.get('Subject', '')),
                        'from': str(msg.get('From', '')),
                        'to': str(msg.get('To', '')),
                        'date': str(msg.get('Date', '')),
                        'message_id': str(msg.get('Message-ID', '')),
                        'text': text_body,
                        'html': html_body,
                        'attachments': attachments,
                    })

                if mark_seen:
                    client.store(uid, '+FLAGS', '\\Seen')

            self.populate_data(data_key, result)
            if attachments_key:
                self.populate_data(attachments_key, all_saved_paths)
            if result_key:
                self.populate_data(result_key, {'ok': True, 'count': len(result), 'error': None})
            logging.info('RECEIVE_EMAIL fetched %d message(s) into %s', len(result), data_key)
        except Exception as ex:
            if fail_on_error:
                raise
            logging.error('RECEIVE_EMAIL ignored error due to fail_on_error=no: %s', ex)
            self.populate_data(data_key, [])
            if attachments_key:
                self.populate_data(attachments_key, [])
            if result_key:
                self.populate_data(result_key, {'ok': False, 'count': 0, 'error': str(ex)})
        finally:
            if client is not None:
                try:
                    client.logout()
                except Exception:
                    pass

