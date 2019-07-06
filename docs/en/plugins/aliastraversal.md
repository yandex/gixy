# [alias_traversal] Path traversal via misconfigured alias

The [alias](https://nginx.ru/en/docs/http/ngx_http_core_module.html#alias) directive is used to replace path of the specified location.
For example, with the following configuration:
```nginx
location /i/ {
    alias /data/w3/images/;
}
```
on request of `/i/top.gif`, the file `/data/w3/images/top.gif` will be sent.

But, if the location doesn't ends with directory separator (i.e. `/`):
```nginx
location /i {
    alias /data/w3/images/;
}
```
on request of `/i../app/config.py`, the file `/data/w3/app/config.py` will be sent.

In other words, the incorrect configuration of `alias` could allow an attacker to read file stored outside the target folder.

## What can I do?
It's pretty simple:
  - you must find all the `alias` directives;
  - make sure that the parent prefixed location ends with directory separator.
  - or if you want to map a signle file make sure the location starts with a `=`, e.g `=/i.gif` instead of `/i.gif`.
