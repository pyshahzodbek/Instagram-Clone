import re
import threading
from django.core.mail import EmailMessage

from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError  # agar DRF bo'lsa

email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
phone_regex = re.compile(r"^\+?[1-9]\d{9,14}$")  # +998901234567 kabi formatga mos

def check_email_or_phone(email_or_phone):
    if re.fullmatch(email_regex, email_or_phone):
        return 'via_email'
    elif re.fullmatch(phone_regex, email_or_phone):
        return 'via_phone'
    else:
        data = {
            "success": False,
            "message": "Email yoki telefon noto‘g‘ri"
        }
        raise ValidationError(data)

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )
        if data.get('content_type') == "html":
            email.content_subtype = 'html'
        EmailThread(email).start()


def send_email(email, code):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {"code": code}
    )
    Email.send_email(
        {
            "subject": "Royhatdan otish",
            "to_email": email,
            "body": html_content,
            "content_type": "html"
        }
    )


