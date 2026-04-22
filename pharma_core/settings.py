"""
Django settings for pharma_core project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-5q--@jyg!c(#0e^*zi53ey!uq90*lcv&)!hzi@6khc(#^ec%j9'

DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin',  # Admin Theme
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'management', # Aapki App
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pharma_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # --- IMPORTANT CHANGE HERE ---
        # Django ko bata rahe hain ke 'templates' folder root directory mein hai
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pharma_core.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# --- JAZZMIN SETTINGS (Admin Panel Design) ---
JAZZMIN_SETTINGS = {
    "site_title": "Pharma Admin",
    "site_header": "Pharma ERP",
    "welcome_sign": "Welcome to Pharmaceutical Admin Panel",
    "search_model": "management.Medicine",
    "icons": {
        "management.Medicine": "fas fa-pills",
        "management.Employee": "fas fa-user-tie",
        "management.SalesOrder": "fas fa-shopping-cart",
    },
    "order_with_respect_to": ["management", "auth"],
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "dark_mode_theme": "darkly",
}

# --- IMPORTANT SETTINGS FOR POPUPS & LOGIN ---

# 1. Allow Iframes (Popup forms ke liye zaroori hai)
X_FRAME_OPTIONS = 'SAMEORIGIN'

# 2. Login Redirects
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'  # Login hone ke baad Dashboard par jaye
LOGOUT_REDIRECT_URL = 'home'      # Logout hone ke baad Home Page par aaye