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
    description = 'Using alias in a prefixed location that doesn\'t ends with directory separator could lead to path ' \
                  'traversal vulnerability. '
    help_url = 'https://github.com/yandex/gixy/blob/master/docs/en/plugins/aliastraversal.md'
    directives = ['alias']

    def audit(self, directive):
        for location in directive.parents:
            if location.name != 'location':
                continue

            if not location.modifier or location.modifier == '^~':
                # We need non-strict prefixed locations
                if not location.path.endswith('/'):
                    self.add_issue(
                        severity=gixy.severity.HIGH if directive.path.endswith('/') else gixy.severity.MEDIUM,
                        directive=[directive, location]
                    )
            break
