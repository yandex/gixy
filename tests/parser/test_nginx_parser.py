import pytest
from gixy.parser.nginx_parser import NginxParser
from gixy.directives.directive import *
from gixy.directives.block import *


def _parse(config):
    return NginxParser(cwd='', allow_includes=False).parse(config)


@pytest.mark.parametrize('config,expected', zip(
    [
        'access_log syslog:server=127.0.0.1,tag=nginx_sentry toolsformat;',
        'user http;',
        'internal;',
        'set $foo "bar";',
        "set $foo 'bar';",
        'proxy_pass http://unix:/run/sock.socket;',
        'rewrite ^/([a-zA-Z0-9]+)$ /$1/${arg_v}.pb break;'
    ],

    [
        [Directive],
        [Directive],
        [Directive],
        [Directive, SetDirective],
        [Directive, SetDirective],
        [Directive],
        [Directive, RewriteDirective]
    ]
))
def test_directive(config, expected):
    assert_config(config, expected)


@pytest.mark.parametrize('config,expected', zip(
    [
        'if (-f /some) {}',
        'location / {}'
    ],

    [
        [Directive, Block, IfBlock],
        [Directive, Block, LocationBlock],
    ]
))
def test_blocks(config, expected):
    assert_config(config, expected)


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
    assert isinstance(tree, Directive)
    assert isinstance(tree, Block)
    assert isinstance(tree, Root)

    assert len(tree.children) == 1
    http = tree.children[0]
    assert isinstance(http, Directive)
    assert isinstance(http, Block)
    assert isinstance(http, HttpBlock)

    assert len(http.children) == 1
    include_server = http.children[0]
    assert isinstance(include_server, Directive)
    assert isinstance(include_server, IncludeBlock)
    assert include_server.file_path == '/etc/nginx/sites/default.conf'

    assert len(include_server.children) == 1
    server = include_server.children[0]
    assert isinstance(server, Directive)
    assert isinstance(server, Block)
    assert isinstance(server, ServerBlock)

    assert len(server.children) == 1
    include_listen = server.children[0]
    assert isinstance(include_listen, Directive)
    assert isinstance(include_listen, IncludeBlock)
    assert include_listen.file_path == '/etc/nginx/conf.d/listen'

    assert len(include_listen.children) == 1
    listen = include_listen.children[0]
    assert isinstance(listen, Directive)
    assert listen.args == ['80']


def test_encoding():
    configs = [
        'bar "\xD1\x82\xD0\xB5\xD1\x81\xD1\x82";'
    ]

    for i, config in enumerate(configs):
        _parse(config)


def assert_config(config, expected):
    tree = _parse(config)
    assert isinstance(tree, Directive)
    assert isinstance(tree, Block)
    assert isinstance(tree, Root)

    child = tree.children[0]
    for ex in expected:
        assert isinstance(child, ex)
