import socket
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, UserProfile, SMSVerification
from api.models import BonusCard
from .serializers import *
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from .models import EmailVerification
from rest_framework.parsers import JSONParser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
import random

class SendCodeView(APIView):
    def post(self, request):
        email_to = request.data.get('email')
        if not email_to:
            return Response({"error": "Email не указан"}, status=status.HTTP_400_BAD_REQUEST)

        code = random.randint(100000, 999999)
        subject = "Ваш код подтверждения"
        message = f"Ваш код: {code}"

        try:
            send_mail(
                subject,
                message,
                'kubanychmuhtarov@gmail.com',  # твой Gmail
                [email_to],
                fail_silently=False,
            )
        except (socket.timeout, ConnectionRefusedError):
            return Response({"error": "Ошибка соединения с SMTP. Проверь интернет/порты."},
                            status=status.HTTP_504_GATEWAY_TIMEOUT)
        except BadHeaderError:
            return Response({"error": "Неверный заголовок письма"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Код отправлен", "code": code}, status=status.HTTP_200_OK)
class VerifyEmailCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        record = EmailVerification.objects.filter(
            email=email,
            code=code,
            is_used=False
        ).order_by('-created_at').first()

        if not record:
            return Response({"error": "Неверный код"}, status=400)

        record.is_used = True
        record.save()

        user = User.objects.filter(email=email).first()
        if user:
            user.is_email_verified = True
            user.save()

        return Response({"message": "Email подтверждён"})



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']

        if User.objects.filter(phone_number=phone_number).exists():
            return Response(
                {'error': 'Пользователь с таким номером уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            phone_number=phone_number,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_phone_verified=False
        )

        UserProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name
        )

        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        SMSVerification.objects.create(phone_number=phone_number, code=code)

        print(f"Код подтверждения для {phone_number}: {code}")

        return Response({
            'message': 'Код подтверждения отправлен',
            'user_id': user.id,
            'verification_code': code,  # В реальном проекте убрать!
            'next_step': 'Используйте этот код для подтверждения телефона в /api/auth/verify-code/'
        }, status=status.HTTP_201_CREATED)


class VerifyCodeView(generics.CreateAPIView):
    serializer_class = VerifyCodeSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        try:
            verification = SMSVerification.objects.filter(
                phone_number=phone_number,
                code=code,
                is_used=False
            ).latest('created_at')

            user = User.objects.get(phone_number=phone_number)
            user.is_phone_verified = True
            user.save()

            card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
            BonusCard.objects.create(user=user, card_number=card_number)

            verification.is_used = True
            verification.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Карта успешно создана! Теперь вы можете экономить на покупках.',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'phone_number': user.phone_number,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })

        except SMSVerification.DoesNotExist:
            return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']

        user = authenticate(phone_number=phone_number, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'phone_number': user.phone_number,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })

        return Response({'error': 'Неверный номер или пароль'}, status=status.HTTP_401_UNAUTHORIZED)


class ForgotPasswordView(generics.CreateAPIView):
    """1. Этап: Ввод номера телефона для получения кода"""
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']

        try:
            user = User.objects.get(phone_number=phone_number)

            # Генерируем 4-значный код
            code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            SMSVerification.objects.create(phone_number=phone_number, code=code)

            print(f"Код для сброса пароля для {phone_number}: {code}")

            return Response({
                'message': 'Код отправлен на ваш номер телефона',
                'reset_code': code,  # В реальном проекте убрать!
                'next_step': 'Используйте этот код для подтверждения в /api/auth/verify-reset-code/'
            })

        except User.DoesNotExist:
            return Response({'error': 'Пользователь с таким номером не найден'},
                            status=status.HTTP_404_NOT_FOUND)


class VerifyResetCodeView(generics.CreateAPIView):
    """2. Этап: Подтверждение кода из SMS"""
    serializer_class = VerifyResetCodeSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        try:
            verification = SMSVerification.objects.filter(
                phone_number=phone_number,
                code=code,
                is_used=False
            ).latest('created_at')

            # Помечаем код как использованный для сброса пароля
            verification.is_used = True
            verification.save()

            return Response({
                'message': 'Код подтвержден успешно',
                'next_step': 'Теперь вы можете установить новый пароль в /api/auth/reset-password/'
            })

        except SMSVerification.DoesNotExist:
            return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(generics.CreateAPIView):
    "3. Этап: Установка нового пароля"
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        try:
            # Проверяем что код был использован на предыдущем этапе
            verification = SMSVerification.objects.filter(
                phone_number=phone_number,
                code=code,
                is_used=True
            ).latest('created_at')

            user = User.objects.get(phone_number=phone_number)
            user.set_password(new_password)
            user.save()

            return Response({'message': 'Пароль успешно изменен'})

        except SMSVerification.DoesNotExist:
            return Response({'error': 'Сначала подтвердите код через /api/auth/verify-reset-code/'},
                            status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    """Профиль пользователя (старая версия)"""
    if request.method == 'GET':
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)