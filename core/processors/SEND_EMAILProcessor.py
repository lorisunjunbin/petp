import logging
import mimetypes
import smtplib
from email.message import EmailMessage

from core.processor import Processor

class SEND_EMAILProcessor(Processor):
    TPL: str = '{"smtp":"","port":25, "name":"", "pwd":"","to":"6099012@qq.com,lori.sun@qq.com","subject":"","content":"","attachment":""}'

    DESC: str = f'''
        Send an email via a specified SMTP server. Supports plain text content and optional file attachments.
        The attachment file type is automatically detected via MIME type guessing.

        - smtp: The SMTP server hostname or IP address (supports expression, default: "")
        - port: The SMTP server port number (default: 25)
        - name: The sender email address used for both login and the "From" header (supports expression, default: "")
        - pwd: The password or app-specific password for SMTP authentication (supports expression, default: "")
        - to: The recipient email address(es), comma-separated for multiple recipients (supports expression, default: "6099012@qq.com,lori.sun@qq.com")
        - subject: The email subject line (supports expression, default: "")
        - content: The email body text content (supports expression, default: "")
        - attachment: The absolute file path of a file to attach; leave empty for no attachment (supports expression, default: "")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_EMAIL

    def process(self):
        smtp = self.expression2str(self.get_param("smtp"))
        port = int(self.expression2str(self.get_param("port")))
        name = self.expression2str(self.get_param("name"))
        pwd = self.expression2str(self.get_param("pwd"))
        to = self.expression2str(self.get_param("to"))

        subject = self.expression2str(self.get_param("subject"))
        content = self.expression2str(self.get_param("content"))
        attachment = self.expression2str(self.get_param("attachment"))

        msg = EmailMessage()

        msg['Subject'] = subject
        msg['From'] = name
        msg['To'] = to

        msg.set_content(content)

        if attachment != None and len(attachment) > 0:
            filename = attachment.split('/')[-1]
            ctype, encoding = mimetypes.guess_type(attachment)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            with open(attachment, 'rb') as fp:
                msg.add_attachment(fp.read(),
                                   maintype=maintype,
                                   subtype=subtype,
                                   filename=filename)

        with smtplib.SMTP(host=smtp, port= port) as s:
            s.login(name, pwd)
            s.send_message(msg)
            logging.info('Email sent to %s (subject: %s)', to, subject)