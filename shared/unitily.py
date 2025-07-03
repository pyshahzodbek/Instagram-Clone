import re

email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
phone_regex=re.compile(r'^\+?[1-9]\d{1,14}$'
)

def check_email_or_phone(email_or_phone):
    if re.fullmatch(email_regex,email_or_phone):
        email_or_phone='email'
    elif re.fullmatch(phone_regex,email_or_phone):
        email_or_phone='phone'
    else:
        data={
            "success":False,
            "message":"Email yoki telefon notugri"
        }
        raise ValueError(data)
    return email_or_phone

