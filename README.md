Indently
========

A tool to apply consistent indentation and formatting to your Python code.

This is still **very much** a work in progress. In addition to being full of
hacks, the source might look weird because the tool is used to format itself.


Example
-------

A long line (over 80 characters) like this

```python
models.Membership.objects.filter(account__in=owner, active=True, created__lte='2014-01-01').select_related('user').distinct().order_by('id')
```

will automatically be indented to look like this:

```python
models.Membership.objects.filter(
    account__in=owner,
    active=True,
    created__lte='2014-01-01',
).select_related(
    'user'
).distinct().order_by(
    'id'
)
```


Frequently Asked Questions
--------------------------

### This doesn't look very PEP-8, question mark?

Actually, it is! I prefer this "waterfall" indentation (for lack of a better
term) over PEP-8's [alignment
style](http://legacy.python.org/dev/peps/pep-0008/#indentation) for a few
reasons:

 * Readability. One arg per line keeps lines short and easier to scan.
   Flush-left formatting is more reminiscent of reading a book.

 * Malleability. I can add or remove lines without needing to significantly
   alter surrounding code. The dangling paren makes it easier to chain function
   calls.

 * Blame. I can quickly see who added a particular argument if I want to ask
   them something about it.


Usage
-----

```shell
$ cat code.py | indently
```

