"""Module defining a parser for MediaWiki code."""

import json

from html.parser import HTMLParser
from transformations import NodeTransformation, ChainedAction, Action, \
                            NodeTypeTransformation, DeleteTransformation
from utils import lookup, remove_prefix, add_dict

TEMPLATE_SPEC = {
    "Definition": lambda x: x in ["definition"],
    "Warnung": lambda x: x in ["1"],
    "Aufgabe": lambda x: x in ["aufgabe", "lösung", "beweis"]
}

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

class MediaWikiCodeParser(ChainedAction):
    """Parses MediaWikiCode and restore template definitions."""

    class MediaWikiCode2HTML(Action):
        """Converts MediaWiki code to HTML"""

        def __call__(self, text):
            return self.api.convert_text_to_html(self.title, text)

    class MediaWikiCodeHTML2JSON(Action):
        """Converts HTML of a MediaWiki document to JSON."""

        def __call__(self, text):
            parser = HTML2JSONParser()

            parser.feed(text)

            return parser.content

    class TemplateDeinclusion(NodeTransformation):
        """Replaces included MediaWiki templates with template
        specification."""

        def is_target_dict(self, obj):
            return lookup(obj, "type") == "element" \
                    and lookup(obj, "attrs", "typeof") == "mw:Transclusion"

        def parse_parameter_value(self, name, param_key, param_value):
            """Parses `param_value` in case `param_key` is a content
            parameter."""
            if name in TEMPLATE_SPEC and TEMPLATE_SPEC[name](param_key):
                parser = MediaWikiCodeParser(api=self.api, title=self.title)

                return parser(param_value)
            else:
                return param_value

        def transform_dict(self, obj):
            template = json.loads(obj["attrs"]["data-mw"])
            template = template["parts"][0]["template"]

            name = template["target"]["wt"].strip()
            name = remove_prefix(name, ":Mathe für Nicht-Freaks: Vorlage:")

            params = template["params"]
            params = {k: v["wt"] for k, v in params.items()}
            params = {key: self.parse_parameter_value(name, key, value) \
                        for key, value in params.items()}

            return {"type": "template", "name": name, "params": params}

class ArticleParser(ChainedAction):

    class LoadArticleContent(NodeTypeTransformation):
        """Loads the content of an article."""

        def transform_article(self, article):
            parser = MediaWikiCodeParser(api=self.api, title=article["title"])

            content = parser(self.api.get_content(article["title"]))

            return add_dict(article, {"content": content})

    class ConvertInlineMath(NodeTransformation):
        def is_target_dict(self, obj):
            return lookup(obj, "attrs", "typeof") == "mw:Extension/math"

        def transform_dict(self, obj):
            formula = json.loads(obj["attrs"]["data-mw"])["body"]["extsrc"]

            return {"type": "inlinemath", "formula": formula}

    class DeleteHeaderAndFooter(DeleteTransformation):

        def shall_delete_dict(self, obj):
            return lookup(obj, "type") == "template" \
                    and obj["name"].startswith("#invoke:")
