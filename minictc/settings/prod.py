from decouple import config
from dj_database_url import parse as dburl
from .base import *

DEBUG = False

# Add production-specific settings, such as database configuration, allowed hosts, and security settings
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", default="", cast=lambda v: [s.strip() for s in v.split(",")]
)

# Add any other production-specific settings here
# (production database, static files and media storage for production, email settings, etc.)

DATABASES = {
    "default": config("DATABASE_URL", cast=dburl),
}
