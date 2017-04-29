class Issue(object):
    def __init__(self, plugin, summary=None, description=None,
                 severity=None, reason=None, help_url=None, directives=None):
        self.plugin = plugin
        self.summary = summary
        self.description = description
        self.severity = severity
        self.reason = reason
        self.help_url = help_url
        if not directives:
            self.directives = []
        elif not hasattr(directives, '__iter__'):
            self.directives = [directives]
        else:
            self.directives = directives
