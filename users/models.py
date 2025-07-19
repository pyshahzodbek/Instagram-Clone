import uuid
from datetime import datetime, timedelta
import random

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from unicodedata import normalize

from shared.models import BaseModels

MANAGER,ADMIN,ODDIY=("MANAGER",'ADMIN','ODDIY')
VIA_PHONE,VIA_EMAIL=('via_phone','via_email')
NEWS,CODE_VEFIRED,DONE,PHOTO_STEP=('NEW','CODE_VEFIRED','DONE','PHOTO_STEP')

class Users(AbstractUser,BaseModels):
    USER_ROLES=(
        (MANAGER,MANAGER),
        (ADMIN,ADMIN),
        (ODDIY,ODDIY)
    )
    AUTH_TYPE=(
        (VIA_EMAIL,VIA_EMAIL),
        (VIA_PHONE,VIA_PHONE)
    )
    AUTH_STATUS=(
        (NEWS,NEWS),
        (CODE_VEFIRED,CODE_VEFIRED),
        (DONE,DONE),
        (PHOTO_STEP,PHOTO_STEP)
    )

    user_roles=models.CharField(max_length=31,choices=USER_ROLES,default=ODDIY)
    auth_type=models.CharField(max_length=31,choices=AUTH_TYPE)
    auth_status=models.CharField(max_length=31,choices=AUTH_STATUS,default=NEWS)
    email=models.EmailField(null=True,unique=True ,blank=True)
    phone_number=models.CharField(max_length=13,null=True,unique=True , blank=True)
    photo = models.ImageField(
        upload_to='user_photo/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heic', 'heif'])]
    )
    def __str__(self):
        return self.username


    @property
    def full_name(self):
        return self.username
    def create_verify_code(self,verify_type):
        code = "".join([str(random.randint(0, 9)) for _ in range(4)])
        UserConfirmation.objects.create(
            user_id=self.id,
            verify_type=verify_type,
            code=code
        )
        return code
    def check_username(self):
        if not self.username:
            temp_username = f'instagram-{uuid.uuid4().__str__().split("-")[-1]}'  # instagram-23324fsdf
            while Users.objects.filter(username=temp_username):
                temp_username = f"{temp_username}{random.randint(0, 1000)}"
            self.username = temp_username

    def check_email(self):
        if self.email:
            normalize_email=self.email.lower()
            self.email=normalize_email

    def check_pass(self):
        if not self.password:
            temp_password=f"password-{uuid.uuid4().__str__().split("-")[-1]}"
            self.password=temp_password

    def hashing_password(self):
        if not self.password.startswith("pbkdf2_sha256"):
            self.set_password(self.password)

    def token(self):
        refresh=RefreshToken.for_user(self)
        return {
            "access":str(refresh.access_token),
            "refresh_token":str(refresh)
        }

    def clean(self):
        self.check_username()
        self.check_email()
        self.check_pass()
        self.hashing_password()

    def save(self,*args,**kwargs):
        self.clean()
        super(Users,self).save(*args,**kwargs)








PHONE_EXPRE=2
EMAIL_EXPRE=5

class UserConfirmation(BaseModels):
    TYPE_CHOISE=(
        (VIA_EMAIL,VIA_EMAIL),
        (VIA_PHONE,VIA_PHONE)
    )
    code=models.CharField(max_length=4)
    verify_type=models.CharField(max_length=31,choices=TYPE_CHOISE)
    user=models.ForeignKey('users.Users',models.CASCADE,related_name='verify_code')
    expiration_time=models.DateTimeField(null=True)
    is_confirmed=models.BooleanField(default=False)


    def __str__(self):
        return str(self.user.__str__())

    def save(self,*args,**kwargs):

        if self.verify_type==VIA_EMAIL:
                self.expiration_time=datetime.now()+timedelta(minutes=EMAIL_EXPRE)
        else:
                self.expiration_time=datetime.now()+timedelta(minutes=PHONE_EXPRE)

        super(UserConfirmation,self).save(*args,**kwargs)


