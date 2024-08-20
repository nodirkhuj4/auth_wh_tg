from django.contrib import admin
from login.models import TgToken, User

# Register your models here.
@admin.register(TgToken)
class TgTokenAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'full_name', 
        'phone_number',
        'otp', 
        'timestamp',
        'used'
    ]
    
admin.site.register(User)