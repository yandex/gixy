# [add_header_redefinition] Redefining of upstream response headers with directive "add_header"

Unfortunately, many people consider the use of `add_header` directive for headers redefining a good practice.
This approach is flawed, which is discussed in Nginx [docs](http://nginx.org/ru/docs/http/ngx_http_headers_module.html#add_header):
> There could be several add_header directives. These directives are inherited from the previous level if and only if there are no add_header directives defined on the current level.

The logic is quite simple: if you set headers at one level (for example, in `server` section) and then at a lower level (let's say `location`) you set some other headers, then the first group won't apply.

It's easy to observe:
  - Configuration:
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
  - Location request `/` (`X-Frame-Options` header is in server response):
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
  - Location request `/new-headers` (headers `Cache-Control` and `Pragma` are present, but there's no `X-Frame-Options`):
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

## What can I do?
There are several ways to solve this problem:
 - dublicate important headers;
 - set all headers at one level (`server` section is a good choice)
 - use [ngx_headers_more](https://www.nginx.com/resources/wiki/modules/headers_more/) module.

No solution is perfect, so choose one based on your needs.