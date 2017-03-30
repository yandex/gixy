import gixy
from gixy.core.issue import Issue


class Plugin(object):
    summary = ''
    description = ''
    help_url = ''
    severity = gixy.severity.UNSPECIFIED
    directives = []
    options = {}

    def __init__(self, config):
        self._issues = []
        self.config = config

    def add_issue(self, directive, summary=None, severity=None, description=None, reason=None, help_url=None):
        self._issues.append(Issue(self, directives=directive, summary=summary, severity=severity,
                                  description=description, reason=reason, help_url=help_url))

    def audit(self, directive):
        pass

    @property
    def issues(self):
        return self._issues

    @property
    def name(self):
        return self.__class__.__name__
