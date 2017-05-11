# [host_spoofing] Request's Host header forgery

Often, an application located behind Nginx needs a correct `Host` header for URL generation (redirects, resources, links in emails etc.).
Spoofing of this header, may leads to a variety of problems, from phishing to SSRF.

> Notice: your application may also use the `X-Forwarded-Host` request header for this functionality.
> In this case you have to ensure the header is set correctly;

## How can I find it?
Most of the time it's a result of using `$http_host` variable instead of `$host`.

And they are quite different:
  * `$host` - host in this order of precedence: host name from the request line, or host name from the “Host” request header field, or the server name matching a request;
  * `$http_host` - "Host" request header.

Config sample:
```nginx
location @app {
  proxy_set_header Host $http_host;
  # Other proxy params
  proxy_pass http://backend;
}
```

## What can I do?
Luckily, all is quite obvious:
 * list all the correct server names in `server name` directive;
 * always use `$host` instead of `$http_host`.

## Additional info
  * [Host of Troubles Vulnerabilities](https://hostoftroubles.com/)
  * [Practical HTTP Host header attacks](http://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html)
