from rest_framework import serializers
from .models import User, UserProfile


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    phone_number = serializers.CharField(max_length=20, required=True)
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs


class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=True)
    code = serializers.CharField(max_length=6, required=True)


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=True)
    password = serializers.CharField(write_only=True, required=True)


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=20,
        required=True,
        help_text="Введите номер телефона для получения кода сброса пароля"
    )


class VerifyResetCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=True)
    code = serializers.CharField(
        max_length=4,
        required=True,
        help_text="Введите 4-значный код из SMS"
    )


class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=True)
    code = serializers.CharField(max_length=4, required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Введите новый пароль"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Повторите новый пароль"
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Пароли не совпадают"})
        return attrs

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Пароли не совпадают"})
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user',)