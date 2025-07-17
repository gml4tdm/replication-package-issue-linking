# Identifier and File Name Identification in Text


## Base Regexes

The following were the basic regexes we used (Python regex syntax):

```python
import re


UPPER_SNAKE_CASE = re.compile(r'\b([A-Z][A-Z0-9]*_[A-Z0-9]+(_[A-Z0-9]+)*\b)')
LOWER_SNAKE_CASE = re.compile(r'\b([a-z][a-z0-9]*_[a-z0-9]+(_[a-z0-9]+)*\b)')
DOTTED_PATH = re.compile(
    r'\b([a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*\.[a-z]*(([A-Z0-9][a-z0-9]*)|(\d))+[A-Z]*\b)'
)
CAMEL_CASE = re.compile(r'\b(?<!\.)([a-z]*(([A-Z0-9][a-z0-9]*)|(\d))+[A-Z]*\b)')

```

We do not explicitly have a regex for file names;
We assume that the file name matches one of the regexes
listed above.

## Extra Validation for CamelCase

For all strings maching the `CAMEL_CASE` pattern, we also performed a post-hoc check to filter out false positives.

First, we split the string up into its constituent parts. Some examples:

- `myVariableName` -> `['my', 'Variable', 'Name']`
- `MyClassName` -> `['My', 'Class', 'Name']`
- `HTTPServer` -> `['HTTP', 'Server']`
- `HttpServer` -> `['Http', 'Server']`

We then make sure the list contains at least two elements. This is because the regex also matches some other strings,
like full upper case words (e.g. the abbreviation HTTP),
which we do not want to consider as valid CamelCase strings.
