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


KEY_WORDS = ['if', 'else', 'until', 'return', 'break', 'repeat', 'void', 'int']
regexes = {
    TokenType.COMMENT: r'\/\*.*\*\/',
    TokenType.NUM: r'\d+',  # 0-9
    TokenType.KEYWORD: r'if|else|until|return|break|repeat|void|int',
    TokenType.ID: r'[a-zA-Z]\w*',  # a-z, A-Z, _
    TokenType.SYMBOL: r'[\(\)\{\}\[\]\+\-\*\=\;\,\:\<]|==',
    TokenType.WHITESPACE: r'\s+'
}


class Token:
    def __init__(self, typee: TokenType, string: str, line_no):
        self.type = typee
        self.string = string
        self.line_number = line_no

    def __str__(self):
        return f'({self.type.value}, {self.string})'

    def __ge__(self, other):
        return self.line_number >= other.line_number

    def __gt__(self, other):
        return self.line_number > other.line_number


class ScannerState(Enum):
    START = 0
    IN_NUM = 1
    IN_ID = 2
    IN_COMMENT = 3
    IN_SYMBOL = 4
    IN_WHITESPACE = 5


class SymbolTable:
    def __init__(self):
        self.table = set(KEY_WORDS)

    def append(self, element: str):
        self.table.add(element)

    def __str__(self):
        string = ''
        counter = 1
        for e in self.table:
            string += str(counter) + '. ' + e + '\n'
            counter += 1
        return string


class CompileException(Exception):
    def __init__(self, line_number: int, message: str):
        super().__init__(message)
        self.line_number = line_number

    def __gt__(self, other):
        return self.line_number > other.line_number

    def __ge__(self, other):
        return self.line_number >= other.line_number


class Scannerr:
    def __init__(self, string: str, symbol_table: SymbolTable):
        self.string = string
        self.pos = 0
        self.state = ScannerState.START
        self.line_number = 1
        self.table = symbol_table

    def is_split_char(self, char: str):
        return (re.fullmatch(regexes[TokenType.SYMBOL], char)) or re.fullmatch(regexes[TokenType.WHITESPACE], char)

    def next_split_char(self):
        curser = self.pos
        while curser < len(self.string):
            if self.is_split_char(self.string[curser]):
                return curser
            curser += 1
        return curser

    def get_next_token(self):
        if self.pos >= len(self.string):
            return Token(TokenType.EOF, 'EOF', -1)
        self.state = ScannerState.START
        # Assigining the state of the scanner based on the first character
        if self.state == ScannerState.START:
            self.init_state()

        # Scanning the string based on the state of the scanner
        if self.state == ScannerState.IN_COMMENT:
            curser = self.pos
            comment_begin_line_num = self.line_number
            while curser < len(self.string):
                if self.string[curser] == '\n':
                    self.line_number += 1

                if self.string[curser] != '*':
                    curser += 1
                elif self.string[curser + 1] == '/':
                    self.state = ScannerState.START
                    token = Token(TokenType.COMMENT, self.string[self.pos:curser - 1], comment_begin_line_num)
                    self.pos = curser + 2
                    return token
                else:
                    curser += 1
            if curser >= len(self.string):
                if curser - self.pos > 6:
                    comment = self.string[self.pos - 2: self.pos + 5] + '...'
                else:
                    comment = self.string[self.pos:curser - 2]
                self.state = ScannerState.START
                self.pos = curser
                raise CompileException(comment_begin_line_num, f'({comment}, Unclosed comment)')

        elif self.state == ScannerState.IN_WHITESPACE:
            curser = self.pos
            while curser < len(self.string) and re.fullmatch(regexes[TokenType.WHITESPACE], self.string[curser]):
                if self.string[curser] == '\n':
                    self.line_number += 1
                curser += 1
            token = Token(TokenType.WHITESPACE, self.string[self.pos:curser], self.line_number)
            self.pos = curser
            self.state = ScannerState.START
            return token

        elif self.state == ScannerState.IN_NUM:
            curser = self.pos
            while curser < len(self.string):
                if self.is_split_char(self.string[curser]):
                    break
                elif not re.match(regexes[TokenType.NUM], self.string[curser]):
                    number = self.string[self.pos:curser + 1]
                    self.pos = curser + 1
                    raise CompileException(self.line_number, f'({number}, Invalid number)')
                curser += 1

            number = self.string[self.pos:curser]
            self.pos = curser
            if not re.fullmatch(regexes[TokenType.NUM], number):
                raise Exception(f'{self.line_number}.  Invalid number: {number}')
            else:
                return Token(TokenType.NUM, number, self.line_number)

        elif self.state == ScannerState.IN_ID:
            curser = self.pos
            while curser < len(self.string):
                if self.is_split_char(self.string[curser]):
                    break
                elif not re.match(regexes[TokenType.ID], self.string[curser]):
                    word = self.string[self.pos:curser + 1]
                    self.pos = curser + 1
                    raise Exception(f'{self.line_number}. Invalid word: {word}')
                curser += 1

            word = self.string[self.pos:curser]
            self.pos = curser
            self.state = ScannerState.START

            if re.fullmatch(regexes[TokenType.KEYWORD], word):
                return Token(TokenType.KEYWORD, word, self.line_number)
            elif re.fullmatch(regexes[TokenType.ID], word):
                self.table.append(word)
                return Token(TokenType.ID, word, self.line_number)
            else:
                raise Exception(f'{self.line_number}. Invalid word: {word}')

        elif self.state == ScannerState.IN_SYMBOL:
            if re.fullmatch(regexes[TokenType.SYMBOL], self.string[self.pos]):
                if self.string[self.pos] == '*' and self.string[self.pos + 1] == '/':
                    e = Exception(f'{self.line_number}. Unmatched comment: {self.string[self.pos:self.pos + 2]}')
                    self.pos += 2
                    self.state = ScannerState.START
                    raise e
                if self.string[self.pos] == '=' and self.string[self.pos + 1] == '=':
                    symbol = self.string[self.pos:self.pos + 2]
                    self.pos += 2
                    self.state = ScannerState.START
                    return Token(TokenType.SYMBOL, symbol, self.line_number)

                symbol = self.string[self.pos]
                self.pos += 1
                self.state = ScannerState.START
                return Token(TokenType.SYMBOL, symbol, self.line_number)

    def init_state(self):
        if self.string[self.pos].isdigit():
            self.state = ScannerState.IN_NUM
        elif self.string[self.pos].isalpha():
            self.state = ScannerState.IN_ID
        elif self.string[self.pos] == '/':
            if self.string[self.pos + 1] == '*':
                self.pos += 2
                self.state = ScannerState.IN_COMMENT
            else:
                e = Exception(f'{self.line_number}. Invalid character: {self.string[self.pos]}')
                self.pos += 1
                raise e

        elif re.fullmatch(regexes[TokenType.WHITESPACE], self.string[self.pos]):
            self.state = ScannerState.IN_WHITESPACE
        elif re.fullmatch(regexes[TokenType.SYMBOL], self.string[self.pos]):
            self.state = ScannerState.IN_SYMBOL
        else:
            e = Exception(f'{self.line_number}. Invalid character: {self.string[self.pos]}')
            self.pos = self.next_split_char()
            raise e


def write_tokens(test_case: str, tokens: list):
    f = open('./PA1_testcases/T' + test_case + '/result_tokens.txt', 'w+')
    to_be_written = ''
    counter = 1
    tokens.sort()
    program_lines = {}
    for token in tokens:
        if token.type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
            if token.line_number not in program_lines.keys():
                program_lines[token.line_number] = [token]
            else:
                program_lines[token.line_number].append(token)
    for line in program_lines.keys():
        to_be_written += str(line) + '.'
        for token in program_lines[line]:
            to_be_written += ' ' + str(token)
        to_be_written += '\n'
    f.write(to_be_written)
    f.close()


def write_errors(test_case: str, errors: list):
    f = open('./PA1_testcases/T' + test_case + '/result_lexical_errors.txt', 'w+')
    to_be_written = ''

    for error in errors:
        to_be_written += str(error) + '\n'
    if to_be_written == '':
        to_be_written = 'There is no lexical error.'
    f.write(to_be_written)
    f.close()


def write_symbols(test_case: str, table: SymbolTable):
    f = open('./PA1_testcases/T' + test_case + '/result_symbol_table.txt', 'w+')
    f.write(str(table))
    f.close()


def main():
    test_case = '01'
    f = open('./PA1_testcases/T' + test_case + '/input.txt', 'r')
    table = SymbolTable()
    scanner = Scannerr(f.read(), table)
    f.close()
    tokens = []
    errors = []

    while True:
        try:
            token = scanner.get_next_token()
            if token.type == TokenType.EOF:
                break
            tokens.append(token)
        except Exception as e:
            errors.append(str(e))
    write_tokens(test_case, tokens)
    write_errors(test_case, errors)
    write_symbols(test_case, table)


main()
