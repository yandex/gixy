import re
import logging
import gixy
from gixy.plugins.plugin import Plugin
from gixy.core.regexp import Regexp

LOG = logging.getLogger(__name__)


class origins(Plugin):
    """
    Insecure example:
        if ($http_referer !~ "^https?://([^/]+metrika.*yandex\.ru/"){
            add_header X-Frame-Options SAMEORIGIN;
        }
    """
    summary = 'Validation regex for "origin" or "referrer" matches untrusted domain.'
    severity = gixy.severity.MEDIUM
    description = 'Improve the regular expression to match only trusted referrers.'
    help_url = 'https://github.com/yandex/gixy/wiki/ru/origins'
    directives = ['if']
    options = {
        'domains': ['*'],
        'https_only': False
    }

    def __init__(self, config):
        super(origins, self).__init__(config)
        if self.config.get('domains') and self.config.get('domains')[0] and self.config.get('domains')[0] != '*':
            domains = '|'.join(re.escape(d) for d in self.config.get('domains'))
        else:
            domains = '[^/.]*\.[^/]{2,7}'

        scheme = 'https{http}'.format(http=('?' if not self.config.get('https_only') else ''))
        regex = r'^{scheme}://(?:[^/.]*\.){{0,10}}(?:{domains})(?::\d*)?(?:/|\?|$)'.format(
            scheme=scheme,
            domains=domains
        )
        self.valid_re = re.compile(regex)

    def audit(self, directive):
        if directive.operand not in {'~', '~*', '!~', '!~*'}:
            # Not regexp
            return

        if directive.variable not in {'$http_referer', '$http_origin'}:
            # Not interesting
            return

        invalid_referers = set()
        regexp = Regexp(directive.value, case_sensitive=(directive.operand in {'~', '!~'}))
        for value in regexp.generate('/', anchored=True):
            if value.startswith('^'):
                value = value[1:]
            else:
                value = 'http://evil.com/' + value

            if value.endswith('$'):
                value = value[:-1]
            elif not value.endswith('/'):
                value += '.evil.com'

            if not self.valid_re.match(value):
                invalid_referers.add(value)

        if invalid_referers:
            invalid_referers = '", "'.join(invalid_referers)
            name = 'origin' if directive.variable == '$http_origin' else 'referrer'
            severity = gixy.severity.HIGH if directive.variable == '$http_origin' else gixy.severity.MEDIUM
            reason = 'Regex matches "{value}" as a valid {name}.'.format(value=invalid_referers, name=name)
            self.add_issue(directive=directive, reason=reason, severity=severity)
