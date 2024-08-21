import uuid
import datetime
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from login.models import User
from login.models import TgToken

class TgBackend(ModelBackend):
    def __init__(self, *args, **kwargs):
        
        self.user_model = get_user_model()

    def get_phone_number_data(self, phone_number):

        phone_number_field = getattr(settings, 'PHONE_NUMBER_FIELD', 'phone_number')
        data = {
            phone_number_field: phone_number
        }
        return data
        

    def create_user(self, tg_token, **extra_fields):

        password = self.user_model.objects.make_random_password()


        password = extra_fields.get('password', password)
        kwargs = {
            'username': tg_token.full_name,
            'tg_id': tg_token.tg_id,
            'password': password,
        }
        
        
        phone_number = tg_token.phone_number
        kwargs.update(self.get_phone_number_data(phone_number))
        user = self.user_model.objects.create_user(**kwargs)
        return user

    def authenticate(self, request, otp=None, **extra_fields):
        if otp is None:
            return

        timestamp_difference = timezone.localtime(timezone.now()) - datetime.timedelta(
            seconds=20
        )
        try:
            tg_token = TgToken.objects.get(
                otp=otp,
                used=False,
                timestamp__gte=timestamp_difference
            )
        except TgToken.DoesNotExist:
            raise TgToken.DoesNotExist

        # 3. Create new user if he doesn't exist. But, if he exists login.
        
        user = self.user_model.objects.filter(
            **self.get_phone_number_data(tg_token.phone_number)
        ).first()

        if not user:
            user = self.create_user(
                tg_token=tg_token,
                **extra_fields
            )
        tg_token.used = True
        tg_token.attempts += 1
        tg_token.save()
        return user
