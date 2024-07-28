from gixy.parser.nginx_parser import NginxParser
from gixy.directives.directive import *


def _get_parsed(config):
    root = NginxParser(cwd='', allow_includes=False).parse(config)
    return root.children[0]


def test_directive():
    config = 'some "foo" "bar";'

    directive = _get_parsed(config)
    assert isinstance(directive, Directive)
    assert directive.name == 'some'
    assert directive.args == ['foo', 'bar']
    assert str(directive) == 'some foo bar;'


def test_add_header():
    config = 'add_header "X-Foo" "bar";'

    directive = _get_parsed(config)
    assert isinstance(directive, AddHeaderDirective)
    assert directive.name == 'add_header'
    assert directive.args == ['X-Foo', 'bar']
    assert directive.header == 'x-foo'
    assert directive.value == 'bar'
    assert not directive.always
    assert str(directive) == 'add_header X-Foo bar;'


def test_add_header_always():
    config = 'add_header "X-Foo" "bar" always;'

    directive = _get_parsed(config)
    assert isinstance(directive, AddHeaderDirective)
    assert directive.name == 'add_header'
    assert directive.args == ['X-Foo', 'bar', 'always']
    assert directive.header == 'x-foo'
    assert directive.value == 'bar'
    assert directive.always
    assert str(directive) == 'add_header X-Foo bar always;'


def test_set():
    config = 'set $foo bar;'

    directive = _get_parsed(config)
    assert isinstance(directive, SetDirective)
    assert directive.name == 'set'
    assert directive.args == ['$foo', 'bar']
    assert directive.variable == 'foo'
    assert directive.value == 'bar'
    assert str(directive) == 'set $foo bar;'
    assert directive.provide_variables


def test_rewrite():
    config = 'rewrite ^ http://some;'

    directive = _get_parsed(config)
    assert isinstance(directive, RewriteDirective)
    assert directive.name == 'rewrite'
    assert directive.args == ['^', 'http://some']
    assert str(directive) == 'rewrite ^ http://some;'
    assert directive.provide_variables

    assert directive.pattern == '^'
    assert directive.replace == 'http://some'
    assert directive.flag == None


def test_rewrite_flags():
    config = 'rewrite ^/(.*)$ http://some/$1 redirect;'

    directive = _get_parsed(config)
    assert isinstance(directive, RewriteDirective)
    assert directive.name == 'rewrite'
    assert directive.args == ['^/(.*)$', 'http://some/$1', 'redirect']
    assert str(directive) == 'rewrite ^/(.*)$ http://some/$1 redirect;'
    assert directive.provide_variables

    assert directive.pattern == '^/(.*)$'
    assert directive.replace == 'http://some/$1'
    assert directive.flag == 'redirect'


def test_root():
    config = 'root /var/www/html;'

    directive = _get_parsed(config)
    assert isinstance(directive, RootDirective)
    assert directive.name == 'root'
    assert directive.args == ['/var/www/html']
    assert str(directive) == 'root /var/www/html;'
    assert directive.provide_variables

    assert directive.path == '/var/www/html'
