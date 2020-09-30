from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.utils import timezone

User = get_user_model()


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email_address = serializers.EmailField(
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
        max_length=128
    )
    account_created = serializers.DateTimeField(read_only=True)
    account_updated = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.set_password(validated_data.get('password', instance.password))
        instance.email_address = validated_data.get('email_address', instance.email_address)
        instance.account_updated = timezone.now()
        instance.save()
        return instance