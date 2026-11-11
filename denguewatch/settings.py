"""
Django settings for denguewatch project.
Campus DengueWatch (Campus Dengue Guard)
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if os.environ.get('DJANGO_DEBUG', 'True') == 'True':
        SECRET_KEY = 'django-insecure-^i5s98xc#-ri)jtvz&yufjremeymb7$hl^n7-rd#fe5_+by7va'
    else:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured("DJANGO_SECRET_KEY environment variable must be set when DEBUG is False.")

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Project apps
    'accounts',
    'reports',
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

ROOT_URLCONF = 'denguewatch.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.actor_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'denguewatch.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Custom User Model (Decision #3)
AUTH_USER_MODEL = 'accounts.RegisteredUser'

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

LANGUAGE_CODE = 'en-us'

# Time zone (Decision #12)
TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files for photo upload (Decision #6)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'heatmap'
LOGOUT_REDIRECT_URL = 'heatmap'

import math

# Campus DengueWatch Domain Settings
# OpenStreetMap 56-node polygon perimeter for ULAB Permanent Campus (Way 1071236443, center 23.759973, 90.348976)
CAMPUS_GEOJSON = {
    "type": "Feature",
    "properties": {
        "name": "ULAB Permanent Campus",
        "osm_way_id": 1071236443,
        "center_lat": 23.759973,
        "center_lng": 90.348976,
    },
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [90.3500835, 23.7606544],
                [90.3501886, 23.7603847],
                [90.3501996, 23.7602854],
                [90.3502093, 23.7601632],
                [90.3502539, 23.7599763],
                [90.3504489, 23.7599771],
                [90.3506369, 23.7599788],
                [90.3507698, 23.7600234],
                [90.3508662, 23.7600716],
                [90.3509826, 23.7598706],
                [90.3509757, 23.7598297],
                [90.3509301, 23.7597714],
                [90.350879, 23.7597098],
                [90.3508184, 23.7596366],
                [90.350286, 23.7592185],
                [90.3502144, 23.7592748],
                [90.3501625, 23.7592312],
                [90.350127, 23.7592449],
                [90.3499325, 23.7591974],
                [90.349538, 23.7589099],
                [90.3489932, 23.7585755],
                [90.3480286, 23.7580935],
                [90.3477276, 23.758661],
                [90.3476342, 23.7589362],
                [90.3479579, 23.7590828],
                [90.347838, 23.759296],
                [90.3477306, 23.7593377],
                [90.3475332, 23.7593022],
                [90.3474528, 23.7593393],
                [90.3473718, 23.7593877],
                [90.3473447, 23.7595073],
                [90.3473027, 23.7596419],
                [90.3473207, 23.7597452],
                [90.3474404, 23.7599304],
                [90.347609, 23.7601551],
                [90.3476963, 23.7602331],
                [90.3477666, 23.7602935],
                [90.3477432, 23.7604163],
                [90.3476496, 23.7604947],
                [90.3476443, 23.7605679],
                [90.3475749, 23.7606258],
                [90.3475728, 23.7606986],
                [90.3476074, 23.7609163],
                [90.3477997, 23.7608977],
                [90.3480073, 23.7608991],
                [90.3481561, 23.7609178],
                [90.3482343, 23.7609],
                [90.3486429, 23.7608451],
                [90.3488438, 23.7608964],
                [90.3489512, 23.7609028],
                [90.3493434, 23.7606399],
                [90.3497894, 23.7605203],
                [90.3498782, 23.7605395],
                [90.349922, 23.760586],
                [90.3499459, 23.7606421],
                [90.3500835, 23.7606544],
            ]
        ],
    },
}

def _build_campus_boundary(geojson: dict, buffer_km: float = 1.0) -> dict:
    """
    Derives bounding box, geometric center, and 1 km buffer zone automatically
    from any provided GeoJSON Feature, FeatureCollection, or Geometry to facilitate easy iterations.
    """
    if "features" in geojson and geojson["features"]:
        geom = geojson["features"][0].get("geometry", {})
        props = geojson["features"][0].get("properties", {})
    else:
        geom = geojson.get("geometry", geojson)
        props = geojson.get("properties", {})

    coords = geom.get("coordinates", [[]])[0] if geom.get("type") == "Polygon" else []
    if coords:
        min_lng = min(pt[0] for pt in coords)
        max_lng = max(pt[0] for pt in coords)
        min_lat = min(pt[1] for pt in coords)
        max_lat = max(pt[1] for pt in coords)
    else:
        min_lng, max_lng = 90.347303, 90.350983
        min_lat, max_lat = 23.758094, 23.760918

    center_lat = props.get('center_lat', round((min_lat + max_lat) / 2.0, 6))
    center_lng = props.get('center_lng', round((min_lng + max_lng) / 2.0, 6))

    # Approximate coordinate offsets for the buffer distance in km
    lat_delta = buffer_km / 111.0
    lng_delta = buffer_km / (111.0 * math.cos(math.radians(center_lat)))

    return {
        'name': props.get('name', 'ULAB Permanent Campus'),
        'campus_type': 'Campus Boundary',
        'min_lat': min_lat,
        'max_lat': max_lat,
        'min_lng': min_lng,
        'max_lng': max_lng,
        'center_lat': center_lat,
        'center_lng': center_lng,
        'buffer_distance_km': buffer_km,
        'buffer_min_lat': min_lat - lat_delta,
        'buffer_max_lat': max_lat + lat_delta,
        'buffer_min_lng': min_lng - lng_delta,
        'buffer_max_lng': max_lng + lng_delta,
        'geojson': geojson,
    }

CAMPUS_BOUNDARY = _build_campus_boundary(CAMPUS_GEOJSON, buffer_km=1.0)

# Daily report limit per registered user (Decision #2)
DAILY_REPORT_LIMIT = 8
