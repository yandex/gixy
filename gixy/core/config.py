import gixy


class Config(object):
    def __init__(self,
                 plugins=None,
                 skips=None,
                 severity=gixy.severity.UNSPECIFIED,
                 output_format=None,
                 output_file=None,
                 allow_includes=True):

        self.severity = severity
        self.output_format = output_format
        self.output_file = output_file
        self.plugins = plugins
        self.skips = skips
        self.allow_includes = allow_includes
        self.plugins_options = {}

    def set_for(self, name, options):
        self.plugins_options[name] = options

    def get_for(self, name):
        if self.has_for(name):
            return self.plugins_options[name]
        return {}

    def has_for(self, name):
        return name in self.plugins_options
