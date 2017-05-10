# [ssrf] Server Side Request Forgery

Server Side Request Forgery - attack that forces a server to perform requests on behalf of an attacker (Nginx in our case).
It's possible when an attacker controls the address of a proxied server (second argument of the `proxy_pass` directive).


## How can I find it?
There are two types of errors that make a server vulnerable:
  - lack of the [internal](http://nginx.org/ru/docs/http/ngx_http_core_module.html#internal) directive. It is used to point out a location that can be used for internal requests only;
  - unsafe internal redirection.

### Lack of the internal directive
Classical misconfig, based on lack of the internal directive, that makes SSRF possible:
```nginx
location ~ /proxy/(.*)/(.*)/(.*)$ {
    proxy_pass $1://$2/$3;
}
```
An attacker has complete control over the proxied address, that makes sending requests on behalf of Nginx possible.

### Unsafe internal redirection
Let's say you have internal location in your config and that location uses some request data as proxied server's address.

E.g.:
```nginx
location ~* ^/internal-proxy/(?<proxy_proto>https?)/(?<proxy_host>.*?)/(?<proxy_path>.*)$ {
    internal;

    proxy_pass $proxy_proto://$proxy_host/$proxy_path ;
    proxy_set_header Host $proxy_host;
}
```

According to Nginx docs, internal requests are:
>  - requests redirected by the **error_page**, **index**, **random_index**, and **try_files** directives; 
>  - requests redirected by the “X-Accel-Redirect” response header field from an upstream server;
>  - subrequests formed by the “include virtual” command of the ngx_http_ssi_module module and by the ngx_http_addition_module module directives;
>  - requests changed by the **rewrite** directive.]>

Accordingly, any unsafe rewrite allows an attacker to make an internal request and control a proxied server's address.

Misconfig example:
```nginx
rewrite ^/(.*)/some$ /$1/ last;

location ~* ^/internal-proxy/(?<proxy_proto>https?)/(?<proxy_host>.*?)/(?<proxy_path>.*)$ {
    internal;

    proxy_pass $proxy_proto://$proxy_host/$proxy_path ;
    proxy_set_header Host $proxy_host;
}
```

## What can I do?
There are everal rules you better follow when writing such configurations:
  - use only `internal location` for proxying;
  - if possible, forbid user data transmission;
  - protect proxied server's address:
    * if the quantity of proxied hosts is limited (when you have S3 or smth), you better hardcode them and choose them with `map` or do it some other way;
    * if you can' list all possible hosts to proxy, you should sign the address.
