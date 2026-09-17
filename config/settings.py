import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv(os.path.join(BASE_DIR, '.env'))

# --- SECURITY SETTINGS ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-development-key')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# --- PRODUCTION HTTPS & SECURITY SETTINGS ---
if not DEBUG:
    # Defaults to True in production, but allows override for local testing with DEBUG=False
    # To test locally with DEBUG=False, add SECURE_SSL_REDIRECT=False to your .env file
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
    
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = "DENY"

    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    
    # Required if deploying behind an Nginx/trusted reverse proxy
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- REST FRAMEWORK CONFIGURATION ---
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
        "user": "300/min",
    },
}

# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",       # <--- REQUIRED FOR ADMIN
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "news_api",
]

MIDDLEWARE = [
    # CORS must be at the very top to intercept requests before security blocks them
    "corsheaders.middleware.CorsMiddleware",
    
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",  # <--- REQUIRED FOR ADMIN
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

# --- POSTGRESQL DATABASE CONFIGURATION ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'cyberbrief_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres@123'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York" # <--- CHANGED FROM Asia/Kolkata TO EST/EDT
USE_I18N = True
USE_TZ = True

# --- STATIC & MEDIA FILES ---
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- URL ROUTING ---
# Appends a slash to URLs (e.g. /api/news -> /api/news/) 
APPEND_SLASH = True

# --- CORS SETTINGS ---
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

# Explicitly whitelist the exact local development URLs
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Safely append production origins from your .env file, rejecting wildcards
env_cors = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if env_cors and env_cors != '*':
    CORS_ALLOWED_ORIGINS.extend([
        origin.strip() for origin in env_cors.split(',') if origin.strip() and origin.strip() != '*'
    ])

# CSRF needs the exact same whitelist
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]