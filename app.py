from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
from scraper import scrape_reviews

# Initialize Flask
app = Flask(__name__)

# Load ML model
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# Load CSV as fallback data
csv_df = pd.read_csv("amazon_reviews.csv", low_memory=False)
csv_df = csv_df[["name", "reviews.text"]].dropna()
csv_df["name_lower"] = csv_df["name"].str.lower()

# Unique product names for autocomplete suggestions
product_names = csv_df["name"].drop_duplicates().tolist()


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        product = request.form["product"]
        source = "web"

        # Step 1: Try live scraping from Flipkart + Amazon
        reviews = scrape_reviews(product)

        # Step 2: Fall back to local CSV if scraping returns nothing
        if not reviews:
            source = "local"
            matched = csv_df[csv_df["name_lower"].str.contains(
                product.lower(), na=False
            )]
            reviews = matched["reviews.text"].tolist()

        if len(reviews) == 0:
            return render_template(
                "index.html",
                product=product,
                total=0,
                pos=0,
                neg=0,
                pos_pct=0,
                neg_pct=0,
                reviews=[],
                source=source
            )

        # ML prediction
        X = vectorizer.transform(reviews)
        predictions = model.predict(X)

        pos = int((predictions == "positive").sum())
        neg = int((predictions == "negative").sum())

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
            reviews=review_data,
            source=source
        )

    return render_template(
        "index.html",
        product=None,
        reviews=[],
        source=None
    )


@app.route("/suggest")
def suggest():
    query = request.args.get("q", "").lower()
    if len(query) < 2:
        return jsonify([])
    matches = [name for name in product_names if query in name.lower()]
    return jsonify(matches[:10])


if __name__ == "__main__":
    app.run(debug=True)