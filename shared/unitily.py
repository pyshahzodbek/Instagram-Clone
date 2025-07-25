import re
import threading
from django.core.mail import EmailMessage
import phonenumbers
from decouple import config

from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
from twilio.rest import Client

email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
phone_regex = re.compile(r"(\+[0-9]+\s*)?(\([0-9]+\))?[\s0-9\-]+[0-9]+")
username_regex=re.compile(r"^[a-zA-Z0-9_.-]+$")

def check_email_or_phone(email_phone_number):

    if re.fullmatch(email_regex, email_phone_number):
        return 'via_email'
    try:
        phone_number = phonenumbers.parse(email_phone_number, None)
        if phonenumbers.is_valid_number(phone_number):
             return 'via_phone'
    except phonenumbers.NumberParseException:
        pass

    else:
        data = {
            "success": False,
            "message": "Email yoki telefon noto‘g‘ri"
        }
        raise ValidationError(data)
def check_auth_type(user_input):
    if re.fullmatch(email_regex,user_input):
        return "email"

    elif re.fullmatch(username_regex,user_input):
        return "username"
    try:
        phone_number = phonenumbers.parse(user_input, None)
        if phonenumbers.is_valid_number(phone_number):
             return 'phone'
    except phonenumbers.NumberParseException:
        pass

    else:
        data={
            "success":False,
            "message":"Email , Username yoki telefon noto'g'ri!"
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


def send_phone_code(phone,code):
    account_sid=config('account_sid')
    auth_token=config('auth_token')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"Your verification code is {code}",
        from_='+14155238886',
        to=phone
    )



