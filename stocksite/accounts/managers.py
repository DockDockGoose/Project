from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class AccountManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, username):
        """
        Create and save a Account with the given userId.
        """
        if not username:
            raise ValueError(_('The username must be set'))

        account = self.model(username=username, **extra_fields)
        account.save()

        return account

    def create_superuser(self, username, **extra_fields):
        """
        Create and save a SuperUser with the given username and password.
        """
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(username, **extra_fields)