from nose.tools import assert_true, assert_false, assert_equals
from gixy.core.regexp import Regexp

'''
CATEGORIES:
    sre_parse.CATEGORY_SPACE
    sre_parse.CATEGORY_NOT_SPACE
    sre_parse.CATEGORY_DIGIT
    sre_parse.CATEGORY_NOT_DIGIT
    sre_parse.CATEGORY_WORD
    sre_parse.CATEGORY_NOT_WORD
    ANY
'''


def test_positive_contains():
    cases = (
        (r'[a-z]', 'a'),
        (r'[a-z]*', 'a'),
        (r'[a-z]*?', 'a'),
        (r'[a-z]+?', 'a'),
        (r'[a-z]', 'z'),
        (r'(?:a|b)', 'b'),
        (r'(/|:|[a-z])', 'g'),
        (r'[^a-z]', '/'),
        (r'[^a-z]', '\n'),
        (r'[^0]', '9'),
        (r'[^0-2]', '3'),
        (r'[^0123a-z]', '9'),
        (r'\s', '\x20'),
        (r'[^\s]', 'a'),
        (r'\d', '1'),
        (r'[^\d]', 'b'),
        (r'\w', '_'),
        (r'[^\w]', '\n'),
        (r'\W', '\n'),
        (r'[^\W]', 'a'),
        (r'.', 'a')
    )
    for case in cases:
        regexp, char = case
        yield check_positive_contain, regexp, char


def test_negative_contains():
    cases = (
        ('[a-z]', '1'),
        ('[a-z]*', '2'),
        ('[a-z]*?', '3'),
        ('[a-z]+?', '4'),
        ('[a-z]', '\n'),
        ('(?:a|b)', 'c'),
        ('(/|:|[a-z])', '\n'),
        ('[^a-z]', 'a'),
        ('[^0]', '0'),
        ('[^0-2]', '0'),
        ('[^0123a-z]', 'z'),
        (r'\s', 'a'),
        (r'[^\s]', '\n'),
        (r'\d', 'f'),
        (r'[^\d]', '2'),
        (r'\w', '\n'),
        (r'[^\w]', '_'),
        (r'\W', 'a'),
        (r'[^\W]', '\n'),
        (r'.', '\n')
    )
    for case in cases:
        regexp, char = case
        yield check_negative_contain, regexp, char


def test_groups_names():
    cases = (
        ('foo', [0]),
        ('(1)(2)(?:3)', [0, 1, 2]),
        ('(1)((2)|(?:3))', [0, 1, 2, 3]),
        ("(?'pcre_7'1as)(?P<outer>(?<inner>2)|(?:3))", [0, 1, 2, 3, 'pcre_7', 'outer', 'inner']),
        ('/proxy/(?<proxy>.*)$', [0, 1, 'proxy'])
    )
    for case in cases:
        regexp, groups = case
        yield check_groups_names, regexp, groups


def test_to_string():
    cases = (
        (r'foo', 'foo'),
        (r'(1)(2)(?:3)', '(1)(2)(?:3)'),
        (r'(1)((2)|(?:3))', '(1)((?:(2)|(?:3)))'),
        (r'\w|1|3-5|[a-z]', '(?:[\w]|1|3\\-5|[a-z])'),
        (r'(1|(?:3)|([4-6]))', '((?:1|(?:3)|([4-6])))'),
        (r'(1|(?:3)|(?P<aaa>[4-6]))', '((?:1|(?:3)|([4-6])))'),
        (r'^sss', '^sss'),
        (r'(^bb|11)$', '((?:^bb|11))$'),
        (r'(http|https)', '(http(?:|s))'),
        (r'1*', '1*'),
        (r'1*?', '1*?'),
        (r'1+', '1+'),
    )
    for case in cases:
        regexp, string = case
        yield check_to_string, regexp, string


def test_positive_startswith():
    cases = (
        (r'foo', 'q', False),
        (r'foo', 'f', True),
        (r'^foo', 'f', False),
        (r'(^foo)', 'f', False),
        (r'(^foo)', 'f', True),
        (r'(^foo|g)', 'f', True),
        (r'(^foo|g)', 'g', True),
        (r'(^foo|g)', 'q', False),
        (r'^[^/]+', '\n', True),
        (r'/[^/]+', '/', True),
        (r'((a))', 'a', False),
        (r'((a))', 'b', False),
        (r'^[a-z]{0}0', '0', False),
        (r'^[a-z]{1}0', 'a', False),
    )
    for case in cases:
        regexp, check, strict = case
        yield check_positive_startswith, regexp, check, strict


def test_negative_startswith():
    cases = (
        (r'foo', '\n', False),
        (r'foo', 'o', True),
        (r'^foo', 'o', False),
        (r'(^foo)', 'q', False),
        (r'(^foo)', 'q', True),
        (r'(^foo|g)', 'q', True),
        (r'(^foo|g)', 'o', True),
        (r'(^foo|g)', '\n', False),
        (r'^[^/]+', '/', True),
        (r'/[^/]+', 'a', True),
        (r'((abc)|(ss))', 'b', True),
        (r'^[a-z]{0}0', 'a', False),
        (r'^[a-z]{0}0', 'g', False),
    )
    for case in cases:
        regexp, check, strict = case
        yield check_negative_startswith, regexp, check, strict


def test_positive_must_contain():
    cases = (
        (r'abc', 'a'),
        (r'abc', 'b'),
        (r'abc', 'c'),
        (r'3+', '3'),
        (r'[0]', '0'),
        (r'([0])', '0'),
        (r'(?:[0])', '0'),
        (r'(?:[0])|0|((((0))))', '0'),
    )
    for case in cases:
        regexp, char = case
        yield check_positive_must_contain, regexp, char


def test_negative_must_contain():
    cases = (
        (r'[a-z]', '1'),
        (r'2{0}1', '2'),
        (r'3?', '3'),
        (r'3*', '3'),
        (r'3*?', '3'),
        (r'3+a', 'b'),
        (r'[a-z]', 'a'),
        (r'(?:a|b)', 'a'),
        (r'(?:a|b)', 'b'),
        (r'(/|:|[a-z])', '/'),
        (r'(/|:|[a-z])', 'z'),
        (r'[^a-z]', '\n'),
        (r'[^0]', '0'),
        (r'[^0-2]', '0'),
        (r'[^0123a-z]', 'z'),
        (r'\s', '\x20'),
        (r'[^\s]', '\n'),
        (r'\d', '3'),
        (r'[^\d]', 'a'),
        (r'\w', 'a'),
        (r'[^\w]', '\n'),
        (r'\W', '\n'),
        (r'[^\W]', 'a'),
        (r'.', '\n')
    )
    for case in cases:
        regexp, char = case
        yield check_negative_must_contain, regexp, char


def test_positive_must_startswith():
    cases = (
        (r'foo', 'f', True),
        (r'^foo', 'f', False),
        (r'(^foo)', 'f', True),
        (r'^((a))', 'a', False),
        (r'((a))', 'a', True),
        (r'^[a-z]{0}0', '0', False),
        (r'^a{1}0', 'a', False),
    )
    for case in cases:
        regexp, check, strict = case
        yield check_positive_must_startswith, regexp, check, strict


def test_negative_must_startswith():
    cases = (
        (r'foo', 'o', False),
        (r'^foo', 'o', False),
        (r'(^foo)', 'o', False),
        (r'[a-z]', '1', True),
        (r'[a-z]', 'a', True),
        (r'/[^/]+', 'a', True),
        (r'3?', '3', True),
        (r'3*', '3', True),
        (r'3*?', '3', True),
        (r'3+a', 'b', True),
        (r'^((a))', 'b', False),
        (r'((a))', 'a', False),
        (r'^a{0}0', 'a', False),
    )
    for case in cases:
        regexp, check, strict = case
        yield check_negative_must_startswith, regexp, check, strict


def test_generate():
    cases = (
        (r'foo', {'foo'}),
        (r'^sss', {'^sss'}),
        (r'(1)(2)(3)', {'123'}),
        (r'(1)((2)|(?:3))', {'12', '13'}),
        (r'(^1?2?|aa/)', {'^', '^1', '^2', '^12', 'aa/'}),
        (r'^https?://yandex.ru', {'^http://yandex|ru', '^https://yandex|ru'}),
        (r'(^bb|11)$', {'^bb$', '11$'}),
        (r'(http|https)', {'http', 'https'}),
        (r'1*', {'', '11111'}),
        (r'1*?', {'', '11111'}),
        (r'1{0}?2', {'2'}),
        (r'1{0}2', {'2'}),
        (r'1+', {'11111'}),
        (r'[^/]?', {'', '|'}),
        (r'^http://(foo|bar)|baz', {'^http://foo', '^http://bar', 'baz'}),
        (r'[^\x00-\x7b|\x7e-\xff]', {'\x7d'}),
        (r'(a|b|c)', {'a', 'b', 'c'}),
        (r'[xyz]', {'x', 'y', 'z'})
    )
    for case in cases:
        regexp, values = case
        yield check_generate, regexp, values


def test_strict_generate():
    reg = Regexp('^foo|bar', strict=True)
    assert_equals(sorted(reg.generate('|', anchored=True)), sorted({'^foo', '^bar'}))


def test_gen_anchor():

    reg = Regexp('^some$')
    val = next(reg.generate('', anchored=False))
    assert_equals(val, 'some')

    reg = Regexp('^some$')
    val = next(reg.generate('', anchored=True))
    assert_equals(val, '^some$')

    reg = Regexp('^some$', strict=True)
    val = next(reg.generate('', anchored=False))
    assert_equals(val, 'some')

    reg = Regexp('^some$', strict=True)
    val = next(reg.generate('', anchored=True))
    assert_equals(val, '^some$')


def test_group_can_contains():
    source = '/some/(?P<action>[^/:.]+)/'
    reg = Regexp(source)
    assert_true(reg.can_contain('\n'),
                'Whole regex "{}" can contains "{}"'.format(source, '\\n'))

    assert_true(reg.group(0).can_contain('\n'),
                'Group 0 from regex "{}" can contains "{}"'.format(source, '\\n'))

    assert_true(reg.group('action').can_contain('\n'),
                'Group "action" from regex "{}" can contains "{}"'.format(source, '\\n'))

    assert_true(reg.group(1).can_contain('\n'),
                'Group 1 from regex "{}" can contains "{}"'.format(source, '\\n'))

    assert_false(reg.group('action').can_contain('/'),
                 'Group "action" from regex "{}" CAN\'T (!) contain "{}"'.format(source, '/'))


def check_positive_contain(regexp, char):
    reg = Regexp(regexp, case_sensitive=True)
    assert_true(reg.can_contain(char),
                '"{}" should contain "{}"'.format(regexp, char))

    reg = Regexp(regexp, case_sensitive=False)
    char = char.upper()
    assert_true(reg.can_contain(char),
                '"{}" (case insensitive) should contain "{}"'.format(regexp, char))


def check_negative_contain(regexp, char):
    reg = Regexp(regexp, case_sensitive=True)
    assert_false(reg.can_contain(char),
                 '"{}" should not contain "{}"'.format(regexp, char))

    reg = Regexp(regexp, case_sensitive=False)
    char = char.upper()
    assert_false(reg.can_contain(char),
                 '"{}" (case insensitive) should not contain "{}"'.format(regexp, char))


def check_positive_startswith(regexp, char, strict):
    reg = Regexp(regexp, case_sensitive=True, strict=strict)
    assert_true(reg.can_startswith(char),
                '"{}" can start\'s with "{}"'.format(regexp, char))

    reg = Regexp(regexp, case_sensitive=False, strict=strict)
    char = char.upper()
    assert_true(reg.can_startswith(char),
                '"{}" (case insensitive) can start\'s with "{}"'.format(regexp, char))


def check_negative_startswith(regexp, char, strict):
    reg = Regexp(regexp, case_sensitive=True, strict=strict)
    assert_false(reg.can_startswith(char),
                 '"{}" can\'t start\'s with "{}"'.format(regexp, char))

    reg = Regexp(regexp, case_sensitive=False, strict=strict)
    char = char.upper()
    assert_false(reg.can_startswith(char),
                 '"{}" (case insensitive) can\'t start\'s with "{}"'.format(regexp, char))


def check_groups_names(regexp, groups):
    reg = Regexp(regexp)
    assert_equals(set(reg.groups.keys()), set(groups))


def check_to_string(regexp, string):
    reg = Regexp(regexp)
    assert_equals(str(reg), string)


def check_positive_must_contain(regexp, char):
    reg = Regexp(regexp, case_sensitive=True)
    assert_true(reg.must_contain(char),
                '"{}" must contain with "{}"'.format(regexp, char))

    reg = Regexp(regexp, case_sensitive=False)
    char = char.upper()
    assert_true(reg.must_contain(char),
                '"{}" (case insensitive) must contain with "{}"'.format(regexp, char))


def check_negative_must_contain(regexp, char):
    reg = Regexp(regexp, case_sensitive=True)
    assert_false(reg.must_contain(char),
                 '"{}" must NOT contain with "{}"'.format(regexp, char))

    reg = Regexp(regexp, case_sensitive=False)
    char = char.upper()
    assert_false(reg.must_contain(char),
                 '"{}" (case insensitive) must NOT contain with "{}"'.format(regexp, char))


def check_positive_must_startswith(regexp, char, strict):
    reg = Regexp(regexp, case_sensitive=True, strict=strict)
    assert_true(reg.must_startswith(char),
                '"{}" MUST start\'s with "{}"'.format(regexp, char))

    reg = Regexp(regexp, case_sensitive=False, strict=strict)
    char = char.upper()
    assert_true(reg.must_startswith(char),
                '"{}" (case insensitive) MUST start\'s with "{}"'.format(regexp, char))


def check_negative_must_startswith(regexp, char, strict):
    reg = Regexp(regexp, case_sensitive=True, strict=strict)
    assert_false(reg.must_startswith(char),
                 '"{}" MUST NOT start\'s with "{}"'.format(regexp, char))

    reg = Regexp(regexp, case_sensitive=False, strict=strict)
    char = char.upper()
    assert_false(reg.must_startswith(char),
                 '"{}" (case insensitive) MUST NOT start\'s with "{}"'.format(regexp, char))

def check_generate(regexp, values):
    reg = Regexp(regexp)
    assert_equals(sorted(reg.generate('|', anchored=True)), sorted(values))
