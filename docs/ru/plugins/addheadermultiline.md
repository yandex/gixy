# [add_header_multiline] Многострочные заголовоки ответа

Многострочных заголовков ответа стоит избегать по нескольким причинам:
  * они признаны устаревшими (см. [RFC 7230](https://tools.ietf.org/html/rfc7230#section-3.2.4));
  * они никогда не поддерживались многими HTTP-клиентами и браузерами. Например, IE/Edge/Nginx.

## Как самостоятельно обнаружить?
Пример плохой конфигурации:
```nginx
# http://nginx.org/ru/docs/http/ngx_http_headers_module.html#add_header
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

## Что делать?
Единственный выход - отказ от многострочных заголовок ответа.