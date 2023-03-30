import re
from enum import Enum
class TokenType(Enum):
    NUM = 'NUM'
    ID = 'ID'
    KEYWORD = 'KEYWORD'
    SYMBOL = 'SYMBOL'
    COMMENT = 'COMMENT'
    WHITESPACE = 'WHITESPACE'
    EOF = 'EOF'

regexes = {
    TokenType.COMMENT: r'\/\*.*\*\/',
    TokenType.NUM: r'\d+', # 0-9
    TokenType.KEYWORD: r'if|else|until|for|return|break|repeat',
    TokenType.ID: r'[a-zA-Z_]\w*', # a-z, A-Z, _
    TokenType.SYMBOL: r'[\(\)\{\}\[\]\+\-\*\/\=\;\,\:\<]|==',
    TokenType.WHITESPACE: r'\s+'
}
Symbol_table = {}

class Token:
    def __init__(self, type: TokenType, string: str):
        self.type = type
        self.string = string

    def __str__(self):
        return f'<{self.type}, {self.string}>'


class Scannerr:
    def __init__(self, string: str):
        self.string = string
        self.pos = 0

    def get_next_token(self):
        if self.pos >= len(self.string):
            return Token(TokenType.EOF, 'EOF')
        for type, regex in regexes.items():
            match = re.match(regex, self.string[self.pos:])
            if match:
                self.pos += match.end()
                return Token(type, match.group())
        raise Exception(f'Invalid character {self.string[self.pos]}')


def main():
    print('meow')
    scanner = Scannerr('if (a == 111)        { return 1; } /* comment */')
    while True:
        token = scanner.get_next_token()
        if token.type == TokenType.EOF:
            break
        print(token)

main()