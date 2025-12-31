from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus
import os

uri = "mongodb+srv://" + quote_plus(os.environ.get("MONGO_USER")) + ":" + quote_plus(os.environ.get("MONGO_PASSWORD")) + "@managers.ijg1b4p.mongodb.net/?appName=MANAGERS"
client = MongoClient(uri, server_api=ServerApi('1'))