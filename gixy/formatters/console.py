from __future__ import absolute_import
from jinja2 import Environment, PackageLoader

from gixy.formatters.base import BaseFormatter


class ConsoleFormatter(BaseFormatter):
    def __init__(self):
        super(ConsoleFormatter, self).__init__()
        env = Environment(loader=PackageLoader('gixy', 'formatters/templates'), trim_blocks=True, lstrip_blocks=True)
        self.template = env.get_template('console.j2')

    def format_reports(self, reports, stats):
        return self.template.render(reports=reports, stats=stats)
