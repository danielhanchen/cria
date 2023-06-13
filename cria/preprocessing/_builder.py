"""
    Copyright Daniel Han-Chen
    Fast customized BeautifulSoup Tree Builders.
"""
__all__ = [
    "HTMLParserTreeBuilder_Fast",
    "LXMLTreeBuilder_Fast",
]

NULL_FUNCTION = lambda *args: None

from bs4.builder._htmlparser import BeautifulSoupHTMLParser, HTMLParserTreeBuilder
from bs4.builder._lxml import LXMLTreeBuilder, LXMLTreeBuilderForXML
from lxml.etree import HTMLParser as LXMLHTMLParser

class BeautifulSoupHTMLParser_Fast(BeautifulSoupHTMLParser):
    REPLACE = "ignore" # Default = replace. We follow LXML's default, which is ignore.
    handle_comment = NULL_FUNCTION
    handle_decl    = NULL_FUNCTION
    handle_pi      = NULL_FUNCTION
pass

class HTMLParserTreeBuilder_Fast(HTMLParserTreeBuilder):
    def feed(self, markup):
        parser = BeautifulSoupHTMLParser_Fast()
        parser.soup = self.soup
        parser.feed(markup)
        parser.close()
        parser.already_closed_empty_element = []
    pass
pass


class LXMLTreeBuilderForXML_Fast(LXMLTreeBuilderForXML):
    comment = NULL_FUNCTION
    doctype = NULL_FUNCTION
    pi      = NULL_FUNCTION
    test_fragment_to_document = NULL_FUNCTION
pass

class LXMLTreeBuilder_Fast(LXMLTreeBuilder, LXMLTreeBuilderForXML_Fast):
    test_fragment_to_document = NULL_FUNCTION

    def feed(self, markup):
        parser = LXMLHTMLParser(encoding          = self.soup.original_encoding,
                                recover           = True,
                                remove_blank_text = True,
                                remove_comments   = True,
                                remove_pis        = True)
        parser.feed(markup)
        parser.close()
        self.parser = parser
    pass
pass
