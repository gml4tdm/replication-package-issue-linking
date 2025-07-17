import re


UPPER_SNAKE_CASE = re.compile(r'\b([A-Z][A-Z0-9]*_[A-Z0-9]+(_[A-Z0-9]+)*\b)')
LOWER_SNAKE_CASE = re.compile(r'\b([a-z][a-z0-9]*_[a-z0-9]+(_[a-z0-9]+)*\b)')
DOTTED_PATH = re.compile(
    r'\b([a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*\.[a-z]*(([A-Z0-9][a-z0-9]*)|(\d))+[A-Z]*\b)'
)
CAMEL_CASE = re.compile(r'\b(?<!\.)([a-z]*(([A-Z0-9][a-z0-9]*)|(\d))+[A-Z]*\b)')


def count_identifiers(x: str) -> int:

    identifiers = []
    identifiers.extend(set(_findall(UPPER_SNAKE_CASE, x)))
    identifiers.extend(set(_findall(LOWER_SNAKE_CASE, x)))
    identifiers.extend(set(_findall(DOTTED_PATH, x)))
    identifiers.extend(
        set(
            _filter_camel_case(
                _findall(CAMEL_CASE, x),
            )
        )
    )

    return len(set(identifiers))


def split_sub_tokens(y: str) -> str:
    to_expand = set(
        _filter_camel_case(
            _findall(CAMEL_CASE, y),
        )
    )
    for token in to_expand:
        x = token
        result = []
        if x[0].islower():
            i = 1
            while i < len(x) and x[i].islower():
                i += 1
            first, x = x[:i], x[i:]
            result.append(first)
        result.extend(re.split(r'(?=[A-Z][a-z])', x))
        repl = ' '.join(result)
        y = y.replace(token, repl)
    return y



def _findall(pattern, text):
    return [
        x if isinstance(x, str) else x[0]
        for x in re.findall(pattern, text)
    ]


def _filter_camel_case(x: list[str]) -> list[str]:
    return [y for y in x if _is_valid_camel_case(y)]


def _is_valid_camel_case(x: str) -> bool:
    atoms = [y for y in re.split(r'([A-Z]+|[0-9]+)', x) if y]
    refined_atoms = []
    for atom, is_last in zip(atoms, [False]*(len(atoms) - 1) + [True]):
        if atom.isupper() and len(atom) > 1:
            if is_last:
                refined_atoms.append(atom)
            else:
                first = atom[:-1]
                last = atom[-1]
                refined_atoms.append(first)
                refined_atoms.append(last)
        else:
            refined_atoms.append(atom)
    words = []
    current = None
    for atom in refined_atoms:
        if atom.isupper():
            if current is not None:
                words.append(current)
                current = None
            if len(atom) > 1:
                words.append(atom)
            else:
                current = atom
        elif atom.isdigit():
            if current is not None:
                words.append(current)
                current = None
            words.append(atom)
        elif current is not None:
            words.append(current + atom)
            current = None
        else:
            words.append(atom)
    if current is not None:
        words.append(current)
    return len(words) > 1
