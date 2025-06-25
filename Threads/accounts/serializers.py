from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils.translation import gettext_lazy as _
from accounts.models import User  # modelingizga moslashtiring

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'first_name', 'last_name', 'bio', 'photo') 


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    photo = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'first_name', 'last_name', 'bio', 'photo', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("login")
        password = attrs.get("password")

        user = None

        # Har xil maydonlar orqali aniqlashga harakat qilamiz
        if "@" in identifier:
            try:
                user_obj = User.objects.get(email=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError(_("Email noto‘g‘ri"))
        elif identifier.startswith("+") or identifier.isdigit():
            try:
                user_obj = User.objects.get(phone=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError(_("Telefon raqam noto‘g‘ri"))
        else:
            try:
                user_obj = User.objects.get(username=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError(_("Username noto‘g‘ri"))

        # Parolni tekshirish
        if not user_obj.check_password(password):
            raise serializers.ValidationError(_("Parol noto‘g‘ri"))

        if not user_obj.is_active:
            raise serializers.ValidationError(_("Foydalanuvchi aktiv emas"))

        attrs["user"] = user_obj
        return attrs
    


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError(_("Token allaqachon yaroqsiz yoki noto‘g‘ri"))