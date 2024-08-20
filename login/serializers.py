from rest_framework import serializers

from login.models import TgToken

class LogInSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6)

    class Meta:
        model=TgToken
        fields=('otp',)
