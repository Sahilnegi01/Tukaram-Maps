from abc import ABC, abstractmethod
from email.message import EmailMessage
import aiosmtplib
from app.core.config import get_settings
class EmailService(ABC):
    @abstractmethod
    async def send_review(self,recipient,subject,html): ...
class SMTPEmailService(EmailService):
    async def send_review(self,recipient,subject,html):
        s=get_settings(); msg=EmailMessage(); msg["From"]="noreply@enforcement-map.local"; msg["To"]=recipient; msg["Subject"]=subject; msg.set_content("Open the HTML version to review this action."); msg.add_alternative(html,subtype="html")
        await aiosmtplib.send(msg,hostname=s.smtp_host,port=s.smtp_port,username=s.smtp_username or None,password=s.smtp_password or None)

