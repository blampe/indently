#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys


start_chars = set(['(', '{', '['])
end_chars = set([')', '}', ']'])


class Token(object):

    def __init__(self, value, offset):
        self.value = value
        self.offset = offset

    def __repr__(self):
        return u"%s(%s, %d)" % (
            self.__class__.__name__,
            repr(self.value),
            self.offset,
        )


class String(Token):
    pass


class Comment(Token):
    pass


class Code(Token):
    pass


def parse_code(source_code):

    begin = 0
    offset = 0
    current_line = ''
    string_context = []
    in_string = False

    while offset < len(source_code):
        char = source_code[offset]
        current_line += char
        in_string = bool(string_context)

        if not in_string and char == '#':
            # we entered a comment, skip ahead
            try:
                comment_end = source_code.index('\n', offset)
            except ValueError:
                # the last line is a comment, nothing left to do
                comment_end = len(source_code) - 1

            if current_line[:-1]:
                yield Code(current_line[:-1], begin)

            yield Comment(source_code[offset:comment_end + 1], offset)
            begin = comment_end + 1
            offset = comment_end + 1
            current_line = ""

            continue

        # we want to ignore brackets in strings like "()"
        if in_string and char in ('"', "'") and source_code[offset - 1] != "\\":
            # need to handle escaping
            if char == string_context[-1]:
                string_context.pop()

            if not string_context:
                yield String(current_line, begin)
                begin = offset + 1
                current_line = ''

        elif not in_string and char in ('"', "'"):
            string_context.append(char)

            if current_line[:-1]:
                yield Code(current_line[:-1], begin)
            begin = offset
            current_line = char

        offset += 1

    if in_string:
        yield String(current_line, begin)
    else:
        yield Code(current_line, begin)


def find_outer_brackets(source_code):
    if not any(start_char in source_code for start_char in start_chars):
        return

    seen_brackets = []

    for token in (t for t in parse_code(source_code) if isinstance(t, Code)):
        for idx, char in enumerate(token.value):
            if char in start_chars:
                assert source_code[token.offset + idx] == char, token
                seen_brackets.append(token.offset + idx)

            if char in end_chars:
                start_loc = seen_brackets.pop()
                if not seen_brackets:
                    yield start_loc, token.offset + idx


def horizontal_location(source_code, loc):
    try:
        return loc - (source_code.rindex('\n', 0, loc) + 1)
    except ValueError:
        return loc


def indent_at(source_code, loc):
    spaces = 0

    # move to the begging on the line
    loc = loc - horizontal_location(source_code, loc)

    while source_code[loc].isspace():
        loc += 1
        spaces += 1

    return spaces * ' '


def extract_args(bracket_body):

    in_comprehension = False

    args = []
    current_line = ""

    start_stops = list(find_outer_brackets(' ' + bracket_body[1:-1]))

    def add_arg(arg):
        thin_arg = ''
        for t in parse_code(arg):
            if isinstance(t, Code):
                thin_arg += re.sub('\s+', ' ', t.value)
            else:
                thin_arg += t.value.strip()
        args.append(thin_arg)

    for token in parse_code(bracket_body[1:-1]):
        if isinstance(token, Comment):
            add_arg(token.value)
            continue

        if isinstance(token, String):
            current_line += token.value
            continue

        for idx, char in enumerate(token.value):
            in_bracket = any(
                start <= token.offset + idx < stop
                for start, stop in start_stops
            )

            if bracket_body[token.offset + idx:token.offset + idx + 5] == ' for ':
                in_comprehension = True

            if char in start_chars | end_chars:
                in_comprehension = False

            if not in_bracket and not in_comprehension and char == ',':
                if current_line.strip():
                    add_arg(current_line.strip())
                    current_line = ""
            else:
                current_line += char

    if current_line.strip():
        add_arg(current_line.strip())

    # preserve singular tuples
    if re.search(r',\s*\)$', bracket_body) and len(args) == 1:
        args[-1] = args[-1] + ','

    return args


def format_source_code(source_code, indent=''):
    transforms = []

    # "let me through i'm a doctor!" says dr dre as he pushes through the crowd
    # & kneels beside the sick man. "this man is dying of no rap songs"
    dr_dre = 128169

    # really need to make this work in-place
    for start, stop in find_outer_brackets(source_code):
        old_bracket = source_code[start:stop+1]
        new_bracket = rewrite_bracket(
            old_bracket,
            indent + indent_at(source_code, start),
            len(indent) + horizontal_location(source_code, start),
        )

        # butt_ninja = re.sub('\S', unichr(dr_dre), old_bracket)
        butt_ninja = unichr(dr_dre) * len(old_bracket) # always newline long chains
        dr_dre += 1

        source_code = source_code[:start] + butt_ninja + source_code[stop+1:]
        transforms.append((butt_ninja, new_bracket))

    for butt_ninja, new in transforms:
        source_code = source_code.replace(butt_ninja, new)

    return source_code


def rewrite_bracket(bracket_body, indent, offset):
    args = extract_args(bracket_body)

    # put all of our args on one line to see if it will fit, and move comments
    # below us
    condensed = bracket_body[0]
    condensed += ', '.join(
        # cleanup newlines in our arg
        format_source_code(arg) for arg in args if not arg.startswith('#'),
    )
    condensed += bracket_body[-1]

    multilined = bracket_body[0]

    # edge case handling for () at the end of a line
    if args:
        multilined += '\n'

    for arg in args:
        multilined += indent + '    '
        multilined += format_source_code(arg, indent + '    ')

        line_end = ','

        # "**kwargs," is a syntax error, as is "*args," if not followed by kwargs.
        if arg.startswith('*') and arg == args[-1]:
            line_end = ''

        # comments don't get mutated, and
        if arg.startswith('#'):
            line_end = ''

        # "(foo)" can't be expanded to "(foo,)" because that now makes it a
        # tuple which has different logical implications.
        if len(args) == 1:
            line_end = ''

        multilined += line_end
        multilined += '\n'

    # edge case handling for () at the end of a line
    if args:
        multilined += indent

    multilined += bracket_body[-1]

    # if you multi-lined your args and they look good, we won't touch them,
    # even if they can fit within 80 characters.
    if offset + len(condensed) < 80 and bracket_body != multilined:
        if any(a.startswith('#') for a in args):
            condensed += '\n' + indent
        return condensed + ('\n' + indent).join(
            a for a in args if a.startswith('#'),
        )

    return multilined


if __name__ == '__main__':
    print format_source_code(sys.stdin.read())
