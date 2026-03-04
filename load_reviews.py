import pandas as pd
from pymongo import MongoClient

# connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

db = client["product_reviews_db"]
collection = db["reviews"]

# read dataset
df = pd.read_csv("amazon_reviews.csv", low_memory=False)

# select needed columns
df = df[["name", "reviews.text"]]

df = df.dropna()

for _, row in df.iterrows():

    review = {
        "product": row["name"].lower(),
        "review": row["reviews.text"]
    }

    collection.insert_one(review)

print("Dataset loaded successfully!")