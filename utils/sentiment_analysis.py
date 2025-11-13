# utils/sentiment_analysis.py
from textblob import TextBlob

def simple_sentiment(text: str) -> dict:
    """
    Return a simple sentiment dict using TextBlob.
    polarity: -1 (negative) .. 1 (positive)
    subjectivity: 0 (objective) .. 1 (subjective)
    label: 'positive' | 'negative' | 'neutral'
    """
    if not text:
        return {"polarity": 0.0, "subjectivity": 0.0, "label": "neutral"}

    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 4)
    subjectivity = round(blob.sentiment.subjectivity, 4)

    if polarity > 0.1:
        label = "positive"
    elif polarity < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return {"polarity": polarity, "subjectivity": subjectivity, "label": label}
