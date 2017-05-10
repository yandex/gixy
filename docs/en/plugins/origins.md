# [origins] Problems with referrer/origin validation

It's not unusual to use regexp for `Referer` or `Origin` headers validation.
Often it is needed for setting the `X-Frame-Options` header (ClickJacking protection) or Cross-Origin Resource Sharing.

The most common errors with this configuration are:
  - regexp errors;
  - 3rd-party domain permissions.

 > By default Gixy doesn't check regexps for 3rd-party domains matching, cause it's unclear wether you can should them. You can pass a list of trusted domains by using the option `--origins-domains example.com,foo.bar`

## How can I find it?
"Eazy"-breezy:
  - you have to find all the `if` directives that are in charge of `$http_origin` or `$http_referer` check;
  - make sure your regexps are a-ok.

Misconfig example:
```nginx
if ($http_origin ~* ((^https://www\.yandex\.ru)|(^https://ya\.ru)/)) {
	add_header 'Access-Control-Allow-Origin' "$http_origin";
	add_header 'Access-Control-Allow-Credentials' 'true';
}
```

TODO(buglloc): cover typical regexp-writing problems
TODO(buglloc): Regex Ninja?

## What can I do?
Fix your regexp or toss it away.
If you use regexp validation for `Referer` request header, then, possibly (not 100%), you could use [ngx_http_referer_module](http://nginx.org/ru/docs/http/ngx_http_referer_module.html).