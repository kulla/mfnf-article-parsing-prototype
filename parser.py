"""Module defining a parser for MediaWiki code."""

from html.parser import HTMLParser

class HTML2JSONParser(HTMLParser):
    """Parser for converting HTML to JSON."""

    def __init__(self):
        super(HTML2JSONParser, self).__init__()

        self.__node_stack = []
        self.root = None

    def handle_starttag(self, tag, attrs):
        node = {"type": "element", "name": tag,
                "attrs": dict(attrs), "children": []}

        if self.__node_stack:
            self.__node_stack[-1]["children"].append(node)
        else:
            assert not self.root, "HTML must contain only one root element"

            self.root = node

        self.__node_stack.append(node)

    def handle_endtag(self, tag):
        assert self.__node_stack
        assert self.__node_stack[-1]["name"] == tag

        self.__node_stack.pop()

    def handle_data(self, data):
        data = data.strip()

        if data:
            assert self.__node_stack, "HTML shall not start with text."

            node = {"type": "text", "data": data}

            self.__node_stack[-1]["children"].append(node)

    def error(self, message):
        raise AssertionError(message)

def html2json(text):
    """Converts HTML to JSON."""
    parser = HTML2JSONParser()

    parser.feed(text)

    return parser.root

def parse_mediawiki_code(api, text):
    """Returns an AST of the MediaWiki code `text`.

    Arguments:
        api  -- instance of MediaWikiAPI
        text -- MediaWiki code"""
    html = api.convert_text_to_html(text)

    html_json = html2json(html)

    return html_json
