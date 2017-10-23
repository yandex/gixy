# [origins] Problems with referrer/origin validation

It's not unusual to use regex for `Referer` or `Origin` headers validation.
Often it is needed for setting the `X-Frame-Options` header (ClickJacking protection) or Cross-Origin Resource Sharing.

The most common errors with this configuration are:
  - regex errors;
  - allow 3rd-party origins.

 > Notice: by default Gixy doesn't check regexes for 3rd-party origins matching.
 > You can pass a list of trusted domains by using the option `--origins-domains example.com,foo.bar`

## How can I find it?
"Eazy"-breezy:
  - you have to find all the `if` directives that are in charge of `$http_origin` or `$http_referer` check;
  - make sure your regexes are a-ok.

Misconfiguration example:
```nginx
if ($http_origin ~* ((^https://www\.yandex\.ru)|(^https://ya\.ru)$)) {
	add_header 'Access-Control-Allow-Origin' "$http_origin";
	add_header 'Access-Control-Allow-Credentials' 'true';
}
```

TODO(buglloc): cover typical regex-writing problems
TODO(buglloc): Regex Ninja?

## What can I do?

  - fix your regex or toss it away :)
  - if you use regex validation for `Referer` request header, then, possibly (not 100%), you could use [ngx_http_referer_module](http://nginx.org/en/docs/http/ngx_http_referer_module.htmll);
  - sometimes it is much better to use the `map` directive without any regex at all.
