from gixy.formatters._jinja import load_template
from gixy.formatters.base import BaseFormatter


class ConsoleFormatter(BaseFormatter):
    def __init__(self):
        super().__init__()
        self.template = load_template("console.j2")

    def format_reports(self, reports, stats):
        return self.template.render(reports=reports, stats=stats)
