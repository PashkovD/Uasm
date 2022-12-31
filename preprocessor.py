from lexer import Lexer


class Preprocessor:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer.lexer
        self.next = self.lexer.token()

    def is_ended(self) -> bool:
        return self.next is None

    def input(self, data: str):
        ...

    def token(self):
        var = self.next
        self.next = self.lexer.token()
        if var.type == "NEWLINE":
            return None
        return var
