#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import ast
import sys

import indently.lib


def parse_args(args=None):
    args = args or sys.argv[1:]

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-l', '--line-length',
        default=79,
        help="Maxinum number of characters per line.",
    )

    parser.add_argument(
        '-i', '--in-place',
        action='store_true',
        help="Rewrite input files. Incompatible with stdin.",
    )

    parser.add_argument(
        '--no-validate',
        action='store_true',
        help="Do not confirm input or output to be valid Python.",
    )

    parser.add_argument(
        'source',
        type=argparse.FileType(),
        nargs='*',
        help="Path to a Python source file, or '-' to read from stdin."
    )

    return parser.parse_args(args)


def rewrite_file(f, args):
    original_source = f.read()

    # Make sure we have valid python
    if not args.no_validate:
        ast.parse(original_source)

    new_source = indently.lib.format_source_code(original_source)

    # Make sure we *still* have valid python
    if not args.no_validate:
        ast.parse(new_source)

    if not args.in_place or f.fileno() == sys.stdin.fileno():
        print new_source
        return

    f.close()

    with open(f.name, 'w') as ff:
        ff.write(new_source)


def main():
    args = parse_args()

    for source in args.source:
        rewrite_file(source, args)


if __name__ == '__main__':
    main()
