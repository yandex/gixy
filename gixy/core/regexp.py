import logging
import re
import random
import itertools
from cached_property import cached_property

from .sre_parse import _parser

LOG = logging.getLogger(__name__)


def _build_reverse_list(original):
    result = []
    for c in range(1, 126):
        c = chr(c)
        if c not in original:
            result.append(c)
    return frozenset(result)


FIX_NAMED_GROUPS_RE = re.compile(r"(?<!\\)\(\?(?:<|')(\w+)(?:>|')")

CATEGORIES = {
    # TODO(buglloc): unicode?
    _parser.CATEGORY_SPACE: _parser.WHITESPACE,
    _parser.CATEGORY_NOT_SPACE: _build_reverse_list(_parser.WHITESPACE),
    _parser.CATEGORY_DIGIT: _parser.DIGITS,
    _parser.CATEGORY_NOT_DIGIT: _build_reverse_list(_parser.DIGITS),
    _parser.CATEGORY_WORD: frozenset('abcdefghijklmnopqrstuvwxyz'
                                     'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                     '0123456789_'),
    _parser.CATEGORY_NOT_WORD: _build_reverse_list(frozenset('abcdefghijklmnopqrstuvwxyz'
                                                             'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                                             '0123456789_')),
    _parser.CATEGORY_LINEBREAK: frozenset('\n'),
    _parser.CATEGORY_NOT_LINEBREAK: _build_reverse_list(frozenset('\n')),
    'ANY': [chr(x) for x in range(1, 127) if x != 10]
}

CATEGORIES_NAMES = {
    _parser.CATEGORY_DIGIT: r'\d',
    _parser.CATEGORY_NOT_DIGIT: r'\D',
    _parser.CATEGORY_SPACE: r'\s',
    _parser.CATEGORY_NOT_SPACE: r'\S',
    _parser.CATEGORY_WORD: r'\w',
    _parser.CATEGORY_NOT_WORD: r'\W',
}


def extract_groups(parsed, top=True):
    result = {}
    if top:
        result[0] = parsed
    for token in parsed:
        if not token:
            # Skip empty tokens
            pass
        elif token[0] == _parser.SUBPATTERN:
            # (group, add_flags, del_flags, pattern)
            if token[1][0] is not None:
                result[token[1][0]] = token[1][3]
            result.update(extract_groups(token[1][3], False))
        elif token[0] == _parser.MIN_REPEAT:
            result.update(extract_groups(token[1][2], False))
        elif token[0] == _parser.MAX_REPEAT:
            result.update(extract_groups(token[1][2], False))
        elif token[0] == _parser.BRANCH:
            result.update(extract_groups(token[1][1], False))
        elif token[0] == _parser.IN:
            result.update(extract_groups(token[1], False))
        elif token[0] == _parser.ATOMIC_GROUP:
            result.update(extract_groups(token[1], False))
        elif isinstance(token, _parser.SubPattern):
            result.update(extract_groups(token, False))
    return result


def _gen_combinator(variants, _merge=True):
    if not hasattr(variants, '__iter__'):
        return [variants] if variants is not None else []

    res = []
    need_product = False
    for var in variants:
        if isinstance(var, list):
            sol = _gen_combinator(var, _merge=False)
            res.append(sol)
            need_product = True
        elif var is not None:
            res.append(var)

    if need_product:
        producted = itertools.product(*res)
        if _merge:
            # TODO(buglloc): ??!
            return list(map(_merge_variants, producted))
        return producted
    elif _merge:
        return list(map(_merge_variants, [res]))
    return res


def _merge_variants(variants):
    result = []
    for var in variants:
        if isinstance(var, tuple):
            result.append(_merge_variants(var))
        else:
            result.append(var)
    return ''.join(result)


class Token(object):
    type = None

    def __init__(self, token, parent, regexp):
        self.token = token
        self.childs = None
        self.parent = parent
        self.regexp = regexp
        self._parse()

    def parse(self):
        pass

    def _parse(self):
        pass

    def _parse_childs(self, childs):
        self.childs = parse(childs, self, regexp=self.regexp)

    def _get_group(self, gid):
        return self.regexp.group(gid)

    def _reg_group(self, gid):
        self.regexp.reg_group(gid, self)

    def can_contain(self, char, skip_literal=True):
        raise NotImplementedError('can_contain must be implemented')

    def can_startswith(self, char, strict=False):
        return self.can_contain(char, skip_literal=False)

    def must_contain(self, char):
        raise NotImplementedError('must_contain must be implemented')

    def must_startswith(self, char, strict=False):
        return self.must_contain(char)

    def generate(self, context):
        raise NotImplementedError('generate must be implemented')

    def __str__(self):
        raise NotImplementedError('__str__ must be implemented')


class AnyToken(Token):
    type = _parser.ANY

    def can_contain(self, char, skip_literal=True):
        return char in CATEGORIES['ANY']

    def must_contain(self, char, skip_literal=True):
        # Char may not be present in ANY token
        return False

    def generate(self, context):
        if context.char in CATEGORIES['ANY']:
            return context.char
        return 'a'

    def __str__(self):
        return '.'


class LiteralToken(Token):
    type = _parser.LITERAL

    def _parse(self):
        self.char = chr(self.token[1])

    def can_contain(self, char, skip_literal=True):
        if skip_literal:
            return False
        return self.char == char

    def must_contain(self, char, skip_literal=True):
        return self.char == char

    def generate(self, context):
        return self.char

    def __str__(self):
        return re.escape(self.char)


class NotLiteralToken(Token):
    type = _parser.NOT_LITERAL

    def _parse(self):
        self.char = chr(self.token[1])
        self.gen_char_list = list(_build_reverse_list(frozenset(self.char)))

    def can_contain(self, char, skip_literal=True):
        return self.char != char

    def must_contain(self, char):
        # Any char MAY not be present in NotLiteral, e.g.: "a" not present in "[^b]"
        return False

    def generate(self, context):
        if self.can_contain(context.char):
            return context.char

        return random.choice(self.gen_char_list)

    def __str__(self):
        return '[^{char}]'.format(char=self.char)


class RangeToken(Token):
    type = _parser.RANGE

    def _parse(self):
        self.left_code = self.token[1][0]
        self.right_code = self.token[1][1]
        self.left = chr(self.left_code)
        self.right = chr(self.right_code)

    def can_contain(self, char, skip_literal=True):
        return self.left <= char <= self.right

    def must_contain(self, char, skip_literal=True):
        return self.left == char == self.right

    def generate(self, context):
        if self.can_contain(context.char):
            return context.char

        return chr(random.randint(self.token[1][0], self.token[1][1]))

    def __str__(self):
        return '{left}-{right}'.format(left=self.left, right=self.right)


class CategoryToken(Token):
    type = _parser.CATEGORY

    def _parse(self):
        self.char_list = CATEGORIES.get(self.token[1], [''])

    def can_contain(self, char, skip_literal=True):
        return char in self.char_list

    def must_contain(self, char, skip_literal=True):
        return frozenset([char]) == self.char_list

    def generate(self, context):
        if self.can_contain(context.char):
            return context.char

        for c in self.char_list:
            return c

    def __str__(self):
        return CATEGORIES_NAMES.get(self.token[1], '\\C')


class MinRepeatToken(Token):
    type = _parser.MIN_REPEAT

    def _parse(self):
        self._parse_childs(self.token[1][2])
        self.min = self.token[1][0]
        self.max = self.token[1][1]

    def can_contain(self, char, skip_literal=True):
        if self.max == 0:
            # [a-z]{0}
            return False
        for child in self.childs:
            if child.can_contain(char, skip_literal=skip_literal):
                return True
        return False

    def must_contain(self, char):
        if self.max == 0:
            # [a-z]{0}
            return False
        if self.min == 0:
            # [a-z]*?
            return False
        for child in self.childs:
            if child.must_contain(char):
                return True
        return False

    def can_startswith(self, char, strict=False):
        if self.max == 0:
            # [a-z]{0}
            if self.childs[0].can_startswith(char, strict):
                return False
            return None
        return self.childs[0].can_startswith(char, strict)

    def must_startswith(self, char, strict=False):
        if self.min == 0:
            # [a-z]*?
            return None
        if self.max == 0:
            # [a-z]{0}
            return None
        return self.childs[0].must_startswith(char, strict=strict)

    def generate(self, context):
        res = []
        if self.min == 0:
            # [a-z]*
            res.append('')
        if self.max == 0:
            # [a-z]{0}
            return res

        for child in self.childs:
            res.extend(child.generate(context))

        result = []
        repeat = self.max if self.max <= context.max_repeat else context.max_repeat
        for val in _gen_combinator([res]):
            result.append(val * repeat)
        return result

    def __str__(self):
        childs = ''.join(str(x) for x in self.childs)
        if self.min == self.max:
            return '{childs}{{{count}}}?'.format(childs=childs, count=self.min)
        if self.min == 0 and self.max == 1:
            return '{childs}?'.format(childs=childs)
        if self.min == 0 and self.max == _parser.MAXREPEAT:
            return '{childs}*?'.format(childs=childs)
        if self.min == 1 and self.max == _parser.MAXREPEAT:
            return '{childs}+?'.format(childs=childs)
        return '{childs}{{{min},{max}}}?'.format(childs=childs, min=self.min, max=self.max)


class MaxRepeatToken(Token):
    type = _parser.MAX_REPEAT

    def _parse(self):
        self._parse_childs(self.token[1][2])
        self.min = self.token[1][0]
        self.max = self.token[1][1]

    def can_contain(self, char, skip_literal=True):
        if self.max == 0:
            # [a-z]{0}
            return False
        for child in self.childs:
            if child.can_contain(char, skip_literal=skip_literal):
                return True
        return False

    def must_contain(self, char):
        if self.max == 0:
            # [a-z]{0}
            return False
        if self.min == 0:
            # [a-z]?
            return False
        for child in self.childs:
            if child.must_contain(char):
                return True
        return False

    def can_startswith(self, char, strict=False):
        if self.max == 0:
            # [a-z]{0}
            if self.childs[0].can_startswith(char, strict):
                return False
            return None
        return self.childs[0].can_startswith(char, strict)

    def must_startswith(self, char, strict=False):
        if self.min == 0:
            # [a-z]*
            return None
        if self.max == 0:
            # [a-z]{0}
            return None
        return self.childs[0].must_startswith(char, strict=strict)

    def generate(self, context):
        res = []
        if self.min == 0:
            # [a-z]*
            res.append('')
        if self.max == 0:
            # [a-z]{0}
            return res

        for child in self.childs:
            res.extend(child.generate(context))

        result = []
        repeat = self.max if self.max <= context.max_repeat else context.max_repeat
        for val in _gen_combinator([res]):
            result.append(val * repeat)
        return result

    def __str__(self):
        childs = ''.join(str(x) for x in self.childs)
        if self.min == self.max:
            return '{childs}{{{count}}}'.format(childs=childs, count=self.min)
        if self.min == 0 and self.max == 1:
            return '{childs}?'.format(childs=childs)
        if self.min == 0 and self.max == _parser.MAXREPEAT:
            return '{childs}*'.format(childs=childs)
        if self.min == 1 and self.max == _parser.MAXREPEAT:
            return '{childs}+'.format(childs=childs)
        return '{childs}{{{min},{max}}}'.format(childs=childs, min=self.min, max=self.max)


class BranchToken(Token):
    type = _parser.BRANCH

    def _parse(self):
        self.childs = []
        for token in self.token[1][1]:
            if not token:
                self.childs.append(EmptyToken(token=token, parent=self.parent, regexp=self.regexp))
            elif isinstance(token, _parser.SubPattern):
                self.childs.append(InternalSubpatternToken(token=token, parent=self.parent, regexp=self.regexp))
            else:
                raise RuntimeError('Unexpected token {0} in branch'.format(token))

    def can_contain(self, char, skip_literal=True):
        for child in self.childs:
            if child.can_contain(char, skip_literal=skip_literal):
                return True
        return False

    def must_contain(self, char):
        return all(child.must_contain(char) for child in self.childs)

    def can_startswith(self, char, strict=False):
        return any(x.can_startswith(char, strict) for x in self.childs)

    def must_startswith(self, char, strict=False):
        return all(x.must_startswith(char, strict) for x in self.childs)

    def generate(self, context):
        res = []
        for child in self.childs:
            values = child.generate(context)
            if isinstance(values, list):
                res.extend(child.generate(context))
            else:
                res.append(values)

        return res

    def __str__(self):
        return '(?:{0})'.format('|'.join(str(x) for x in self.childs))


class SubpatternToken(Token):
    type = _parser.SUBPATTERN

    def _parse(self):
        # (group, add_flags, del_flags, pattern)
        self._parse_childs(self.token[1][3])
        self.group = self.token[1][0]
        if self.group is not None:
            self._reg_group(self.group)

    def can_contain(self, char, skip_literal=True):
        for child in self.childs:
            if child.can_contain(char, skip_literal=skip_literal):
                return True
        return False

    def must_contain(self, char):
        for child in self.childs:
            if child.must_contain(char):
                return True
        return False

    def can_startswith(self, char, strict=False):
        if isinstance(self.childs[0], AtToken):
            if len(self.childs) > 1:
                for child in self.childs[1:]:
                    can = child.can_startswith(char, strict)
                    if can is None:
                        continue
                    return can
            return False
        elif not strict and not isinstance(self.childs[0], (SubpatternToken, InternalSubpatternToken)):
            # Not strict regexp w/o ^ can starts with any character
            return char in CATEGORIES['ANY']

        for child in self.childs:
            can = child.can_startswith(char, strict)
            if can is None:
                continue
            return can
        return None

    def must_startswith(self, char, strict=False):
        if isinstance(self.childs[0], AtToken):
            if len(self.childs) > 1:
                for child in self.childs[1:]:
                    must = child.must_startswith(char, strict=True)
                    if must is None:
                        continue
                    return must
            return False
        elif not strict and not isinstance(self.childs[0], (SubpatternToken, InternalSubpatternToken)):
            # Not strict regexp w/o ^ MAY NOT starts with any character
            return False

        for child in self.childs:
            must = child.must_startswith(char, strict=strict)
            if must is None:
                continue
            return must
        return None

    def generate(self, context):
        res = []
        for child in self.childs:
            res.append(child.generate(context))

        return _gen_combinator(res)

    def __str__(self):
        childs = ''.join(str(x) for x in self.childs)
        if self.group is None:
            return '(?:{childs})'.format(childs=childs)
        return '({childs})'.format(childs=childs)


class InternalSubpatternToken(Token):
    type = _parser.SUBPATTERN

    def _parse(self):
        self._parse_childs(self.token)
        self.group = None

    def can_contain(self, char, skip_literal=True):
        for child in self.childs:
            if child.can_contain(char, skip_literal=skip_literal):
                return True
        return False

    def must_contain(self, char):
        for child in self.childs:
            if child.must_contain(char):
                return True
        return False

    def can_startswith(self, char, strict=False):
        if isinstance(self.childs[0], AtToken):
            if len(self.childs) > 1:
                for child in self.childs[1:]:
                    can = child.can_startswith(char, strict)
                    if can is None:
                        continue
                    return can
            return False
        elif not strict and not isinstance(self.childs[0], (SubpatternToken, InternalSubpatternToken)):
            # Not strict regexp w/o ^ can starts with any character
            return char in CATEGORIES['ANY']

        for child in self.childs:
            can = child.can_startswith(char, strict)
            if can is None:
                continue
            return can
        return None

    def must_startswith(self, char, strict=False):
        if isinstance(self.childs[0], AtToken):
            if len(self.childs) > 1:
                for child in self.childs[1:]:
                    must = child.must_startswith(char, strict=True)
                    if must is None:
                        continue
                    return must
            return False
        elif not strict and not isinstance(self.childs[0], (SubpatternToken, InternalSubpatternToken)):
            # Not strict regexp w/o ^ MAY NOT starts with any character
            return False

        for child in self.childs:
            must = child.must_startswith(char, strict=strict)
            if must is None:
                continue
            return must
        return None

    def generate(self, context):
        res = []
        for child in self.childs:
            res.append(child.generate(context))

        return _gen_combinator(res)

    def __str__(self):
        return ''.join(str(x) for x in self.childs)


class AtomicGroupToken(Token):
    type = _parser.ATOMIC_GROUP

    def _parse(self):
        self._parse_childs(self.token[1])

    def can_contain(self, char, skip_literal=True):
        for child in self.childs:
            if child.can_contain(char, skip_literal=skip_literal):
                return True
        return False

    def must_contain(self, char):
        return False

    def can_startswith(self, char, strict=False):
        return any(x.can_startswith(char, strict) for x in self.childs)

    def must_startswith(self, char, strict=False):
        return False

    def generate(self, context):
        res = []
        for child in self.childs:
            res.append(child.generate(context))

        return _gen_combinator(res) + ['']

    def __str__(self):
        childs = ''.join(str(x) for x in self.childs)
        return '(?>{childs})'.format(childs=childs)


class InToken(Token):
    type = _parser.IN

    def _parse(self):
        self.childs = parse(self.token[1], self)

    def can_contain(self, char, skip_literal=True):
        can = False
        negative = False
        for child in self.childs:
            if isinstance(child, NegateToken):
                negative = True
            else:
                can = child.can_contain(char, skip_literal=False)

            if can:
                break
        if can and not negative:
            # a in [a-z]
            return True
        if not can and negative:
            # a in [^b-z]
            return True
        return False

    def must_contain(self, char):
        # Any character MAY not be present in IN
        return False

    def _generate_positive(self, context):
        result = []
        for child in self.childs:
            if isinstance(child, (NegateToken, EmptyToken)):
                pass
            else:
                result.append(child.generate(context=context))
        return result

    def _generate_negative(self, context):
        blacklisted = set()
        # TODO(buglloc): move chars list into the tokens?
        for child in self.childs:
            if isinstance(child, (NegateToken, EmptyToken)):
                pass
            elif isinstance(child, LiteralToken):
                blacklisted.add(child.char)
            elif isinstance(child, RangeToken):
                blacklisted.update(chr(c) for c in range(child.left_code, child.right_code + 1))
            elif isinstance(child, CategoryToken):
                blacklisted.update(child.char_list)
            else:
                LOG.info('Unexpected child "{0!r}"'.format(child))

        for char in _build_reverse_list(set()):
            if char not in blacklisted:
                return char

    def generate(self, context):
        if self.can_contain(context.char, skip_literal=False):
            return context.char

        is_negative = self.childs and isinstance(self.childs[0], NegateToken)
        if is_negative:
            # [^a-z]
            return self._generate_negative(context)
        # [a-z]
        return self._generate_positive(context)

    def __str__(self):
        return '[{childs}]'.format(childs=''.join(str(x) for x in self.childs))


class AtToken(Token):
    type = _parser.AT

    def _parse(self):
        self.begin = self.token[1] == _parser.AT_BEGINNING
        self.end = self.token[1] == _parser.AT_END

    def can_contain(self, char, skip_literal=True):
        return False

    def must_contain(self, char):
        return False

    def generate(self, context):
        if context.anchored:
            if self.begin:
                return '^'
            if self.end:
                return '$'
        return None

    def __str__(self):
        if self.begin:
            return '^'
        if self.end:
            return '$'
        LOG.warn('unexpected AT token: %s', self.token)


class NegateToken(Token):
    type = _parser.NEGATE

    def can_contain(self, char, skip_literal=True):
        return False

    def must_contain(self, char):
        return False

    def can_startswith(self, char, strict=False):
        return None

    def must_startswith(self, char, strict=False):
        return None

    def generate(self, context):
        return None

    def __str__(self):
        return '^'


class GroupRefToken(Token):
    type = _parser.GROUPREF

    def _parse(self):
        self.id = self.token[1]
        self.group = self._get_group(self.id)

    def can_contain(self, char, skip_literal=True):
        return self.group.can_contain(char, skip_literal=skip_literal)

    def must_contain(self, char):
        return self.group.must_contain(char)

    def can_startswith(self, char, strict=False):
        return self.group.can_startswith(char, strict=strict)

    def must_startswith(self, char, strict=False):
        return self.group.must_startswith(char, strict=strict)

    def generate(self, context):
        return self.group.generate(context)

    def __str__(self):
        return '\\\\{0}'.format(self.id)


class AssertToken(Token):
    type = _parser.ASSERT

    def can_contain(self, char, skip_literal=True):
        # TODO(buglloc): Do it!
        return False

    def must_contain(self, char):
        # TODO(buglloc): Do it!
        return False

    def can_startswith(self, char, strict=False):
        return None

    def must_startswith(self, char, strict=False):
        return None


class AssertNotToken(Token):
    type = _parser.ASSERT_NOT

    def can_contain(self, char, skip_literal=True):
        # TODO(buglloc): Do it!
        return False

    def must_contain(self, char):
        # TODO(buglloc): Do it!
        return False

    def can_startswith(self, char, strict=False):
        return None

    def must_startswith(self, char, strict=False):
        return None


class EmptyToken(Token):
    type = None

    def can_contain(self, char, skip_literal=True):
        return False

    def must_contain(self, char):
        # TODO(buglloc): Do it!
        return False

    def can_startswith(self, char, strict=False):
        return None

    def must_startswith(self, char, strict=False):
        return None

    def generate(self, context):
        return ''

    def __str__(self):
        return ''


def parse(sre_obj, parent=None, regexp=None):
    result = []
    for token in sre_obj:
        if not token:
            result.append(EmptyToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.ANY:
            result.append(AnyToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.LITERAL:
            result.append(LiteralToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.NOT_LITERAL:
            result.append(NotLiteralToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.RANGE:
            result.append(RangeToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.CATEGORY:
            result.append(CategoryToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.MIN_REPEAT:
            result.append(MinRepeatToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.MAX_REPEAT:
            result.append(MaxRepeatToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.BRANCH:
            result.append(BranchToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.SUBPATTERN:
            result.append(SubpatternToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.ATOMIC_GROUP:
            result.append(AtomicGroupToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.IN:
            result.append(InToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.NEGATE:
            result.append(NegateToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.AT:
            result.append(AtToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.GROUPREF:
            result.append(GroupRefToken(token=token, parent=parent, regexp=regexp))
        elif token[0] == _parser.ASSERT:
            pass  # TODO(buglloc): Do it!
        elif token[0] == _parser.ASSERT_NOT:
            pass  # TODO(buglloc): Do it!
        else:
            LOG.info('Unexpected token "{0}"'.format(token[0]))

    return result


class GenerationContext(object):
    def __init__(self, char, max_repeat=5, strict=False, anchored=True):
        self.char = char
        self.max_repeat = max_repeat
        self.strict = strict
        self.anchored = anchored


class Regexp(object):
    def __init__(self, source, strict=False, case_sensitive=True, _root=None, _parsed=None):
        """
        Gixy Regexp class, parse and provide helpers to work with it.

        :param str source: regexp, e.g. ^foo$.
        :param bool strict: anchored or not.
        :param bool case_sensitive: case sensitive or not.
        """

        self.source = source
        self.strict = strict
        self.case_sensitive = case_sensitive
        self._root = _root
        self._parsed = _parsed
        self._groups = {}

    def can_startswith(self, char):
        """
        Checks if regex can starts with the specified char.
        Example:
          Regexp('[a-z][0-9]').can_startswith('s') -> True
          Regexp('[a-z][0-9]').can_startswith('0') -> True
          Regexp('^[a-z][0-9]').can_startswith('0') -> False
          Regexp('[a-z][0-9]', strict=True).can_startswith('0') -> False

        :param str char: character to test.
        :return bool: True if regex can starts with the specified char, False otherwise.
        """

        return self.root.can_startswith(
            char=char if self.case_sensitive else char.lower(),
            strict=self.strict
        )

    def can_contain(self, char, skip_literal=True):
        """
        Checks if regex can contain the specified char.
        Example:
          Regexp('[a-z][0-9]').can_contain('s') -> True
          Regexp('[a-z][0-9]').can_contain('0') -> True
          Regexp('[a-z][0-9]').can_contain('/') -> False
          Regexp('[a-z][0-9]/').can_contain('/') -> False
          Regexp('[a-z][0-9]/').can_contain('/', skip_literal=False) -> True

        :param str char: character to test.
        :param bool skip_literal: skip literal tokens.
        :return bool: True if regex can contain the specified char, False otherwise.
        """

        return self.root.can_contain(
            char=char if self.case_sensitive else char.lower(),
            skip_literal=skip_literal
        )

    def must_startswith(self, char):
        """
        Checks if regex MUST starts with the specified char.
        Example:
          Regexp('[a-z][0-9]').must_startswith('s') -> False
          Regexp('s[a-z]').must_startswith('s') -> False
          Regexp('^s[a-z]').must_startswith('s') -> True
          Regexp('s[a-z]', strict=True).must_startswith('s') -> True

        :param str char: character to test.
        :return bool: True if regex must starts with the specified char, False otherwise.
        """

        return self.root.must_startswith(
            char=char if self.case_sensitive else char.lower(),
            strict=self.strict
        )

    def must_contain(self, char):
        """
        Checks if regex MUST contain the specified char.
        Example:
          Regexp('[a-z][0-9]').must_contain('s') -> False
          Regexp('[a-z][0-9]s').must_contain('s') -> True

        :param str char: character to test.
        :return bool: True if regex MUST contain the specified char, False otherwise.
        """

        return self.root.must_contain(
            char=char if self.case_sensitive else char.lower()
        )

    def generate(self, char, anchored=False, max_repeat=5):
        """
        Generate values that match regex.
        Example:
          Regexp('.a?').generate('s') -> ['s', 'sa']
          Regexp('(?:^http|https)://.').generate('s') -> ['http://s', 'https://s']
          Regexp('(?:^http|https)://.').generate('s', anchored=True) -> ['^http://s', 'https://s']


        :param str char: "dangerous" character, generator try to place it wherever possible.
        :param bool anchored: place anchors in generated values.
        :param int max_repeat: maximum count of repeated group (e.g. "a+" provides "aaaaa").
        :return list of str: True if regex can contain the specified char, False otherwise.
        """

        context = GenerationContext(char, anchored=anchored, max_repeat=max_repeat)
        for val in self.root.generate(context=context):
            if anchored and self.strict and not val.startswith('^'):
                yield '^' + val
            else:
                yield val

    def group(self, name):
        """
        Returns group by specified name.

        :param name: name of the group.
        :return Regexp: Regexp object for this group.
        """

        if name in self.groups:
            return self.groups[name]
        return Regexp('')

    def reg_group(self, gid, token):
        self._groups[gid] = token

    def get_group(self, gid):
        return self._groups[gid]

    @cached_property
    def groups(self):
        result = {}
        for name, parsed in extract_groups(self.parsed).items():
            result[name] = Regexp('compiled', _parsed=parsed, strict=True, case_sensitive=self.case_sensitive)
        for name, group in self.parsed.state.groupdict.items():
            result[name] = result[group]
        return result

    @property
    def root(self):
        if self._root:
            return self._root

        self._root = InternalSubpatternToken(self.parsed, parent=None, regexp=self)
        self._groups[0] = self._root
        return self._root

    @property
    def parsed(self):
        # TODO(buglloc): Ugly hack!
        if self._parsed:
            return self._parsed

        try:
            self._parsed = _parser.parse(FIX_NAMED_GROUPS_RE.sub('(?P<\\1>', self.source))
        except _parser.error as e:
            LOG.fatal('Failed to parse regex: %s (%s)', self.source, str(e))
            raise e

        return self._parsed

    def __str__(self):
        return str(self.root)
