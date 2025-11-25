from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),  # 1. Ввод номера
    path('verify-reset-code/', VerifyResetCodeView.as_view(), name='verify_reset_code'),  # 2. Ввод кода
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),  # 3. Новый пароль
    path('profile/',ProfileView.as_view(), name='profile'),
    path('email/send-code/', SendCodeView.as_view(), name='send_email_code'),
    path('email/verify-code/', VerifyEmailCodeView.as_view(), name='verify_email_code'),

]