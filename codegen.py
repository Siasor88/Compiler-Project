from scanner import SymbolTable, Token, TokenType

variable_size = 4


def get_token_value(token: Token):
    # token_value = token.type.value if token.type in [TokenType.ID, TokenType.NUM,
    #                                                  TokenType.EOF] else token.string
    return token.string


# class Function:
#     def __init__(self, name, return_type, params, return_value, return_addr, start_addr, local_vars, scope):
#         pass

class CodeGenerator:
    def __init__(self):
        self.scope0_decelerations = []
        self.symbol_table = []
        self.break_states = []
        self.return_states = []
        self.params = []
        self.current_scope = 0
        self.SS = list()
        self.PB = {}
        self.PC = 2
        self.array_dec_stalled = []

        self.arg_collector = ['_']
        self.function_table = {}
        self.current_address = 500
        self.current_function_name = ''

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

    def get_address(self, name, scope=-1):
        try:
            if scope == -1:
                scope = self.current_scope
            if name == 'output':
                return 'output'
            print(f"Current Symbol Table {self.symbol_table}")
            print(f"Current Scope: {self.current_scope}")
            candidates = []
            for i in self.symbol_table:
                if i[0] == name:
                    candidates.append((i[3], i[2]))
            candidates.sort()
            print(f"Candidates for {name}: {candidates}")
            return candidates[-1][1]
        except:
            "bega raftim"

    def get_scope(self, var_name):
        for var in reversed(self.symbol_table):
            if var_name == var[0]:
                return var[3]

    def dec_var(self, next_token):
        name = self.SS[-1]
        var_type = self.SS[-2]
        self.pop(2)
        t1 = self.get_temp()
        self.symbol_table.append([name, var_type, t1, self.current_scope, variable_size])
        return

    def dec_arr(self, token):
        token_value = get_token_value(token)
        size = int(token_value)
        name = self.SS[-1]
        self.pop(2)
        address = self.get_temp()
        array_mem = self.get_temp(int(size))
        self.generate_code('ASSIGN', f'#{array_mem}', address)
        self.symbol_table.append([name, 'array', address, self.current_scope, size * variable_size])
        if self.current_scope == 0:
            self.array_dec_stalled.append(('ASSIGN', f'#{array_mem}', address))
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
        array_symbol_address = self.SS[-2]
        self.pop(2)
        tmp1, tmp2 = self.get_temp(), self.get_temp()
        self.generate_code('MULT', index, '#4', tmp1)
        # addr = self.array_table[array_symbol_address]
        # self.generate_code('ASSIGN', '#' + str(addr), array_symbol_address)
        self.generate_code('ADD', tmp1, array_symbol_address, tmp2)
        print(f'Pushed to Stack at function arr_acc value: @{tmp2}')
        self.SS.append(f'@{tmp2}')
        print("Stack after this push:", self.SS)


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

    def get_params(self, token):
        self.params = []
        return

    def create_function_frame(self, token):
        return_addr = self.get_temp()
        start_addr = self.PC
        func_params = self.params
        function_name = self.SS[-1]

        if function_name == 'main':
            self.generate_code('ASSIGN', '#0', '0', loc=0)
            self.generate_code('JP', self.PC, loc=1)
            for stalled_dec in self.array_dec_stalled:
                self.generate_code(*stalled_dec)
        function_return_type = self.SS[-2]
        self.pop(2)
        scope = self.current_scope
        function_return_value = self.get_temp()
        self.function_table[(function_name, scope)] = {
            'name': function_name,
            'return_addr': return_addr,
            'return_type': function_return_type,
            'return_value': function_return_value,
            'start_addr': start_addr,
            'params': func_params,
            'scope': scope,
            'local_vars': []
        }
        self.current_function_name = function_name
        self.symbol_table.append([function_name, 'function', (function_name, scope), self.current_scope, -1])
        return

    def create_new_return_scope(self, token):
        self.return_states.append('new_scope')
        return

    def save_return(self, token):
        # set the return value
        # print("current function table", self.function_table)
        #if the current function type is void, push dummy 0
        if self.function_table[(self.current_function_name, 0)]['return_type'] == 'void':
            self.SS.append(0)
        self.generate_code('ASSIGN', self.SS[-1],
                           self.function_table[(self.current_function_name, 0)]['return_value'],loc=self.PC)
        self.pop()
        self.return_states.append(self.PC+1)
        self.PC += 2
        pass

    def fill_returns(self, token):
        if self.current_function_name == 'main':
            return
        # find the last "new-scope" in return states
        last_scope = 0
        for i in reversed(range(len(self.return_states))):
            if self.return_states[i] == "new_scope":
                last_scope = i
                break
        locations = self.return_states[last_scope + 1:]
        self.return_states = self.return_states[:last_scope]
        locations.append(self.PC)
        self.PC += 1
        function_scope = self.get_scope(self.current_function_name)
        for j in locations:
            self.generate_code('JP',
                               '@' + self.function_table[(self.current_function_name, function_scope)]['return_addr'],
                               loc=j)
        pass

    def add_param(self, token):
        param_type = self.SS[-2]
        param_name = self.SS[-1]
        self.pop(2)
        param_addr = self.get_temp()
        self.params.append([param_name, param_type, param_addr, self.current_scope + 1, variable_size])
        self.symbol_table.append([param_name, param_type, param_addr, self.current_scope + 1, variable_size])
        return

    def add_param_array(self, token):
        param_type = self.SS[-2]
        param_name = self.SS[-1]
        self.pop(2)
        param_addr = self.get_temp()
        self.params.append([param_name, 'array', param_addr, self.current_scope + 1, -1])
        self.symbol_table.append([param_name, 'array', param_addr, self.current_scope + 1, -1])
        return

    def define_new_scope(self, token):
        self.current_scope += 1

    def end_scope(self, token):
        for element in reversed(self.symbol_table):
            if element[3] == self.current_scope:
                self.symbol_table.remove(element)
                # self.current_address -= element[4]
        self.current_scope -= 1
        # TODO
        return

    def begin_new_arg_scope(self, token):
        function_name = '_' + self.SS[-1]
        self.arg_collector.append(function_name)
        return

    def collect_argument(self, token):
        arg = self.SS[-1]
        self.pop()
        self.arg_collector.append(arg)
        print("current collected args after this collection:", self.arg_collector)
        return

    def call_function(self, token):
        # TODO ADD a condition when function name is OUTPUT
        # print("all functions:", self.function_table)
        index = 0
        for i in reversed(range(len(self.arg_collector))):
            if self.arg_collector[i] == '_':
                index = i
                break

        arguments = self.arg_collector[index + 1:]
        self.arg_collector = self.arg_collector[:index]
        print("the stack is currently:", self.SS)
        func_name = self.SS[-1]
        self.pop()
        function_scope = self.get_scope(func_name)
        function_args = self.function_table[func_name]['params']
        if len(function_args) != len(arguments):
            print("function args:", function_args, "arguments:", arguments)
            raise Exception('Fucked Up Function Call')
        for arg1, arg2 in zip(arguments, function_args):
            adr_arg2 = arg2[2]
            self.generate_code('ASSIGN', arg1, adr_arg2)
        print("arguments were set")
        function_addr = self.function_table[func_name]['start_addr']
        function_return_addr_var = self.function_table[func_name]['return_addr']
        function_return_value = self.function_table[func_name]['return_value']
        function_return_type = self.function_table[func_name]['return_type']
        # TODO check there might be a bug here, it should be tested
        return_addr = self.PC + 2
        self.generate_code('ASSIGN', f'#{return_addr}', function_return_addr_var)
        self.generate_code('JP', function_addr)
        self.arg_collector.append('_')
        if function_return_type != 'void':
            returned_value = self.get_temp()
            self.generate_code('ASSIGN', function_return_value, returned_value)
            self.SS.append(returned_value)
        else:
            self.SS.append(0)
        return
