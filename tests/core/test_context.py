from nose.tools import with_setup, assert_equals, assert_not_equals, assert_true
from gixy.core.context import get_context, pop_context, push_context, purge_context, CONTEXTS, Context
from gixy.directives.block import Root
from gixy.core.variable import Variable
from gixy.core.regexp import Regexp


def setup():
    assert_equals(len(CONTEXTS), 0)


def tear_down():
    purge_context()


@with_setup(setup, tear_down)
def test_push_pop_context():
    root_a = Root()
    push_context(root_a)
    assert_equals(len(CONTEXTS), 1)
    root_b = Root()
    push_context(root_b)
    assert_equals(len(CONTEXTS), 2)

    poped = pop_context()
    assert_equals(len(CONTEXTS), 1)
    assert_equals(poped.block, root_b)
    poped = pop_context()
    assert_equals(len(CONTEXTS), 0)
    assert_equals(poped.block, root_a)


@with_setup(setup, tear_down)
def test_push_get_purge_context():
    root = Root()
    push_context(root)
    assert_equals(len(CONTEXTS), 1)
    assert_equals(get_context().block, root)
    root = Root()
    push_context(root)
    assert_equals(len(CONTEXTS), 2)
    assert_equals(get_context().block, root)

    purge_context()
    assert_equals(len(CONTEXTS), 0)


@with_setup(setup, tear_down)
def test_add_variables():
    context = push_context(Root())
    assert_equals(len(context.variables['index']), 0)
    assert_equals(len(context.variables['name']), 0)

    one_str_var = Variable('1')
    context.add_var('1', one_str_var)
    one_int_var = Variable(1)
    context.add_var(1, one_int_var)
    some_var = Variable('some')
    context.add_var('some', some_var)

    assert_equals(len(context.variables['index']), 1)
    assert_equals(context.variables['index'][1], one_int_var)
    assert_equals(len(context.variables['name']), 1)
    assert_equals(context.variables['name']['some'], some_var)
    context.clear_index_vars()
    assert_equals(len(context.variables['index']), 0)
    assert_equals(len(context.variables['name']), 1)
    assert_equals(context.variables['name']['some'], some_var)


@with_setup(setup, tear_down)
def test_get_variables():
    context = push_context(Root())
    assert_equals(len(context.variables['index']), 0)
    assert_equals(len(context.variables['name']), 0)

    one_var = Variable(1)
    context.add_var(1, one_var)
    some_var = Variable('some')
    context.add_var('some', some_var)

    assert_equals(context.get_var(1), one_var)
    assert_equals(context.get_var('some'), some_var)
    # Checks not existed variables, for now context may return None
    assert_equals(context.get_var(0), None)
    assert_equals(context.get_var('not_existed'), None)
    # Checks builtins variables
    assert_true(context.get_var('uri'))
    assert_true(context.get_var('document_uri'))
    assert_true(context.get_var('arg_asdsadasd'))
    assert_true(context.get_var('args'))


@with_setup(setup, tear_down)
def test_context_depend_variables():
    push_context(Root())
    assert_equals(len(get_context().variables['index']), 0)
    assert_equals(len(get_context().variables['name']), 0)

    get_context().add_var(1, Variable(1, value='one'))
    get_context().add_var('some', Variable('some', value='some'))

    assert_equals(get_context().get_var(1).value, 'one')
    assert_equals(get_context().get_var('some').value, 'some')

    # Checks top context variables are still exists
    push_context(Root())
    assert_equals(get_context().get_var(1).value, 'one')
    assert_equals(get_context().get_var('some').value, 'some')

    # Checks variable overriding
    get_context().add_var('some', Variable('some', value='some_new'))
    get_context().add_var('foo', Variable('foo', value='foo'))
    assert_not_equals(get_context().get_var('some').value, 'some')
    assert_equals(get_context().get_var('some').value, 'some_new')
    assert_equals(get_context().get_var('foo').value, 'foo')
    assert_equals(get_context().get_var(1).value, 'one')

    # Checks variables after restore previous context
    pop_context()
    assert_not_equals(get_context().get_var('some').value, 'some_new')
    assert_equals(get_context().get_var('some').value, 'some')
    assert_equals(get_context().get_var('foo'), None)
    assert_equals(get_context().get_var(1).value, 'one')


@with_setup(setup, tear_down)
def test_push_failed_with_regexp_py35_gixy_10():
    push_context(Root())
    assert_equals(len(get_context().variables['index']), 0)
    assert_equals(len(get_context().variables['name']), 0)

    regexp = Regexp('^/some/(.*?)')
    for name, group in regexp.groups.items():
        get_context().add_var(name, Variable(name=name, value=group))

    push_context(Root())
