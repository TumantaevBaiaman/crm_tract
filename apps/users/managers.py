from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext as _


class CustomUserManager(BaseUserManager):


    def create_user(self, email, username='', password=None):
        if not email:
            raise ValueError("User must have an email")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        print(user.password)  # change password to hash
        user.is_admin = False
        user.is_staff = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)  # change password to hash
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user