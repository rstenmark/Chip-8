from collections import deque
from copy import deepcopy
from typing import Sequence

_LINE_MAX_TOKENS = 4


def parse_all_bases(s: str) -> int:
    """Tries to parse the passed string as base-10, then base-16, then base-2."""
    try:
        # decimal
        value = int(s, 10)
    except ValueError:
        try:
            # hexadecimal
            value = int(s, 16)
        except ValueError:
            # binary
            value = int(s, 2)

    return value


class InstructionSizeException(Exception):
    def __init__(self, *args):
        super().__init__(args)


class Token(object):
    """Token base class"""

    def __init__(self, raw: str):
        assert isinstance(raw, str) is True
        self.raw: str = raw


class ParentToken(Token):
    """Parent tokens can contain a constrained number (default 4) of
    child tokens. The child tokens can themselves be ParentTokens."""

    def __init__(self, raw: str):
        super().__init__(raw)
        self.children = deque(maxlen=_LINE_MAX_TOKENS)

    def __repr__(self):
        return f"<{self.__class__.__name__} ({len(self.children)} children)> -> {self.children}"


class LeafToken(Token):
    """Leaf Tokens represent individual tokens that cannot contain other tokens."""

    def __init__(self, raw: str):
        super().__init__(raw)

    def __repr__(self):
        try:
            return f"<{self.__class__.__name__}> = {self.value}"
        except AttributeError:
            return f"<{self.__class__.__name__}> -> {self.raw}"


class InstToken(ParentToken):
    """Instruction tokens encapsulate an entire instruction."""

    def __init__(self, raw: str, children: Sequence[Token] = None):
        super().__init__(raw)
        if children is None:
            self.children = deque(maxlen=_LINE_MAX_TOKENS)
        else:
            assert 1 <= len(children) <= 4
            self.children = deque(children, maxlen=len(children))

    def append(self, token: Token):
        self.children.append(token)


class NameToken(LeafToken):
    """Name tokens are leaf tokens representing an instruction name."""

    def __init__(self, raw: str):
        super().__init__(raw)
        assert isinstance(raw, str)
        self.value = raw


class ImmToken(LeafToken):
    """Immediate tokens are leaf tokens representing an immediate integer value."""

    def __init__(self, raw: str, value: int):
        super().__init__(raw)
        self.value = value


class RegToken(LeafToken):
    """Register tokens are leaf tokens representing a register reference
    using the syntax r0 - r16."""

    def __init__(self, raw: str, value: int):
        super().__init__(raw)
        self.value = value


class EscToken(LeafToken):
    """Encountering an Escape token will cause the tokenizer to disregard
    it and all following tokens in the Line."""

    def __init__(self, raw: str):
        super().__init__(raw)


class Tokenizer(object):
    class SpecialCharactersEnum:
        ESCAPE = "#"
        PREPROCESSOR = "."
        REGISTER = "r"

    def __init__(self):
        self.buf = deque()

    def push_line(self, raw: str, string_sequence: Sequence[str]) -> int:
        """Tokenizes a single line of source that has been stripped of delimiters
        and placed in a sequence, and pushes it onto the end of the Tokenizer's
        output buffer."""

        children = []
        for idx, s in enumerate(string_sequence):
            match idx:
                case 0:
                    # Match token 0, char 0:
                    match s[0]:
                        case self.SpecialCharactersEnum.ESCAPE:
                            children.append(EscToken(s))
                            # Skip any following tokens in sequence
                            break
                        case _:
                            # Instruction name
                            children.append(NameToken(s))
                case 1:
                    # Match token 1, char 0:
                    match s[0]:
                        case self.SpecialCharactersEnum.REGISTER:
                            # Extract target register number (base-10 only)
                            tgt_reg = int(s[1:])
                            children.append(RegToken(s, tgt_reg))
                        case _:
                            # Immediate value
                            children.append(ImmToken(s, parse_all_bases(s)))
                case 2:
                    # Match token 2, char 0:
                    match s[0]:
                        case self.SpecialCharactersEnum.REGISTER:
                            # Extract target register number (base-10 only)
                            tgt_reg = int(s[1:])
                            children.append(RegToken(s, tgt_reg))
                        case _:
                            # Immediate value
                            children.append(ImmToken(s, parse_all_bases(s)))
                case 3:
                    # 3rd operand always immediate value
                    children.append(ImmToken(s, parse_all_bases(s)))
                case _:
                    raise InstructionSizeException()

        self.buf.append(InstToken(raw, children))
        return len(self.buf)

    def dump(self) -> deque[Token]:
        """Returns a copy of the Tokenizer's buffer. The Tokenizer's buffer is
        cleared after this operation."""
        ret = deepcopy(self.buf)
        self.buf = self.buf.clear()
        return ret
