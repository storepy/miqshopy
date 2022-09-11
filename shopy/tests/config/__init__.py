from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

SECRET_KEY = 'test-key'
AUTH_USER_MODEL = 'core.User'

SITE_ID = 1
API_PATH = 'api/v1'
CORS_ORIGIN = 'http://127.0.0.1:3000'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #
    'django.contrib.sites',
    'django.contrib.sitemaps',
    #
    'rest_framework',

    'miq.analytics',
    'miq.core',
    'miq.staff',

    'shopy.shop',
    'shopy.store',
    'shopy.sales',

]

ROOT_URLCONF = 'shopy.tests.config.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME':'test_mydb',
        # 'USER': 'myuser',
        # 'PASSWORD': 'mypassword',
        # 'HOST': '',
        # 'PORT': '',
    },
}

MIDDLEWARE = [
    # CORS
    # 'miq.core.middleware.CORSMiddleware',
    #
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'miq.core.middleware.SiteMiddleware',
    'miq.analytics.middlewares.AnalyticsMiddleware',
    'shopy.shop.middleware.ShopMiddleware',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        # 'DIRS': [TEMPLATES_DIR],
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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Set for all views
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 16,
}
