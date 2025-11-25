from pathlib import Path
import os
from decouple import config


# Пути проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность
SECRET_KEY = 'django-insecure-+4_8yd)_@s!6)y^gk#e8z8@bedu^re%h3uu-_q8$(chyha(yum)'

DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['applemob.onrender.com', 'localhost', '127.0.0.1']

# Статика
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Приложения
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'corsheaders',

    'rest_framework',

    'api',
    'users',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ДОЛЖЕН БЫТЬ ПОСЛЕ SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# URL конфигурация
ROOT_URLCONF = 'core.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'core.wsgi.application'

# База данных (SQLite для простого старта)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Локализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Статика

# Кастомная модель пользователя
AUTH_USER_MODEL = 'users.User'

# Авто-поля
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки почты для разработки (выводит письма в консоль)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'kubanychmuhtarov@gmail.com'


# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'kubanychmuhtarov@gmail.com'
# EMAIL_HOST_PASSWORD = 'yqfr dluj opnx kyyj'  # пароль для приложений
#

#
# INSTALLED_APPS += ['anymail']
#
# EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
# ANYMAIL = {
#     "SENDGRID_API_KEY": "твой_sendgrid_api_key",
# }
# DEFAULT_FROM_EMAIL = "kubanychmuhtarov@gmail.com"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Авто-создание суперпользователя
import os

if not os.environ.get('SUPERUSER_CREATED'):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='kubanychmuhtarov@gmail.com',
            password='1234'  # Поменяйте пароль!
        )
        os.environ['SUPERUSER_CREATED'] = '1'
