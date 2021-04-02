import os
from dotenv import load_dotenv
from starlette.datastructures import CommaSeparatedStrings, Secret
# from databases import DatabaseURL

API_V1_STR = "/api"

load_dotenv(".env")

PROJECT_NAME = os.getenv("PROJECT_NAME", "Stocksite Day-Trading API")
ALLOWED_HOSTS = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", ""))

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USER = os.getenv("MONGO_USER", "userdb")
MONGO_PASS = os.getenv("MONGO_PASSWORD", "pass")
MONGO_DB = os.getenv("MONGO_DB", "stocksite_dev")

MONGODB_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"


print("ppp", MONGODB_URL)
database_name = MONGO_DB
accounts_collection = "accounts"