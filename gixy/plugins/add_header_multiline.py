import gixy
from gixy.plugins.plugin import Plugin


class add_header_multiline(Plugin):
    """
    Insecure example:
add_header Content-Security-Policy "
    default-src: 'none';
    img-src data: https://mc.yandex.ru https://yastatic.net *.yandex.net https://mc.yandex.${tld} https://mc.yandex.ru;
    font-src data: https://yastatic.net;";
    """
    summary = 'Found a multi-line header.'
    severity = gixy.severity.LOW
    description = ('Multi-line headers are deprecated (see RFC 7230). '
                   'Some clients never supports them (e.g. IE/Edge).')
    help_url = 'https://github.com/yandex/gixy/blob/master/docs/en/plugins/addheadermultiline.md'
    directives = ['add_header', 'more_set_headers']

    def audit(self, directive):
        header_values = get_header_values(directive)
        for value in header_values:
            if '\n\x20' in value or '\n\t' in value:
                self.add_issue(directive=directive)
                break


def get_header_values(directive):
    if directive.name == 'add_header':
        return [directive.args[1]]

    # See headers more documentation: https://github.com/openresty/headers-more-nginx-module#description
    result = []
    skip_next = False
    for arg in directive.args:
        if arg in ['-s', '-t']:
            # Skip next value, because it's not a header
            skip_next = True
        elif arg.startswith('-'):
            # Skip any options
            pass
        elif skip_next:
            skip_next = False
        elif not skip_next:
            result.append(arg)
    return result
