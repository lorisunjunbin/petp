import logging
import mimetypes
import smtplib
from email.message import EmailMessage

from core.processor import Processor

class SEND_EMAILProcessor(Processor):
    TPL: str = '{"smtp":"","port":25, "name":"", "pwd":"","to":"6099012@qq.com,lori.sun@qq.com","subject":"","content":"","attachment":""}'

    DESC: str = f'''
        Able to send email from given smtp.
       {TPL}
       
    '''
    def process(self):
        smtp = self.expression2str(self.get_param("smtp"))
        port = self.get_param("port")
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

        if len(attachment) > 0:
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
            logging.debug("email successfully sent! ")