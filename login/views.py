from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist

from login.serializers import LogInSerializer
from login.models import TgToken


class ValidateOTP(CreateAPIView):
    queryset = TgToken.objects.all()
    serializer_class = LogInSerializer
    
    def post(self, request, format=None):
        ser = self.serializer_class(
            data=request.data, context={'request': request}
        )
        if ser.is_valid():
            otp = request.data.get("otp")
            try:
                user = authenticate(request, otp=otp)
                print(user)
                if user:
                    last_login = user.last_login

                response = {
                    "full_name": user.username,
                    "phone_number": str(user.phone_number),
                    "telegram_id": user.tg_id,
                    "last_login": last_login
                }
                return Response(response, 200)
            except ObjectDoesNotExist:
                return Response(
                    {'reason': "OTP doesn't exist"},
                    406
                )
        return Response(
            {'reason': ser.errors}, 406)