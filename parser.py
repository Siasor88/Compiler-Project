# create an enum with choices a and b and c
from enum import Enum
from compiler import Scannerr, Token, SymbolTable, TokenType
import json

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


class TransitionTypes(Enum):
    Terminal = 1
    NonTerminal = 2


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





# create a class for states
class State:
    def __init__(self, name, is_final):
        self.name = name
        self.transitions = []
        # self.id = len(all_states)
        # all_states.append(self)
        self.first = []
        self.follow = []
        self.is_final = is_final

    def move(self, token):
        for transition in self.transitions:
            if transition.transition_type == TransitionTypes.Terminal:
                if transition.symbol == "ID" or transition.symbol == "NUM":
                    if token.TokenType == TokenType.ID or token.TokenType == TokenType.NUM:
                        # todo get_new_token should be called and the token should be updated
                        return transition.final_state
                elif transition.symbol == token.value:
                    # todo get_new_token should be called and the token should be updated
                    return transition.final_state
            elif transition.transition_type == TransitionTypes.NonTerminal and token.TokenType in self.first:
                # todo: move(new_state) should be called and if upon success, the transition should take place
                return transition.final_state
        # todo if no transition is found, an error should be raised
        return None


class Rule:
    def __init__(self, LHS: States, RHS: list):
        self.LHS = LHS
        self.RHS = RHS.copy()

    def appliable(self, token: Token):
        token_value = self.get_token_value(token)
        if token_value in FIRSTS[self.LHS.value]:
            for variable in self.RHS:
                if variable in Terminals:
                    if variable == token_value:
                        return True
                    elif variable == 'EPSILON':
                        if token_value in FOLLOWS[self.LHS.value]:
                            return True
                elif token_value in FIRSTS[variable.value]:
                    return True
                elif 'EPSILON' not in FIRSTS[variable]:
                    return False
        if token_value in FOLLOWS[self.LHS.value]:
            return True

    def get_token_value(self, token):
        token_value = token.string
        if token.type in [TokenType.ID, TokenType.NUM]:
            token_value = token.type.value
        return token_value

    def __str__(self):
        return f'{self.LHS.value} -> ' + str.join(" ",str(self.RHS).replace(",", "").replace("]", "").replace("[", "").replace("\'", "").split())


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


file = open('./Productions.json')

json_file = json.load(file)
rules = {}
for variable in json_file.keys():
    if variable not in rules.keys():
        rules[variable] = []
    for rule in json_file[variable]:
        rules[variable].append(Rule(LHS=get_state_by_name(variable), RHS=rule))
print(rules['Declaration_list'][0])
file.close()

# TODO : add transitions and states and first and follow sets for grammar

# scanner = Scannerr()
# token = scanner.get_next_token()
# starting_state = None
# while token.TokenType != TokenType.EOF:
#     print("meow")
