
from enum import Enum


class TokenType(Enum):
    NUM = 'NUM'
    ID = 'ID'
    KEYWORD = 'KEYWORD'
    SYMBOL = 'SYMBOL'
    COMMENT = 'COMMENT'
    WHITESPACE = 'WHITESPACE'


class Token:
    def __init__(self, type: TokenType, string: str):
        self.type = type
        self.string = string

    def __str__(self):
        return f'<{self.type}, {self.string}>'



def get_next_token():
    pass


