# [http_splitting] HTTP Splitting

HTTP Splitting - attack that use improper input validation. It usually targets web application located behind Nginx (HTTP Request Splitting) or its users (HTTP Response Splitting).

Vulnerability is created when an attacker can insert newline character `\n` or `\r` into request or into response, created by Nginx.

## How can I find it?
You should always pay attention to:
 - variables that are used in directives, responsible for the request creation (for they may contain CRLF), e.g. `rewrite`, `return`, `add_header`, `proxy_set_header` or `proxy_pass`;
 - `$uri` and `$document_uri` variables, and in which directives they are used, because these variables contain decoded URL-encoded value;
 - variables, that are selected from an exclusive range, e.g. `(?P<myvar>[^.]+)`.


An example of configuration that contains variable, selected from an exclusive range:
```nginx
server {
    listen 80 default;

    location ~ /v1/((?<action>[^.]*)\.json)?$ {
        add_header X-Action $action;
        return 200 "OK";
    }
}
```

Exploitation:
```http
GET /v1/see%20below%0d%0ax-crlf-header:injected.json HTTP/1.0
Host: localhost

HTTP/1.1 200 OK
Server: nginx/1.11.10
Date: Mon, 13 Mar 2017 21:21:29 GMT
Content-Type: application/octet-stream
Content-Length: 2
Connection: close
X-Action: see below
x-crlf-header:injected

OK
```

As you can see, an attacker could add `x-crlf-header: injected` response header. This was possible because:
  - `add_header` doesn't encode or validate input value on suggestion that author knows about the consequences;
  - the path value is normalize before location processing;
  - `$action` value was given from a regexp with an exclusive range: `[^.]*`;
  - as the result, `$action` value is equal to `see below\r\nx-crlf-header:injected` and on its use the response header was added.

## What can I do?
  - try to use safe variables, e.g. `$request_uri` instead of `$uri`;
  - forbid the use of the new line symbol in the exclusive range by using `/some/(?<action>[^/\s]+)` instead of `/some/(?<action>[^/]+`
  - it could be a good idea to validate `$uri` (only if you're sure you know what are you getting into).
