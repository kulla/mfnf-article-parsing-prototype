"""Module defining a parser for MediaWiki code."""

import json

from html.parser import HTMLParser
from transformations import JSONTransformation, ChainedTransformation
from utils import lookup

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

class MediaWikiParser(ChainedTransformation):

    class MediaWiki2JSON:
        """Converts HTML of a MediaWiki document to JSON."""

        def __call__(self, text):
            parser = HTML2JSONParser()

            parser.feed(text)

            return parser.content

    class TemplateDeinclusion(JSONTransformation):
        """Replaces included MediaWiki templates with template specification."""

        def transform_dict(self, obj):
            if lookup(obj, "type") == "element" \
                    and lookup(obj, "attrs", "typeof") == "mw:Transclusion":
                template = json.loads(obj["attrs"]["data-mw"])
                template = template["parts"][0]["template"]

                name = template["target"]["wt"].strip()

                params = template["params"]
                params = {key: value["wt"] for key, value in params.items()}

                return {"type": "template", "name": name, "params": params}
            else:
                return super().transform_dict(obj)

def parse_article(api, article):
    """Parses the article `article`."""
    article["content"] = api.convert_text_to_html(article["title"],
                                                  article["content"])


    article["content"] = MediaWikiParser()(article["content"])

    return article
