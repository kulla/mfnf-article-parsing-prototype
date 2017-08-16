"""Module defining a parser for MediaWiki code."""

from html.parser import HTMLParser

class HTML2JSONParser(HTMLParser):
    """Parser for converting HTML to JSON."""

    def __init__(self):
        super(HTML2JSONParser, self).__init__()

        self.__node_stack = []
        self.content = []

    def handle_starttag(self, tag, attrs):
        node = {"type": "element", "name": tag,
                "attrs": dict(attrs), "children": []}

        if self.__node_stack:
            self.__node_stack[-1]["children"].append(node)
        else:
            self.content.append(node)

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

def mediawikihtml2json(text):
    """Converts HTML of a MediaWiki document to JSON."""
    parser = HTML2JSONParser()

    parser.feed(text)

    return parser.content

def parse_article(api, article):
    """Parses the article `article`."""
    article["content"] = api.convert_text_to_html(article["title"],
                                                  article["content"])
    article["content"] = mediawikihtml2json(article["content"])

    return article
