from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class UsernameOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, phone_number=None, **kwargs):
        user = None
        if phone_number:
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                return None
        elif username:
            return super().authenticate(request, username=username, password=password, **kwargs)
        if user and user.check_password(password):
            return user
        return None
