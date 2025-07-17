##############################################################################
##############################################################################
# Imports
##############################################################################

from __future__ import annotations

import dataclasses
import re
import typing
import warnings


##############################################################################
##############################################################################
# AST
##############################################################################

@dataclasses.dataclass(frozen=True, slots=True)
class Raw:
    content: str

    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return self.content


@dataclasses.dataclass(frozen=True, slots=True)
class Heading:
    text: FormattedText
    level: int

    def visit(self, visitor):
        return visitor(
            Heading(
                text=self.text.visit(visitor),
                level=self.level
            )
        )
    def reconstruct(self):
        return f'h{self.level}. {self.text.reconstruct()}'

@dataclasses.dataclass(frozen=True, slots=True)
class Strong:
    content: FormattedText

    def visit(self, visitor):
        return visitor(Strong(content=self.content.visit(visitor)))

    def reconstruct(self):
        return f'*{self.content.reconstruct()}*'

@dataclasses.dataclass(frozen=True, slots=True)
class Emphasis:
    content: FormattedText

    def visit(self, visitor):
        return visitor(Emphasis(content=self.content.visit(visitor)))

    def reconstruct(self):
        return f'_{self.content.reconstruct()}_'

@dataclasses.dataclass(frozen=True, slots=True)
class Citation:
    content: FormattedText

    def visit(self, visitor):
        return visitor(Citation(content=self.content.visit(visitor)))

    def reconstruct(self):
        return f'??{self.content.reconstruct()}??'

@dataclasses.dataclass(frozen=True, slots=True)
class Deleted:
    content: FormattedText

    def visit(self, visitor):
        return visitor(Deleted(content=self.content.visit(visitor)))

    def reconstruct(self):
        return f'-{self.content.reconstruct()}-'

@dataclasses.dataclass(frozen=True, slots=True)
class Inserted:
    content: FormattedText

    def visit(self, visitor):
        return visitor(Inserted(content=self.content.visit(visitor)))

    def reconstruct(self):
        return f'+{self.content.reconstruct()}+'

@dataclasses.dataclass(frozen=True, slots=True)
class SuperScript:
    content: FormattedText

    def visit(self, visitor):
        return visitor(SuperScript(content=self.content.visit(visitor)))

    def reconstruct(self):
        return f'^{self.content.reconstruct()}^'

@dataclasses.dataclass(frozen=True, slots=True)
class SubScript:
    content: FormattedText

    def visit(self, visitor):
        return visitor(SubScript(content=self.content.visit(visitor)))

    def reconstruct(self):
        return f'~{self.content.reconstruct()}~'

@dataclasses.dataclass(frozen=True, slots=True)
class Monospaced:
    content: FormattedText

    def visit(self, visitor):
        return visitor(Monospaced(content=self.content.visit(visitor)))

    def reconstruct(self):
        return f'{{{{{self.content.reconstruct()}}}}}'

@dataclasses.dataclass(frozen=True, slots=True)
class BlockQuote:
    content: FormattedText

    def visit(self, visitor):
        return visitor(BlockQuote(content=self.content.visit(visitor)))

    def reconstruct(self):
        return f'bq. {self.content.reconstruct()}'

@dataclasses.dataclass(frozen=True, slots=True)
class Quote:
    content: FormattedText
    
    def visit(self, visitor):
        return visitor(Quote(content=self.content.visit(visitor)))

    def reconstruct(self):
        return _reconstruct_block('quote', None, self.content.reconstruct())

@dataclasses.dataclass(frozen=True, slots=True)
class HorizontalRule:
    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return '----'

@dataclasses.dataclass(frozen=True, slots=True)
class LongDash:
    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return '---'

@dataclasses.dataclass(frozen=True, slots=True)
class ShortDash:
    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return '--'

@dataclasses.dataclass(frozen=True, slots=True)
class LineBreak:
    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return '\\\\'

@dataclasses.dataclass(frozen=True, slots=True)
class ColorBlock:
    color: str
    content: FormattedText
    
    def visit(self, visitor):
        return visitor(
            ColorBlock(
                color=self.color,
                content=self.content.visit(visitor)
            )
        )

    def reconstruct(self):
        return _reconstruct_block('color', self.color, self.content.reconstruct())


@dataclasses.dataclass(frozen=True, slots=True)
class NoFormatBlock:
    content: str
    options: dict[str, str]

    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return _reconstruct_block('noformat',
                                  _reconstruct_frame_options(self.options),
                                  self.content)


@dataclasses.dataclass(frozen=True, slots=True)
class PanelBlock:
    content: FormattedText
    options: dict[str, str]

    def visit(self, visitor):
        return visitor(
            PanelBlock(
                options=self.options,
                content=self.content.visit(visitor)
            )
        )

    def reconstruct(self):
        return _reconstruct_block('panel',
                                  _reconstruct_frame_options(self.options),
                                  self.content.reconstruct())


@dataclasses.dataclass(frozen=True, slots=True)
class CodeBlock:
    content: str
    language: str | None
    options: dict[str, str]

    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return _reconstruct_block('code',
                                  _reconstruct_frame_options(self.options),
                                  self.content,
                                  positional=self.language)


@dataclasses.dataclass(frozen=True, slots=True)
class Table:
    header: list[FormattedText] | None
    rows: list[list[FormattedText]]

    def visit(self, visitor):
        h = None
        if self.header is not None:
            h = [x.visit(visitor) for x in self.header]
        return visitor(
            Table(
                header=h,
                rows=[
                    [x.visit(visitor) for x in y]
                    for y in self.rows
                ]
            )
        )

    def reconstruct(self):
        if self.header is not None:
            header = self._reconstruct_row(self.header, '||') + '\n'
        else:
            header = ''
        body = '\n'.join(self._reconstruct_row(row, '|') for row in self.rows)
        return f'{header}{body}'

    def _reconstruct_row(self, row: list[FormattedText], sep: str) -> str:
        base = sep.join(r.reconstruct() for r in row)
        return f'{sep}{base}{sep}'


@dataclasses.dataclass(frozen=True, slots=True)
class Emoticon:
    code: str

    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return self.code


@dataclasses.dataclass(frozen=True, slots=True)
class AnchorLink:
    url: str

    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return f'[#{self.url}]'

@dataclasses.dataclass(frozen=True, slots=True)
class AttachmentLink:
    name: str

    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return f'[^{self.name}]'

@dataclasses.dataclass(frozen=True, slots=True)
class Link:
    name: str | None
    url: str

    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        if self.name is not None:
            return f'[{self.name}|{self.url}]'
        return f'[{self.url}]'

@dataclasses.dataclass(frozen=True, slots=True)
class MailToLink:
    address: str

    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return f'[mailto:{self.address}]'

@dataclasses.dataclass(frozen=True, slots=True)
class DownloadLink:
    url: str

    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return f'[{self.url}]'

@dataclasses.dataclass(frozen=True, slots=True)
class Anchor:
    page: str
    name: str

    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return f'{{{self.page}:{self.name}}}'

@dataclasses.dataclass(frozen=True, slots=True)
class UserLink:
    user_name: str

    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        return f'[~{self.user_name}]'

@dataclasses.dataclass(frozen=True, slots=True)
class Embeddable:
    space_key: str | None
    page: str | None
    url: str
    thumbnail: bool
    options: dict[str, str]

    def visit(self, visitor):
        return visitor(self)

    def reconstruct(self):
        if self.space_key is not None:
            assert self.page is not None
            loc = f'{self.space_key}:{self.page}^{self.url}'
        else:
            loc = f'{self.url}'
        args = []
        if self.thumbnail:
            args.append('thumbnail')
        args.extend(f'{k}={v}' for k, v in self.options.items())
        if not args:
            return f'!{loc}!'
        return f'!{loc}|{",".join(args)}!'

@dataclasses.dataclass(frozen=True, slots=True)
class FormattedText:
    content: list[FormattedFragment]

    def visit(self, visitor):
        return visitor(
            FormattedText(
                content=[x.visit(visitor) for x in self.content]
            )
        )

    def reconstruct(self):
        return ''.join(x.reconstruct() for x in self.content)

@dataclasses.dataclass(frozen=True, slots=True)
class Listing:
    depths: list[str]
    items: list[FormattedText]

    def visit(self, visitor):
        return visitor(
            Listing(
                depths=self.depths,
                items=[x.visit(visitor) for x in self.items]
            )
        )

    def reconstruct(self):
        lines = []
        for depth, item in zip(self.depths, self.items):
            lines.append(
                self._reconstruct_prefix(depth) + ' ' + item.reconstruct()
            )
        return ''.join(lines)

    def _reconstruct_prefix(self, depth: str) -> str:
        return depth


FormattedFragment = typing.Union[
    Heading,
    Strong, Emphasis, Citation, Deleted,
    Inserted, SuperScript, SubScript, Monospaced,

    AnchorLink, AttachmentLink, Link, MailToLink,
    DownloadLink, Anchor, UserLink,
    Embeddable,
    BlockQuote, Quote, ColorBlock,

    HorizontalRule, LongDash, ShortDash, LineBreak,

    NoFormatBlock, PanelBlock, CodeBlock,

    Table, Listing,

    Emoticon,

    Raw
]

def _reconstruct_block(tag: str,
                       options: str | None,
                       content: str, *,
                       positional=None) -> str:
    if options is not None and positional is not None:
        open_tag = f'{tag}:{positional},{options}'
    elif options is not None:
        open_tag = f'{tag}:{options}'
    elif positional is not None:
        open_tag = f'{tag}:{positional}'
    else:
        open_tag = tag
    return f'{{{open_tag}}}{content}{{{tag}}}'


def _reconstruct_frame_options(options: dict[str, str]) -> str | None:
    if not options:
        return None
    return '|'.join(f'{k}={v}' for k, v in options.items())


##############################################################################
##############################################################################
# Stream
##############################################################################


class Stream:
    def __init__(self, text: str):
        self._text = text
        self._pos = 0
        self._first_col = True

    def __bool__(self) -> bool:
        return self._pos < len(self._text)

    def __repr__(self):
        return 'Stream<{}...>'.format(self._text[self._pos:self._pos+10])

    def consume(self) -> str:
        out = self._text[self._pos]
        self._pos += 1
        self._first_col = out == '\n'
        return out

    def scan(self,
             pattern, *,
             first_col=False,
             trim_start=0,
             trim_end=0) -> str | None:
        if first_col and not self._first_col:
            return None
        pattern = re.compile(pattern)
        m = pattern.match(self._text[self._pos:])
        if m:
            self._pos += len(m.group())
            self._first_col = m.group()[-1] == '\n'
            end = len(m.group()) - trim_end
            return m.group()[trim_start:end]
        return None

    def scan_substream(self,
                       pattern, *,
                       first_col=False,
                       trim_start=0,
                       trim_end=0) -> Stream | None:
        first = self._first_col
        out = self.scan(pattern,
                        first_col=first_col,
                        trim_start=trim_start,
                        trim_end=trim_end)
        if out is not None:
            s = Stream(out)
            s._first_col = first
            return s


##############################################################################
##############################################################################
# Parsing
##############################################################################


def parse_jira(text: str) -> FormattedText:
    return _parse_formatted_text(Stream(text))


def _parse_formatted_text(stream: Stream) -> FormattedText:
    blocks = []
    functions = [
        _maybe_parse_heading,
        # List before effects, so that the list is not parsed as strong
        _maybe_parse_list,
        _maybe_parse_effect,
        _maybe_parse_block_quote,
        _maybe_parse_no_format,
        _maybe_parse_text_break,
        _maybe_parse_color,
        _maybe_parse_emoticon,
        _maybe_parse_attachment,
        _maybe_parse_panel,
        _maybe_parse_code,
        _maybe_parse_table,
        # Must become after blocks.
        # Otherwise, {code:xml} (or similar) is parsed as anchor.
        _maybe_parse_link,
    ]
    while stream:
        for func in functions:
            if (r := func(stream)) is not None:
                blocks.append(r)
                break
        else:
            if blocks and isinstance(blocks[-1], Raw):
                blocks[-1] = Raw(blocks[-1].content + stream.consume())
            else:
                blocks.append(Raw(stream.consume()))

    return FormattedText(content=blocks)


def _maybe_parse_heading(stream: Stream) -> FormattedFragment | None:
    if (h := stream.scan(r'h[1-6]\. ', first_col=True)) is not None:
        level = int(h[1])
        text = stream.scan_substream(r'[^\n]*\n?')
        return Heading(text=_parse_formatted_text(text), level=level)


def _maybe_parse_effect(stream: Stream) -> FormattedFragment | None:
    template = r'{start}(?!\s).*?(?<!\\|\s){stop}'
    warnings.warn(
        'Parsing of Emphasis (_) and Deleted (-) is disabled for '
        'Jira issues to avoid parsing ambiguity caused by filenames.',
    )
    delimiters = [
        (r'\*', r'\*', Strong),
        #('_', '_', Emphasis),
        (r'\?\?', r'\?\?', Citation),
        #('-', '-', Deleted),
        (r'\+', r'\+', Inserted),
        (r'\^', r'\^', SuperScript),
        ('~', '~', SubScript),
        (r'\{\{', r'\}\}', Monospaced),
        (r'\{quote\}', r'\{quote\}', Quote),
    ]
    for delim in delimiters:
        pattern = template.format(start=delim[0], stop=delim[1])
        x = len(delim[0].replace('\\', ''))
        y = len(delim[1].replace('\\', ''))
        if (m := stream.scan_substream(pattern, trim_start=x, trim_end=y)) is not None:
            return delim[2](content=_parse_formatted_text(m))


def _maybe_parse_block_quote(stream: Stream) -> FormattedFragment | None:
    if (_b := stream.scan(r'bq\. ', first_col=True)) is not None:
        text = stream.scan_substream(r'[^\n]*')
        return BlockQuote(_parse_formatted_text(text))


def _maybe_parse_text_break(stream: Stream) -> FormattedFragment | None:
    if stream.scan(r'----\s*\n') is not None:
        return HorizontalRule()

    if stream.scan(r'--- ') is not None:
        return LongDash()

    if stream.scan(r'-- ') is not None:
        return ShortDash()

    if stream.scan(r'\\\\') is not None:
        return LineBreak()


def _maybe_parse_color(stream: Stream) -> FormattedFragment | None:
    pattern = r'{color:.*?}(.|\n)*(?<!\\){color}'
    if (m := stream.scan_substream(pattern, trim_end=len('{color}'))) is not None:
        c = m.scan(r'{color:.*?}')
        assert c is not None
        return ColorBlock(
            color=c.removeprefix('{color:').removesuffix('}'),
            content=_parse_formatted_text(m)
        )

def _maybe_parse_emoticon(stream: Stream) -> FormattedFragment | None:
    emoticons = [
        ':)', ':(', ':P', ':D', ';)', '(y)', '(n)', '(i)', '(/)', '(x)', '(!)',
        '(+)', '(-)', '(?)', '(on)', '(off)', '(*)', '(*r)', '(*g)', '(*b)',
        '(*y)', '(flag)', '(flagoff)'
    ]
    emoticons = [re.escape(x) for x in emoticons]
    for e in emoticons:
        if (m := stream.scan(e)) is not None:
            return Emoticon(code=m)

def _maybe_parse_link(stream: Stream) -> FormattedFragment | None:
    anchor_pattern = r'{[a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-]+}'
    if (a := stream.scan(anchor_pattern)) is not None:
        a = a.removeprefix('{').removesuffix('}')
        page, name = a.split(':')
        return Anchor(page=page, name=name)

    if (m := stream.scan(r'\[[^]|]+\|[a-zA-Z0-9\-_./:]+\]')) is not None:
        m = m.removeprefix('[').removesuffix(']')
        name, url = m.split('|')
        return Link(name=name, url=url)

    patterns = [
        (r'#[a-zA-Z0-9\-_]', AnchorLink, lambda x: x.removeprefix('#')),
        (r'~[a-zA-Z0-9\-_]', UserLink, lambda x: x.removeprefix('~')),
        (r'mailto:[a-zA-Z0-9\-_.]+@[a-zA-Z0-9\-_.]+', MailToLink, lambda x: x.removeprefix('mailto:')),
        (r'file://[a-zA-Z0-9\-_./:]+', DownloadLink, lambda x: x),
        (r'^[a-zA-Z0-9\-_./:]+', AttachmentLink, lambda x: x.removeprefix('^')),
    ]
    for pattern, cls, transform in patterns:
        full_pattern = rf'\[{pattern}\]'
        if (m := stream.scan(full_pattern)) is not None:
            m = m.removeprefix('[').removesuffix(']')
            return cls(transform(m))

    if (m := stream.scan(r'\[http(s?)://[a-zA-Z0-9\-_./:]+\]')) is not None:
        return Link(name=None, url=m.removeprefix('[').removesuffix(']'))


def _maybe_parse_attachment(stream: Stream) -> FormattedFragment | None:
    g = r'[a-zA-Z0-9_\-]+'
    a = fr'thumbnail|{g}={g}'
    pattern = rf'!({g}:{g}\^)?[a-zA-Z0-9\-_./:]+(\|({a})(,\s*({a}))*)?!'
    if (e := stream.scan(pattern)) is not None:
        e = e.removeprefix('!').removesuffix('!')
        if '^' in e:
            location, rest = e.split('^')
            page, name = location.split(':')
        else:
            page = name = None
            rest = e
        if '|' in rest:
            obj_name, args = rest.split('|')
        else:
            obj_name = rest
            args = None
        if args is not None:
            thumbnail = 'thumbnail' in args
            args = args.replace('thumbnail', '')
            parsed_args = {}
            for x in args.split(','):
                if not x:
                    continue
                k, v = x.split('=')
                parsed_args[k.strip()] = v.strip()
        else:
            thumbnail = False
            parsed_args = {}
        return Embeddable(
            space_key=page,
            page=name,
            url=obj_name,
            thumbnail=thumbnail,
            options=parsed_args
        )

def _maybe_parse_panel(stream: Stream) -> FormattedFragment | None:
    if (res := _parse_pattern_with_args_helper('panel', stream)) is not None:
        m, args, _ = res
        return PanelBlock(options=args, content=_parse_formatted_text(m))

def _maybe_parse_no_format(stream: Stream) -> FormattedFragment | None:
    if (res := _parse_pattern_with_args_helper('noformat', stream)) is not None:
        m, args, _ = res
        content = m.scan(r'(.|\n)*')
        return NoFormatBlock(content=content, options=args)

def _maybe_parse_code(stream: Stream) -> FormattedFragment | None:
    if (res := _parse_pattern_with_args_helper('code', stream)) is not None:
        m, args, pos = res
        assert len(pos) <= 1
        if len(pos) == 1:
            lan = pos[0]
        else:
            lan = None
        return CodeBlock(content=m.scan(r'(.|\n)*'), language=lan, options=args)

def _parse_pattern_with_args_helper(name:  str, stream: Stream):
    pattern = rf'{{{name}(:[^}}]+)?}}(.|\n)*(?<!\\){{{name}}}'
    if (m := stream.scan_substream(pattern, trim_end=len(name) + 2)) is not None:
        h = m.scan(rf'{{{name}(:[^}}]+)?}}')
        assert h is not None
        h = h.removeprefix('{' + name).removesuffix('}').removeprefix(':')
        args = {}
        pos = []
        if h:
            for x in h.split('|'):
                if '=' not in x:
                    pos.append(x)
                else:
                    k, v = x.split('=')
                    args[k.strip()] = v.strip()
        return m, args, pos

def _maybe_parse_table(stream: Stream) -> FormattedFragment | None:
    header_pattern = r'\|\|([^|\n]+(?<!\\)\|\|)+\s*'
    if (header := stream.scan_substream(header_pattern)) is not None:
        header_items = _table_parse_helper(header, r'\|\|')
    else:
        header_items = None

    rows = []
    row_pattern = r'\|([^|\n]+(?<!\\)\|)+\s*'
    while (row := stream.scan_substream(row_pattern)) is not None:
        rows.append(_table_parse_helper(row, r'\|'))
    if not header_items and not rows:
        return None
    return Table(header=header_items, rows=rows)

def _table_parse_helper(stream: Stream, sep) -> list[FormattedText] | None:
    items = []
    while stream:
        stream.scan(sep)
        cell = stream.scan_substream(r'[^\|\n]+')
        if cell is None:
            break
        items.append(_parse_formatted_text(cell))
    return items

def _maybe_parse_list(stream: Stream) -> FormattedFragment | None:
    included = []
    while stream:
        if (r := stream.scan_substream(r'\s*[*\-#]+ [^\n]*\n?', first_col=True)) is not None:
            included.append(r)
        elif included and (_r := stream.scan('\n')) is not None:
            continue
        else:
            break
    if not included:
        return None
    depths = []
    items = []
    for item in included:
        p = item.scan(r'\s*[*\-#]+ ').removesuffix(' ')
        assert p is not None
        depths.append(p)
        items.append(_parse_formatted_text(item))
    return Listing(depths=depths, items=items)


if __name__ == '__main__':
    import json
    import sys

    with open('../../../../../outputs/tajo-packed-new/issue-features/0.json') as f:
        data = json.load(f)

    if len(sys.argv) > 1 and sys.argv[1] == 'sample':
        import random
        issue = random.choice(data)
        body = issue['description']
        print(body)
        k = parse_jira(body)
    else:
        i = 0
        matched = 0
        for issue in data:
            body = issue['description']
            #print(body)
            k = parse_jira(body)
            i += 1
            good = body == k.reconstruct()
            #if '*source*' in body:
            #    print(body)
            #    break
            if not good:
                import difflib
                import string
                diffs = [
                    x[2:] for x in difflib.ndiff(body, k.reconstruct())
                    if x[0] != ' '
                ]
                if not set(diffs) <= set(string.whitespace):
                    print(diffs)
                    print(body)
                    print(k)
                    print(k.reconstruct())
                    import difflib
                    for i, x in enumerate(difflib.ndiff(body, k.reconstruct())):
                        if x[0] != ' ':
                            prefix = body[max(0, i - 5):i-1]
                            suffix = body[i:i+5]
                            print(f'{prefix}|{x[1:]}|{suffix}')
                    break
            matched += good
            print(f'{i} ({matched})')