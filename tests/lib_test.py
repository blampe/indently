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
            something=True
        ).filter(
            something_else_really_cray_cray_cray_cray_crazy=True
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

    assert expected == result


def test_find_outer_brackets_with_comment_character_in_list_comprehension():
    source_code = "(f('x') for x in xs if not x.z('#'))"

    start, stop = lib.find_outer_brackets(source_code).next()

    assert (start, stop) == (0, len(source_code) - 1)


def test_format_source_code_preserves_singular_tuples():
    source_code = """
                                                                        foo=('bar',)
    """
    expected = """
                                                                        foo=(
                                                                            'bar',
                                                                        )
    """

    result = lib.format_source_code(source_code)

    assert expected == result

def test_format_source_code_preserves_singular_newlined_tuples():
    source_code = """
    foo=(
        'bar',
    )
    """
    expected = """
    foo=('bar',)
    """

    result = lib.format_source_code(source_code)

    assert expected == result

def test_format_source_code_doesnt_add_too_many_commas():
    source_code = """
                                                                f(a=1, b=2, c=3,)
    """

    expected = """
                                                                f(
                                                                    a=1,
                                                                    b=2,
                                                                    c=3,
                                                                )
    """
    result = lib.format_source_code(source_code)

    assert expected == result


def test_format_source_code_doesnt_create_singular_suples():
    source_code = """
    if (first_condition or second_condition) and (third_condition or fourth_condition):
    """
    expected = """
    if (first_condition or second_condition) and (
        third_condition or fourth_condition
    ):
    """

    result = lib.format_source_code(source_code)

    assert expected == result


def test_format_source_code_doesnt_break_up_implicit_tuple_in_comprehensions():
    source_code = """
        (sum(x, y, z) for x, y, z in [(1, 2, 3), (4, 5, 6)] if (True and True and ' for '))
    """
    expected = """
        (
            sum(x, y, z) for x, y, z in [(1, 2, 3), (4, 5, 6)] if (
                True and True and ' for '
            )
        )
    """
    # i might prefer something like this
    #(
        #sum(x, y, z) for (
            #x, y, z,
        #) in [(1, 2, 3), (4, 5, 6)])
    #)

    result = lib.format_source_code(source_code)

    assert expected == result


def test_format_source_code_with_sqlalchemy_query():
    source_code = """
    models.Membership.objects.filter(account__in=owner, active=True, created__lte='2014-01-01').select_related('user').distinct().order_by('id')
    """

    expected = """
    models.Membership.objects.filter(
        account__in=owner,
        active=True,
        created__lte='2014-01-01',
    ).select_related(
        'user'
    ).distinct().order_by(
        'id'
    )
    """
    result = lib.format_source_code(source_code)

    assert expected == result


def test_format_source_code_doesnt_add_comma_after_star_args():
    source_code = """
                                                                          (*args)
    """
    expected = """
                                                                          (
                                                                              *args
                                                                          )
    """
    result = lib.format_source_code(source_code)

    assert expected == result


def test_format_source_code_repairs_dangling_operators():
    source_code = "('a' +\n'b')"
    expected = "('a' + 'b')"

    result = lib.format_source_code(source_code)

    assert expected == result


def test_format_source_code_calculates_line_limit_correctly():
    source_code = """
        foo = f(
            aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,
            bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb,
            ccccccccccccccccccccccccccccccccccc,
            ddddddddddddddddddddddddddddddddddd,
            e=(ffffffffffffffffffffffffffffffff, gggggggggggggggggggggggggggggggg),
        )
    """
    expected = """
        foo = f(
            aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,
            bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb,
            ccccccccccccccccccccccccccccccccccc,
            ddddddddddddddddddddddddddddddddddd,
            e=(
                ffffffffffffffffffffffffffffffff,
                gggggggggggggggggggggggggggggggg,
            ),
        )
    """
    result = lib.format_source_code(lib.format_source_code(source_code))

    assert expected == result


def test_format_source_code_handles_newlined_args():
    source_code = """
        id_to_balance_map = dict((id, currency.ZERO)
                                for id in payment_account_ids)
    """
    expected = """
        id_to_balance_map = dict(
            (id, currency.ZERO) for id in payment_account_ids
        )
    """
    result = lib.format_source_code(lib.format_source_code(source_code))

    assert expected == result


def test_format_source_code_can_handle_a_string_within_a_string():
    source_code = """
        def foo(self):
            this_should_be_ignored = "(not ' real)"

        def really_long_function_name_that_will_need_to_be_shortened_aaaaaaaaaaaaaaaaaaaaaaaaaa(self):
            pass
    """
    expected = """
        def foo(self):
            this_should_be_ignored = "(not ' real)"

        def really_long_function_name_that_will_need_to_be_shortened_aaaaaaaaaaaaaaaaaaaaaaaaaa(
            self
        ):
            pass
    """
    result = lib.format_source_code(source_code)

    assert expected == result
