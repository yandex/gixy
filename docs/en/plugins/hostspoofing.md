# [host_spoofing] Request's Host header forgery

Often, an application located behind Nginx needs a correct `Host` header for URL generation (redirects, resources, links in emails etc.).
An attacker can spoof this header, which leads to a variety of problems, from phishing to SSRF. To prevent this, avoid:
> Relience on `X-Forwarded-Host` request header;
> In this case you have to ensure the header is set correctly at proxies;

## How can I find it?
Most of the time it's a result of using `$http_host` variable instead of `$host`.

And they are quite different:
  * `$http` - host in order of priority: host name from request string, host name form `Host` request header, or a server name, compliant to the request;
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
Luckly, all is quite obvious:
 * list all the correct server names in `server name` directive;
 * always use `$host` instead of `$http_host`.

## Additional info
  * [Host of Troubles Vulnerabilities](https://hostoftroubles.com/)
  * [Practical HTTP Host header attacks](http://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html)