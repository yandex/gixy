import gixy
from gixy.plugins.plugin import Plugin
from gixy.core.variable import compile_script


class http_splitting(Plugin):
    """
    Insecure examples:
        rewrite ^ http://$host$uri;
        return 301 http://$host$uri;
        proxy_set_header "X-Original-Uri" $uri;
        proxy_pass http://upstream$document_uri;

        location ~ /proxy/(a|b)/(\W*)$ {
            set $path $2;
            proxy_pass http://storage/$path;
        }
    """

    summary = 'Possible HTTP-Splitting vulnerability.'
    severity = gixy.severity.HIGH
    description = 'Using variables that can contain "\\n" may lead to http injection.'
    help_url = 'https://github.com/yandex/gixy/blob/master/docs/en/plugins/httpsplitting.md'
    directives = ['rewrite', 'return', 'add_header', 'proxy_set_header', 'proxy_pass']

    def audit(self, directive):
        value = _get_value(directive)
        if not value:
            return

        for var in compile_script(value):
            if not var.can_contain('\n') and not var.can_contain('\r'):
                continue
            reason = 'At least variable "${var}" can contain "\\n"'.format(var=var.name)
            self.add_issue(directive=[directive] + var.providers, reason=reason)


def _get_value(directive):
    if directive.name == 'proxy_pass' and len(directive.args) >= 1:
        return directive.args[0]
    elif len(directive.args) >= 2:
        return directive.args[1]
    return None
