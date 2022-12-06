from typing import Dict, List, Union


class MachineFile:
    def __init__(self):
        self.data = bytearray()
        self.symbols: Dict[str, int] = {}
        self.relocations: Dict[int, List[str]] = {}

    @property
    def current_pos(self) -> int:
        return len(self.data)

    def write(self, data: Union[bytearray, bytes]):
        self.data += data
