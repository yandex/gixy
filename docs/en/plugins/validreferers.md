# [valid_referers] none in valid_referers
Module [ngx_http_referer_module](http://nginx.org/en/docs/http/ngx_http_referer_module.html) allows to block the access to service for requests with wrong `Referer` value.
It's often used for setting `X-Frame-Options` header (ClickJacking protection), but there may be other cases.

Typical problems with this module's config:
  * use of `server_names` with bad server name (`server_name` directive);
  * too broad and/or bad regexes;
  * use of `none`.

> Notice: at the moment, Gixy can only detect the use of `none` as a valid referer.

## Why none is bad?
According to [docs](http://nginx.org/ru/docs/http/ngx_http_referer_module.html#valid_referers):
> `none` - the “Referer” field is missing in the request header;

Still, it's important to remember that any resource can make user's browser to make a request without a `Referer` request header.
E.g.:
  - in case of redirect from HTTPS to HTTP;
  - by setting up the [Referrer Policy](https://www.w3.org/TR/referrer-policy/);
  - a request with opaque origin, `data:` scheme, for example.

So, by using `none` as a valid referer, you nullify any attemps in refferer validation.