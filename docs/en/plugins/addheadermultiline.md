# [add_header_multiline] Multiline response headers

You should avoid using multiline response headers, because:
  * they are deprecated (see [RFC 7230](https://tools.ietf.org/html/rfc7230#section-3.2.4));
  * some HTTP-clients and web browser never supported them (e.g. IE/Edge/Nginx).

## How can I find it?
Misconfiguration example:
```nginx
# http://nginx.org/en/docs/http/ngx_http_headers_module.html#add_header
add_header Content-Security-Policy "
    default-src: 'none';
    script-src data: https://yastatic.net;
    style-src data: https://yastatic.net;
    img-src data: https://yastatic.net;
    font-src data: https://yastatic.net;";

# https://www.nginx.com/resources/wiki/modules/headers_more/
more_set_headers -t 'text/html text/plain'
    'X-Foo: Bar
        multiline';
```

## What can I do?
The only solution is to never use multiline response headers.
