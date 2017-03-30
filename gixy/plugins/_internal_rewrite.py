import re
import logging
import gixy
from gixy.plugins.plugin import Plugin
from gixy.core.regexp import Regexp
from gixy.core.variable import EXTRACT_RE
from gixy.core.utils import is_indexed_name


LOG = logging.getLogger(__name__)

# TODO(buglloc): Complete it!


class internal_rewrite(Plugin):
    """
    Insecure example:
        location ~* ^/internal-proxy/(https?)/(.*?)/(.*) {
            internal;
            proxy_pass $1://$2/$3;
        }

        rewrite "^/([^?.]+[^/?.])(?:\?(.*))?$"                                  "/$1.xml" last;
    """

    summary = 'Some internal rewrite'
    severity = gixy.severity.HIGH
    description = 'Some descr'
    help_url = 'https://github.com/yandex/gixy/wiki/ru/internalrewrite'
    directives = ['location']

    def audit(self, directive):
        if not directive.is_internal:
            # Not internal location
            return

        values = _gen_location_values(directive)
        # print([x for x in values])
        for rewrite in directive.parent.find('rewrite', flat=True):
            if rewrite.flag not in {None, 'last', 'break'}:
                # Not internal rewrite
                continue
            rewrite_regex = _construct_rewrite_regex(rewrite)
            if not rewrite_regex:
                # We can't build results regexp  :(
                continue

            for value in values:
                if re.match(rewrite_regex, value):
                    # YAY!
                    self.add_issue([directive, rewrite])


def _gen_location_values(location):
    if location.modifier not in ('~', '~*'):
        # Prefixed location
        return [location.path]

    regex = Regexp(location.path, case_sensitive=location.modifier == '~*', strict=True)
    return regex.generate(char='a', anchored=False)


def _construct_rewrite_regex(rewrite):
    regex = Regexp(rewrite.pattern, case_sensitive=True)
    parts = {}
    for name, group in regex.groups.items():
        parts[name] = group

    return _compile_script(rewrite.replace, parts)


def _compile_script(script, parts):
    result = []
    for i, var in enumerate(EXTRACT_RE.split(str(script))):
        if i % 2:
            # Variable
            var = var.strip('{}\x20')
            if is_indexed_name(var):
                var = int(var)
            if var not in parts:
                LOG.warn('Can\'t find variable "{}"'.format(var))
                return
            result.append(str(parts[var]))
        elif var:
            # Literal
            result.append(var)
    return ''.join(result)
