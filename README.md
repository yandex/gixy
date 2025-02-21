GIXY
====
[![Mozilla Public License 2.0](https://img.shields.io/github/license/yandex/gixy.svg?style=flat-square)](https://github.com/yandex/gixy/blob/master/LICENSE)
[![Build Status](https://img.shields.io/travis/yandex/gixy.svg?style=flat-square)](https://travis-ci.org/yandex/gixy)
[![Your feedback is greatly appreciated](https://img.shields.io/maintenance/yes/2019.svg?style=flat-square)](https://github.com/yandex/gixy/issues/new)
[![GitHub issues](https://img.shields.io/github/issues/yandex/gixy.svg?style=flat-square)](https://github.com/yandex/gixy/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/yandex/gixy.svg?style=flat-square)](https://github.com/yandex/gixy/pulls)

# Overview
<img align="right" width="192" height="192" src="/docs/logo.png">

Gixy is a tool for analyzing Nginx configurations, designed to help administrators, security engineers, and developers detect and mitigate security risks before they become critical vulnerabilities.

Its primary goal is to prevent security misconfigurations by identifying unsafe directives, improper access controls, and other configuration flaws that could expose systems to attacks. Gixy also automates flaw detection, allowing users to efficiently audit their Nginx configurations without manual inspection.Gixy helps strengthen the security posture of web applications and services that rely on Nginx. Whether used in CI/CD pipelines, manual audits, or automated security testing, Gixy provides a robust solution for securing Nginx environments.

**Supported Python versions**: 2.7, 3.5, 3.6 and 3.7

**OS Compability**: GNU/Linux, macOS, Windows

**Disclaimer**: Gixy is well tested only on GNU/Linux, other Operating Systems may have some issues.

# Functionality
Currently, Gixy can find: (Click on the links if you want more information on the topics)
  * [ssrf] Server Side Request Forgery
  	* Detects improper handling of user-supplied URLs
  	* (https://github.com/yandex/gixy/blob/master/docs/en/plugins/ssrf.md)
  * [http_splitting] HTTP Splitting
  	* Identifies improperly handled user-controlled headers that could lead to HTTP header injection and response splitting attacks
  	* (https://github.com/yandex/gixy/blob/master/docs/en/plugins/httpsplitting.md)
  * [origins] Problems with referrer/origin validation
  	* Checks for incorrect validation of Referer or Origin headers in security-sensitive requests
  	* (https://github.com/yandex/gixy/blob/master/docs/en/plugins/origins.md)
  * [add_header_redefinition] Redefining of response headers by  "add_header" directive
  	* Detects multiple definitions of response headers using add_header
  	* (https://github.com/yandex/gixy/blob/master/docs/en/plugins/addheaderredefinition.md)
  * [host_spoofing] Request's Host header forgery
  	* Detects scenarios where an attacker can spoof the Host header
  	* (https://github.com/yandex/gixy/blob/master/docs/en/plugins/hostspoofing.md)
  * [valid_referers] none in valid_referers
  	* Identifies misconfigurations in valid_referers
  	* (https://github.com/yandex/gixy/blob/master/docs/en/plugins/validreferers.md)
  * [[add_header_multiline] Multiline response headers]
  	* Detects vulnerabilities caused by multi-line response headers,
  	* (https://github.com/yandex/gixy/blob/master/docs/en/plugins/addheadermultiline.md)
  * [alias_traversal] Path traversal via misconfigured alias
  	* Identifies potential directory traversal vulnerabilities caused by incorrect use of the alias directive
  	* (https://github.com/yandex/gixy/blob/master/docs/en/plugins/aliastraversal.md)

🔧 Want to see what’s coming next? [Issues labeled with "new plugin"](https://github.com/yandex/gixy/issues?q=is%3Aissue+is%3Aopen+label%3A%22new+plugin%22)

# Installation
Gixy is distributed on [PyPI](https://pypi.python.org/pypi/gixy). The best way to install it is with pip:
```bash
python3 -m venv gixy_env
source gixy_env/bin/activate
pip install gixy
```

Run Gixy and check results:
```bash
gixy
```
To verify installation, run:
```bash
gixy --version
```
# Usage
Basic Scan

By default Gixy will try to analyze Nginx configuration placed in `/etc/nginx/nginx.conf`.
But you can always specify needed path:

Example Output:

```
$ gixy /etc/nginx/nginx.conf

==================== Results ===================

Problem: [http_splitting] Possible HTTP-Splitting vulnerability.
Description: Using variables that can contain "\n" may lead to http injection.
Additional info: https://github.com/yandex/gixy/blob/master/docs/ru/plugins/httpsplitting.md
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
$ gixy --skips http_splitting /etc/nginx/nginx.conf

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

## Docker usage

Gixy is available as a Docker image [from the Docker hub](https://hub.docker.com/r/yandex/gixy/). To
use it, mount the configuration that you want to analyse as a volume and provide the path to the
configuration file when running the Gixy image.

**Scan a Configuration File**

```
$ docker run --rm -v `pwd`/nginx.conf:/etc/nginx/conf/nginx.conf yandex/gixy /etc/nginx/conf/nginx.conf
```

If you have an image that already contains your nginx configuration, you can share the configuration
with the Gixy container as a volume.

**Scan a Running Nginx Container**

```
$  docker run --rm --name nginx -d -v /etc/nginx
nginx:alpinef68f2833e986ae69c0a5375f9980dc7a70684a6c233a9535c2a837189f14e905

$  docker run --rm --volumes-from nginx yandex/gixy /etc/nginx/nginx.conf

==================== Results ===================
No issues found.

==================== Summary ===================
Total issues:
    Unspecified: 0
    Low: 0
    Medium: 0
    High: 0

```

# Contributing
Contributions to Gixy are always welcome! You can help us in different ways:
  * Open an issue with suggestions for improvements and errors you're facing;
  * Fork this repository and submit a pull request;
  * Improve the documentation.

Code guidelines:
  * Python code style should follow [pep8](https://www.python.org/dev/peps/pep-0008/) standards whenever possible;
  * Pull requests with new plugins must have unit tests for it.
  * Follow pre-use code sytle 
  
