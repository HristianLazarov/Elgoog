from flask import Flask, render_template, request
import requests
import re
import time
import random
from urllib.parse import quote

app = Flask(__name__)

SEARCH_API = "https://en.wikipedia.org/w/rest.php/v1/search/page"
RANDOM_API = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "ElgoogSearch/1.1 (educational project)"}


def words(text):
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def get_search_articles(query):
    response = requests.get(
        SEARCH_API,
        params={"q": query, "limit": 8},
        headers=HEADERS,
        timeout=12
    )
    response.raise_for_status()
    return response.json().get("pages", [])


def get_random_articles():
    response = requests.get(
        RANDOM_API,
        params={
            "action": "query",
            "list": "random",
            "rnnamespace": 0,
            "rnlimit": 50,
            "format": "json"
        },
        headers=HEADERS,
        timeout=12
    )
    response.raise_for_status()

    pages = response.json().get("query", {}).get("random", [])
    return [
        {
            "title": page["title"],
            "key": page["title"].replace(" ", "_"),
            "description": "Wikipedia article",
            "excerpt": ""
        }
        for page in pages
    ]


def terrible_score(query, article):
    query_words = words(query)
    article_words = (
        words(article.get("title", ""))
        | words(article.get("description", ""))
        | words(article.get("excerpt", ""))
    )

    if not query_words:
        return 0

    overlap = len(query_words & article_words)
    return overlap * 100 + random.random()


def search_articles(query):
    matching = get_search_articles(query)
    random_pages = get_random_articles()

    combined = {}
    for article in random_pages + matching:
        combined[article.get("title", "")] = article

    results = list(combined.values())
    results.sort(key=lambda article: terrible_score(query, article))
    return results


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return render_template("index.html")

    started = time.perf_counter()

    try:
        articles = search_articles(query)
        results = []

        for article in articles[:50]:
            key = article.get("key") or article.get("title", "").replace(" ", "_")
            results.append({
                "title": article.get("title", "Untitled"),
                "description": article.get("description") or "Wikipedia article",
                "excerpt": article.get("excerpt") or "",
                "url": "https://en.wikipedia.org/wiki/" + quote(key, safe="()_,")
            })

        elapsed = time.perf_counter() - started
        return render_template(
            "results.html",
            query=query,
            results=results,
            elapsed=f"{elapsed:.2f}"
        )

    except requests.RequestException:
        return render_template(
            "results.html",
            query=query,
            results=[],
            elapsed="—",
            error="Search is temporarily unavailable. Please try again."
        )


if __name__ == "__main__":
    app.run(debug=True)
