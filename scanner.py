from enum import Enum
from typing import List



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
    TokenType.NUM: r'\d+',  # 0-9
    TokenType.KEYWORD: ['if', 'else', 'until', 'return', 'break', 'repeat', 'void', 'int'],
    TokenType.SYMBOL: ['[', '(', ')', '{', '}', '[', ']', '+', '-', '*', '=', ';', ',', ':', '<', '=='],
    TokenType.WHITESPACE: [' ', '\n', '\t', '\32', '\r', '\v', '\f']
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
            string += str(counter) + '.' + '\t' + e + '\n'
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
        return (char in regexes[TokenType.SYMBOL]) or char in regexes[TokenType.WHITESPACE]

    def next_split_char(self):
        curser = self.pos
        while curser < len(self.string):
            if self.is_split_char(self.string[curser]):
                return curser
            curser += 1
        return curser

    def is_valid_char(self, char: str):
        return char.isalnum() or \
               char in regexes[TokenType.SYMBOL] or \
               char in regexes[TokenType.WHITESPACE] or \
               char == '/'

    def get_next_token(self):
        if self.pos >= len(self.string):
            return Token(TokenType.EOF, 'EOF', self.line_number)
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
            while curser < len(self.string) and self.string[curser] in regexes[TokenType.WHITESPACE]:
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
                elif not self.string[curser].isdigit():
                    number = self.string[self.pos:curser + 1]
                    self.pos = curser + 1
                    raise CompileException(self.line_number, f'({number}, Invalid number)')
                curser += 1

            number = self.string[self.pos:curser]
            self.pos = curser
            if not number.isdecimal():
                raise CompileException(self.line_number, f'({number}, Invalid number)')
            else:
                return Token(TokenType.NUM, number, self.line_number)

        elif self.state == ScannerState.IN_ID:
            curser = self.pos
            while curser < len(self.string):
                if self.is_split_char(self.string[curser]) or self.string[curser] == '/':
                    break
                elif not self.string[curser].isalnum():
                    word = self.string[self.pos:curser + 1]
                    self.pos = curser + 1
                    raise CompileException(self.line_number, f'({word}, Invalid input)')
                curser += 1

            word = self.string[self.pos:curser]
            self.pos = curser
            self.state = ScannerState.START

            if word in regexes[TokenType.KEYWORD]:
                return Token(TokenType.KEYWORD, word, self.line_number)
            elif word.isidentifier():
                self.table.append(word)
                return Token(TokenType.ID, word, self.line_number)
            else:
                raise CompileException(self.line_number, f'({word}, Invalid word)')

        elif self.state == ScannerState.IN_SYMBOL:
            if self.string[self.pos] in regexes[TokenType.SYMBOL]:
                if self.string[self.pos] == '*':
                    if self.string[self.pos + 1] == '/':
                        e = CompileException(self.line_number,
                                             f'({self.string[self.pos:self.pos + 2]}, Unmatched comment)')
                        self.pos += 2
                        self.state = ScannerState.START
                        raise e
                    elif not self.is_valid_char(self.string[self.pos + 1]):
                        symbol = self.string[self.pos: self.pos + 2]
                        self.pos += 2
                        raise CompileException(self.line_number, f'({symbol}, Invalid input)')

                if self.string[self.pos] == '=':
                    if self.string[self.pos + 1] == '=':
                        symbol = self.string[self.pos:self.pos + 2]
                        self.pos += 2
                        self.state = ScannerState.START
                        return Token(TokenType.SYMBOL, symbol, self.line_number)
                    elif self.is_valid_char(self.string[self.pos + 1]):
                        symbol = self.string[self.pos]
                        self.pos += 1
                        return Token(TokenType.SYMBOL, symbol, self.line_number)
                    else:
                        symbol = self.string[self.pos: self.pos + 2]
                        self.pos += 2
                        raise CompileException(self.line_number, f'({symbol}, Invalid input)')
                symbol = self.string[self.pos]
                self.pos += 1

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

            elif self.string[self.pos + 1] == '/':
                e = CompileException(self.line_number, f'({self.string[self.pos]}, Invalid input)')
                self.pos += 1
                raise e
            elif self.is_valid_char(self.string[self.pos + 1]):
                e = CompileException(self.line_number, f'({self.string[self.pos]}, Invalid input)')
                self.pos += 1
                raise e
            else:
                e = CompileException(self.line_number, f'({self.string[self.pos: self.pos + 2]}, Invalid input)')
                self.pos += 2
                raise e
        elif self.string[self.pos] in regexes[TokenType.WHITESPACE]:
            self.state = ScannerState.IN_WHITESPACE
        elif self.string[self.pos] in regexes[TokenType.SYMBOL]:
            self.state = ScannerState.IN_SYMBOL
        else:
            e = CompileException(self.line_number, f'({self.string[self.pos]}, Invalid input)')
            self.pos += 1
            raise e


def write_tokens(test_case: str, tokens: list):
    # f = open('./PA1_testcases/T' + test_case + '/result_tokens.txt', 'w+')
    f = open('./tokens.txt', 'w+')
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
        to_be_written += str(line) + '.\t'
        for idx, token in enumerate(program_lines[line]):
            to_be_written += str(token) + (' ' if idx != len(program_lines[line]) - 1 else '')
        to_be_written += '\n'
    f.write(to_be_written)
    f.close()


def write_errors(test_case: str, errors: List[CompileException]):
    # f = open('./PA1_testcases/T' + test_case + '/result_lexical_errors.txt', 'w+')
    f = open('lexical_errors.txt', 'w+')
    to_be_written = ''
    errors.sort()
    program_lines = {}
    for error in errors:
        if error.line_number not in program_lines.keys():
            program_lines[error.line_number] = []
        program_lines[error.line_number].append(error)

    for line in program_lines.keys():
        to_be_written += str(line) + '.' + '\t'
        for idx, error in enumerate(program_lines[line]):
            to_be_written += str(error) + (' ' if idx != len(program_lines[line]) - 1 else '')
        to_be_written += '\n'

    if to_be_written == '':
        to_be_written = 'There is no lexical error.'
    f.write(to_be_written)
    f.close()


def write_symbols(test_case: str, table: SymbolTable):
    # f = open('./PA1_testcases/T' + test_case + '/result_symbol_table.txt', 'w+')
    f = open('symbol_table.txt', 'w+')
    f.write(str(table))
    f.close()


# exec(open('compiler.py').read())
# def main():
#     test_cases = ['0' + str(i) for i in range(1, 10)] + ['10']
#     for test_case in test_cases:
#         f = open('./PA1_testcases/T' + test_case + '/input.txt', 'r')
#         # f = open('input.txt', 'r')
#         table = SymbolTable()
#         scanner = Scannerr(f.read(), table)
#         f.close()
#         tokens = []
#         errors = []
#
#         while True:
#             try:
#                 token = scanner.get_next_token()
#                 if token.type == TokenType.EOF:
#                     break
#                 tokens.append(token)
#             except CompileException as e:
#                 errors.append(e)
#         write_tokens(test_case, tokens)
#         write_errors(test_case, errors)
#         write_symbols(test_case, table)


# main()

# create an enum with choices a and b and c
# import sys
# from enum import Enum
# # from Scanner import Scannerr, Token, SymbolTable, TokenType
# import json
# from anytree import Node, RenderTree
#
# file = open('Resources/First_Follows.json')
#
# json_file = json.load(file)
# FIRSTS, FOLLOWS = json_file['first'], json_file['follow']
#
# file.close()
# #
# # f = open('input.txt', 'r')
# # table = SymbolTable()
# # scanner = Scannerr(f.read(), table)
# # f.close()
# tokens = []
# errors = []
#
#
# # nodex = Node('ali')
# # nodee = Node('ali', parent=nodex)
# # nodee = Node('ali', parent=nodex)
# # for pre, fill, node in RenderTree(nodex):
# #     print("%s%s" % (pre, node.name))
#
#
# def new_token(scanner: Scannerr):
#     token = scanner.get_next_token()
#     while token.type == TokenType.COMMENT or token.type == TokenType.WHITESPACE:
#         token = scanner.get_next_token()
#     if token.type == TokenType.EOF:
#         token.string = "$"
#     return token
#
#
# Terminals = ["ID", ";", "[", "NUM", "]", "(", ")", "int", "void", ",", "{", "}", "break", "if", "else", "repeat",
#              "until", "return", "=", "<", "==", "+", "-", "*", "EPSILON", "$"]
#
#
# class States(Enum):
#     Program = 'Program'
#     Declaration_list = 'Declaration_list'
#     Declaration = 'Declaration'
#     Declaration_initial = 'Declaration_initial'
#     Declaration_prime = 'Declaration_prime'
#     Var_declaration_prime = 'Var_declaration_prime'
#     Fun_declaration_prime = 'Fun_declaration_prime'
#     Type_specifier = 'Type_specifier'
#     Params = 'Params'
#     Param_list = 'Param_list'
#     Param = 'Param'
#     Param_prime = 'Param_prime'
#     Compound_stmt = 'Compound_stmt'
#     Statement_list = 'Statement_list'
#     Statement = 'Statement'
#     Expression_stmt = 'Expression_stmt'
#     Selection_stmt = 'Selection_stmt'
#     Iteration_stmt = 'Iteration_stmt'
#     Return_stmt = 'Return_stmt'
#     Return_stmt_prime = 'Return_stmt_prime'
#     Expression = 'Expression'
#     B = 'B'
#     H = 'H'
#     Simple_expression_zegond = 'Simple_expression_zegond'
#     Simple_expression_prime = 'Simple_expression_prime'
#     C = 'C'
#     Relop = 'Relop'
#     Additive_expression = 'Additive_expression'
#     Additive_expression_prime = 'Additive_expression_prime'
#     Additive_expression_zegond = 'Additive_expression_zegond'
#     D = 'D'
#     Addop = 'Addop'
#     Term = 'Term'
#     Term_prime = 'Term_prime'
#     Term_zegond = 'Term_zegond'
#     G = 'G'
#     Factor = 'Factor'
#     Var_call_prime = 'Var_call_prime'
#     Var_prime = 'Var_prime'
#     Factor_prime = 'Factor_prime'
#     Factor_zegond = 'Factor_zegond'
#     Args = 'Args'
#     Arg_list = 'Arg_list'
#     Arg_list_prime = 'Arg_list_prime'
#
#
# def get_state_by_name(name):
#     for state in States:
#         if state.value == name:
#             return state
#     return None
#
#
# class Rule:
#     def __init__(self, LHS: States, RHS: list):
#         self.LHS = LHS
#         self.RHS = RHS.copy()
#
#     def appliable(self, token: Token):
#         token_value = self.get_token_value(token)
#         if token_value in FIRSTS[self.LHS.value]:
#             variable = self.RHS[0]
#             if variable in Terminals:
#                 if variable == token_value:
#                     return True
#                 elif variable == 'EPSILON':
#                     if token_value in FOLLOWS[self.LHS.value]:
#                         return True
#             elif token_value in FIRSTS[variable.value]:
#                 return True
#             elif token_value in FOLLOWS[variable.value] and 'EPSILON' in FIRSTS[variable.value]:
#                 return True
#             # if variable in Terminals:
#             #     if variable == token_value:
#             #         return True
#             #     elif variable == 'EPSILON':
#             #         if token_value in FOLLOWS[self.LHS.value]:
#             #             return True
#             # elif token_value in FIRSTS[variable.value]:
#             #     return True
#             # elif token_value in FOLLOWS[variable.value]:
#             #     return True
#             # else:
#             #     return False
#         if token_value in FOLLOWS[self.LHS.value] and 'EPSILON' in FIRSTS[self.LHS.value]:
#             flag = True
#             for variable in self.RHS:
#                 if variable in Terminals:
#                     if variable == 'EPSILON':
#                         continue
#                     else:
#                         flag = False
#                         break
#                 if 'EPSILON' not in FIRSTS[variable.value]:
#                     flag = False
#                     break
#             if flag:
#                 return True
#         return False
#
#     def get_token_value(self, token):
#         token_value = token.string
#         if token.type in [TokenType.ID, TokenType.NUM]:
#             token_value = token.type.value
#         return token_value
#
#
# def create_rule_from_production(state, path):
#     rhs = []
#     for variable in path:
#         if get_state_by_name(variable) is not None:
#             rhs.append(get_state_by_name(variable))
#         elif variable in Terminals:
#             rhs.append(variable)
#     the_rule = Rule(state, rhs)
#
#     return the_rule
#
#
# class Transition:
#     def __init__(self, variable, rules):
#         self.variable = variable
#         self.rules = rules
#
#     def get_token_value(self, token):
#         token_value = token.string
#         if token.type in [TokenType.ID, TokenType.NUM]:
#             token_value = token.type.value
#         return token_value
#
#     def appliable(self, token: Token):
#         for rule in self.rules:
#             if rule.appliable(token):
#                 return rule
#         return None
#
#
# def remove_from_adj(id, adj):
#     # print("removing ", id, " was called ")
#     for key in adj:
#         if id in adj[key][0]:
#             adj[key][0].remove(id)
#
#
# # creating transitions and rules from the production.json file
# file = open('Resources/Productions.json')
# json_file = json.load(file)
# file.close()
# productions = json_file
# transitions = {}
# # iterate over all the names in States Enum
# for initial_state in States:
#     if initial_state.value in Terminals:
#         continue
#     transition = Transition(initial_state, [])
#     for production in productions[initial_state.value]:
#         rule = create_rule_from_production(initial_state, production)
#         transition.rules.append(rule)
#     transitions[initial_state.value] = transition
#
#
# # rule = transitions['Term_prime'].rules[0]
# # print(rule.LHS, rule.RHS)
# # token = Token(TokenType.SYMBOL, "*",5)
# # print(rule.appliable(token))
# # # exit the program
# # exit(0)
#
#
# def get_name_of_children(adj, node):
#     neighbors = adj[node][0]
#     names = []
#     for neighbor in neighbors:
#         names.append(adj[neighbor][1])
#     return names
#
#
# def create_tree(adj: dict):
#     root = Node("Program")
#     current_node = 1
#     stack = [current_node]
#     visited = []
#     node_map = {1: root}
#     while stack:
#         current_node = stack[-1]
#         stack.pop()
#         father = node_map[current_node]
#         for node in (adj[current_node][0]):
#             stack.append(node)
#             tree_node = Node(str(adj[node][1]).replace('_', '-'), parent=father)
#             node_map[node] = tree_node
#     # Node('$', parent=root)
#     return root
#
#
# def draw_tree(adj: dict, addr: str):
#     ori = sys.stdout
#     with open(addr, "w") as f:
#         sys.stdout = f
#         root = create_tree(adj)
#         for pre, fill, node in RenderTree(root):
#             print("%s%s" % (pre, node.name))
#     sys.stdout = ori
#
#
# def main():
#     # test_cases = ['0' + str(i) + "/" for i in range(1, 10)] + ['10/']
#     test_cases = ['']
#     for test_case in test_cases:
#         # addr = './P2_testcases/T'+ test_case +'/'
#         addr = './' + test_case
#         file = open(addr + 'input.txt', 'r')
#         table = SymbolTable()
#         scanner = Scannerr(file.read(), table)
#         file.close()
#         token = new_token(scanner)
#         ## print("New Token:", token)
#         # queue = [get_state_by_name('Program')]
#         id_counter = 2
#         queue = [('Program', 1)]
#         adj = {}
#
#         # file = open(addr + 'syntax_errors_result.txt', 'w')
#         file = open(addr + 'syntax_errors.txt', 'w')
#         has_syntax_error = False
#
#         while True:
#             current_state = queue[0][0]
#
#             if type(current_state) != str:
#                 current_state = current_state.value
#
#             if current_state == '$':
#                 adj[queue[0][1]] = ([], '$')
#                 queue.pop(0)
#                 break
#             if current_state == 'EPSILON':
#                 adj[queue[0][1]] = ([], 'epsilon')
#                 queue.pop(0)
#                 continue
#             if current_state in Terminals:
#                 if current_state == token.string:
#                     adj[queue[0][1]] = ([], token)
#                     queue.pop(0)
#                     token = new_token(scanner)
#                     ## print("New Token:", token)
#                     continue
#                 elif current_state == 'NUM' and token.type == TokenType.NUM:
#                     adj[queue[0][1]] = ([], token)
#                     queue.pop(0)
#                     token = new_token(scanner)
#                     ## print("New Token:", token)
#                     continue
#                 elif current_state == 'ID' and token.type == TokenType.ID:
#                     adj[queue[0][1]] = ([], token)
#                     queue.pop(0)
#                     token = new_token(scanner)
#                     ## print("New Token:", token)
#                     continue
#                 else:
#                     token_value = token.type.value if token.type in [TokenType.ID, TokenType.NUM,
#                                                                      TokenType.EOF] else token.string
#                     file.write(f"#{token.line_number} : syntax error, missing {str(current_state).replace('_', '-')}\n")
#                     has_syntax_error = True
#                     remove_from_adj(queue[0][1], adj)
#                     queue.pop(0)
#                     continue
#
#             # value = current_state
#             # if type(current_state) is not str:
#             #     value = current_state.value
#
#             transition = transitions[current_state]
#             rule = transition.appliable(token)
#             if rule is None:
#                 token_value = token.type.value if token.type in [TokenType.ID, TokenType.NUM,
#                                                                  TokenType.EOF] else token.string
#                 if token_value in FOLLOWS[current_state]:
#                     file.write(f"#{token.line_number} : syntax error, missing {str(current_state).replace('_', '-')}\n")
#                     has_syntax_error = True
#                     remove_from_adj(queue[0][1], adj)
#                     queue.pop(0)
#                     continue
#                 else:
#                     if token.type == TokenType.EOF:
#                         has_syntax_error = True
#                         file.write(
#                             f"#{token.line_number} : syntax error, Unexpected {str(token_value).replace('_', '-')}\n")
#                         for i in range(len(queue)):
#                             remove_from_adj(queue[i][1], adj)
#                         break
#                     file.write(f"#{token.line_number} : syntax error, illegal {str(token_value).replace('_', '-')}\n")
#                     token = new_token(scanner)
#                     continue
#             else:
#                 # print(rule.LHS, rule.RHS)
#                 adj[queue[0][1]] = ([], rule.LHS.value)
#                 new_states = [(variable, id_counter + i + 1) for i, variable in enumerate(rule.RHS)]
#                 id_counter += len(rule.RHS)
#                 if current_state == 'Program':
#                     new_states.append(('$', id_counter + 1))
#                     id_counter += 1
#                 # adj[queue[0][1]][0].append([state[1] for state in new_states])
#                 for state in new_states:
#                     adj[queue[0][1]][0].append(state[1])
#                 queue.pop(0)
#                 queue = new_states + queue
#                 ## print("new queue", queue)
#                 # print(rule.LHS.value, '->',
#                 #       ' '.join([variable.value if type(variable) == States else variable for variable in rule.RHS]))
#         if not has_syntax_error:
#             file.write("There is no syntax error.")
#         file.close()
#         # for key in adj:
#         #     print(key, "->", adj[key][0])
#
#         draw_tree(adj, addr + 'parse_tree.txt')
