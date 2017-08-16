"""Creates a PDF from an article of the project „Mathe für Nicht-Freaks“."""

import requests

from api import MediaWikiAPI

def run_script():
    """Runs this script."""
    api = MediaWikiAPI(requests.Session())

    print(api.get_content("Mathe für Nicht-Freaks: Was ist Analysis?"))

if __name__ == "__main__":
    run_script()
