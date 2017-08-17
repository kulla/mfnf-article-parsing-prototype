"""Creates a PDF from an article of the project „Mathe für Nicht-Freaks“."""

import json
import requests

from api import HTTPMediaWikiAPI
from cachecontrol import CacheControl
from parser import parse_article

# title of article which shall be converted to PDF
ARTICLE = "Mathe für Nicht-Freaks: Ableitung und Differenzierbarkeit"

def run_script():
    """Runs this script."""
    req = CacheControl(requests.Session())
    api = HTTPMediaWikiAPI(req)

    article = {"type": "article", "title": ARTICLE}

    article = parse_article(api, article)

    print(json.dumps(article, indent=2))

if __name__ == "__main__":
    run_script()
