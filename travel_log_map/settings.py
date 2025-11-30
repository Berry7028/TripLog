"""
travel_log_map プロジェクト用の Django 設定。
Django 5.2.6 で 'django-admin startproject' を実行して生成されました。
設定に関する詳細は https://docs.djangoproject.com/en/5.2/topics/settings/ を参照してください。
各設定項目と値の一覧は https://docs.djangoproject.com/en/5.2/ref/settings/ を参照してください。
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

def _env_int(name: str, default: int) -> int:
    """環境変数を整数として取得。変換できない場合はデフォルト値。"""

    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default

# dj_database_url は本番環境へのデプロイ時のみ必要
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# プロジェクト内のパスを BASE_DIR / 'subdir' のように構築
BASE_DIR = Path(__file__).resolve().parent.parent

# .env と .env.local から環境変数を読み込む
load_dotenv(BASE_DIR / '.env')
load_dotenv(BASE_DIR / '.env.local')

# .env.local からも読み込む（ローカル上書き用）
load_dotenv(BASE_DIR / '.env.local')

# 開発向けの簡易設定。 本番環境には不向き
# 詳細: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# 【セキュリティ警告】本番で使用するSECRET_KEYは絶対に公開しない
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-=c9_%nizo8@fm9njwyx)f*_^qd(jv^1@(!613de^98a93*d3=h')

# 【セキュリティ警告】本番環境で DEBUG=True にしないこと
# 環境変数が未設定の場合はローカル開発向けに True を既定とする
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['*']

# アプリケーション定義
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'spots',
]

# 本番環境では whitenoise.runserver_nostatic を追加して Django の静的ファイル配信を無効化
if not DEBUG:
    INSTALLED_APPS.insert(0, 'whitenoise.runserver_nostatic')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# whitenoise のミドルウェアは本番環境のみ有効化
if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'travel_log_map.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'travel_log_map.wsgi.application'

# データベース設定
# 参考: https://docs.djangoproject.com/en/5.2/ref/settings/#databases

if 'DATABASE_URL' in os.environ and dj_database_url:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# パスワード検証
# 参考: https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

# 国際化設定
# 参考: https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True

# 静的ファイル（CSS・JavaScript・画像など）
# 参考: https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 静的ファイルの追加設定
STATICFILES_DIRS = [
    BASE_DIR / 'spots' / 'static',
]

# whitenoise のストレージクラスは本番環境のみ利用
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # 本番環境向け WhiteNoise 設定
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True

# 既定の主キー型
# 参考: https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# メディアファイル（ユーザーアップロード）
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ログイン・ログアウト関連URL
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# 外部アクセス用の CSRF 設定
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://8000-ij3w7fliisck5f9nvstl9-41315974.manusvm.computer',
    'https://8001-ij3w7fliisck5f9nvstl9-41315974.manusvm.computer',
    'https://*.manusvm.computer',
]

# iframe 埋め込みを許可（VS Code Simple Browser 対応）
X_FRAME_OPTIONS = 'ALLOWALL'


UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY', '')
IMAGE_LOOKUP_ENABLED = bool(UNSPLASH_ACCESS_KEY)

if not IMAGE_LOOKUP_ENABLED:
    logging.getLogger(__name__).warning(
        "Image auto lookup disabled (UNSPLASH_ACCESS_KEY not set). "
        "Wikipedia fallback will still be attempted."
    )  