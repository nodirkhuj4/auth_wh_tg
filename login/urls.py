from django.urls import path

from login.views import ValidateOTP

urlpatterns = [
    path('validate', 
         ValidateOTP.as_view(), 
         name='validate_otp'
    )
]