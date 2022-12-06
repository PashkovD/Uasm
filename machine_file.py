from typing import Dict, List, Union, Tuple

from typeguard import typechecked

from not_int import NotInt


class MachineFile:
    def __init__(self):
        self.data = bytearray()
        self.symbols: Dict[str, int] = {}
        self.relocations: List[Tuple[int, str, int]] = []

    @property
    def current_pos(self) -> int:
        return len(self.data)

    @typechecked
    def write(self, data: Union[bytearray, bytes]) -> None:
        self.data.extend(data)

    @typechecked
    def write_int(self, num: NotInt) -> None:
        for i, f in num.symbols.items():
            self.relocations.append((self.current_pos, i, f))
        self.data.append((num.num % 256 + 256) % 256)

    def apply_relocations(self) -> None:
        for i, f, j in self.relocations:
            self.data[i] = ((self.data[i] + self.symbols[f] * j) % 256 + 256) % 256
