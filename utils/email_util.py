import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.config_loader import loader


class EmailUtil:
    @staticmethod
    def send_email(receivers: list, subject, body):
        conf = loader.load_all().mail_config
        smtp_server = conf.smtp_server
        smtp_port = conf.smtp_port
        smtp_username = conf.smtp_username
        smtp_password = conf.smtp_password
        # 创建一个带附件的邮件对象
        message = MIMEMultipart()
        message['From'] = smtp_username
        message['To'] = ', '.join(receivers)
        message['Subject'] = Header(subject, 'utf-8')

        # 添加邮件正文
        message.attach(MIMEText(body, 'plain', 'utf-8'))

        # 发送邮件
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(smtp_username, receivers, message.as_string())
            print("邮件发送成功")
        except Exception as e:
            print(f"邮件发送失败：{str(e)}")
