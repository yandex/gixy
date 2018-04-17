from nose.tools import assert_equals, assert_true, assert_false
from tests.asserts import assert_is_instance, assert_is_none, assert_is_not_none
from gixy.parser.nginx_parser import NginxParser
from gixy.directives.block import *

# TODO(buglloc): what about include block?


def _get_parsed(config):
    root = NginxParser(cwd='', allow_includes=False).parse(config)
    return root.children[0]


def test_block():
    config = 'some {some;}'

    directive = _get_parsed(config)
    assert_is_instance(directive, Block)
    assert_true(directive.is_block)
    assert_true(directive.self_context)
    assert_false(directive.provide_variables)


def test_http():
    config = '''
http {
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;
}
    '''

    directive = _get_parsed(config)
    assert_is_instance(directive, HttpBlock)
    assert_true(directive.is_block)
    assert_true(directive.self_context)
    assert_false(directive.provide_variables)


def test_server():
    config = '''
server {
    listen 80;
    server_name _;
    server_name cool.io;
}

    '''

    directive = _get_parsed(config)
    assert_is_instance(directive, ServerBlock)
    assert_true(directive.is_block)
    assert_true(directive.self_context)
    assert_equals([d.args[0] for d in directive.get_names()], ['_', 'cool.io'])
    assert_false(directive.provide_variables)


def test_location():
    config = '''
location / {
}
    '''

    directive = _get_parsed(config)
    assert_is_instance(directive, LocationBlock)
    assert_true(directive.is_block)
    assert_true(directive.self_context)
    assert_true(directive.provide_variables)
    assert_is_none(directive.modifier)
    assert_equals(directive.path, '/')
    assert_false(directive.is_internal)


def test_location_internal():
    config = '''
location / {
    internal;
}
    '''

    directive = _get_parsed(config)
    assert_is_instance(directive, LocationBlock)
    assert_true(directive.is_internal)


def test_location_modifier():
    config = '''
location = / {
}
    '''

    directive = _get_parsed(config)
    assert_is_instance(directive, LocationBlock)
    assert_equals(directive.modifier, '=')
    assert_equals(directive.path, '/')


def test_if():
    config = '''
if ($some) {
}
    '''

    directive = _get_parsed(config)
    assert_is_instance(directive, IfBlock)
    assert_true(directive.is_block)
    assert_false(directive.self_context)
    assert_false(directive.provide_variables)
    assert_equals(directive.variable, '$some')
    assert_is_none(directive.operand)
    assert_is_none(directive.value)


def test_if_modifier():
    config = '''
if (-f /some) {
}
    '''

    directive = _get_parsed(config)
    assert_is_instance(directive, IfBlock)
    assert_equals(directive.operand, '-f')
    assert_equals(directive.value, '/some')
    assert_is_none(directive.variable)


def test_if_variable():
    config = '''
if ($http_some = '/some') {
}
    '''

    directive = _get_parsed(config)
    assert_is_instance(directive, IfBlock)
    assert_equals(directive.variable, '$http_some')
    assert_equals(directive.operand, '=')
    assert_equals(directive.value, '/some')


def test_block_some_flat():
    config = '''
    some {
        default_type  application/octet-stream;
        sendfile        on;
        if (-f /some/) {
            keepalive_timeout  65;
        }
    }
        '''

    directive = _get_parsed(config)
    for d in ['default_type', 'sendfile', 'keepalive_timeout']:
        c = directive.some(d, flat=True)
        assert_is_not_none(c)
        assert_equals(c.name, d)


def test_block_some_not_flat():
    config = '''
    some {
        default_type  application/octet-stream;
        sendfile        on;
        if (-f /some/) {
            keepalive_timeout  65;
        }
    }
        '''

    directive = _get_parsed(config)
    c = directive.some('keepalive_timeout', flat=False)
    assert_is_none(c)


def test_block_find_flat():
    config = '''
    some {
        directive 1;
        if (-f /some/) {
            directive 2;
        }
    }
        '''

    directive = _get_parsed(config)
    finds = directive.find('directive', flat=True)
    assert_equals(len(finds), 2)
    assert_equals([x.name for x in finds], ['directive', 'directive'])
    assert_equals([x.args[0] for x in finds], ['1', '2'])


def test_block_find_not_flat():
    config = '''
    some {
        directive 1;
        if (-f /some/) {
            directive 2;
        }
    }
        '''

    directive = _get_parsed(config)
    finds = directive.find('directive', flat=False)
    assert_equals(len(finds), 1)
    assert_equals([x.name for x in finds], ['directive'])
    assert_equals([x.args[0] for x in finds], ['1'])


def test_block_map():
    config = '''
map $some_var $some_other_var {
    a   b;
    default c;
}
    '''

    directive = _get_parsed(config)
    assert_is_instance(directive, MapBlock)
    assert_true(directive.is_block)
    assert_false(directive.self_context)
    assert_true(directive.provide_variables)
    assert_equals(directive.variable, 'some_other_var')
