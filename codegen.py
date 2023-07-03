from compiler import SymbolTable, Token, TokenType

variable_size = 4


def get_token_value(token: Token):
    # token_value = token.type.value if token.type in [TokenType.ID, TokenType.NUM,
    #                                                  TokenType.EOF] else token.string
    return token.string


class CodeGenerator:
    def __init__(self):
        self.symbol_table = []
        self.break_states = []
        self.SS = list()
        self.PB = {}
        self.PC = 0
        self.current_address = 500

    def pop(self, n: int = 1):
        for i in range(n):
            self.SS.pop()
        return

    def call_routine(self, routine_name: str, token):
        print(routine_name, token)
        self.__getattribute__(routine_name.lower())(token)

    def generate_code(self, inst, arg1, arg2='', arg3='', loc: int = -1):
        if loc == -1:
            loc = self.PC
            self.PC += 1
        self.PB[loc] = f'{loc}\t({inst}, {arg1}, {arg2}, {arg3})'
        print("Generating code", self.PB[loc])

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
        var_type = self.SS[-2]
        self.pop(2)
        t1 = self.get_temp()
        self.symbol_table.append([name, var_type, t1])
        return

    def dec_arr(self, token):
        token_value = get_token_value(token)
        size = int(token_value)
        name = self.SS[-1]
        self.pop(2)
        address = self.get_temp()
        array_mem = self.get_temp(int(size))
        self.generate_code('ASSIGN', f'#{array_mem}', address)
        self.symbol_table.append([name, 'array', address])
        return

    def mul(self, token):
        operand1 = self.SS[-1]
        operand2 = self.SS[-2]
        self.pop(2)
        operator = 'MULT'
        tmp_var = self.get_temp()
        self.generate_code(operator, operand1, operand2, tmp_var)

        print(f'Pushed to Stack at function mul value: {tmp_var}')
        self.SS.append(tmp_var)
        print("Stack after this push:", self.SS)
        return

    def push_type(self, token):
        token_value = get_token_value(token)
        print(f'Pushed to Stack at function push_type value: {token_value}')
        self.SS.append(token_value)
        print("Stack after this push:", self.SS)
        return

    def pid(self, token):
        token_value = get_token_value(token)
        addr = self.get_address(token_value)
        print(f'Pushed to Stack at function pid value: {addr}')
        self.SS.append(addr)
        print("Stack after this push:", self.SS)
        return

    def assign(self, token):
        operand1 = self.SS[-1]
        operand2 = self.SS[-2]
        self.pop(2)
        self.generate_code('ASSIGN', operand1, operand2)
        self.SS.append(operand2)
        return

    def pop_extra(self, token):
        self.pop()
        return

    def arr_acc(self, token):
        index = self.SS[-1]
        array_address = self.SS[-2]
        self.pop(2)
        tmp1, tmp2 = self.get_temp(), self.get_temp()
        self.generate_code('MULT', index, '#4', tmp1)
        self.generate_code('ADD', tmp1, array_address, tmp2)
        print(f'Pushed to Stack at function arr_acc value: @{tmp2}')
        self.SS.append(f'@{tmp2}')
        print("Stack after this push:", self.SS)
        pass

    def pushop(self, token):
        token_value = get_token_value(token)
        print(f'Pushed to Stack at function pushop value: {token_value}')
        self.SS.append(token_value)
        print("Stack after this push:", self.SS)
        return

    def cmp(self, token):
        operand2 = self.SS[-1]
        operator = self.SS[-2]
        operand1 = self.SS[-3]
        self.pop(3)
        tmp_var = self.get_temp()
        operator = 'EQ' if operator == '==' else 'LT'
        self.generate_code(operator, operand1, operand2, tmp_var)

        print(f'Pushed to Stack at function cmp value: {tmp_var}')
        self.SS.append(tmp_var)
        print("Stack after this push:", self.SS)
        return

    def add_sub(self, token):
        operand1 = self.SS[-1]
        operator = self.SS[-2]
        operand2 = self.SS[-3]
        self.pop(3)
        print(operand1, operator, operand2)
        tmp_var = self.get_temp()
        operator = 'ADD' if operator == '+' else 'SUB'

        self.generate_code(operator, operand2, operand1, tmp_var)
        print(f'Pushed to Stack at function add_sub value: {tmp_var}')
        self.SS.append(tmp_var)
        print("Stack after this push:", self.SS)
        return

    def pnum(self, token):
        tmp_var = self.get_temp()
        token_value = get_token_value(token)
        self.generate_code('ASSIGN', '#' + token_value, tmp_var)
        # TODO check here
        print(f'Pushed to Stack at function pnum value: {tmp_var}')
        self.SS.append(tmp_var)
        print("Stack after this push:", self.SS)
        return

    def output(self, token):
        expression = self.SS[-1]
        self.pop()
        self.generate_code('PRINT', expression)
        return

    def print_symbol_table(self):
        print(self.symbol_table)

    def pidn(self, token):
        token_value = get_token_value(token)
        print(f'Pushed to Stack at function pidn value: {token_value}')
        self.SS.append(token_value)
        print("Stack after this push:", self.SS)
        return

    def save_index(self, token):
        print(f'Pushed to Stack at function save_index value: {self.PC}')
        self.SS.append(self.PC)
        print("Stack after this push:", self.SS)
        self.PC += 1
        return

    def jpf(self, token):
        jump_add = self.SS[-1]
        condition = self.SS[-2]
        self.pop(2)
        self.generate_code('JPF', condition, str(self.PC + 1), loc=jump_add)
        self.save_index(token)

        return

    def jump(self, token):
        jump_add = self.SS[-1]
        self.pop()
        self.generate_code('JP', str(self.PC), loc=jump_add)
        return

    def save_break_addr(self, lookahead):
        self.break_states.append(self.PC)
        self.PC += 1
        return

    def add_to_breaks_save(self, token):
        self.break_states.append("new-block")
        self.save_index(token)
        return

    def until_jump(self, token):
        condition = self.SS[-1]
        repeat_addr = int(self.SS[-2])
        self.pop(2)
        tmp_var = self.get_temp()
        self.generate_code('ASSIGN', '#0', tmp_var, loc=repeat_addr)
        self.generate_code('JPF', condition, str(repeat_addr))
        last_break = 0
        for i in reversed(range(len(self.break_states))):
            if self.break_states[i] == "new-break":
                last_break = i
                break
        print(last_break)
        breaks = self.break_states[last_break + 1:]
        print(breaks)
        print(self.break_states)
        for i in self.break_states[last_break + 1:]:
            self.generate_code('JP', self.PC, loc=i)
        self.break_states = self.break_states[:last_break]

        return
