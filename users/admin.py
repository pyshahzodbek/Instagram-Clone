from django.contrib import admin

from  .models import Users,UserConfirmation

class UserModelAdmin(admin.ModelAdmin):
    list_display = ['id','email','phone_number']

admin.site.register(Users,UserModelAdmin)
admin.site.register(UserConfirmation)
