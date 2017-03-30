import gixy
from gixy.plugins.plugin import Plugin


class force_https(Plugin):
    """
    Insecure example:
        rewrite ^.*/(foo)(/|/index.xml)?$ http://test.com/foo?;
    """
    summary = 'Found redirection to HTTP URL.'
    severity = gixy.severity.LOW
    description = 'Should be https://... URL while redirection.'
    help_url = 'https://github.com/yandex/gixy/wiki/ru/forcehttps'
    directives = ['rewrite', 'return']

    def audit(self, directive):
        for a in directive.args:
            if a.startswith('http://'):
                self.add_issue(directive=directive)
                break
