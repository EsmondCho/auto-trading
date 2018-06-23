from Decryptous.settings.base import *

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '172.31.18.194']

CORS_ORIGIN_WHITELIST = (
    'localhost:8080',
    '127.0.0.1:8080',
    'decryptous.com',
    'www.decryptous.com'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'decryptous',
        'USER': 'decryptous',
        'PASSWORD': 'Decrypt110@',
        'HOST': 'idc0.wiselight.kr',
        'PORT': '3306',
    }
}

# 비밀번호 추가!!
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://idc0.wiselight.kr:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'PASSWORD': '123123123',
        }
    }
}