import re
import logging

from gixy.core.regexp import Regexp
from gixy.core.context import get_context

LOG = logging.getLogger(__name__)
# See ngx_http_script_compile in http/ngx_http_script.c
EXTRACT_RE = re.compile(r'\$([1-9]|[a-z_][a-z0-9_]*|\{[a-z0-9_]+\})', re.IGNORECASE)


def compile_script(script):
    """
    Compile Nginx script to list of variables.
    Example:
        compile_script('http://$foo:$bar') ->
            [Variable('http://'), Variable($foo), Variable(':', Variable($bar).

    :param str script: Nginx scrip.
    :return Variable[]: list of variable.
    """
    depends = []
    context = get_context()
    for i, var in enumerate(EXTRACT_RE.split(str(script))):
        if i % 2:
            # Variable
            var = var.strip('{}\x20')
            var = context.get_var(var)
            if var:
                depends.append(var)
        elif var:
            # Literal
            depends.append(Variable(name=None, value=var, have_script=False))
    return depends


class Variable(object):
    def __init__(self, name, value=None, boundary=None, provider=None, have_script=True):
        """
        Gixy Nginx variable class - parse and provide helpers to work with it.

        :param str|None name: variable name.
        :param str|Regexp value: variable value..
        :param Regexp boundary: variable boundary set.
        :param Directive provider: directive that provide variable (e.g. if, location, rewrite, etc).
        :param bool have_script: may variable have nginx script or not (mostly used to indicate a string literal).
        """

        self.name = name
        self.value = value
        self.regexp = None
        self.depends = None
        self.boundary = boundary
        self.provider = provider
        if isinstance(value, Regexp):
            self.regexp = value
        elif have_script:
            self.depends = compile_script(value)

    def can_contain(self, char):
        """
        Checks if variable can contain the specified char.

        :param str char: character to test.
        :return: True if variable can contain the specified char, False otherwise.
        """

        # First of all check boundary set
        if self.boundary and not self.boundary.can_contain(char):
            return False

        # Then regexp
        if self.regexp:
            return self.regexp.can_contain(char, skip_literal=True)

        # Then dependencies
        if self.depends:
            return any(dep.can_contain(char) for dep in self.depends)

        # Otherwise user can't control value of this variable
        return False

    def can_startswith(self, char):
        """
        Checks if variable can starts with the specified char.

        :param str char: character to test.
        :return: True if variable can starts with the specified char, False otherwise.
        """

        # First of all check boundary set
        if self.boundary and not self.boundary.can_startswith(char):
            return False

        # Then regexp
        if self.regexp:
            return self.regexp.can_startswith(char)

        # Then dependencies
        if self.depends:
            return self.depends[0].can_startswith(char)

        # Otherwise user can't control value of this variable
        return False

    def must_contain(self, char):
        """
        Checks if variable MUST contain the specified char.

        :param str char: character to test.
        :return: True if variable must contain the specified char, False otherwise.
        """

        # First of all check boundary set
        if self.boundary and self.boundary.must_contain(char):
            return True

        # Then regexp
        if self.regexp:
            return self.regexp.must_contain(char)

        # Then dependencies
        if self.depends:
            return any(dep.must_contain(char) for dep in self.depends)

        # Otherwise checks literal
        return self.value and char in self.value

    def must_startswith(self, char):
        """
        Checks if variable MUST starts with the specified char.

        :param str char: character to test.
        :return: True if variable must starts with the specified char.
        """

        # First of all check boundary set
        if self.boundary and self.boundary.must_startswith(char):
            return True

        # Then regexp
        if self.regexp:
            return self.regexp.must_startswith(char)

        # Then dependencies
        if self.depends:
            return self.depends[0].must_startswith(char)

        # Otherwise checks literal
        return self.value and self.value[0] == char

    @property
    def providers(self):
        """
        Returns list of variable provides.

        :return Directive[]: providers.
        """
        result = []
        if self.provider:
            result.append(self.provider)
        if self.depends:
            for dep in self.depends:
                result += dep.providers
        return result
