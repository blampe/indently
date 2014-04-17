#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re


start_chars = set(['(', '{', '['])
end_chars = set([')', '}', ']'])


def find_outer_brackets(source_code):
    if not any(start_char in source_code for start_char in start_chars):
        return

    seen_brackets = []
    string_context = []

    loc = 0
    in_string = False

    while loc < len(source_code):
        char = source_code[loc]

        if not in_string and char == '#':
            # we entered a comment, skip ahead
            try:
                loc = source_code.index('\n', loc)
                continue
            except ValueError:
                # the last line is a comment, nothing left to do
                break

        # we want to ignore brackets in strings like "()"
        if in_string and char in ('"', "'"):
            # need to handle escaping
            if char == string_context[-1]:
                string_context.pop()
            in_string = bool(string_context)
        elif not in_string and char in ('"', "'"):
            string_context.append(char)
            in_string = True

        if not in_string and char in start_chars:
            seen_brackets.append(loc)

        if not in_string and char in end_chars:
            start_loc = seen_brackets.pop()
            if not seen_brackets:
                yield start_loc, loc

        loc += 1


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

    loc = 1
    in_string = False
    in_comprehension = False

    args = []
    current_line = ""
    string_context = []

    start_stops = list(find_outer_brackets(' ' + bracket_body[1:-1]))

    while loc < len(bracket_body) - 1:
        char = bracket_body[loc]

        if not in_string and char == '#':
            # include the comment but skip ahead to the next portion of our line
            new_loc = bracket_body.index('\n', loc)
            args.append(bracket_body[loc:new_loc].strip())
            loc = new_loc
            continue

        # we want to ignore brackets in strings like "()"
        if in_string and char in ('"', "'"):
            # need to handle escaping
            if char == string_context[-1]:
                string_context.pop()
            in_string = bool(string_context)
        elif not in_string and char in ('"', "'"):
            string_context.append(char)
            in_string = True

        in_bracket = any(start <= loc <= stop for start, stop in start_stops)

        if char in start_chars | end_chars:
            in_comprehension = False

        if not in_string and bracket_body[loc:loc+5] == ' for ':
            in_comprehension = True

        if not in_string and not in_bracket and not in_comprehension and char == ',':
            if current_line.strip():
                args.append(current_line.strip())
                current_line = ""
        else:
            current_line += char

        loc += 1

    if current_line.strip():
        args.append(current_line.strip())

    # preserve singular tuples
    if bracket_body[-2:] == ',)' and len(args) == 1: # regex match?
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
            horizontal_location(source_code, start),
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
        format_source_code(re.sub('\s+', ' ', arg).strip()) for arg in args if not arg.startswith('#'),
    )
    condensed += bracket_body[-1]

    if offset + len(condensed) < 80:
        if any(a.startswith('#') for a in args):
            condensed += '\n' + indent
        return condensed + ('\n' + indent).join(
            a for a in args if a.startswith('#'),
        )

    result = bracket_body[0]

    # edge case handling for () at the end of a line
    if args:
        result += '\n'

    for arg in args:
        result += indent + '    '
        result += format_source_code(arg, indent + '    ')

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

        result += line_end
        result += '\n'

    # edge case handling for () at the end of a line
    if args:
        result += indent

    result += bracket_body[-1]

    return result
