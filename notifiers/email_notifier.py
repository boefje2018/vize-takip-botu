import os
import smtplib
from email.message import EmailMessage


class EmailNotifier:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "")
        port_str = os.getenv("SMTP_PORT", "")
        self.smtp_port = int(port_str) if port_str else 587
        self.email_address = os.getenv("EMAIL_ADDRESS", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.email_to = os.getenv("EMAIL_TO", "")
        self.enabled = bool(self.smtp_server and self.email_address and self.email_password and self.email_to)

    def send(self, subject: str, body: str) -> bool:
        if not self.enabled:
            return False
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = self.email_address
            msg["To"] = self.email_to
            msg.set_content(body)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.starttls()
                smtp.login(self.email_address, self.email_password)
                smtp.send_message(msg)
            return True
        except Exception:
            return False
