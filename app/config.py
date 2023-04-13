import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_DB = os.getenv('DB_DB')
DB_POOL_NAME = os.getenv('DB_POOL_NAME')
DB_POOL_SIZE = 20
DB_PORT = os.getenv('DB_PORT')

# Flask app configuration
DEBUG = os.getenv('DEBUG')
PORT = os.getenv('PORT')
HOST = os.getenv('HOST')
JSON_AS_ASCII = False
TEMPLATES_AUTO_RELOAD = True
JASONIFY_MIMETYPE = 'application/json;charset=utf-8'
JSON_PRETTYPRINT_REGULAR = "True"

S3_BUCKET = os.getenv('S3_BUCKET')
S3_KEY_ID = os.getenv('S3_KEY_ID')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
S3_LOCATION = os.getenv('S3_LOCATION')
# CLOUDFRONT = os.getenv('CLOUDFRONT')

# Line login
client_id = os.getenv("client_id")
call_back = os.getenv("call_back")
client_secret = os.getenv("client_secret")

# Price-Pick
PP_SECRET_KEY = os.getenv("PP_SECRET_KEY")
PP_JWT_ALGO = os.getenv("PP_JWT_ALGO")

# Line bot
Notify_client_id = os.getenv("Notify_client_id")
Notify_channel_access_token = os.getenv("Notify_channel_access_token")
