from gixy.core.context import get_context, push_context, purge_context
from gixy.directives.block import Root
from gixy.core.regexp import Regexp
from gixy.core.variable import Variable

def setup_function():
    push_context(Root())


def teardown_function():
    purge_context()


def test_literal():
    var = Variable(name='simple', value='$uri', have_script=False)
    assert not var.depends
    assert not var.regexp
    assert var.value == '$uri'

    assert not var.can_startswith('$')
    assert not var.can_contain('i')
    assert var.must_contain('$')
    assert var.must_contain('u')
    assert not var.must_contain('a')
    assert var.must_startswith('$')
    assert not var.must_startswith('u')


def test_regexp():
    var = Variable(name='simple', value=Regexp('^/.*'))
    assert not var.depends
    assert var.regexp

    assert var.can_startswith('/')
    assert not var.can_startswith('a')
    assert var.can_contain('a')
    assert not var.can_contain('\n')
    assert var.must_contain('/')
    assert not var.must_contain('a')
    assert var.must_startswith('/')
    assert not var.must_startswith('a')


def test_script():
    get_context().add_var('foo', Variable(name='foo', value=Regexp('.*')))
    var = Variable(name='simple', value='/$foo')
    assert var.depends
    assert not var.regexp

    assert not var.can_startswith('/')
    assert not var.can_startswith('a')
    assert var.can_contain('/')
    assert var.can_contain('a')
    assert not var.can_contain('\n')
    assert var.must_contain('/')
    assert not var.must_contain('a')
    assert var.must_startswith('/')
    assert not var.must_startswith('a')


def test_regexp_boundary():
    var = Variable(name='simple', value=Regexp('.*'), boundary=Regexp('/[a-z]', strict=True))
    assert not var.depends
    assert var.regexp

    assert var.can_startswith('/')
    assert not var.can_startswith('a')
    assert not var.can_contain('/')
    assert var.can_contain('a')
    assert not var.can_contain('0')
    assert not var.can_contain('\n')
    assert var.must_contain('/')
    assert not var.must_contain('a')
    assert var.must_startswith('/')
    assert not var.must_startswith('a')


def test_script_boundary():
    get_context().add_var('foo', Variable(name='foo', value=Regexp('.*'), boundary=Regexp('[a-z]', strict=True)))
    var = Variable(name='simple', value='/$foo', boundary=Regexp('[/a-z0-9]', strict=True))
    assert var.depends
    assert not var.regexp

    assert not var.can_startswith('/')
    assert not var.can_startswith('a')
    assert not var.can_contain('/')
    assert var.can_contain('a')
    assert not var.can_contain('\n')
    assert not var.can_contain('0')
    assert var.must_contain('/')
    assert not var.must_contain('a')
    assert var.must_startswith('/')
    assert not var.must_startswith('a')
