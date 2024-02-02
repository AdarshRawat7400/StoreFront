import os
from decouple import config
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-pmwhm(7i!-zs&hhtc%e9+=@r_&acpcekr94t0m^2l#jl$)z8(c')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    # 'social_django',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'crispy_forms',
    'crispy_bootstrap5',
    'datatableview',
    'django_countries',
    'phonenumber_field',
    "django_extensions",
    "django_ckeditor_5"
] + [
    'apps.core',
    'apps.users',
    'apps.store',
    'apps.payments',
    'apps.frontend',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

SOCIAL_AUTH_AUTH0_DOMAIN = config('AUTH0_DOMAIN')
SOCIAL_AUTH_AUTH0_KEY = config('AUTH0_CLIENT_ID')
SOCIAL_AUTH_AUTH0_SECRET = config('AUTH0_CLIENT_SECRET')

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],

    }
    ,'description': {
        # Your desired CKEditor 5 configuration options
    }
 }
SOCIAL_AUTH_AUTH0_SCOPE = [
    'openid',
    'profile',
    'email',
]


SITE_ID = 1
LOGIN_REDIRECT_URL = '/'

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '572879279979-ojt65gat9rmt77epas4qj3fuea1an65u.apps.googleusercontent.com',
            'secret': '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',
            'key': '666',
        },
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'storefront.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, 'db.sqlite3')
    },
    # 'default': dj_database_url.config(
    #     default='postgres://storefront_fth4_user:NRwr11CWNYvwojYjQTAKGzqt7viTt9Pc@dpg-cn7klpnsc6pc73ca8ovg-a.oregon-postgres.render.com/storefront_fth4',
    #     conn_max_age=600,
    # )
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

AUTH_USER_MODEL = 'users.Users'

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

STRIPE_PUBLIC_KEY = 'pk_test_lX3r6OMjOU2yzFsNSHq6belT00EY82kZmH'
STRIPE_SECRET_KEY = 'sk_test_tn0CTDaIJHUJyAqhsf39cfsC00LNjsqDnb'

# URL where users will be redirected if they try to access a protected resource without being authenticated
# LOGIN_URL = 'login/'

# URL where users will be redirected after a successful login
# LOGIN_REDIRECT_URL = '/'

# # URL where users will be redirected after a successful logout
# LOGOUT_REDIRECT_URL = '/'


# DJANGO-ALLAUTH

SITE_ID = 1

LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.auth0.Auth0OAuth2',
    'allauth.account.auth_backends.AuthenticationBackend',
]
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
# ACCOUNT_EMAIL_SUBJECT_PREFIX = env.str("ALLAUTH_ACCOUNT_EMAIL_SUBJECT_PREFIX")

ACCOUNT_FORMS = {
    "login": "apps.frontend.forms.CustomLoginForm",
    "signup": "apps.frontend.forms.CustomSignUpForm",
    # "add_email": "allauth.account.forms.AddEmailForm",
    # "change_password": "allauth.account.forms.ChangePasswordForm",
    # "set_password": "allauth.account.forms.SetPasswordForm",
    # "reset_password": "allauth.account.forms.ResetPasswordForm",
    # "reset_password_from_key": "allauth.account.forms.ResetPasswordKeyForm",
    # "disconnect": "allauth.socialaccount.forms.DisconnectForm",
}

SOCIALACCOUNT_ADAPTER = 'apps.core.adapters.CustomSocialAccountAdapter'


PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

# Django REST Framework


# Ckeditor


customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload"
        ],
    },
    "comment": {
        "language": {"ui": "en", "content": "en"},
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
        ],
    },
    "extends": {
        "language": "en",
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": [
            "heading",
            "codeBlock",
            "|",
            "outdent",
            "indent",
            "|",
            "bold",
            "italic",
            "link",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "insertImage",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
            "sourceEditing",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
                "toggleImageCaption",
                "|"
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
        "list": {
            "properties": {
                "styles": True,
                "startIndex": True,
                "reversed": True,
            }
        },
        "htmlSupport": {
            "allow": [
                {"name": "/.*/", "attributes": True, "classes": True, "styles": True}
            ]
        },
    },
}