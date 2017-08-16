"""Creates a PDF from an article of the project „Mathe für Nicht-Freaks“."""

import requests

from api import HTTPMediaWikiAPI
from cachecontrol import CacheControl

ARTICLE = "Mathe für Nicht-Freaks: Was ist Analysis?"

def run_script():
    """Runs this script."""
    req = CacheControl(requests.Session())
    api = HTTPMediaWikiAPI(req)

    print(api.get_content(ARTICLE))

if __name__ == "__main__":
    run_script()
