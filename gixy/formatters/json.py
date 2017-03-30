from __future__ import absolute_import

import json

from gixy.formatters.base import BaseFormatter


class JsonFormatter(BaseFormatter):
    def format_reports(self, reports, stats):
        return json.dumps(reports, sort_keys=True, indent=2, separators=(',', ': '))
