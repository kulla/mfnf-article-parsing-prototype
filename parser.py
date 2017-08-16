"""Module defining a parser for MediaWiki code."""

def parse_mediawiki_code(api, text):
    """Returns an AST of the MediaWiki code `text`.

    Arguments:
        api  -- instance of MediaWikiAPI
        text -- MediaWiki code"""
    return api.convert_text_to_html(text)
