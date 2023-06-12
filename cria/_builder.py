"""
    Copyright Daniel Han-Chen
    Fast customized BeautifulSoup Tree Builders.
"""
__all__ = [
    "HTMLParserTreeBuilder_Fast",
    "LXMLTreeBuilder_Fast",
]

from bs4.builder import ParserRejectedMarkup
from bs4.builder._htmlparser import BeautifulSoupHTMLParser, HTMLParserTreeBuilder
from bs4.builder._lxml import LXMLTreeBuilder, LXMLTreeBuilderForXML
from lxml.etree import HTMLParser as LXMLHTMLParser, ParserError as LXMLParserError
from functools import partial
from sys import maxsize as MAX_SIZE_T

LXMLHTMLParser = partial(LXMLHTMLParser,
                         recover           = True,
                         remove_blank_text = True,
                         remove_comments   = True,
                         remove_pis        = True)
NULL_FUNCTION = lambda *args: None


class BeautifulSoupHTMLParser_Fast(BeautifulSoupHTMLParser):
    REPLACE = "ignore"
    handle_comment = NULL_FUNCTION
    handle_decl    = NULL_FUNCTION
    handle_pi      = NULL_FUNCTION
pass

class HTMLParserTreeBuilder_Fast(HTMLParserTreeBuilder):
    def feed(self, markup):
        args, kwargs = self.parser_args
        parser = BeautifulSoupHTMLParser_Fast()
        parser.soup = self.soup
        try: parser.feed(markup)
        except AssertionError as e: raise ParserRejectedMarkup(e)
        parser.close()
        parser.already_closed_empty_element = []
    pass
pass


class LXMLTreeBuilderForXML_Fast(LXMLTreeBuilderForXML):
    CHUNK_SIZE = MAX_SIZE_T
    comment = NULL_FUNCTION
    doctype = NULL_FUNCTION
    pi      = NULL_FUNCTION
    test_fragment_to_document = NULL_FUNCTION
pass

class LXMLTreeBuilder_Fast(LXMLTreeBuilder, LXMLTreeBuilderForXML_Fast):
    test_fragment_to_document = NULL_FUNCTION
    default_parser = lambda *args: LXMLHTMLParser
pass
