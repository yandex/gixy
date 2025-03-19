from nose.tools import assert_equal, assert_false, assert_true
from tests.asserts import assert_is_instance
from gixy.parser.nginx_parser import NginxParser
from gixy.directives.directive import Directive, AddHeaderDirective, SetDirective, RewriteDirective, RootDirective


def _get_parsed(config):
    root = NginxParser(cwd='', allow_includes=False).parse(config)
    return root.children[0]


def test_directive():
    config = 'some "foo" "bar";'

    directive = _get_parsed(config)
    assert_is_instance(directive, Directive)
    assert_equal(directive.name, 'some')
    assert_equal(directive.args, ['foo', 'bar'])
    assert_equal(str(directive), 'some foo bar;')


def test_add_header():
    config = 'add_header "X-Foo" "bar";'

    directive = _get_parsed(config)
    assert_is_instance(directive, AddHeaderDirective)
    assert_equal(directive.name, 'add_header')
    assert_equal(directive.args, ['X-Foo', 'bar'])
    assert_equal(directive.header, 'x-foo')
    assert_equal(directive.value, 'bar')
    assert_false(directive.always)
    assert_equal(str(directive), 'add_header X-Foo bar;')


def test_add_header_always():
    config = 'add_header "X-Foo" "bar" always;'

    directive = _get_parsed(config)
    assert_is_instance(directive, AddHeaderDirective)
    assert_equal(directive.name, 'add_header')
    assert_equal(directive.args, ['X-Foo', 'bar', 'always'])
    assert_equal(directive.header, 'x-foo')
    assert_equal(directive.value, 'bar')
    assert_true(directive.always)
    assert_equal(str(directive), 'add_header X-Foo bar always;')


def test_set():
    config = 'set $foo bar;'

    directive = _get_parsed(config)
    assert_is_instance(directive, SetDirective)
    assert_equal(directive.name, 'set')
    assert_equal(directive.args, ['$foo', 'bar'])
    assert_equal(directive.variable, 'foo')
    assert_equal(directive.value, 'bar')
    assert_equal(str(directive), 'set $foo bar;')
    assert_true(directive.provide_variables)


def test_rewrite():
    config = 'rewrite ^ http://some;'

    directive = _get_parsed(config)
    assert_is_instance(directive, RewriteDirective)
    assert_equal(directive.name, 'rewrite')
    assert_equal(directive.args, ['^', 'http://some'])
    assert_equal(str(directive), 'rewrite ^ http://some;')
    assert_true(directive.provide_variables)

    assert_equal(directive.pattern, '^')
    assert_equal(directive.replace, 'http://some')
    assert_equal(directive.flag, None)


def test_rewrite_flags():
    config = 'rewrite ^/(.*)$ http://some/$1 redirect;'

    directive = _get_parsed(config)
    assert_is_instance(directive, RewriteDirective)
    assert_equal(directive.name, 'rewrite')
    assert_equal(directive.args, ['^/(.*)$', 'http://some/$1', 'redirect'])
    assert_equal(str(directive), 'rewrite ^/(.*)$ http://some/$1 redirect;')
    assert_true(directive.provide_variables)

    assert_equal(directive.pattern, '^/(.*)$')
    assert_equal(directive.replace, 'http://some/$1')
    assert_equal(directive.flag, 'redirect')


def test_root():
    config = 'root /var/www/html;'

    directive = _get_parsed(config)
    assert_is_instance(directive, RootDirective)
    assert_equal(directive.name, 'root')
    assert_equal(directive.args, ['/var/www/html'])
    assert_equal(str(directive), 'root /var/www/html;')
    assert_true(directive.provide_variables)

    assert_equal(directive.path, '/var/www/html')
