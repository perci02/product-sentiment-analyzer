# SentimentIQ — Product Sentiment Analyzer

🔗 **Live Demo:** [https://sentimentiq.up.railway.app](https://sentimentiq.up.railway.app)

Analyze customer reviews with AI-powered sentiment analysis. Search any product and instantly see whether reviews are positive or negative.

## Tech Stack
- **Backend:** Flask, Python
- **ML:** scikit-learn (Logistic Regression + TF-IDF)
- **Data:** Live web scraping (Flipkart + Amazon) with CSV fallback
- **Frontend:** HTML/CSS, Chart.js, Font Awesome
- **Deployment:** Railway

## How It Works
1. User searches for a product name
2. App scrapes live reviews from Flipkart & Amazon
3. If scraping fails, falls back to local CSV dataset (34K+ Amazon reviews)
4. Reviews are vectorized using TF-IDF
5. Logistic Regression model predicts sentiment (positive/negative)
6. Results are displayed with charts, stats, and review cards

## Features
- Live web scraping from Flipkart & Amazon
- Fallback to 34K+ local Amazon reviews
- Interactive bar and doughnut charts
- Sentiment score with positive/negative breakdown
- Product autocomplete suggestions
- Sample review cards with sentiment labels

