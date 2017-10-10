GIXY
====
[![Mozilla Public License 2.0](https://img.shields.io/github/license/yandex/gixy.svg?style=flat-square)](https://github.com/yandex/gixy/blob/master/LICENSE)
[![Build Status](https://img.shields.io/travis/yandex/gixy.svg?style=flat-square)](https://travis-ci.org/yandex/gixy)
[![Your feedback is greatly appreciated](https://img.shields.io/maintenance/yes/2017.svg?style=flat-square)](https://github.com/yandex/gixy/issues/new)
[![GitHub issues](https://img.shields.io/github/issues/yandex/gixy.svg?style=flat-square)](https://github.com/yandex/gixy/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/yandex/gixy.svg?style=flat-square)](https://github.com/yandex/gixy/pulls)

# Overview
<img align="right" width="192" height="192" src="/docs/logo.png">

Gixy — это утилита для анализа конфигурации Nginx.
Большей частью служит для обнаружения проблем безопасности, но может искать и иные ошибки.

Официально поддерживаются версии Python 2.7, 3.5 и 3.6

&nbsp;
# Что умеет
На текущий момент Gixy способна обнаружить:
  * [[ssrf] Server Side Request Forgery](https://github.com/yandex/gixy/blob/master/docs/ru/plugins/ssrf.md)
  * [[http_splitting] HTTP Splitting](https://github.com/yandex/gixy/blob/master/docs/ru/plugins/httpsplitting.md)
  * [[origins] Проблемы валидации referrer/origin](https://github.com/yandex/gixy/blob/master/docs/ru/plugins/origins.md)
  * [[add_header_redefinition] Переопределение "вышестоящих" заголовков ответа директивой "add_header"](https://github.com/yandex/gixy/blob/master/docs/ru/plugins/addheaderredefinition.md)
  * [[host_spoofing] Подделка заголовка запроса Host](https://github.com/yandex/gixy/blob/master/docs/ru/plugins/hostspoofing.md)
  * [[valid_referers] none in valid_referers](https://github.com/yandex/gixy/blob/master/docs/ru/plugins/validreferers.md)
  * [[add_header_multiline] Многострочные заголовоки ответа](https://github.com/yandex/gixy/blob/master/docs/ru/plugins/addheadermultiline.md)
  * [[alias_traversal] Path traversal при использовании alias](https://github.com/yandex/gixy/blob/master/docs/ru/plugins/aliastraversal.md)

Проблемы, которым Gixy только учится можно найти в [Issues с меткой "new plugin"](https://github.com/yandex/gixy/issues?q=is%3Aissue+is%3Aopen+label%3A%22new+plugin%22)

# Установка
Наиболее простой способ установки Gixy - воспользоваться pip для установки из [PyPI](https://pypi.python.org/pypi/gixy):
```bash
pip install gixy
```

# Использование
После установки должна стать доступна консольная утилита `gixy`.
По умолчанию Gixy ищет конфигурацию по стандартному пути `/etc/nginx/nginx.conf`, однако вы можете указать специфичное расположение:
```
$ gixy /etc/nginx/nginx.conf

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

Gixy умеет обрабатывать директиву `include` и попробует максимально корректно обработать все зависимости, если что-то пошло не так можно попробовать запустить `gixy` с флагом `-d` для вывода дополнительной информации.
Все доступные опции:
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

# Contributing
Contributions to Gixy are always welcome! You can help us in different ways:
  * Open an issue with suggestions for improvements and errors you're facing;
  * Fork this repository and submit a pull request;
  * Improve the documentation.

Code guidelines:
  * Python code style should follow [pep8](https://www.python.org/dev/peps/pep-0008/) standards whenever possible;
  * Pull requests with new plugins must have unit tests for it.
