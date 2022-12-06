from typing import Dict, List, Union

from not_int import NotInt


class MachineFile:
    def __init__(self):
        self.data = bytearray()
        self.symbols: Dict[str, int] = {}
        self.relocations: Dict[int, List[str]] = {}

    @property
    def current_pos(self) -> int:
        return len(self.data)

    def write(self, data: Union[bytearray, bytes]) -> None:
        self.data += data

    def write_int(self, num: NotInt) -> None:
        for i, f in num.symbols.items():
            self.relocations[self.current_pos] = self.relocations.get(self.current_pos, []) + [i] * f
        self.write(bytes((num.num % 256 + 256) % 256, ))
