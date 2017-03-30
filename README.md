GIXY
====

# Overview
Gixy is a tool for Nginx configuration analyzing. The main goal of Gixy is to prevent misconfiguration and automate flaw detection.
Currently supported Python versions is 2.7 and 3.4+.
Disclaimer: Gixy is well tested only on GNU/Linux, in other OS may have some issues.

# Installation
Gixy is distributed on PyPI. The best way to install it is with pip:
```bash
pip install bandit
```

Run Gixy and check results:
```bash
gixy
```

# Usage
By default Gixy will try to analyze Nginx configuration placed in `/etc/nginx/nginx.conf`. But you can always specify needed path:
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

Or skip some tests:
```
$ ./gixy-cli.py --skips http_splitting /etc/nginx/nginx.conf

==================== Results ===================
No issues found.

==================== Summary ===================
Total issues:
    Unspecified: 0
    Low: 0
    Medium: 0
    High: 0
```

Or something else, you can find all other `gixy` arguments with the help command: `gixy --help`

# Documentation
Full documentation and recommendations can be found [here](https://github.com/yandex/gixy/wiki/ru/) (sorry, but Russian language only so far)

# Contributing
Contributions to Gixy are always welcome! You can help us in different ways:
  * Open an issue with suggestions for improvements and errors you're facing;
  * Fork this repository and submit a pull request;
  * Improve the documentation.

Code guidelines:
  * Python code style should follow [PEP8 standards][pep8] standards whenever possible;
  * Pull requests with new plugins must contain unit tests for it.
