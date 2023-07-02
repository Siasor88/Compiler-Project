from compiler import SymbolTable, Token, TokenType

variable_size = 4


def get_token_value(toke: Token):
    token_value = token.type.value if token.type in [TokenType.ID, TokenType.NUM,
                                                     TokenType.EOF] else token.string
    return token_value


class CodeGenerator:
    def __init__(self):
        self.symbol_table = []
        self.SS = list()
        self.PB = {}
        self.PC = 0
        self.current_address = 1000

    def pop(self, n: int = 1):
        for i in range(n):
            self.SS.pop()
        return

    def call_routine(self, routine_name: str, token):
        self.__getattribute__(routine_name.lower())(token)

    def generate_code(self, inst, arg1, arg2='', arg3=''):
        self.PB[self.PC] = f'{inst}, {arg1}, {arg2}, {arg3}'
        self.PC += 1

    def get_temp(self, size=1):
        start_address = str(self.current_address)
        for i in range(size):
            self.generate_code('ASSIGN', '#0', str(self.current_address))
            self.current_address += variable_size
        return start_address

    def get_address(self, name):
        if name == 'output':
            return 'output'
        for i in self.symbol_table:
            if i[0] == name:
                return i[2]

    def dec_var(self, next_token):
        name = self.SS[-1]
        self.SS.pop()
        t1 = self.get_temp()
        self.symbol_table.append([name, 'int', t1])

    def dec_array(self, next_token):
        size = int(next_token)
        name = self.SS[-1]
        self.SS.pop()
        address = self.get_temp()
        array_mem = self.get_temp(int(size))
        self.generate_code('ASSIGN', f'#{address}', array_mem)
        self.symbol_table.append([name, 'array', address])

    def mul(self, token):
        operand1 = self.SS[-1]
        operand2 = self.SS[-2]
        operator = 'MUL'
        tmp_var = self.get_temp()
        self.generate_code(operator, operand1, operand2, tmp_var)
        self.pop(2)
        self.SS.append(tmp_var)
        return

    def push_type(self, token):
        token_value = get_token_value(token)
        self.SS.append(token_value)
        pass

    def pid(self, token):
        token_value = get_token_value(token)
        addr = self.get_address(token_value)
        self.SS.append(addr)
        return

    def assign(self, token):
        operand1 = self.SS[-1]
        operand2 = self.SS[-2]
        self.pop(2)
        self.generate_code('ASSIGN', operand1, operand2)
        return

    def arr_acc(self, token):
        pass

    def pushop(self, token):
        token_value = get_token_value(token)
        self.SS.append(token_value)
        return

    def cmp(self, token):
        pass

    def add_sub(self, token):
        operand1 = self.SS[-1]
        operator = self.SS[-2]
        operand2 = self.SS[-3]
        tmp_var = self.get_temp()
        operator = 'ADD' if operator == '+' else 'SUB'
        self.generate_code(operator, operand1, operand2, tmp_var)
        self.pop(3)
        self.SS.append(tmp_var)
        return

    def pnum(self, token):
        tmp_var = self.get_temp()
        token_value = get_token_value(token)
        self.generate_code('ASSIGN', '#' + token_value, tmp_var)
        #TODO check here
        self.SS.append(tmp_var)
        return

    def output(self, token):
        expression = self.SS[-1]
        self.generate_code('PRINT', expression)
        self.pop()
        return
