import gixy
from gixy.plugins.plugin import Plugin


class valid_referers(Plugin):
    """
    Insecure example:
        valid_referers none server_names *.webvisor.com;
    """
    summary = 'Used "none" as valid referer.'
    severity = gixy.severity.HIGH
    description = 'Never trust undefined referer.'
    help_url = 'https://github.com/yandex/gixy/blob/master/docs/en/plugins/validreferers.md'
    directives = ['valid_referers']

    def audit(self, directive):
        if 'none' in directive.args:
            self.add_issue(directive=directive)
