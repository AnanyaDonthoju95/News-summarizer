import os
import json
import requests
from bs4 import BeautifulSoup

def extract_article_text(url):
    """Fetch main article text using BeautifulSoup."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (NewsSummarizer)"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 50]
        text = " ".join(paragraphs)
        return text[:10000]  # limit for safety
    except Exception as e:
        print("extract_article_text error:", e)
        return None


def summarize_locally(text, max_sentences=15):
    """Simple extractive summarizer."""
    try:
        import re
        from collections import Counter

        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) <= max_sentences:
            return " ".join(sentences)

        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        stop = set((
            "the","and","for","that","with","this","from","have","are","was","were","will","would",
            "there","their","about","which","when","where","your","into","been","also","they","them",
            "over","after","before","more","most","some","such","than","then","because","while",
            "between","under","through","these","those"
        ))
        freq = Counter(w for w in words if w not in stop)

        def score(s):
            terms = re.findall(r'\b[a-zA-Z]{3,}\b', s.lower())
            return sum(freq.get(t, 0) for t in terms)

        ranked = sorted(((score(s), i, s) for i, s in enumerate(sentences)), reverse=True)
        top = sorted(ranked[:max_sentences], key=lambda x: x[1])
        return " ".join(s for _, _, s in top)
    except Exception:
        return text[:800]


def lambda_handler(event, context):
    try:
        # Default CORS headers (add these to all responses)
        cors_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            "Access-Control-Allow-Headers": "Content-Type"
        }

        # Handle preflight OPTIONS request
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps({"message": "CORS preflight OK"})
            }

        body = {}
        if event.get("body"):
            try:
                body = json.loads(event["body"])
            except Exception:
                body = {}
        if not body and event.get("queryStringParameters"):
            body = event.get("queryStringParameters") or {}

        url = body.get("url")
        if not url:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({"error": "Missing 'url' in request body"})
            }

        article = extract_article_text(url)
        if not article:
            return {
                "statusCode": 422,
                "headers": cors_headers,
                "body": json.dumps({"error": "Could not extract article text (paywall/JS)"})
            }

        summary = summarize_locally(article, max_sentences=15)

        return {
            "statusCode": 200,
            "headers": {**cors_headers, "Content-Type": "application/json"},
            "body": json.dumps({"summary": summary, "source": "local"})
        }

    except Exception as e:
        print("lambda_handler error:", e)
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)})
        }