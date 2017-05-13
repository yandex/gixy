from nose.tools import assert_equals, assert_is_instance, assert_false, assert_true
from gixy.parser.nginx_parser import NginxParser
from gixy.directives.directive import *


def _get_parsed(config):
    root = NginxParser(cwd='', allow_includes=False).parse(config)
    return root.children[0]


def test_directive():
    config = 'some "foo" "bar";'

    directive = _get_parsed(config)
    assert_is_instance(directive, Directive)
    assert_equals(directive.name, 'some')
    assert_equals(directive.args, ['foo', 'bar'])
    assert_equals(str(directive), 'some foo bar;')


def test_add_header():
    config = 'add_header "X-Foo" "bar";'

    directive = _get_parsed(config)
    assert_is_instance(directive, AddHeaderDirective)
    assert_equals(directive.name, 'add_header')
    assert_equals(directive.args, ['X-Foo', 'bar'])
    assert_equals(directive.header, 'x-foo')
    assert_equals(directive.value, 'bar')
    assert_false(directive.always)
    assert_equals(str(directive), 'add_header X-Foo bar;')


def test_add_header_always():
    config = 'add_header "X-Foo" "bar" always;'

    directive = _get_parsed(config)
    assert_is_instance(directive, AddHeaderDirective)
    assert_equals(directive.name, 'add_header')
    assert_equals(directive.args, ['X-Foo', 'bar', 'always'])
    assert_equals(directive.header, 'x-foo')
    assert_equals(directive.value, 'bar')
    assert_true(directive.always)
    assert_equals(str(directive), 'add_header X-Foo bar always;')


def test_set():
    config = 'set $foo bar;'

    directive = _get_parsed(config)
    assert_is_instance(directive, SetDirective)
    assert_equals(directive.name, 'set')
    assert_equals(directive.args, ['$foo', 'bar'])
    assert_equals(directive.variable, 'foo')
    assert_equals(directive.value, 'bar')
    assert_equals(str(directive), 'set $foo bar;')
    assert_true(directive.provide_variables)


def test_rewrite():
    config = 'rewrite ^ http://some;'

    directive = _get_parsed(config)
    assert_is_instance(directive, RewriteDirective)
    assert_equals(directive.name, 'rewrite')
    assert_equals(directive.args, ['^', 'http://some'])
    assert_equals(str(directive), 'rewrite ^ http://some;')
    assert_true(directive.provide_variables)

    assert_equals(directive.pattern, '^')
    assert_equals(directive.replace, 'http://some')
    assert_equals(directive.flag, None)


def test_rewrite_flags():
    config = 'rewrite ^/(.*)$ http://some/$1 redirect;'

    directive = _get_parsed(config)
    assert_is_instance(directive, RewriteDirective)
    assert_equals(directive.name, 'rewrite')
    assert_equals(directive.args, ['^/(.*)$', 'http://some/$1', 'redirect'])
    assert_equals(str(directive), 'rewrite ^/(.*)$ http://some/$1 redirect;')
    assert_true(directive.provide_variables)

    assert_equals(directive.pattern, '^/(.*)$')
    assert_equals(directive.replace, 'http://some/$1')
    assert_equals(directive.flag, 'redirect')


def test_root():
    config = 'root /var/www/html;'

    directive = _get_parsed(config)
    assert_is_instance(directive, RootDirective)
    assert_equals(directive.name, 'root')
    assert_equals(directive.args, ['/var/www/html'])
    assert_equals(str(directive), 'root /var/www/html;')
    assert_true(directive.provide_variables)

    assert_equals(directive.path, '/var/www/html')
