import logging
import os

import gixy
from gixy.core.config import Config
from gixy.core.context import get_context, pop_context, purge_context, push_context
from gixy.core.plugins_manager import PluginsManager
from gixy.parser.nginx_parser import NginxParser

LOG = logging.getLogger(__name__)


class Manager:
    def __init__(self, config=None):
        self.root = None
        self.config = config or Config()
        self.auditor = PluginsManager(config=self.config)

    def audit(self, file_path, file_data, is_stdin=False):
        LOG.debug(f"Audit config file: {file_path}")
        parser = NginxParser(
            cwd=os.path.dirname(file_path) if not is_stdin else "",
            allow_includes=self.config.allow_includes,
        )
        self.root = parser.parse(content=file_data.read(), path_info=file_path)

        push_context(self.root)
        self._audit_recursive(self.root.children)

    @property
    def results(self):
        for plugin in self.auditor.plugins:
            if plugin.issues:
                yield plugin

    @property
    def stats(self):
        stats = dict.fromkeys(gixy.severity.ALL, 0)
        for plugin in self.auditor.plugins:
            base_severity = plugin.severity
            for issue in plugin.issues:
                # TODO(buglloc): encapsulate into Issue class?
                severity = issue.severity if issue.severity else base_severity
                stats[severity] += 1
        return stats

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
