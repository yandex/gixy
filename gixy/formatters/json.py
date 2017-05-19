from __future__ import absolute_import

import json

from gixy.formatters.base import BaseFormatter


class JsonFormatter(BaseFormatter):
    def format_reports(self, reports, stats):
        result = []
        for path, issues in reports.items():
            for issue in issues:
                result.append(dict(
                    path=path,
                    plugin=issue['plugin'],
                    summary=issue['summary'],
                    severity=issue['severity'],
                    description=issue['description'],
                    reference=issue['help_url'],
                    reason=issue['reason'],
                    config=issue['config']
                ))

        return json.dumps(result, sort_keys=True, indent=2, separators=(',', ': '))
