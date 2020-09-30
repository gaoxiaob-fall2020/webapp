from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import uuid
from django.utils import timezone


class UserManager(BaseUserManager):
    def create(self, **args):
        required_args = ['first_name', 'last_name', 'email_address', 'password'] 
        for arg in required_args: 
            if arg not in args:
                raise ValueError(f'User creation requires: {required_args}')

        user = self.model(
            first_name = args['first_name'], 
            last_name = args['last_name'],
            email_address = self.normalize_email(args['email_address']),
        )
        user.set_password(args['password'])
        user.save(using=self._db)
        return user

    def create_superuser(self, **args):
        user = self.create(**args)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    # password
    email_address = models.EmailField(
        max_length=255, 
        unique=True,
    )
    account_created = models.DateTimeField(
        default=timezone.now,
        editable=False
    )
    account_updated = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email_address'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return f'{self.email_address}'
    
