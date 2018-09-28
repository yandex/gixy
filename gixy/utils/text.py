from __future__ import absolute_import
from six import PY3, text_type, binary_type


def to_bytes(obj, encoding='latin1', errors='strict', nonstring='replace'):
    if isinstance(obj, binary_type):
        return obj

    if isinstance(obj, text_type):
        try:
            # Try this first as it's the fastest
            return obj.encode(encoding, errors)
        except UnicodeEncodeError:
            return b'failed_to_encode'

    if nonstring == 'simplerepr':
        try:

            value = str(obj)
        except UnicodeError:
            try:
                value = repr(obj)
            except UnicodeError:
                # Giving up
                return b'failed_to_encode'
    elif nonstring == 'passthru':
        return obj
    elif nonstring == 'replace':
        return b'failed_to_encode'
    elif nonstring == 'strict':
        raise TypeError('obj must be a string type')
    else:
        raise TypeError('Invalid value %s for to_bytes\' nonstring parameter' % nonstring)

    return to_bytes(value, encoding, errors)


def to_text(obj, encoding='latin1', errors='strict', nonstring='replace'):
    if isinstance(obj, text_type):
        return obj

    if isinstance(obj, binary_type):
        try:
            return obj.decode(encoding, errors)
        except UnicodeEncodeError:
            return u'failed_to_encode'

    if nonstring == 'simplerepr':
        try:
            value = str(obj)
        except UnicodeError:
            try:
                value = repr(obj)
            except UnicodeError:
                # Giving up
                return u'failed_to_encode'
    elif nonstring == 'passthru':
        return obj
    elif nonstring == 'replace':
        return u'failed_to_encode'
    elif nonstring == 'strict':
        raise TypeError('obj must be a string type')
    else:
        raise TypeError('Invalid value %s for to_text\'s nonstring parameter' % nonstring)

    return to_text(value, encoding, errors)


if PY3:
    to_native = to_text
else:
    to_native = to_bytes
