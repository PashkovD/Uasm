from typing import Dict, Union

from typeguard import typechecked


class NotInt:
    def __init__(self, num: int, symbols: Dict[str, int] = None):
        self.num: int = num
        self.symbols: Dict[str, int] = symbols
        if self.symbols is None:
            self.symbols = {}

    def __repr__(self):
        return f"{type(self).__name__}({self.num},{self.symbols})"

    @typechecked
    def __add__(self, other: Union["NotInt", int]) -> "NotInt":
        if isinstance(other, int):
            return NotInt(self.num + other, self.symbols)
        symbols = self.symbols.copy()
        for i, f in other.symbols.items():
            symbols[i] = symbols.get(i, 0) + f
        return NotInt(self.num + other.num, symbols)

    def __neg__(self) -> "NotInt":
        symbols = self.symbols.copy()
        for i, f in self.symbols.items():
            symbols[i] = symbols.get(i, 0) - f
        return NotInt(-self.num, symbols)

    def __sub__(self, other) -> "NotInt":
        return self + (-other)
