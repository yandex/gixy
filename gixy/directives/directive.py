from gixy.core.variable import Variable
from gixy.core.regexp import Regexp


def get_overrides():
    result = {}
    for klass in Directive.__subclasses__():
        if not klass.nginx_name:
            continue

        if not klass.__name__.endswith('Directive'):
            continue

        result[klass.nginx_name] = klass
    return result


class Directive(object):
    nginx_name = None
    is_block = False
    provide_variables = False

    def __init__(self, name, args, raw=None):
        self.name = name
        self.parent = None
        self.args = args
        self._raw = raw

    def set_parent(self, parent):
        self.parent = parent

    @property
    def parents(self):
        parent = self.parent
        while parent:
            yield parent
            parent = parent.parent

    @property
    def variables(self):
        raise NotImplementedError()

    def __str__(self):
        return '{name} {args};'.format(name=self.name, args=' '.join(self.args))


class AddHeaderDirective(Directive):
    nginx_name = 'add_header'

    def __init__(self, name, args):
        super(AddHeaderDirective, self).__init__(name, args)
        self.header = args[0].lower()
        self.value = args[1]
        self.always = False
        if len(args) > 2 and args[2] == 'always':
            self.always = True


class SetDirective(Directive):
    nginx_name = 'set'
    provide_variables = True

    def __init__(self, name, args):
        super(SetDirective, self).__init__(name, args)
        self.variable = args[0].strip('$')
        self.value = args[1]

    @property
    def variables(self):
        return [Variable(name=self.variable, value=self.value, provider=self)]


class AuthRequestSetDirective(Directive):
    nginx_name = 'auth_request_set'
    provide_variables = True

    def __init__(self, name, args):
        super(AuthRequestSetDirective, self).__init__(name, args)
        self.variable = args[0].strip('$')
        self.value = args[1]

    @property
    def variables(self):
        return [Variable(name=self.variable, value=self.value, provider=self)]


class PerlSetDirective(Directive):
    nginx_name = 'perl_set'
    provide_variables = True

    def __init__(self, name, args):
        super(PerlSetDirective, self).__init__(name, args)
        self.variable = args[0].strip('$')
        self.value = args[1]

    @property
    def variables(self):
        return [Variable(name=self.variable, provider=self, have_script=False)]


class SetByLuaDirective(Directive):
    nginx_name = 'set_by_lua'
    provide_variables = True

    def __init__(self, name, args):
        super(SetByLuaDirective, self).__init__(name, args)
        self.variable = args[0].strip('$')
        self.value = args[1]

    @property
    def variables(self):
        return [Variable(name=self.variable, provider=self, have_script=False)]


class RewriteDirective(Directive):
    nginx_name = 'rewrite'
    provide_variables = True
    boundary = Regexp(r'[^\s\r\n]')

    def __init__(self, name, args):
        super(RewriteDirective, self).__init__(name, args)
        self.pattern = args[0]
        self.replace = args[1]
        self.flag = None
        if len(args) > 2:
            self.flag = args[2]

    @property
    def variables(self):
        regexp = Regexp(self.pattern, case_sensitive=True)
        result = []
        for name, group in regexp.groups.items():
            result.append(Variable(name=name, value=group, boundary=self.boundary, provider=self))
        return result


class RootDirective(Directive):
    nginx_name = 'root'
    provide_variables = True

    def __init__(self, name, args):
        super(RootDirective, self).__init__(name, args)
        self.path = args[0]

    @property
    def variables(self):
        return [Variable(name='document_root', value=self.path, provider=self)]


class AliasDirective(Directive):
    nginx_name = 'alias'

    def __init__(self, name, args):
        super(AliasDirective, self).__init__(name, args)
        self.path = args[0]
