from pathlib import Path
import os
from corsheaders.defaults import default_headers


# Global variables
CLIENT_URL = "http://localhost:8080"
#CLIENT_URL = "http://192.168.0.6:8080"
BLOCKCHAIN_OBSERVER_URL = 'https://bsc-dataseed1.binance.org:443'
BSC_TOKEN = 'UVJAQIZX2RFWE7D7YENNVY7URH7RB9IDEH'
BSC_API = 'https://api.bscscan.com/api'
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-secret-test-key-1234567890'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#SECURE_SSL_REDIRECT = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'api.bscscan.com', 'bsc-dataseed1.binance.org', 'azi-online.com', '192.168.0.6']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'rest_authtoken',

    'oauth2_provider',
    'social_django',
    'drf_social_oauth2',

    'socketio',
    'eventlet',
    
    'api',
    'interface',
    'players',
    'content',
    'games',    
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "allauth.account.middleware.AccountMiddleware",
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'azi_online.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'azi_online/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',                
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]


WSGI_APPLICATION = 'azi_online.wsgi.application'
#ASGI_APPLICATION = 'azi_online.asgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

#MEDIA_URL = '/article_images/'
#MEDIA_ROOT = os.path.join(BASE_DIR, '')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {    
    'DEFAULT_AUTHENTICATION_CLASSES': (                
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',  # django-oauth-toolkit >= 1.0.0
        'drf_social_oauth2.authentication.SocialAuthentication',
    ),
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'drf_social_oauth2.backends.DjangoOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.google.GoogleOAuth2',    
]

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

SITE_ID = 1

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_USERNAME_UNIQUE = False


CORS_ALLOWED_ORIGINS = [
    CLIENT_URL,    
    "https://api.bscscan.com:443",
    "http://httpbin.org:80",
    "http://api.bscscan.com:80",
    "http://127.0.0.1:8080",
    "https://127.0.0.1:8080",
    "http://bsc-dataseed1.binance.org:80",
    "https://azi-online.com:8080",
    "https://azi-online.com:443",
    "http://azi-online.com:8080"
]


CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False


ACCOUNT_EMAIL_VERIFICATION = 'none'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True


# Включите конфигурацию для каналов
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer', # Используйте InMemoryChannelLayer для отладки или 'channels.layers.RedisChannelLayer' для продакшена
    },
}
