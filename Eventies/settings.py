"""
Django settings for Eventies project.

Generated by 'django-admin startproject' using Django 1.11.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
from decouple import config, Csv
import dj_database_url
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.gis',
    #APIs de developers
    'widget_tweaks',
    'sortedm2m',
    'mapwidgets',#mapa dinamico googlemaps
    'datetimewidget',#widget para formulario de calendario
    'django_cron',
    #APPs propias
    'events',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]
#donde se guardan las traducciones de enlaces
ROOT_URLCONF = 'Eventies.urls'
#configuracion de templates de la web
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Added for photos
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'Eventies.wsgi.application'


# Database
"""
para cuando se cree una base de datos externa
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}
"""
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
#django.db.backends.postgresql_psycopg2 --> posgreSQL sin tratamiento de geolocalizacion

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'eventies',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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



# Agregamos los idiomas
LANGUAGE_CODE = 'es'

from django.utils.translation import ugettext_lazy as _
LANGUAGES = (
    ('en', _('English')),
    ('es', _('Spanish')),
)

# Definimos la ruta de los archivos de idiomas
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

#
# Media added for photos
#
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SITE_ID = 1

# Redirecciones de sesion
LOGIN_REDIRECT_URL = 'home'

LOGOUT_REDIRECT_URL = 'home'

LOGIN_URL = 'login'

#console email backend para usar un gestor de correo  en fase de produccion
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#APIs codes
MAP_WIDGETS = {
    "GooglePointFieldWidget": (
        ("zoom", 15),
        ("mapCenterLocationName", "madrid"),
        ("GooglePlaceAutocompleteOptions", {'componentRestrictions': {'country': 'es'}}),
        ("markerFitZoom", 12),
    ),
    "GOOGLE_MAP_API_KEY": "AIzaSyAOt21MFO0p-9eB7yNqwSKN76RjAEXNERE"
}

GEOIP_PATH = '/libarys/'

#modelo predeterminado de usuario
AUTH_USER_MODEL = 'accounts.User'

USE_L10N = True
USE_TZ = True
USE_I18N = True


CRON_CLASSES = [
    "django_cron.cron.FailedRunsNotificationCronJob",
    "events.recommender.Recomender"
]