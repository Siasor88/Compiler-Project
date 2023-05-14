# create an enum with choices a and b and c
from enum import Enum
from compiler import Scannerr, Token, SymbolTable, TokenType
import json
from anytree import Node, RenderTree

file = open('./First_Follows.json')

json_file = json.load(file)
FIRSTS, FOLLOWS = json_file['first'], json_file['follow']

file.close()
#
# f = open('input.txt', 'r')
# table = SymbolTable()
# scanner = Scannerr(f.read(), table)
# f.close()
tokens = []
errors = []


# nodex = Node('ali')
# nodee = Node('ali', parent=nodex)
# nodee = Node('ali', parent=nodex)
# for pre, fill, node in RenderTree(nodex):
#     print("%s%s" % (pre, node.name))


def new_token():
    token = scanner.get_next_token()
    while token.type == TokenType.COMMENT or token.type == TokenType.WHITESPACE:
        token = scanner.get_next_token()
    if token.type == TokenType.EOF:
        token.string = "$"
    return token


Terminals = ["ID", ";", "[", "NUM", "]", "(", ")", "int", "void", ",", "{", "}", "break", "if", "else", "repeat",
             "until", "return", "=", "<", "==", "+", "-", "*", "EPSILON", "$"]


class States(Enum):
    Program = 'Program'
    Declaration_list = 'Declaration_list'
    Declaration = 'Declaration'
    Declaration_initial = 'Declaration_initial'
    Declaration_prime = 'Declaration_prime'
    Var_declaration_prime = 'Var_declaration_prime'
    Fun_declaration_prime = 'Fun_declaration_prime'
    Type_specifier = 'Type_specifier'
    Params = 'Params'
    Param_list = 'Param_list'
    Param = 'Param'
    Param_prime = 'Param_prime'
    Compound_stmt = 'Compound_stmt'
    Statement_list = 'Statement_list'
    Statement = 'Statement'
    Expression_stmt = 'Expression_stmt'
    Selection_stmt = 'Selection_stmt'
    Iteration_stmt = 'Iteration_stmt'
    Return_stmt = 'Return_stmt'
    Return_stmt_prime = 'Return_stmt_prime'
    Expression = 'Expression'
    B = 'B'
    H = 'H'
    Simple_expression_zegond = 'Simple_expression_zegond'
    Simple_expression_prime = 'Simple_expression_prime'
    C = 'C'
    Relop = 'Relop'
    Additive_expression = 'Additive_expression'
    Additive_expression_prime = 'Additive_expression_prime'
    Additive_expression_zegond = 'Additive_expression_zegond'
    D = 'D'
    Addop = 'Addop'
    Term = 'Term'
    Term_prime = 'Term_prime'
    Term_zegond = 'Term_zegond'
    G = 'G'
    Factor = 'Factor'
    Var_call_prime = 'Var_call_prime'
    Var_prime = 'Var_prime'
    Factor_prime = 'Factor_prime'
    Factor_zegond = 'Factor_zegond'
    Args = 'Args'
    Arg_list = 'Arg_list'
    Arg_list_prime = 'Arg_list_prime'


def get_state_by_name(name):
    for state in States:
        if state.value == name:
            return state
    return None


class Rule:
    def __init__(self, LHS: States, RHS: list):
        self.LHS = LHS
        self.RHS = RHS.copy()

    def appliable(self, token: Token):
        token_value = self.get_token_value(token)
        if token_value in FIRSTS[self.LHS.value]:
            variable = self.RHS[0]
            if variable in Terminals:
                if variable == token_value:
                    return True
                elif variable == 'EPSILON':
                    if token_value in FOLLOWS[self.LHS.value]:
                        return True
            elif token_value in FIRSTS[variable.value]:
                return True
            elif token_value in FOLLOWS[variable.value] and 'EPSILON' in FIRSTS[variable.value]:
                return True
            # if variable in Terminals:
            #     if variable == token_value:
            #         return True
            #     elif variable == 'EPSILON':
            #         if token_value in FOLLOWS[self.LHS.value]:
            #             return True
            # elif token_value in FIRSTS[variable.value]:
            #     return True
            # elif token_value in FOLLOWS[variable.value]:
            #     return True
            # else:
            #     return False
        if token_value in FOLLOWS[self.LHS.value] and 'EPSILON' in FIRSTS[self.LHS.value]:
            flag = True
            for variable in self.RHS:
                if variable in Terminals:
                    if variable == 'EPSILON':
                        continue
                    else:
                        flag = False
                        break
                if 'EPSILON' not in FIRSTS[variable.value]:
                    flag = False
                    break
            if flag:
                return True
        return False

    def get_token_value(self, token):
        token_value = token.string
        if token.type in [TokenType.ID, TokenType.NUM]:
            token_value = token.type.value
        return token_value


def create_rule_from_production(state, path):
    rhs = []
    for variable in path:
        if get_state_by_name(variable) is not None:
            rhs.append(get_state_by_name(variable))
        elif variable in Terminals:
            rhs.append(variable)
    the_rule = Rule(state, rhs)
    return the_rule


class Transition:
    def __init__(self, variable, rules):
        self.variable = variable
        self.rules = rules

    def get_token_value(self, token):
        token_value = token.string
        if token.type in [TokenType.ID, TokenType.NUM]:
            token_value = token.type.value
        return token_value

    def appliable(self, token: Token):
        for rule in self.rules:
            if rule.appliable(token):
                return rule
        return None


# creating transitions and rules from the production.json file
file = open('./Productions.json')
json_file = json.load(file)
file.close()
productions = json_file
transitions = {}
# iterate over all the names in States Enum
for initial_state in States:
    if initial_state.value in Terminals:
        continue
    transition = Transition(initial_state, [])
    for production in productions[initial_state.value]:
        rule = create_rule_from_production(initial_state, production)
        transition.rules.append(rule)
    transitions[initial_state.value] = transition

# rule = transitions['Term_prime'].rules[0]
# print(rule.LHS, rule.RHS)
# token = Token(TokenType.SYMBOL, "*",5)
# print(rule.appliable(token))
# # exit the program
# exit(0)


file = open('./P2_testcases/T01/input.txt', 'r')
table = SymbolTable()
scanner = Scannerr(file.read(), table)
file.close()
token = new_token()
print("New Token:", token)
# queue = [get_state_by_name('Program')]
id_counter = 2
queue = [(get_state_by_name('Program'), 1), ('$', 2)]
adj = {}

while True:
    current_state = queue[0][0]
    print("Current State:", current_state.value if type(current_state) == States else current_state)
    print("id", queue[0][1])
    if current_state == '$':
        adj[queue[0][1]] = ([],'$')
        queue.pop(0)
        break
    if current_state == 'EPSILON':
        adj[queue[0][1]] = ([], 'EPSILON')
        queue.pop(0)
        continue
    if current_state in Terminals:
        if current_state == token.string:
            adj[queue[0][1]] = ([], token)
            queue.pop(0)
            token = new_token()
            print("New Token:", token)
            continue
        elif current_state == 'NUM':
            if token.type == TokenType.NUM:
                adj[queue[0][1]] = ([], token)
                queue.pop(0)
                token = new_token()
                print("New Token:", token)
                continue
        elif current_state == 'ID':
            if token.type == TokenType.ID:
                adj[queue[0][1]] = ([], token)
                queue.pop(0)
                token = new_token()
                print("New Token:", token)
                continue
        else:
            raise Exception('Syntax Error')
    transition = transitions[current_state.value]
    rule = transition.appliable(token)
    if rule is None:
        raise Exception('meow Error')
    else:
        # print(rule.LHS, rule.RHS)
        adj[queue[0][1]] = ([], rule.LHS.value)
        new_states = [(variable, id_counter + i + 1) for i, variable in enumerate(rule.RHS)]
        print("new states", new_states)
        id_counter += len(rule.RHS)
        # adj[queue[0][1]][0].append([state[1] for state in new_states])
        for state in new_states:
            adj[queue[0][1]][0].append(state[1])
        queue.pop(0)
        queue = new_states + queue
        print("new queue", queue)
        # print(rule.LHS.value, '->',
        #       ' '.join([variable.value if type(variable) == States else variable for variable in rule.RHS]))


def get_name_of_children(adj, node):
    neighbors = adj[node][0]
    names = []
    for neighbor in neighbors:
        names.append(adj[neighbor][1])
    return names


def create_tree(adj: dict):
    root = Node("Program")
    current_node = 1
    stack = [current_node]
    visited = []
    node_map = {1: root}
    while stack:
        current_node = stack[-1]
        stack.pop()
        father = node_map[current_node]
        for node in reversed(adj[current_node][0]):
            stack.append(node)
            tree_node = Node(adj[node][1], parent=father)
            node_map[node] = tree_node
    return root


def draw_tree(adj: dict):
    root = create_tree(adj)
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))

# draw_tree(adj)
