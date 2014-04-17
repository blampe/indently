#!/usr/bin/env python
# -*- coding: utf-8 -*-
from indently import lib


def test_format_source_code_with_complicated_source():
    source_code = """
        well = foo(100, 2.3, True, this_is_a_really_long_argsdajsasjhdalksdjhalsdjhalskjdhalsjhlasa=1,
            b=2,e=4, # helo
            # this is another comment
            c={
                '1': 3  # this is a comment, {}
            },
            d=[
                _ for _ in range(10),],

            g=another_function(102,                     arg=b),
                    h="something, something else",
            **kwargs
                        ).filter(         something=True
    ).filter(something_else_really_cray_cray_cray_cray_crazy=True).all()

        this_should_be_condensed = bar(
                a=1, # but this comment should be saved
    c=3, d=5,
        b=2, # and this one too
                                )

        def foo(self):
            \"\"\"(ignored docstring)\"\"\"
            this_should_be_ignored = "(not real)"

        def bar(same, signature):
            pass

        def really_long_function_name_that_will_need_to_be_shortened_aaaaaaaaaaaaaaaaaaaaaaaaaa(same, signature):
            pass
    """
    # this_should_be_ignored = "(not \"' real)"



    expected = """
        well = foo(
            100,
            2.3,
            True,
            this_is_a_really_long_argsdajsasjhdalksdjhalsdjhalskjdhalsjhlasa=1,
            b=2,
            e=4,
            # helo
            # this is another comment
            # this is a comment, {}
            c={'1': 3},
            d=[_ for _ in range(10)],
            g=another_function(102, arg=b),
            h="something, something else",
            **kwargs
        ).filter(
            something=True,
        ).filter(
            something_else_really_cray_cray_cray_cray_crazy=True,
        ).all()

        this_should_be_condensed = bar(a=1, c=3, d=5, b=2)
        # but this comment should be saved
        # and this one too

        def foo(self):
            \"\"\"(ignored docstring)\"\"\"
            this_should_be_ignored = "(not real)"

        def bar(same, signature):
            pass

        def really_long_function_name_that_will_need_to_be_shortened_aaaaaaaaaaaaaaaaaaaaaaaaaa(
            same,
            signature,
        ):
            pass
    """

    # call it twice to clean up long and straggling long lines
    result = lib.format_source_code(lib.format_source_code(source_code))

    assert result == expected

def test_format_source_code_with_list_comprehension():
    source_code = "condensed = bracket_body[0] + ', '.join(format_source_code(arg) for arg in args if not arg.startswith('#')) + bracket_body[-1]"
    expected = """condensed = bracket_body[0] + ', '.join(
    format_source_code(arg) for arg in args if not arg.startswith('#'),
) + bracket_body[
    -1,
]"""

    result = lib.format_source_code(source_code)

    assert result == expected

def test_outer_brackets_with_list_comprehension():
    source_code = "(f('x') for x in xs if not x.z('#'))"

    start, stop = lib.find_outer_brackets(source_code).next()

    assert (start, stop) == (0, len(source_code) - 1)
