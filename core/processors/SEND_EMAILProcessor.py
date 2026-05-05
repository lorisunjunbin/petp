import logging
import mimetypes
import os
import ssl
import smtplib
from email.message import EmailMessage

from core.processor import Processor

class SEND_EMAILProcessor(Processor):
    TPL: str = '{"smtp":"","port":25, "name":"", "pwd":"","to":"6099012@qq.com,lori.sun@qq.com","cc":"","bcc":"","subject":"","content":"","content_type":"plain","attachment":"","attachments":"","use_tls":"no","use_ssl":"no","timeout":"30","fail_on_error":"yes","result_key":""}'

    DESC: str = '''
        Send an email via a specified SMTP server.
        Supports plain/html content, CC/BCC, and one-or-more attachments.

        - smtp: The SMTP server hostname or IP address (supports expression, default: "")
        - port: The SMTP server port number (default: 25)
        - name: The sender email address used for both login and the "From" header (supports expression, default: "")
        - pwd: The password or app-specific password for SMTP authentication (supports expression, default: "")
        - to: The recipient email address(es), comma-separated for multiple recipients (supports expression, default: "6099012@qq.com,lori.sun@qq.com")
        - cc: Optional CC recipient address(es), comma-separated (supports expression, default: "")
        - bcc: Optional BCC recipient address(es), comma-separated (supports expression, default: "")
        - subject: The email subject line (supports expression, default: "")
        - content: The email body text content (supports expression, default: "")
        - content_type: "plain" or "html" for body content (supports expression, default: "plain")
        - attachment: Legacy single attachment path (supports expression, default: "")
        - attachments: Multiple attachment paths separated by comma/semicolon/newline (supports expression, default: "")
        - use_tls: "yes" to enable STARTTLS (default: "no")
        - use_ssl: "yes" to use SMTP over SSL directly (default: "no")
        - timeout: SMTP connection timeout seconds (supports expression, default: "30")
        - fail_on_error: "yes" to raise error; "no" to log and continue (default: "yes")
        - result_key: data_chain key to store send result {"ok": bool, "error": str|None}; only written when set (default: "")
    '''

    def get_category(self) -> str:
        return super().CATE_EMAIL

    @staticmethod
    def _split_list(raw: str) -> list[str]:
        if not raw:
            return []
        normalized = raw.replace(';', ',').replace('\n', ',')
        return [item.strip() for item in normalized.split(',') if item and item.strip()]

    def _resolve_attachments(self, single_path: str, multiple_paths: str) -> list[str]:
        merged = []
        if single_path and single_path.strip():
            merged.append(single_path.strip())
        merged.extend(self._split_list(multiple_paths))

        # Keep ordering stable but drop duplicates.
        deduped = []
        seen = set()
        for path in merged:
            if path in seen:
                continue
            seen.add(path)
            deduped.append(path)
        return deduped

    @staticmethod
    def _add_attachment(msg: EmailMessage, attachment_path: str) -> None:
        filename = os.path.basename(attachment_path)
        ctype, encoding = mimetypes.guess_type(attachment_path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(attachment_path, 'rb') as fp:
            msg.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=filename)

    @staticmethod
    def _as_yes(value: str) -> bool:
        return str(value).strip().lower() == 'yes'

    def process(self):
        fail_on_error = self._as_yes(self.explain_param_or_default('fail_on_error', 'yes'))
        result_key = self.explain_param_or_default('result_key', '').strip()

        try:
            smtp = self.explain_param_or_default('smtp', '').strip()
            port = self.explain_param_as_int('port', 25)
            name = self.explain_param_or_default('name', '').strip()
            pwd = self.explain_param_or_default('pwd', '').strip()

            to = self._split_list(self.explain_param_or_default('to', ''))
            cc = self._split_list(self.explain_param_or_default('cc', ''))
            bcc = self._split_list(self.explain_param_or_default('bcc', ''))

            subject = self.explain_param_or_default('subject', '')
            content = self.explain_param_or_default('content', '')
            content_type = self.explain_param_or_default('content_type', 'plain').strip().lower()
            use_tls = self._as_yes(self.explain_param_or_default('use_tls', 'no'))
            use_ssl = self._as_yes(self.explain_param_or_default('use_ssl', 'no'))
            timeout = float(self.explain_param_or_default('timeout', '30'))

            legacy_attachment = self.explain_param_or_default('attachment', '')
            attachments = self.explain_param_or_default('attachments', '')
            attachment_paths = self._resolve_attachments(legacy_attachment, attachments)

            if not smtp:
                raise ValueError('smtp is required for SEND_EMAIL')
            if not (to or cc or bcc):
                raise ValueError('at least one recipient is required (to/cc/bcc)')

            msg = EmailMessage()
            msg['Subject'] = subject
            if name:
                msg['From'] = name
            if to:
                msg['To'] = ', '.join(to)
            if cc:
                msg['Cc'] = ', '.join(cc)

            if content_type == 'html':
                # Keep a plain fallback for clients that do not render HTML.
                msg.set_content('This email contains HTML content.')
                msg.add_alternative(content, subtype='html')
            else:
                msg.set_content(content)

            for attachment_path in attachment_paths:
                if not os.path.isfile(attachment_path):
                    raise FileNotFoundError(f'Attachment not found: {attachment_path}')
                self._add_attachment(msg, attachment_path)

            use_ssl_effective = use_ssl
            use_tls_effective = use_tls

            if (not use_ssl) and use_tls and port == 465:
                # 465 is implicit SSL in most providers; STARTTLS is typically for 587.
                use_ssl_effective = True
                use_tls_effective = False
                logging.warning('Port 465 with use_tls=yes detected. Auto-switching to implicit SSL.')

            if use_ssl and use_tls:
                # Common practice: 465 for implicit SSL, 587/25 for STARTTLS.
                if port in (587, 25):
                    use_ssl_effective = False
                    use_tls_effective = True
                    logging.warning('Both use_ssl and use_tls are enabled on port %s. Using STARTTLS.', port)
                else:
                    use_ssl_effective = True
                    use_tls_effective = False
                    logging.warning('Both use_ssl and use_tls are enabled on port %s. Using implicit SSL.', port)

            smtp_client_cls = smtplib.SMTP_SSL if use_ssl_effective else smtplib.SMTP

            with smtp_client_cls(host=smtp, port=port, timeout=timeout) as s:
                if use_tls_effective and not use_ssl_effective:
                    s.starttls()
                if name and pwd:
                    s.login(name, pwd)
                recipients = to + cc + bcc
                s.send_message(msg, to_addrs=recipients)

            logging.info('Email sent to %s (subject: %s)', ','.join(to + cc + bcc), subject)
            if result_key:
                self.populate_data(result_key, {'ok': True, 'error': None})
        except ssl.SSLError as ex:
            msg = str(ex)
            if 'WRONG_VERSION_NUMBER' in msg:
                raise RuntimeError(
                    f'SMTP SSL handshake failed ({msg}). Check port/security mode: '
                    f'use_ssl=yes usually with 465; use_tls=yes usually with 587.'
                ) from ex
            if fail_on_error:
                raise
            logging.error('SEND_EMAIL ignored SSL error due to fail_on_error=no: %s', ex)
            if result_key:
                self.populate_data(result_key, {'ok': False, 'error': str(ex)})
        except Exception as ex:
            if fail_on_error:
                raise
            logging.error('SEND_EMAIL ignored error due to fail_on_error=no: %s', ex)
            if result_key:
                self.populate_data(result_key, {'ok': False, 'error': str(ex)})
