Gixy is a static analysis tool for Ngix config files. It is best at finding security misconfigurations, but can be also used to detect general errors.

## What it can do
Right now Gixy can find:
  * [[ssrf] Server Side Request Forgery](https://github.com/yandex/gixy/blob/master/docs/en/plugins/ssrf.md)
  * [[http_splitting] HTTP Splitting](https://github.com/yandex/gixy/blob/master/docs/en/plugins/httpsplitting.md)
  * [[origins] Problems with referrer/origin validation](https://github.com/yandex/gixy/blob/master/docs/en/plugins/origins.md)
  * [[add_header_redefinition] Redefining of upstream response headers with directive "add_header"](https://github.com/yandex/gixy/blob/master/docs/en/plugins/addheaderredefinition.md)
  * [[host_spoofing] Request's Host header forgery](https://github.com/yandex/gixy/blob/master/docs/en/plugins/hostspoofing.md)
  * [[valid_referers] none in valid_referers](https://github.com/yandex/gixy/blob/master/docs/en/plugins/validreferers.md)
  * [[add_header_multiline] Multiline response headers](https://github.com/yandex/gixy/blob/master/docs/en/plugins/addheadermultiline.md)

You can find things that Gixy is learning to detect at [Issues labeled with "new plugin"](https://github.com/yandex/gixy/issues?q=is%3Aissue+is%3Aopen+label%3A%22new+plugin%22)

##Installation
The easiest way to install Gixy is to use pip:
```bash
pip install gixy
```
The tool is compatible with Python 2.7/3.5/3.6

## Using Gixy
After installation you can find `gixy` in your command line. Buy default Gixy is working with `/etc/nginx/nginx.conf` folder, which is standart for Nginx installations, but you can provide a custom path as an argument:
```
$ gixy /www/configs/nginx/nginx.conf
```

==================== Results ===================

Problem: [http_splitting] Possible HTTP-Splitting vulnerability.
Description: Using variables that can contain "\n" may lead to http injection.
Additional info: https://github.com/yandex/gixy/wiki/ru/httpsplitting
Reason: At least variable "$action" can contain "\n"
Pseudo config:
include /etc/nginx/sites/default.conf;

  server {

    location ~ /v1/((?<action>[^.]*)\.json)?$ {
      add_header X-Action $action;
    }
  }


==================== Summary ===================
Total issues:
    Unspecified: 0
    Low: 0
    Medium: 0
    High: 1
```
Gixy can process `include` directive and tries to handle all the dependencies. If something went wrong, you can launch Gixy with the `d` flag, which enables debug mode for extra information.

To view all options:
```
$ gixy -h
usage: gixy [-h] [-c CONFIG_FILE] [--write-config CONFIG_OUTPUT_PATH]
            [-v] [-l] [-f {console,text,json}] [-o OUTPUT_FILE] [-d]
            [--tests TESTS] [--skips SKIPS] [--disable-includes]
            [--origins-domains domains]
            [--origins-https-only https_only]
            [--add-header-redefinition-headers headers]
            [nginx.conf]

Gixy - a Nginx configuration [sec]analyzer

positional arguments:
  nginx.conf            Path to nginx.conf, e.g. /etc/nginx/nginx.conf

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config CONFIG_FILE
                        config file path
  --write-config CONFIG_OUTPUT_PATH
                        takes the current command line args and writes them
                        out to a config file at the given path, then exits
  -v, --version         show program's version number and exit
  -l, --level           Report issues of a given severity level or higher (-l
                        for LOW, -ll for MEDIUM, -lll for HIGH)
  -f {console,text,json}, --format {console,text,json}
                        Specify output format
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        Write report to file
  -d, --debug           Turn on debug mode
  --tests TESTS         Comma-separated list of tests to run
  --skips SKIPS         Comma-separated list of tests to skip
  --disable-includes    Disable "include" directive processing

plugins options:
  --origins-domains domains
                        Default: *
  --origins-https-only https_only
                        Default: False
  --add-header-redefinition-headers headers
                        Default: content-security-policy,x-xss-
                        protection,x-frame-options,x-content-type-
                        options,strict-transport-security,cache-control


available plugins:
  host_spoofing
  add_header_multiline
  http_splitting
  valid_referers
  origins
  add_header_redefinition
  ssrf
```

