import os
from gixy.formatters.base import BaseFormatter

FORMATTERS = {}


def import_formatters():
    files_list = os.listdir(os.path.dirname(__file__))
    for formatter_file in files_list:
        if not formatter_file.endswith(".py") or formatter_file.startswith('_'):
            continue
        __import__('gixy.formatters.' + os.path.splitext(formatter_file)[0], None, None, [''])


def get_all():
    if len(FORMATTERS):
        return FORMATTERS

    import_formatters()
    for klass in BaseFormatter.__subclasses__():
        FORMATTERS[klass.__name__.replace('Formatter', '').lower()] = klass

    return FORMATTERS
