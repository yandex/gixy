from nose.tools import assert_true, assert_false


'''
Various nose.tools helpers that doesn't exists in Python 2.6 Unittest :(
Must be removed with drop Python 2.6 support
'''


def assert_is_instance(obj, cls, msg=None):
    """Same as assert_true(isinstance(obj, cls)), with a nicer
    default message."""
    if not msg:
        msg = '{orig} is not an instance of {test}'.format(orig=type(obj), test=cls)
    assert_true(isinstance(obj, cls), msg=msg)


def assert_is_none(obj, msg=None):
    """Same as assert_true(obj is None), with a nicer default message."""
    if not msg:
        msg = '{orig!r} is not None'.format(orig=obj)
    assert_true(obj is None, msg=msg)


def assert_is_not_none(obj, msg=None):
    """Same as assert_false(obj is None), with a nicer default message."""
    if not msg:
        msg = '{orig!r} is None'.format(orig=obj)
    assert_false(obj is None, msg=msg)


def assert_in(member, container, msg=None):
    """Just like assert_true(a in b), but with a nicer default message."""
    if not msg:
        msg = '{member!r} not found in {container!r}'.format(member=member, container=container)
    assert_true(member in container, msg=msg)
