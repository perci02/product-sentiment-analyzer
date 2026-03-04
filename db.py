from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["product_reviews"]
collection = db["reviews"]