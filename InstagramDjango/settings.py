from pathlib import Path
from datetime import timedelta
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(_file_).resolve().parent.parent

import os
from decouple import config
import dj_database_url
from cryptography.fernet import Fernet

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ipg=fxwoc(c47cvfml)9634=bhp6%p)84y(pwu7(5d^!-eqr'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = [*]
ALLOWED_HOSTS = ['astrolemon.onrender.com', 'localhost', '127.0.0.1', '159.203.44.134', '*']

AUTH_USER_MODEL = "accounts.CustomUser"

CLIENT_URL = 'http://127.0.0.1:8000'


from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'perform-instagram-tasks-every-30-minutes': {
        'task': 'InstagramDjangoApp.tasks.schedule_instagram_tasks',  # Ensure this is correct
        # 'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'schedule': crontab(minute=0, hour='*/12'),  # Every 12 hours
        # 'schedule': crontab(minute=0, hour=0),  # Every day at midnight
    },
}

CELERY_BROKER_URL = 'rediss://red-cracaa5ds78s73cr8eq0:uIwNua8gEWPIvHb3J7uDIOOJC9MhHUAb@oregon-redis.render.com:6379'
CELERY_RESULT_BACKEND = 'rediss://red-cracaa5ds78s73cr8eq0:uIwNua8gEWPIvHb3J7uDIOOJC9MhHUAb@oregon-redis.render.com:6379'
CELERY_IMPORTS = ['InstagramDjangoApp.tasks']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'InstagramDjangoApp.apps.InstagramdjangoappConfig',
    "rest_framework",
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_celery_beat',
    "rest_framework.authtoken",
    'drf_spectacular',
]

STRIPE_SECRET_KEY = "sk_test_51PfoFIGdWNCS6S2AxrbzhTVpVj48M6K93ckImG65Kv22bwXsKdtMPiMeQrwkC1Y1dzpR3mbDVQBAnhhtrCh51LKi00pDplQCBo"
STRIPE_WEBHOOK_SECRET = 'we_1PwrfUGdWNCS6S2A572bqekt'

STRIPE_PLAN_IDS_BASIC = 'price_1PniXeGdWNCS6S2ANAsPtGrA'
STRIPE_PLAN_IDS_MEDIUM = 'price_1PniD3GdWNCS6S2A3jRkGUBp'
STRIPE_PLAN_IDS_PREMIUM = 'price_1PniDuGdWNCS6S2AhT49vOd7'

REST_FRAMEWORK = {
    "NON_FIELD_ERRORS_KEY": "errors",
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "InstagramDjango.pagination.CustomPagination",
    "PAGE_SIZE": 10,
}

ENCRYPTION_KEY = 'q1Ga2jyQI714puuXRkERcKJUiQvpFREDmIJo2b4Xg0s='

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}


SPECTACULAR_SETTINGS = {
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "DEFAULT_GENERATOR_CLASS": "drf_spectacular.generators.SchemaGenerator",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "COMPONENT_SPLIT_PATCH": True,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
    },
    "UPLOADED_FILES_USE_URL": True,
    "TITLE": "AstraLemon",
    "DESCRIPTION": "AstraLemon APIs",
    "VERSION": "1.0.0",
    "LICENCE": {"name": "BSD License"},
    "CONTACT": {"name": "Macsauce", "email": "brasheed240@gmail.com"},
}

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    
]

ROOT_URLCONF = 'InstagramDjango.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ['templates'],
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

WSGI_APPLICATION = 'InstagramDjango.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DATABASES["default"] = dj_database_url.parse('postgres://postgres.attklowsmdgjlxhwtmqd:Astrolemondb100%@aws-0-us-west-1.pooler.supabase.com:6543/postgres')

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

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['https://astrolemon.onrender.com']

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'brasheed240@gmail.com'
EMAIL_HOST_PASSWORD = 'vhghnszeyyqmxohc'
EMAIL_USE_SSL = True
