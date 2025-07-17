import abc
import enum

import nltk

from . import jira


class TextCleanupMode(enum.Enum):
    Raw = enum.auto()
    RemoveFormatting = enum.auto()
    RemoveFormattingAndBlocks = enum.auto()
    RemoveFormattingAndReplaceBlocks = enum.auto()
    RemoveFormattingAndReplaceBlocksAndReplaceNames = enum.auto()

    def remove_formatting(self) -> bool:
        return self != self.Raw

    def remove_blocks(self) -> bool:
        return self == self.RemoveFormattingAndBlocks

    def replace_blocks(self) -> bool:
        return (
            self == self.RemoveFormattingAndReplaceBlocks
                or self == self.RemoveFormattingAndReplaceBlocksAndReplaceNames
        )

    def replace_names(self) -> bool:
        return self == self.RemoveFormattingAndReplaceBlocksAndReplaceNames


class TextCleaner(abc.ABC):

    def __init__(self, mode: TextCleanupMode):
        self.mode = mode

    @abc.abstractmethod
    def clean(self, text: str) -> str:
        pass

    @abc.abstractmethod
    def sent_tokenize(self, text: str) -> list[str]:
        pass


class JiraTextCleaner(TextCleaner):

    _text_effects = (
        jira.Strong, jira.Emphasis, jira.Citation, jira.Deleted,
        jira.Inserted, jira.SuperScript, jira.SubScript, jira.Monospaced,
        jira.BlockQuote, jira.Quote, jira.ColorBlock, jira.Quote
    )
    _links = (
        jira.Link, jira.Anchor, jira.AnchorLink, jira.AttachmentLink,
        jira.UserLink, jira.DownloadLink, jira.Embeddable, jira.MailToLink
    )
    _structure = (
        jira.HorizontalRule, jira.ShortDash, jira.LongDash,
        jira.LineBreak
    )
    _blocks = (jira.NoFormatBlock, jira.PanelBlock, jira.CodeBlock)

    def clean(self, text: str) -> str:
        ast = jira.parse_jira(text)
        ast = ast.visit(self._mapper)
        return ast.reconstruct()

    def _mapper(self, node):
        if not self.mode.remove_formatting():
            return node

        if isinstance(node, jira.Raw):
            return node
        if isinstance(node, jira.Heading):
            return node.text
        if isinstance(node, self._text_effects):
            return node.content
        if isinstance(node, jira.Emoticon):
            return jira.Raw('')
        if isinstance(node, self._structure):
            return jira.Raw('')
        if isinstance(node, self._links):
            return jira.Raw('')

        if isinstance(node, jira.Listing):
            out = []
            for item in node.items[:-1]:
                out.append(item)
                out.append(jira.Raw('\n'))
            out.append(node.items[-1])
            return jira.FormattedText(out)

        if self.mode.remove_blocks():
            if isinstance(node, self._blocks):
                return jira.Raw('')
            if isinstance(node, jira.Table):
                return jira.Raw('')
        elif self.mode.replace_blocks():
            if isinstance(node, jira.NoFormatBlock):
                return jira.Raw('NoFormatBlock')
            if isinstance(node, jira.PanelBlock):
                return jira.Raw('PanelBlock')
            if isinstance(node, jira.CodeBlock):
                return jira.Raw('CodeBlock')
            if isinstance(node, jira.Table):
                return jira.Raw('Table')
        else:
            if isinstance(node, self._blocks):
                return node
            if isinstance(node, jira.Table):
                return node

        if isinstance(node, jira.FormattedText):
            return node

        raise NotImplementedError(f'Not implemented for {type(node)}')

    def sent_tokenize(self, text: str) -> list[str]:
        marker = '__BLOCKMARKER'
        while marker in text:
            marker = '_' + marker
        ast = jira.parse_jira(text)
        blocks = []
        ast = ast.visit(self._tok_mapper_builder(marker, blocks))
        text = ast.reconstruct()
        parts = text.split(marker)
        sentences = []
        assert len(parts) == len(blocks) + 1
        for part, block in zip(parts[:-1], blocks, strict=True):
            if part:
                sentences.extend(nltk.sent_tokenize(part))
            sentences.append(block)
        if parts[-1]:
            sentences.extend(nltk.sent_tokenize(parts[-1]))
        return sentences

    def _tok_mapper_builder(self, marker: str, blocks: list):
        def mapper(node):
            if isinstance(node, self._blocks):
                if isinstance(node, jira.NoFormatBlock):
                    blocks.append(
                        node.content
                    )
                elif isinstance(node, jira.PanelBlock):
                    blocks.append(
                        node.content
                    )
                elif isinstance(node, jira.CodeBlock):
                    blocks.append(
                        node.content
                    )
                return jira.Raw(marker)
            return node
        return mapper
