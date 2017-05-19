from __future__ import absolute_import

import gixy
from gixy.directives import block


class BaseFormatter(object):
    skip_parents = set([block.Root, block.HttpBlock])

    def __init__(self):
        self.reports = {}
        self.stats = dict.fromkeys(gixy.severity.ALL, 0)

    def format_reports(self, reports, stats):
        raise NotImplementedError("Formatter must override format_reports function")

    def feed(self, path, manager):
        for severity in gixy.severity.ALL:
            self.stats[severity] += manager.stats[severity]

        self.reports[path] = []
        for result in manager.results:
            report = self._prepare_result(manager.root,
                                          summary=result.summary,
                                          severity=result.severity,
                                          description=result.description,
                                          issues=result.issues,
                                          plugin=result.name,
                                          help_url=result.help_url)
            self.reports[path].extend(report)

    def flush(self):
        return self.format_reports(self.reports, self.stats)

    def _prepare_result(self, root, issues, severity, summary, description, plugin, help_url):
        result = {}
        for issue in issues:
            report = dict(
                plugin=plugin,
                summary=issue.summary or summary,
                severity=issue.severity or severity,
                description=issue.description or description,
                help_url=issue.help_url or help_url,
                reason=issue.reason or '',
            )
            key = ''.join(report.values())
            report['directives'] = issue.directives
            if key in result:
                result[key]['directives'].extend(report['directives'])
            else:
                result[key] = report

        for report in result.values():
            if report['directives']:
                config = self._resolve_config(root, report['directives'])
            else:
                config = ''

            del report['directives']
            report['config'] = config
            yield report

    def _resolve_config(self, root, directives):
        points = set()
        for directive in directives:
            points.add(directive)
            points.update(p for p in directive.parents)

        result = self._traverse_tree(root, points, 0)
        return '\n'.join(result)

    def _traverse_tree(self, tree, points, level):
        result = []
        for leap in tree.children:
            if leap not in points:
                continue
            printable = type(leap) not in self.skip_parents
            # Special hack for includes
            # TODO(buglloc): fix me
            have_parentheses = type(leap) != block.IncludeBlock

            if printable:
                if leap.is_block:
                    result.append('')
                directive = str(leap).replace('\n', '\n' + '\t' * (level + 1))
                result.append('{indent:s}{dir:s}'.format(indent='\t' * level, dir=directive))

            if leap.is_block:
                result.extend(self._traverse_tree(leap, points, level + 1 if printable else level))
                if printable and have_parentheses:
                    result.append('{indent:s}}}'.format(indent='\t' * level))

        return result
