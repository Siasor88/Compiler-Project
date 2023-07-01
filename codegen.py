variable_size = 4
symbol_table = []


class CodeGenerator:
    def __init__(self):
        self.SS = list()
        self.PB = {}
        self.PC = 0
        self.current_address = 1000

    def call_routine(self,routine_name,token):
        self.__getattribute__(routine_name)(token)


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
        for i in symbol_table:
            if i[0] == name:
                return i[2]

    def dec_var(self, next_token):
        name = self.SS[-1]
        self.SS.pop()
        t1 = self.get_temp()
        symbol_table.append([name, 'int', t1])

    def dec_array(self, next_token):
        size = int(next_token)
        name = self.SS[-1]
        self.SS.pop()
        address = self.get_temp()
        array_mem = self.get_temp(int(size))
        self.generate_code('ASSIGN', f'#{address}', array_mem)
        symbol_table.append([name, 'array', address])
