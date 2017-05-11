# [add_header_redefinition] Переопределение "вышестоящих" заголовков ответа директивой "add_header"

К сожалению, многие считают что с помощью директивы `add_header` можно произвольно доопределять заголовки ответа.
Это не так, о чем сказано в [документации](http://nginx.org/ru/docs/http/ngx_http_headers_module.html#add_header) к Nginx:
> Директив `add_header` может быть несколько. Директивы наследуются с предыдущего уровня при условии, что на данном уровне не описаны свои директивы `add_header`.

К слову, так работает наследование большинства директив в nginx'е. Если вы задаёте что-то на каком-то уровне конфигурации (например, в локейшене), то наследования с предыдущих уровней (например, с http секции) - не будет.

В этом довольно легко убедится:
  - Конфигурация:
```nginx
server {
  listen 80;
  add_header X-Frame-Options "DENY" always;
  location / {
      return 200 "index";
  }

  location /new-headers {
    # Add special cache control
    add_header Cache-Control "no-cache, no-store, max-age=0, must-revalidate" always;
    add_header Pragma "no-cache" always;

    return 200 "new-headers";
  }
}
```
  - Запрос к локейшену `/` (заголовок `X-Frame-Options` есть в ответе сервера):
```http
GET / HTTP/1.0

HTTP/1.1 200 OK
Server: nginx/1.10.2
Date: Mon, 09 Jan 2017 19:28:33 GMT
Content-Type: application/octet-stream
Content-Length: 5
Connection: close
X-Frame-Options: DENY

index
```
  - Запрос к локейшену `/new-headers` (есть заголовки `Cache-Control` и `Pragma`, но нет `X-Frame-Options`):
```http
GET /new-headers HTTP/1.0


HTTP/1.1 200 OK
Server: nginx/1.10.2
Date: Mon, 09 Jan 2017 19:29:46 GMT
Content-Type: application/octet-stream
Content-Length: 11
Connection: close
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache

new-headers
```

## Что делать?
Существует несколько способов решить эту проблему:
  - продублировать важные заголовки;
  - устанавливать заголовки на одном уровне, например, в серверной секции;
  - использовать модуль [ngx_headers_more](https://www.nginx.com/resources/wiki/modules/headers_more/).

Каждый из способов имеет свои преимущества и недостатки, какой предпочесть зависит от ваших потребностей. 