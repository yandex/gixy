from __future__ import absolute_import

from gixy.formatters.base import BaseFormatter
from gixy.formatters._jinja import load_template


class TextFormatter(BaseFormatter):
    def __init__(self):
        super(TextFormatter, self).__init__()
        self.template = load_template('text.j2')

    def format_reports(self, reports, stats):
        return self.template.render(reports=reports, stats=stats)
