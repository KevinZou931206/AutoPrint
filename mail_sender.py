"""
邮件发送模块
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import os
from datetime import datetime
from logger import logger

class EmailSender:
    """邮件发送类"""
    def __init__(self):
        # 读取环境变量中的邮箱配置
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.qq.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 465))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        self.receiver_email = os.getenv('RECEIVER_EMAIL', '')
        
    def is_configured(self):
        """检查邮件配置是否完整"""
        return (self.smtp_server and self.sender_email and 
                self.sender_password and self.receiver_email)
    
    def send_error_notification(self, subject, error_message, stack_trace=None):
        """发送错误通知邮件"""
        if not self.is_configured():
            logger.error("邮件配置不完整，无法发送邮件")
            return False
        
        try:
            # 创建邮件内容
            message = MIMEMultipart()
            # 正确设置From头，使用formataddr确保符合RFC标准
            message['From'] = formataddr(("自动化打单配货程序", self.sender_email))
            message['To'] = self.receiver_email
            message['Subject'] = Header(f"{subject} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'utf-8')
            
            # 邮件正文
            content = f"""
            <html>
            <body>
                <h2>自动化打单配货程序异常通知</h2>
                <p><strong>错误时间：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>错误信息：</strong>{error_message}</p>
            """
            
            if stack_trace:
                content += f"""
                <p><strong>错误堆栈：</strong></p>
                <pre>{stack_trace}</pre>
                """
                
            content += """
            </body>
            </html>
            """
            
            message.attach(MIMEText(content, 'html', 'utf-8'))
            
            # 发送邮件
            if self.smtp_port == 465:
                # 使用SSL连接
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                # 使用普通连接
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()  # 启用TLS加密
                
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, self.receiver_email, message.as_string())
            server.quit()
            
            logger.info(f"错误通知邮件已发送至 {self.receiver_email}")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            return False

# 创建全局邮件发送器实例
email_sender = EmailSender() 