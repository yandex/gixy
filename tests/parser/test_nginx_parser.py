from nose.tools import assert_equal
from tests.asserts import assert_is_instance
from gixy.parser.nginx_parser import NginxParser
from gixy.directives.directive import *
from gixy.directives.block import *


def _parse(config):
    return NginxParser(cwd='', allow_includes=False).parse(config)


def test_directive():
    configs = [
        'access_log syslog:server=127.0.0.1,tag=nginx_sentry toolsformat;',
        'user http;',
        'internal;',
        'set $foo "bar";',
        "set $foo 'bar';",
        'proxy_pass http://unix:/run/sock.socket;',
        'rewrite ^/([a-zA-Z0-9]+)$ /$1/${arg_v}.pb break;'
    ]

    expected = [
        [Directive],
        [Directive],
        [Directive],
        [Directive, SetDirective],
        [Directive],
        [Directive, RewriteDirective]
    ]

    for i, config in enumerate(configs):
        return assert_config, config, expected[i]


def test_blocks():
    configs = [
        'if (-f /some) {}',
        'location / {}'
    ]

    expected = [
        [Directive, Block, IfBlock],
        [Directive, Block, LocationBlock],
    ]

    for i, config in enumerate(configs):
        yield assert_config, config, expected[i]


def test_dump_simple():
    config = '''
# configuration file /etc/nginx/nginx.conf:
http {
    include sites/*.conf;
}

# configuration file /etc/nginx/conf.d/listen:
listen 80;

# configuration file /etc/nginx/sites/default.conf:
server {
    include conf.d/listen;
}
    '''

    tree = _parse(config)
    assert_is_instance(tree, Directive)
    assert_is_instance(tree, Block)
    assert_is_instance(tree, Root)

    assert_equal(len(tree.children), 1)
    http = tree.children[0]
    assert_is_instance(http, Directive)
    assert_is_instance(http, Block)
    assert_is_instance(http, HttpBlock)

    assert_equal(len(http.children), 1)
    include_server = http.children[0]
    assert_is_instance(include_server, Directive)
    assert_is_instance(include_server, IncludeBlock)
    assert_equal(include_server.file_path, '/etc/nginx/sites/default.conf')

    assert_equal(len(include_server.children), 1)
    server = include_server.children[0]
    assert_is_instance(server, Directive)
    assert_is_instance(server, Block)
    assert_is_instance(server, ServerBlock)

    assert_equal(len(server.children), 1)
    include_listen = server.children[0]
    assert_is_instance(include_listen, Directive)
    assert_is_instance(include_listen, IncludeBlock)
    assert_equal(include_listen.file_path, '/etc/nginx/conf.d/listen')

    assert_equal(len(include_listen.children), 1)
    listen = include_listen.children[0]
    assert_is_instance(listen, Directive)
    assert_equal(listen.args, ['80'])


def assert_config(config, expected):
    tree = _parse(config)
    assert_is_instance(tree, Directive)
    assert_is_instance(tree, Block)
    assert_is_instance(tree, Root)

    child = tree.children[0]
    for ex in expected:
        assert_is_instance(child, ex)
