import gixy
from gixy.plugins.plugin import Plugin


class add_header_redefinition(Plugin):
    """
    Insecure example:
        server {
            add_header X-Content-Type-Options nosniff;
            location / {
                add_header X-Frame-Options DENY;
            }
        }
    """
    summary = 'Nested "add_header" drops parent headers.'
    severity = gixy.severity.MEDIUM
    description = ('"add_header" replaces ALL parent headers. '
                   'See documentation: http://nginx.org/en/docs/http/ngx_http_headers_module.html#add_header')
    help_url = 'https://github.com/yandex/gixy/wiki/ru/addheaderredefinition'
    directives = ['server', 'location', 'if']
    options = {'headers': {'x-frame-options',
                           'x-content-type-options',
                           'x-xss-protection',
                           'content-security-policy',
                           'strict-transport-security',
                           'cache-control'}
               }

    def __init__(self, config):
        super(add_header_redefinition, self).__init__(config)
        self.interesting_headers = self.config.get('headers')

    def audit(self, directive):
        if not directive.is_block:
            # Skip all not block directives
            return

        actual_headers = get_headers(directive)
        if not actual_headers:
            return

        for parent in directive.parents:
            parent_headers = get_headers(parent)
            if not parent_headers:
                continue

            diff = (parent_headers - actual_headers) & self.interesting_headers

            if len(diff):
                self._report_issue(directive, parent, diff)

            break

    def _report_issue(self, current, parent, diff):
        directives = []
        # Add headers from parent level
        directives.extend(parent.find('add_header'))
        # Add headers from current level
        directives.extend(current.find('add_header'))
        reason = 'Parent headers "{headers}" was dropped in current level'.format(headers='", "'.join(diff))
        self.add_issue(directive=directives, reason=reason)


def get_headers(directive):
    headers = directive.find('add_header')
    if not headers:
        return set()

    return set(map(lambda d: d.header, headers))
