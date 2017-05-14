from cached_property import cached_property

from gixy.directives.directive import Directive
from gixy.core.variable import Variable
from gixy.core.regexp import Regexp


def get_overrides():
    result = {}
    for klass in Block.__subclasses__():
        if not klass.nginx_name:
            continue

        if not klass.__name__.endswith('Block'):
            continue

        result[klass.nginx_name] = klass
    return result


class Block(Directive):
    nginx_name = None
    is_block = True
    self_context = True

    def __init__(self, name, args):
        super(Block, self).__init__(name, args)
        self.children = []

    def some(self, name, flat=True):
        for child in self.children:
            if child.name == name:
                return child
            if flat and child.is_block and not child.self_context:
                result = child.some(name, flat=flat)
                if result:
                    return result
        return None

    def find(self, name, flat=False):
        result = []
        for child in self.children:
            if child.name == name:
                result.append(child)
            if flat and child.is_block and not child.self_context:
                result += child.find(name)
        return result

    def find_recursive(self, name):
        result = []
        for child in self.children:
            if child.name == name:
                result.append(child)
            if child.is_block:
                result += child.find_recursive(name)
        return result

    def append(self, directive):
        directive.set_parent(self)
        self.children.append(directive)

    def __str__(self):
        return '{name} {args} {{'.format(name=self.name, args=' '.join(self.args))


class Root(Block):
    nginx_name = None

    def __init__(self):
        super(Root, self).__init__(None, [])


class HttpBlock(Block):
    nginx_name = 'http'

    def __init__(self, name, args):
        super(HttpBlock, self).__init__(name, args)


class ServerBlock(Block):
    nginx_name = 'server'

    def __init__(self, name, args):
        super(ServerBlock, self).__init__(name, args)

    def get_names(self):
        return self.find('server_name')

    def __str__(self):
        server_names = [str(sn) for sn in self.find('server_name')]
        if server_names:
            return 'server {{\n{0}'.format('\n'.join(server_names[:2]))
        return 'server {'


class LocationBlock(Block):
    nginx_name = 'location'
    provide_variables = True

    def __init__(self, name, args):
        super(LocationBlock, self).__init__(name, args)
        if len(args) == 2:
            self.modifier, self.path = args
        else:
            self.modifier = None
            self.path = args[0]

    @property
    def is_internal(self):
        return self.some('internal') is not None

    @cached_property
    def variables(self):
        if not self.modifier or self.modifier not in ('~', '~*'):
            return []

        regexp = Regexp(self.path, case_sensitive=self.modifier == '~')
        result = []
        for name, group in regexp.groups.items():
            result.append(Variable(name=name, value=group, boundary=None, provider=self))
        return result


class IfBlock(Block):
    nginx_name = 'if'
    self_context = False

    def __init__(self, name, args):
        super(IfBlock, self).__init__(name, args)
        self.operand = None
        self.value = None
        self.variable = None

        if len(args) == 1:
            # if ($slow)
            self.variable = args[0]
        elif len(args) == 2:
            # if (!-e $foo)
            self.operand, self.value = args
        elif len(args) == 3:
            # if ($request_method = POST)
            self.variable, self.operand, self.value = args
        else:
            raise Exception('Unknown "if" definition, args: {0!r}'.format(args))

    def __str__(self):
        return '{name} ({args}) {{'.format(name=self.name, args=' '.join(self.args))


class IncludeBlock(Block):
    nginx_name = 'include'
    self_context = False

    def __init__(self, name, args):
        super(IncludeBlock, self).__init__(name, args)
        self.file_path = args[0]

    def __str__(self):
        return 'include {0};'.format(self.file_path)


class MapBlock(Block):
    nginx_name = 'map'
    self_context = False
    provide_variables = True

    def __init__(self, name, args):
        super(MapBlock, self).__init__(name, args)
        self.source = args[0]
        self.variable = args[1].strip('$')

    @cached_property
    def variables(self):
        # TODO(buglloc): Finish him!
        return [Variable(name=self.variable, value='', boundary=None, provider=self, have_script=False)]
