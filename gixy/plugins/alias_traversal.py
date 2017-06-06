import gixy
from gixy.plugins.plugin import Plugin


class alias_traversal(Plugin):
    """
    Insecure example:
        location /files {
            alias /home/;
        }
    """
    summary = 'Path traversal via misconfigured alias.'
    severity = gixy.severity.HIGH
    description = 'TODO'
    help_url = 'https://github.com/yandex/gixy/blob/master/docs/en/plugins/aliastraversal.md'
    directives = ['alias']

    def audit(self, directive):
        for location in directive.parents:
            if location.name != 'location':
                continue
            if not location.modifier or location.modifier == '^~':
                # We need non-strict prefixed locations
                if not location.path.endswith('/'):
                    self.add_issue(directive=[directive, location])
            break
