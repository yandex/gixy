import os
from gixy.directives.directive import Directive

DIRECTIVES = {}


def import_directives():
    files_list = os.listdir(os.path.dirname(__file__))
    for directive_file in files_list:
        if not directive_file.endswith(".py") or directive_file.startswith('_'):
            continue
        __import__('gixy.directives.' + os.path.splitext(directive_file)[0], None, None, [''])


def get_all():
    if len(DIRECTIVES):
        return DIRECTIVES

    import_directives()
    for klass in Directive.__subclasses__():
        if not klass.nginx_name:
            continue
        DIRECTIVES[klass.nginx_name] = klass

    return DIRECTIVES
