
from decouple import config


DEBUG = config('DEBUG', default=True, cast=bool)

DATABASE_URL = config('DATABASE_URL')

DATABASE_NAME = config('DATABASE_NAME', default='ilumi')
