import logging
import copy

from gixy.core.utils import is_indexed_name

LOG = logging.getLogger(__name__)

CONTEXTS = []


def get_context():
    return CONTEXTS[-1]


def purge_context():
    del CONTEXTS[:]


def push_context(block):
    if len(CONTEXTS):
        context = copy.deepcopy(get_context())
    else:
        context = Context()
    context.set_block(block)
    CONTEXTS.append(context)
    return context


def pop_context():
    return CONTEXTS.pop()


class Context(object):
    def __init__(self):
        self.block = None
        self.variables = {
            'index': {},
            'name': {}
        }

    def set_block(self, directive):
        self.block = directive
        return self

    def clear_index_vars(self):
        self.variables['index'] = {}
        return self

    def add_var(self, name, var):
        if is_indexed_name(name):
            var_type = 'index'
            name = int(name)
        else:
            var_type = 'name'

        self.variables[var_type][name] = var
        return self

    def get_var(self, name):
        if is_indexed_name(name):
            var_type = 'index'
            name = int(name)
        else:
            var_type = 'name'

        result = None
        try:
            result = self.variables[var_type][name]
        except KeyError:
            if var_type == 'name':
                # Only named variables can be builtins
                import gixy.core.builtin_variables as builtins

                if builtins.is_builtin(name):
                    result = builtins.builtin_var(name)

        if not result:
            LOG.info("Can't find variable '{}'".format(name))
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        result.block = copy.copy(self.block)
        result.variables = {
            'index': copy.copy(self.variables['index']),
            'name': copy.copy(self.variables['name'])
        }
        return result
