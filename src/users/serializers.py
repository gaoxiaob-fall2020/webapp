import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()


# Custom password validator
def pwdValidator(pwd):
    if len(pwd) <= 8:
        raise ValidationError('Password must contain at least 9 characters.')
    if not re.search('[A-Z]', pwd) or not re.search('[0-9]', pwd) or not re.search('[@#?!+%]', pwd):
        raise ValidationError(
            'Enter a password with at least 1 uppercase letter, 1 number, and 1 special character in [@#?!+%].'
        )


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    username = serializers.EmailField(
        # read_only=True,
        max_length=255,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='User with that email already exists'
            )
        ]
    )
    password = serializers.CharField(
        write_only=True,
        max_length=128,
        validators=[pwdValidator]
    )
    account_created = serializers.DateTimeField(read_only=True)
    account_updated = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.set_password(validated_data.get('password', instance.password))
        instance.username = validated_data.get('username', instance.username)
        instance.account_updated = timezone.now()
        instance.save()
        return instance
