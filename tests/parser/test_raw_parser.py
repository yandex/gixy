from nose.tools import assert_equals
import mock
from six import StringIO
from six.moves import builtins
from gixy.parser.raw_parser import *


def test_directive():
    config = '''
access_log syslog:server=127.0.0.1,tag=nginx_sentry toolsformat;
user http;
internal;
set $foo "bar";
set $foo 'bar';
proxy_pass http://unix:/run/sock.socket;
rewrite ^/([a-zA-Z0-9]+)$ /$1/${arg_v}.pb break;
    server_name some.tld ~^(www\.)?podberi.(?:ru|com|ua)$
    ~^(www\.)?guru.yandex.ru$;
        '''

    expected = [
        ['access_log', 'syslog:server=127.0.0.1,tag=nginx_sentry', 'toolsformat'],
        ['user', 'http'],
        ['internal'],
        ['set', '$foo', 'bar'],
        ['set', '$foo', 'bar'],
        ['proxy_pass', 'http://unix:/run/sock.socket'],
        ['rewrite', '^/([a-zA-Z0-9]+)$', '/$1/${arg_v}.pb', 'break'],
        ['server_name', 'some.tld', '~^(www\.)?podberi.(?:ru|com|ua)$', '~^(www\.)?guru.yandex.ru$']
    ]

    assert_config(config, expected)


def test_block():
    config = '''
http {
}
        '''

    expected = [['http', [], []]]
    assert_config(config, expected)


def test_block_with_child():
    config = '''
http {
    gzip  on;
}
        '''

    expected = [['http', [], [['gzip', 'on']]]]
    assert_config(config, expected)


def test_location_simple():
    config = '''
location / {
}
location = /foo {
}
location ~ ^/bar {
}
location ~* ^/baz$ {
}
location ^~ ^/bazz {
}
# Whitespace may be omitted:((
location ~\.(js|css)$ {
}
        '''

    expected = [['location', ['/'], []],
                ['location', ['=', '/foo'], []],
                ['location', ['~', '^/bar'], []],
                ['location', ['~*', '^/baz$'], []],
                ['location', ['^~', '^/bazz'], []],
                ['Whitespace may be omitted:(('],
                ['location', ['~', '\.(js|css)$'], []]]

    assert_config(config, expected)


def test_quoted_strings():
    config = '''
some_sq '\\'la\\.\\/\\"';
some_dq '\\'la\\.\\/\\"';
        '''

    expected = [['some_sq', '\'la\\.\\/\"'],
                ['some_dq', '\'la\\.\\/\"']]

    assert_config(config, expected)


def test_location_child():
    config = '''
location = /foo {
     proxy_pass http://unix:/run/sock.socket;
}
        '''

    expected = [['location', ['=', '/foo'], [
        ['proxy_pass', 'http://unix:/run/sock.socket']
    ]]]
    assert_config(config, expected)


def test_nested_location():
    config = '''
location ~* ^/foo {
    location = /foo/bar {
        internal;
        proxy_pass http://any.yandex.ru;
    }

    location = /foo/baz {
        proxy_pass upstream;
    }
}
        '''

    expected = [['location', ['~*', '^/foo'], [
        ['location', ['=', '/foo/bar'], [
            ['internal'],
            ['proxy_pass', 'http://any.yandex.ru']
        ]],
        ['location', ['=', '/foo/baz'], [
            ['proxy_pass', 'upstream']
        ]],
    ]]]

    assert_config(config, expected)


def test_hash_block():
    config = '''
geo $geo {
    default        0;

    127.0.0.1      2;
    192.168.1.0/24 1;
    10.1.0.0/16    1;

    ::1            2;
    2001:0db8::/32 1;
}
        '''

    expected = [['geo', ['$geo'], [
        ['default', '0'],
        ['127.0.0.1', '2'],
        ['192.168.1.0/24', '1'],
        ['10.1.0.0/16', '1'],
        ['::1', '2'],
        ['2001:0db8::/32', '1']
    ]]]

    assert_config(config, expected)


def test_hash_block_in_location():
    config = '''
location /iphone/ {
    types {
      text/html  html htm shtml;
      application/json json;
      application/rss+xml  rss;
      text/vnd.sun.j2me.app-descriptor  jad;
    }
}
        '''

    expected = [['location', ['/iphone/'], [
        ['types', [], [
            ['text/html', 'html', 'htm', 'shtml'],
            ['application/json', 'json'],
            ['application/rss+xml', 'rss'],
            ['text/vnd.sun.j2me.app-descriptor', 'jad']
        ]],
    ]]]

    assert_config(config, expected)


def test_named_location():
    config = '''
location @foo {
    proxy_pass http://any.yandex.ru;
}
        '''

    expected = [['location', ['@foo'], [
        ['proxy_pass', 'http://any.yandex.ru']
    ]]]

    assert_config(config, expected)


def test_if():
    config = '''
# http://nginx.org/ru/docs/http/ngx_http_rewrite_module.html#if

if ($http_user_agent ~ MSIE) {
    rewrite ^(.*)$ /msie/$1 break;
}

if ($http_cookie ~* "id=([^;]+)(?:;|$)") {
    set $id $1;
}

if ($request_method = POST) {
    return 405;
}

if ($slow) {
    limit_rate 10k;
}

if ($invalid_referer) {
    return 403;
}

if (!-e "/var/data/$dataset") {
    return 503;
}

if ($https_or_slb = (by_slb|https)) {
}

if ($host ~* (lori|rage2)\.yandex\.(ru|ua|com|com\.tr)) {
    set $x_frame_options ALLOW;
}
        '''

    expected = [
        ['http://nginx.org/ru/docs/http/ngx_http_rewrite_module.html#if'],
        ['if', ['$http_user_agent', '~', 'MSIE'], [
            ['rewrite', '^(.*)$', '/msie/$1', 'break']
        ]],
        ['if', ['$http_cookie', '~*', 'id=([^;]+)(?:;|$)'], [
            ['set', '$id', '$1']
        ]],
        ['if', ['$request_method', '=', 'POST'], [
            ['return', '405']
        ]],
        ['if', ['$slow'], [
            ['limit_rate', '10k']
        ]],
        ['if', ['$invalid_referer'], [
            ['return', '403']
        ]],
        ['if', ['!-e', '/var/data/$dataset'], [
            ['return', '503']
        ]],
        ['if', ['$https_or_slb', '=', '(by_slb|https)'], [
        ]],
        ['if', ['$host', '~*', '(lori|rage2)\.yandex\.(ru|ua|com|com\.tr)'], [
            ['set', '$x_frame_options', 'ALLOW']
        ]],
    ]

    assert_config(config, expected)


def test_hash_block_map():
    config = '''
# http://nginx.org/ru/docs/http/ngx_http_map_module.html

map $http_host $name {
    hostnames;

    default       0;

    example.com   1;
    *.example.com 1;
    example.org   2;
    *.example.org 2;
    .example.net  3;
    wap.*         4;
}

map $http_user_agent $mobile {
    default       0;
    "~Opera Mini" 1;
}
        '''

    expected = [
        ['http://nginx.org/ru/docs/http/ngx_http_map_module.html'],
        ['map', ['$http_host', '$name'], [
            ['hostnames'],
            ['default', '0'],
            ['example.com', '1'],
            ['*.example.com', '1'],
            ['example.org', '2'],
            ['*.example.org', '2'],
            ['.example.net', '3'],
            ['wap.*', '4'],
        ]],
        ['map', ['$http_user_agent', '$mobile'], [
            ['default', '0'],
            ['~Opera Mini', '1'],
        ]]
    ]

    assert_config(config, expected)


def test_upstream():
    config = '''
# http://nginx.org/ru/docs/http/ngx_http_upstream_module.html

upstream backend {
    server backend1.example.com       weight=5;
    server backend2.example.com:8080;
    server unix:/tmp/backend3;

    server backup1.example.com:8080   backup;
    server backup2.example.com:8080   backup;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
        '''

    expected = [
        ['http://nginx.org/ru/docs/http/ngx_http_upstream_module.html'],
        ['upstream', ['backend'], [
            ['server', 'backend1.example.com', 'weight=5'],
            ['server', 'backend2.example.com:8080'],
            ['server', 'unix:/tmp/backend3'],
            ['server', 'backup1.example.com:8080', 'backup'],
            ['server', 'backup2.example.com:8080', 'backup'],
        ]],
        ['server', [], [
            ['location', ['/'], [
                ['proxy_pass', 'http://backend']
            ]]
        ]]]

    assert_config(config, expected)


def test_issue_8():
    config = '''
# http://nginx.org/ru/docs/http/ngx_http_upstream_module.html
if ($http_referer ~* (\.(ru|ua|by|kz)/(pages/music|partners/|page-no-rights\.xml)) ) {
    set $temp A;
}
        '''

    expected = [
        ['http://nginx.org/ru/docs/http/ngx_http_upstream_module.html'],
        ['if', ['$http_referer', '~*', '(\.(ru|ua|by|kz)/(pages/music|partners/|page-no-rights\.xml))'], [
            ['set', '$temp', 'A']
        ]]
    ]

    assert_config(config, expected)


def test_issue_11():
    config = '''
init_by_lua_block {
    tvm = require "nginx.tvm"
}
        '''

    expected = [
        ['init_by_lua_block', [], ['tvm', '=', 'require', '"nginx.tvm"']]
    ]

    assert_config(config, expected)


def test_lua_block():
    config = '''
# https://github.com/openresty/lua-nginx-module#typical-uses
location = /lua {
 # MIME type determined by default_type:
 default_type 'text/plain';

 content_by_lua_block {
     local res = ngx.location.capture("/some_other_location")
     if res then
         ngx.say("status: ", res.status)
         ngx.say("body:")
         ngx.print(res.body)
     end
 }
}
        '''

    expected = [
        ['https://github.com/openresty/lua-nginx-module#typical-uses'],
        ['location', ['=', '/lua'], [
            ['MIME type determined by default_type:'],
            ['default_type', 'text/plain'],
            ['content_by_lua_block', [], [
                'local', 'res', '=', 'ngx.location.capture(', '"/some_other_location"', ')',
                'if', 'res', 'then',
                    'ngx.say(', '"status: "', ',', 'res.status)',
                    'ngx.say(', '"body:"', ')',
                    'ngx.print(res.body)',
                'end']]
        ]]
    ]

    assert_config(config, expected)


def test_lua_block_brackets():
    config = '''
location = /foo {
 rewrite_by_lua_block {
     res = ngx.location.capture("/memc",
         { args = { cmd = "incr", key = ngx.var.uri } }
     )
 }

 proxy_pass http://blah.blah.com;
}
        '''

    expected = [
        ['location', ['=', '/foo'], [
            ['rewrite_by_lua_block', [], [
                'res', '=', 'ngx.location.capture(', '"/memc"', ',',
                    ['args', '=', ['cmd', '=', '"incr"', ',', 'key', '=', 'ngx.var.uri']],
                ')']],
            ['proxy_pass', 'http://blah.blah.com']
        ]]
    ]

    assert_config(config, expected)


def test_file_delims():
    config = '''
# configuration file /etc/nginx/nginx.conf:
http {
    include sites/*.conf;
}

# configuration file /etc/nginx/sites/default.conf:
server {

}
        '''

    expected = [
        ['/etc/nginx/nginx.conf'],
        ['http', [], [
            ['include', 'sites/*.conf']
        ]],
        ['/etc/nginx/sites/default.conf'],
        ['server', [], []]
    ]

    assert_config(config, expected)


def test_comments():
    config = '''
# Some comment
add_header X-Some-Comment some;

# 
# Comment with padding
# 
add_header X-Padding-Comment padding;

#
add_header X-Blank-Comment blank;
        '''

    expected = [
        ['Some comment'],
        ['add_header', 'X-Some-Comment', 'some'],
        [''],
        ['Comment with padding'],
        [''],
        ['add_header', 'X-Padding-Comment', 'padding'],
        [''],
        ['add_header', 'X-Blank-Comment', 'blank'],
    ]

    assert_config(config, expected)


def assert_config(config, expected):
    with mock.patch('%s.open' % builtins.__name__) as mock_open:
        mock_open.return_value = StringIO(config)
        actual = RawParser().parse('/foo/bar')
        assert_equals(actual.asList(), expected)
