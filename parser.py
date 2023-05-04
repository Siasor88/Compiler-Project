# create an enum with choices a and b and c
import enum
from compiler import Scannerr, Token, SymbolTable, TokenType

f = open('input.txt', 'r')
table = SymbolTable()
scanner = Scannerr(f.read(), table)
f.close()
tokens = []
errors = []


class TransitionTypes(enum):
    Terminal = 1
    NonTerminal = 2


states = []


def get_state_by_name(name):
    for state in states:
        if state.name == name:
            return state
    return None


def get_state_by_id(id):
    return states[id]


# create a class for states
class State:
    def __init__(self, name, is_final):
        self.name = name
        self.transitions = []
        self.id = len(states)
        states.append(self)
        self.first = []
        self.follow = []
        self.is_final = is_final

    def move(self, token):
        for transition in self.transitions:
            if transition.transition_type == TransitionTypes.Terminal:
                if transition.symbol == "ID" or transition.symbol == "NUM":
                    if token.TokenType == TokenType.ID or token.TokenType == TokenType.NUM:
                        #todo get_new_token should be called and the token should be updated
                        return transition.final_state
                elif transition.symbol == token.value:
                    # todo get_new_token should be called and the token should be updated
                    return transition.final_state
            elif transition.transition_type == TransitionTypes.NonTerminal and token.TokenType in self.first:
                #todo: move(new_state) should be called and if upon success, the transition should take place
                return transition.final_state
        #todo if no transition is found, an error should be raised
        return None


class Transition:
    def __init__(self, transition_type, initial_state, final_state, symbol):
        self.transition_type = transition_type
        self.initial_state = initial_state
        self.final_state = final_state
        self.symbol = symbol
        self.initial_state.transitions.append(self)


# TODO : add transitions and states and first and follow sets for grammar


token = scanner.get_next_token()
starting_state = None
while token.TokenType != TokenType.EOF:
    print("meow")
