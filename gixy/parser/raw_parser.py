import re
import logging
from cached_property import cached_property

from pyparsing import (
    Literal, Suppress, White, Word, alphanums, Forward, Group, Optional, Combine,
    Keyword, OneOrMore, ZeroOrMore, Regex, QuotedString, nestedExpr)

LOG = logging.getLogger(__name__)


class NginxQuotedString(QuotedString):
    def __init__(self, quoteChar):
        super(NginxQuotedString, self).__init__(quoteChar, escChar='\\', multiline=True)
        # Nginx parse quoted values in special manner:
        # '^https?:\/\/yandex\.ru\/\00\'\"' -> ^https?:\/\/yandex\.ru\/\00'"
        # TODO(buglloc): research and find another special characters!

        self.escCharReplacePattern = '\\\\(\'|")'


class RawParser(object):
    """
    A class that parses nginx configuration with pyparsing
    """

    def __init__(self):
        self._script = None

    def parse(self, file_path):
        """
        Returns the parsed tree.
        """
        # Temporary, dirty hack :(
        content = open(file_path).read()
        content = re.sub(r'(if\s.+)\)\)(\s*\{)?$', '\\1) )\\2', content, flags=re.MULTILINE)
        return self.script.parseString(content, parseAll=True)
        # return self.script.parseFile(file_path, parseAll=True)

    @cached_property
    def script(self):
        # constants
        left_bracket = Suppress("{")
        right_bracket = Suppress("}")
        semicolon = Suppress(";")
        space = White().suppress()
        keyword = Word(alphanums + ".+-_/")
        path = Word(alphanums + ".-_/")
        variable = Word("$_-" + alphanums)
        value_wq = Regex(r'(?:\([^\s;]*\)|\$\{\w+\}|[^\s;(){}])+')
        value_sq = NginxQuotedString(quoteChar="'")
        value_dq = NginxQuotedString(quoteChar='"')
        value = (value_dq | value_sq | value_wq)
        # modifier for location uri [ = | ~ | ~* | ^~ ]
        location_modifier = (
            Keyword("=") |
            Keyword("~*") | Keyword("~") |
            Keyword("^~"))
        # modifier for if statement
        if_modifier = Combine(Optional("!") + (
            Keyword("=") |
            Keyword("~*") | Keyword("~") |
            (Literal("-") + (Literal("f") | Literal("d") | Literal("e") | Literal("x")))))
        condition = (
            (if_modifier + Optional(space) + value) |
            (variable + Optional(space + if_modifier + Optional(space) + value))
        )

        # rules
        include = (
            Keyword("include") +
            space +
            value +
            semicolon
        )("include")

        directive = (
            keyword +
            ZeroOrMore(space + value) +
            semicolon
        )("directive")

        file_delimiter = (
            Suppress("# configuration file ") +
            path +
            Suppress(":")
        )("file_delimiter")

        comment = (
            Regex(r"#.*")
        )("comment").setParseAction(_fix_comment)

        hash_value = Group(
            value +
            ZeroOrMore(space + value) +
            semicolon
        )("hash_value")

        generic_block = Forward()
        if_block = Forward()
        location_block = Forward()
        hash_block = Forward()
        unparsed_block = Forward()

        sub_block = OneOrMore(Group(if_block |
                                    location_block |
                                    hash_block |
                                    generic_block |
                                    include |
                                    directive |
                                    file_delimiter |
                                    comment |
                                    unparsed_block))

        if_block << (
            Keyword("if") +
            Suppress("(") +
            Group(condition) +
            Suppress(")") +
            Group(
                left_bracket +
                Optional(sub_block) +
                right_bracket)
        )("block")

        location_block << (
            Keyword("location") +
            Group(
                Optional(space + location_modifier) +
                Optional(space) + value) +
            Group(
                left_bracket +
                Optional(sub_block) +
                right_bracket)
        )("block")

        hash_block << (
            keyword +
            Group(OneOrMore(space + variable)) +
            Group(
                left_bracket +
                Optional(OneOrMore(hash_value)) +
                right_bracket)
        )("block")

        generic_block << (
            keyword +
            Group(ZeroOrMore(space + variable)) +
            Group(
                left_bracket +
                Optional(sub_block) +
                right_bracket)
        )("block")

        unparsed_block << (
            keyword +
            Group(ZeroOrMore(space + variable)) +
            nestedExpr(opener="{", closer="}")
        )("unparsed_block")

        return sub_block


def _fix_comment(string, location, tokens):
    """
    Returns "cleared" comment text

    :param string: original parse string
    :param location: location in the string where matching started
    :param tokens: list of the matched tokens, packaged as a ParseResults_ object
    :return: list of the cleared comment tokens
    """

    comment = tokens[0][1:].strip()
    return [comment]
