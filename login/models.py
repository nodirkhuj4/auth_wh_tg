import os
import datetime
import hashlib


from phonenumber_field.modelfields import PhoneNumberField

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.db import models
from django.utils import timezone





class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, phone_number,
                     password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        username = self.model.normalize_username(username)
        user = self.model(
            username=username, phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, phone_number,
                             password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, phone_number, password,
                                 **extra_fields)

    def create_superuser(self, username, phone_number, password,
                         **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, phone_number, password,
                                 **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = PhoneNumberField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(max_length=100)
    tg_id = models.CharField(max_length=90)
    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    
    def __str__(self) -> str:
        return self.username
        




class TgToken(models.Model):
    phone_number = PhoneNumberField(editable=False)
    tg_id = models.CharField(max_length=90)
    full_name = models.CharField(max_length=100)
    otp = models.CharField(max_length=40, editable=False)
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    attempts = models.IntegerField(default=0)
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "OTP Token"
        verbose_name_plural = "OTP Tokens"

    def __str__(self):
        return "{} - {}".format(self.phone_number, self.otp)

    @classmethod
    def create_otp_for_tg(cls, tg_id, phone_number, full_name):

        timestamp_difference = timezone.localtime(timezone.now()) - datetime.timedelta(
            seconds=20
        )

        otps = cls.objects.filter(
            tg_id=tg_id, 
            used=False,
            timestamp__gte=timestamp_difference
        )

        if otps.exists():
            return False
        
        otp = cls.generate_otp()
        tg_token = TgToken(
            tg_id=tg_id, 
            phone_number=phone_number, 
            otp=otp,
            full_name=full_name
        )

        tg_token.save()
        return otp
    

    @classmethod
    def generate_otp(cls, length=6):
        hash_algorithm = 'sha256'
        m = getattr(hashlib, hash_algorithm)()
        m.update(getattr(settings, 'SECRET_KEY', None).encode('utf-8'))
        m.update(os.urandom(16))
        otp = str(int(m.hexdigest(), 16))[-length:]
        return otp