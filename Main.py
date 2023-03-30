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
    TokenType.NUM: r'\d+',  # 0-9
    TokenType.KEYWORD: r'if|else|until|for|return|break|repeat|void|int',
    TokenType.ID: r'[a-zA-Z]\w*',  # a-z, A-Z, _
    TokenType.SYMBOL: r'[\(\)\{\}\[\]\+\-\*\=\;\,\:\<]|==',
    TokenType.WHITESPACE: r'\s+'
}
Symbol_table = {}


class Token:
    def __init__(self, type: TokenType, string: str):
        self.type = type
        self.string = string

    def __str__(self):
        return f'<{self.type}, {self.string}>'


class Scanner_State(Enum):
    START = 0
    IN_NUM = 1
    IN_ID = 2
    IN_COMMENT = 3
    IN_SYMBOL = 4
    IN_WHITESPACE = 5


class Scannerr:
    def __init__(self, string: str):
        self.string = string
        self.pos = 0
        self.state = Scanner_State.START
        self.line_number = 1

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
            return Token(TokenType.EOF, 'EOF')
        self.state = Scanner_State.START
        # Assigining the state of the scanner based on the first character
        if self.state == Scanner_State.START:
            if self.string[self.pos].isdigit():
                self.state = Scanner_State.IN_NUM
            elif self.string[self.pos].isalpha():
                self.state = Scanner_State.IN_ID
            elif self.string[self.pos] == '/':
                if self.string[self.pos + 1] == '*':
                    self.pos += 2
                    self.state = Scanner_State.IN_COMMENT
                else:
                    e = Exception(f'Invalid character at line {self.line_number}: {self.string[self.pos]}')
                    self.pos = self.next_split_char()

                    raise e

            elif re.fullmatch(regexes[TokenType.WHITESPACE], self.string[self.pos]):
                self.state = Scanner_State.IN_WHITESPACE
            elif re.fullmatch(regexes[TokenType.SYMBOL], self.string[self.pos]):
                self.state = Scanner_State.IN_SYMBOL
            else:
                e = Exception(f'Invalid character at line {self.line_number}: {self.string[self.pos]}')
                self.pos = self.next_split_char()
                raise e

        # Scanning the string based on the state of the scanner
        if self.state == Scanner_State.IN_COMMENT:
            curser = self.pos
            while curser < len(self.string):
                if self.string[curser] == '\n':
                    self.line_number += 1

                if self.string[curser] != '*':
                    curser += 1
                elif self.string[curser + 1] == '/':
                    self.state = Scanner_State.START
                    token = Token(TokenType.COMMENT, self.string[self.pos:curser - 1])
                    self.pos = curser + 2
                    return token
                else:
                    curser += 1
            if curser >= len(self.string):
                if curser - self.pos > 7:
                    comment = self.string[self.pos:self.pos + 7] + '...'
                else:
                    comment = self.string[self.pos:curser - 2]
                self.state = Scanner_State.START
                self.pos = curser
                raise Exception(f'Unclosed comment at {comment}')

        elif self.state == Scanner_State.IN_WHITESPACE:
            curser = self.pos
            while curser < len(self.string) and re.fullmatch(regexes[TokenType.WHITESPACE], self.string[curser]):
                if self.string[curser] == '\n':
                    self.line_number += 1
                curser += 1
            token = Token(TokenType.WHITESPACE, self.string[self.pos:curser])
            self.pos = curser
            self.state = Scanner_State.START
            return token

        elif self.state == Scanner_State.IN_NUM:
            curser = self.pos
            while curser < len(self.string):
                if self.is_split_char(self.string[curser]):
                    break
                curser += 1
            number = self.string[self.pos:curser]
            self.pos = curser
            self.state = Scanner_State.START
            if not re.fullmatch(regexes[TokenType.NUM], number):
                raise Exception(f'Invalid number at line {self.line_number}: {number}')
            else:
                return Token(TokenType.NUM, number)

        elif self.state == Scanner_State.IN_ID:
            curser = self.pos
            while curser < len(self.string):
                if self.is_split_char(self.string[curser]):
                    break
                curser += 1

            word = self.string[self.pos:curser]
            self.pos = curser
            self.state = Scanner_State.START

            if re.fullmatch(regexes[TokenType.KEYWORD], word):
                return Token(TokenType.KEYWORD, word)
            elif re.fullmatch(regexes[TokenType.ID], word):
                # TODO symbol table
                # print(bool(re.match(regexes[TokenType.ID], word)))
                return Token(TokenType.ID, word)
            else:
                raise Exception(f'Invalid word at line {self.line_number}: {word}')

        elif self.state == Scanner_State.IN_SYMBOL:
            if re.fullmatch(regexes[TokenType.SYMBOL], self.string[self.pos]):
                if (self.string[self.pos] == '*' and self.string[self.pos + 1] == '/'):
                    e = Exception(f'Unmatched comment at line {self.line_number}: {self.string[self.pos]}')
                    self.pos += 2
                    self.state = Scanner_State.START
                    raise e
                if (self.string[self.pos] == '=' and self.string[self.pos + 1] == '='):
                    symbol = self.string[self.pos:self.pos + 2]
                    self.pos += 2
                    self.state = Scanner_State.START
                    return Token(TokenType.SYMBOL, symbol)
                symbol = self.string[self.pos]
                self.pos += 1
                self.state = Scanner_State.START
                return Token(TokenType.SYMBOL, symbol)


Address = "Desktop/uni/semester 6/Compiler/PA1_testcases/T01"


def main():
    scanner = Scannerr('''/* test case */
void main(void){
	int prod;
	int i ;
		prod = 1;
		i = 1;
	repeat {
		prod = i * prod ;
		i = i + 2;
	} until (i << 7)
		output(prod);
		return;


}''')
    while True:
        try:
            token = scanner.get_next_token()
            if token.type == TokenType.EOF:
                break
            print(token)
        except Exception as e:
            print(e)


main()
