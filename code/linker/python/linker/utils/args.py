import builtins
import dataclasses
import types
import typing

T = typing.TypeVar('T')

def parse(x: str, into: type[T]) -> T:
    if into is dict:
        return _parse_dict(x)
    if not dataclasses.is_dataclass(into):
        raise ValueError(f'{into} is not a dataclass')
    fields = typing.get_type_hints(into)
    kw = {}
    for pair in _split(x, ','):
        k, v = pair.split('=', maxsplit=1)
        if k not in fields:
            print(k, fields)
            raise ValueError(f'Unknown field {k} in {into}')
        field_type = _maybe_unpack_optional(fields[k])
        kw[k] = _parse_type(v, field_type)
    return into(**kw)


def _parse_dict(x: str) -> dict:
    fields = {}
    for pair in _split(x, ','):
        k, v = pair.split('=', maxsplit=1)
        field_type_name, field_value = v.split(':')
        field_type = getattr(builtins, field_type_name)
        fields[k] = _parse_type(field_value, field_type)
    return fields


def _split(x: str, on: str) -> list[str]:
    prev = 0
    split_indices = []
    opened_curly = 0
    opened_square = 0
    if f'{on}{on}' in x:
        raise ValueError(f'Double commas in {x}')
    for i, c in enumerate(x):
        if c == on and opened_curly == 0 and opened_square == 0:
            split_indices.append((prev, i))
            prev = i + 1
        elif c == '{':
            opened_curly += 1
        elif c == '}':
            opened_curly -= 1
            if opened_curly < 0:
                raise ValueError(f'Mismatched braces in {x}')
        elif c == '[':
            opened_square += 1
        elif c == ']':
            opened_square -= 1
            if opened_square < 0:
                raise ValueError(f'Mismatched square brackets in {x}')
    if opened_curly != 0 or opened_square != 0:
        raise ValueError(f'Mismatched braces in {x}')
    split_indices.append((prev, len(x)))
    return [x[i:j] for i, j in split_indices if x[i:j]]


def _parse_type(x: str, field_type):
    if _is_literal(field_type):
        # Only support literal strings for now
        if x not in field_type.__args__:
            raise ValueError(f'Invalid literal value {x} for {field_type}')
        return x
    elif (inner := _is_list_type(field_type)) is not None:
        return [_parse_type(y, inner) for y in _split(x, ';')]
    elif _is_dict_type(field_type):
        if not x.startswith('{') or not x.endswith('}'):
            raise ValueError(f'Expected {{...}} for dict {field_type}')
        return parse(x[1:-1], field_type)
    elif dataclasses.is_dataclass(field_type):
        if not x.startswith('{') or not x.endswith('}'):
            raise ValueError(f'Expected {{...}} for dataclass {field_type}')
        return parse(x[1:-1], field_type)
    elif field_type is bool:
        if x == 'True':
            return True
        elif x == 'False':
            return False
        else:
            raise ValueError(f'Invalid bool value {x}')
    else:
        return field_type(x)


def _is_list_type(x) -> type | None:
    o = typing.get_origin(x)
    if o is not None and issubclass(o, list):
        assert len(typing.get_args(x)) == 1
        return typing.get_args(x)[0]
    return None


def _is_dict_type(x):
    o = typing.get_origin(x)
    return issubclass(x, dict) or (o is not None and issubclass(o, dict))


def _is_literal(x):
    o = typing.get_origin(x)
    return o is not None and o is typing.Literal


def _maybe_unpack_optional(x) -> type:
    o = typing.get_origin(x)
    if o in (typing.Union, types.UnionType):
        args = typing.get_args(x)
        if len(args) != 2 or types.NoneType not in args:
            return x
        return list(set(args) - {types.NoneType})[0]
    return x



# @dataclasses.dataclass
# class IndividualLossConfig:
#     name: str
#     weight: float
#     options: dict
# @dataclasses.dataclass
# class LossConfig:
#     losses: list[IndividualLossConfig]

# k = 'losses={name=DiceWithLogitsLoss,weight=0.5,options={}};{name=BinaryFocalWithLogitsLoss,weight=0.5,options={gamma=int:2}}'
# print(parse(k, LossConfig))