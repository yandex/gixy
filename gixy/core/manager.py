import os
import logging

import gixy
from gixy.core.plugins_manager import PluginsManager
from gixy.core.context import get_context, pop_context, push_context, purge_context
from gixy.parser.nginx_parser import NginxParser
from gixy.core.config import Config

LOG = logging.getLogger(__name__)


class Manager(object):
    def __init__(self, config=None):
        self.root = None
        self.config = config or Config()
        self.auditor = PluginsManager(config=self.config)
        self.stats = {gixy.severity.UNSPECIFIED: 0,
                      gixy.severity.LOW: 0,
                      gixy.severity.MEDIUM: 0,
                      gixy.severity.HIGH: 0}

    def audit(self, file_path, file_data, is_stdin=False):
        LOG.debug("Audit config file: {fname}".format(fname=file_path))
        parser = NginxParser(
            cwd=os.path.dirname(file_path) if not is_stdin else '',
            allow_includes=self.config.allow_includes)
        self.root = parser.parse(content=file_data.read(), path_info=file_path)

        push_context(self.root)
        self._audit_recursive(self.root.children)

    def get_results(self):
        for plugin in self.auditor.plugins:
            if plugin.issues:
                self.stats[plugin.severity] += len(plugin.issues)
                yield plugin

    def _audit_recursive(self, tree):
        for directive in tree:
            self._update_variables(directive)
            self.auditor.audit(directive)
            if directive.is_block:
                if directive.self_context:
                    push_context(directive)
                self._audit_recursive(directive.children)
                if directive.self_context:
                    pop_context()

    def _update_variables(self, directive):
        # TODO(buglloc): finish him!
        if not directive.provide_variables:
            return

        context = get_context()
        for var in directive.variables:
            if var.name == 0:
                # All regexps must clean indexed variables
                context.clear_index_vars()
            context.add_var(var.name, var)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        purge_context()
