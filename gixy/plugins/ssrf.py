import re

import gixy
from gixy.plugins.plugin import Plugin
from gixy.core.context import get_context
from gixy.core.variable import compile_script


class ssrf(Plugin):
    """
    Insecure examples:
        location ~ /proxy/(.*)/(.*)/(.*)$ {
            set $scheme $1;
            set $host $2;
            set $path $3;
            proxy_pass $scheme://$host/$path;
        }

        location /proxy/ {
            proxy_pass $arg_some;
        }
    """

    summary = 'Possible SSRF (Server Side Request Forgery) vulnerability.'
    severity = gixy.severity.HIGH
    description = 'The configuration may allow attacker to create a arbitrary requests from the vulnerable server.'
    help_url = 'https://github.com/yandex/gixy/blob/master/docs/ru/plugins/ssrf.md'
    directives = ['proxy_pass']

    def __init__(self, config):
        super(ssrf, self).__init__(config)
        self.parse_uri_re = re.compile(r'(?P<scheme>[^?#/)]+://)?(?P<host>[^?#/)]+)')

    def audit(self, directive):
        value = directive.args[0]
        if not value:
            return

        context = get_context()
        if context.block.name == 'location' and context.block.is_internal:
            # Exclude internal locations
            return

        parsed = self.parse_uri_re.match(value)
        if not parsed:
            return

        res = self._check_script(parsed.group('scheme'), directive)
        if not res:
            self._check_script(parsed.group('host'), directive)

    def _check_script(self, script, directive):
        for var in compile_script(script):
            if var.must_contain('/'):
                # Skip variable checks
                return False
            if var.can_contain('.'):
                # Yay! Our variable can contain any symbols!
                reason = 'At least variable "${var}" can contain untrusted user input'.format(var=var.name)
                self.add_issue(directive=[directive] + var.providers, reason=reason)
                return True
        return False
