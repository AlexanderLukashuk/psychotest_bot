from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["psych_tests_bot"]
tests_collection = db["tests"]
print(db.list_collection_names())
