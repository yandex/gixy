from __future__ import absolute_import
from jinja2 import Environment, PackageLoader

from gixy.utils.text import to_text


def load_template(name):
    env = Environment(loader=PackageLoader('gixy', 'formatters/templates'), trim_blocks=True, lstrip_blocks=True)
    env.filters['to_text'] = to_text_filter
    return env.get_template(name)


def to_text_filter(text):
    try:
        return text.encode('latin1').decode('utf-8')
    except UnicodeEncodeError:
        return to_text(text)
