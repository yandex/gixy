import gixy
from gixy.plugins.plugin import Plugin


class host_spoofing(Plugin):
    """
    Insecure example:
        proxy_set_header Host $http_host
    """
    summary = 'The proxied Host header may be spoofed.'
    severity = gixy.severity.MEDIUM
    description = 'In most cases "$host" variable are more appropriate, just use it.'
    help_url = 'https://github.com/yandex/gixy/docs/ru/plugins/hostspoofing.md'
    directives = ['proxy_set_header']

    def audit(self, directive):
        name, value = directive.args
        if name.lower() != 'host':
            # Not a "Host" header
            return

        if value == '$http_host' or value.startswith('$arg_'):
            self.add_issue(directive=directive)
