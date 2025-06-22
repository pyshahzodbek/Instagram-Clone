from django.contrib.auth.models import AbstractUser
from django.db import models
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
    photo=models.ImageField(upload_to='user_photo/',null=True,blank=True)

    def __str__(self):
        return self.username


