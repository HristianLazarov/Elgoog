ELGOOG

A Google-inspired search engine with a deliberately backwards ranking algorithm.
Search results are real Wikipedia pages.

RUN IT
1. Install Python 3.
2. Open a terminal in this folder.
3. Install dependencies:
       python -m pip install -r requirements.txt
4. Start the website:
       python app.py
5. Open this address in your browser:
       http://127.0.0.1:5000

The app asks Wikipedia for real search results, calculates a basic word-match
score, then sorts from the LOWEST match score to the HIGHEST. In other words,
the pages that match your search least are shown first.

This is a small student project, not a full-web search index. It searches
Wikipedia's public search API and requires an internet connection.
