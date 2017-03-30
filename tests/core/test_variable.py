from nose.tools import assert_true, assert_false, assert_equals, with_setup
from gixy.core.context import get_context, push_context, purge_context
from gixy.directives.block import Root
from gixy.core.regexp import Regexp
from gixy.core.variable import Variable

def setup():
    push_context(Root())


def tear_down():
    purge_context()


@with_setup(setup, tear_down)
def test_literal():
    var = Variable(name='simple', value='$uri', have_script=False)
    assert_false(var.depends)
    assert_false(var.regexp)
    assert_equals(var.value, '$uri')

    assert_false(var.can_startswith('$'))
    assert_false(var.can_contain('i'))
    assert_true(var.must_contain('$'))
    assert_true(var.must_contain('u'))
    assert_false(var.must_contain('a'))
    assert_true(var.must_startswith('$'))
    assert_false(var.must_startswith('u'))


@with_setup(setup, tear_down)
def test_regexp():
    var = Variable(name='simple', value=Regexp('^/.*'))
    assert_false(var.depends)
    assert_true(var.regexp)

    assert_true(var.can_startswith('/'))
    assert_false(var.can_startswith('a'))
    assert_true(var.can_contain('a'))
    assert_false(var.can_contain('\n'))
    assert_true(var.must_contain('/'))
    assert_false(var.must_contain('a'))
    assert_true(var.must_startswith('/'))
    assert_false(var.must_startswith('a'))


@with_setup(setup, tear_down)
def test_script():
    get_context().add_var('foo', Variable(name='foo', value=Regexp('.*')))
    var = Variable(name='simple', value='/$foo')
    assert_true(var.depends)
    assert_false(var.regexp)

    assert_false(var.can_startswith('/'))
    assert_false(var.can_startswith('a'))
    assert_true(var.can_contain('/'))
    assert_true(var.can_contain('a'))
    assert_false(var.can_contain('\n'))
    assert_true(var.must_contain('/'))
    assert_false(var.must_contain('a'))
    assert_true(var.must_startswith('/'))
    assert_false(var.must_startswith('a'))


@with_setup(setup, tear_down)
def test_regexp_boundary():
    var = Variable(name='simple', value=Regexp('.*'), boundary=Regexp('/[a-z]', strict=True))
    assert_false(var.depends)
    assert_true(var.regexp)

    assert_true(var.can_startswith('/'))
    assert_false(var.can_startswith('a'))
    assert_false(var.can_contain('/'))
    assert_true(var.can_contain('a'))
    assert_false(var.can_contain('0'))
    assert_false(var.can_contain('\n'))
    assert_true(var.must_contain('/'))
    assert_false(var.must_contain('a'))
    assert_true(var.must_startswith('/'))
    assert_false(var.must_startswith('a'))


@with_setup(setup, tear_down)
def test_script_boundary():
    get_context().add_var('foo', Variable(name='foo', value=Regexp('.*'), boundary=Regexp('[a-z]', strict=True)))
    var = Variable(name='simple', value='/$foo', boundary=Regexp('[/a-z0-9]', strict=True))
    assert_true(var.depends)
    assert_false(var.regexp)

    assert_false(var.can_startswith('/'))
    assert_false(var.can_startswith('a'))
    assert_false(var.can_contain('/'))
    assert_true(var.can_contain('a'))
    assert_false(var.can_contain('\n'))
    assert_false(var.can_contain('0'))
    assert_true(var.must_contain('/'))
    assert_false(var.must_contain('a'))
    assert_true(var.must_startswith('/'))
    assert_false(var.must_startswith('a'))
