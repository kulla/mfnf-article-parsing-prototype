"""Creates a PDF from an article of the project „Mathe für Nicht-Freaks“."""

import json
import requests

from api import HTTPMediaWikiAPI
from cachecontrol import CacheControl
from parser import parse_mediawiki_code

# title of article which shall be converted to PDF
ARTICLE = "Mathe für Nicht-Freaks: Was ist Analysis?"

def run_script():
    """Runs this script."""
    req = CacheControl(requests.Session())
    api = HTTPMediaWikiAPI(req)

    # Get content of article
    article_text = api.get_content(ARTICLE)

    # Parse article's content
    article_ast = parse_mediawiki_code(api, article_text)

    print(json.dumps(article_ast, indent=2))

if __name__ == "__main__":
    run_script()
