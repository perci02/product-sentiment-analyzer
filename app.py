from flask import Flask, render_template, request
import pickle
from pymongo import MongoClient

# Initialize Flask
app = Flask(__name__)

# Load ML model
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# Connect MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["product_reviews_db"]
collection = db["reviews"]


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        product = request.form["product"]

        # Search reviews from MongoDB
        cursor = collection.find({
            "product": {"$regex": product, "$options": "i"}
        })

        reviews = [doc["review"] for doc in cursor]

        if len(reviews) == 0:
            return render_template(
                "index.html",
                product=product,
                total=0,
                pos=0,
                neg=0,
                pos_pct=0,
                neg_pct=0,
                reviews=[]
            )

        # ML prediction
        X = vectorizer.transform(reviews)
        predictions = model.predict(X)

        pos = sum(predictions == "positive")
        neg = sum(predictions == "negative")

        total = len(reviews)

        pos_pct = round((pos / total) * 100, 2)
        neg_pct = round((neg / total) * 100, 2)

        review_data = []

        for r, p in zip(reviews, predictions):
            review_data.append({
                "text": r,
                "sentiment": p,
                "product": product
            })

        return render_template(
            "index.html",
            product=product,
            total=total,
            pos=pos,
            neg=neg,
            pos_pct=pos_pct,
            neg_pct=neg_pct,
            reviews=review_data
        )

    return render_template(
        "index.html",
        product=None,
        reviews=[]
    )


if __name__ == "__main__":
    app.run(debug=True)