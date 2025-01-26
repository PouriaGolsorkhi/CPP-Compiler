import re
from collections import defaultdict

import re
from collections import defaultdict

# token
TOKEN_PATTERNS = [
    ("reservedword", r"\b(int|float|void|return|if|while|cin|cout|continue|break|using|iostream|namespace|std|main|for|class|#include)\b"),
    ("identifier", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("number", r"\b\d+(\.\d+)?\b"),
    ("symbol", r"[\|,;+\-*/=!><=()\{\}]"),
    ("string", r"(['\"]).*?\1"),
    ("WHITESPACE", r"\s+"),
]


# Lexer for tokens
class Lexer:
    def __init__(self, token_patterns):
        self.token_patterns = token_patterns
        self.regex_patterns = [(name, re.compile(pattern)) for name, pattern in token_patterns]

    def tokenize(self, code):
        tokens = []
        pos = 0
        while pos < len(code):
            match = None
            for token_name, regex in self.regex_patterns:
                regex_match = regex.match(code, pos)
                if regex_match:
                    match = (token_name, regex_match.group(0))
                    break
            if not match:
                raise Exception(f"Invalid token at position {pos}: {code[pos]}")
            token_name, token_value = match
            if token_name != "WHITESPACE":  # نادیده گرفتن فاصله‌ها
                tokens.append((token_name, token_value))
            pos = regex_match.end()
        return tokens


# cfg
grammar = {
    "Start": ["S N M"],
    "S": ["#include S", "ε"],
    "N": ["using namespace std ;", "ε"],
    "M": ["int main ( ) { T V }"],
    "T": ["Id T", "L T", "Loop T", "Input T", "Output T", "ε"],
    "V": ["return 0 ;", "ε"],
    "Id": ["int L", "float L"],
    "L": ["identifier Assign Z"],
    "Z": [", identifier Assign Z", ";"],
    "Operation": ["number P", "identifier P"],
    "P": ["O W P", "ε"],
    "O": ["+", "-", "*"],
    "W": ["number", "identifier"],
    "Assign": ["= Operation", "ε"],
    "Expression": ["Operation K Operation"],
    "K": ["==", ">=", "<=", "!="],
    "Loop": ["while ( Expression ) { T }"],
    "Input": ["cin >> identifier F ;"],
    "F": [">> identifier F", "ε"],
    "Output": ["cout << C H ;"],
    "H": ["<< C H", "ε"],
    "C": ["number", "string", "identifier"]
}


#First
first_sets = {
    "Start": {"#include", "using", "int"},
    "S": {"#include", "ε"},
    "N": {"using", "ε"},
    "W": {"identifier", "number"},
    "M": {"int"},
    "T": {"int", "float", "identifier", "while", "cin", "cout", "ε"},
    "V": {"return", "ε"},
    "L": {"identifier"},
    "P": {"ε", "+", "*", "-"},
    "O": {"+", "*", "-"},
    "Z": {",", ";"},
    "K": {"!=", "<=", ">=", "=="},
    "F": {"ε", ">>"},
    "H": {"ε", "<<"},
    "C": {"number", "string", "identifier"},
    "Id": {"int", "float"},
    "Loop": {"while"},
    "Input": {"cin"},
    "Output": {"cout"},
    "Expression": {"identifier", "number"},
    "Operation": {"identifier", "number"},
    "Assign": {"ε", "="},
}

#Follow

def compute_follow():
    follow_sets = {}
    for lhs in grammar:
        follow_sets[lhs] = set()
    follow_sets["Start"].add("$")
    updated = True
    while(updated):
        updated = False
        for lhs in grammar: 
            for production in grammar[lhs]:
                production_symbols = production.split()
                for i, sym in enumerate(production_symbols):
                    if sym in grammar:
                        allepsilon = True
                        before_size = len(follow_sets[sym])
                        for j in range(1,len(production_symbols) - i):
                            next_symbol = production_symbols[i + j]
                            if next_symbol in grammar:
                                follow_sets[sym].update(first_sets[next_symbol] - {"ε"})
                                if "ε" not in first_sets[next_symbol]:
                                    allepsilon = False
                                    break
                            else:
                                follow_sets[sym].add(next_symbol)
                                allepsilon = False
                                after_size = len(follow_sets[sym])
                                if after_size != before_size:
                                    updated = True
                                break
                            after_size = len(follow_sets[sym])
                            if after_size != before_size:
                                updated = True
                        if allepsilon:
                            follow_sets[sym].update(follow_sets[lhs])
                            after_size = len(follow_sets[sym])
                            if after_size != before_size:
                                updated = True
    return follow_sets

# creating and saving parse table
def create_parse_table(grammar, first_sets, follow_sets):
    parse_table = defaultdict(dict)
    for non_terminal in grammar:
        for production in grammar[non_terminal]:
            first = set()
            for symbol in production.split():
                if symbol in first_sets:
                    first.update(first_sets[symbol])
                    if "ε" not in first_sets[symbol]:
                        if "ε" in first:
                            first.remove("ε")
                        break
                else:
                    first.add(symbol)
                    break
            for terminal in first:
                if terminal != "ε":
                    parse_table[non_terminal][terminal] = production
            if "ε" in first:
                
                follow_sets[non_terminal]
                for terminal in follow_sets[non_terminal]:
                    parse_table[non_terminal][terminal] = production
    return parse_table

def save_parse_table(parse_table,filename="parse_table.txt"):
    terminals = set()
    for non_terminal in parse_table:
        terminals.update(parse_table[non_terminal].keys())
    terminals = sorted(terminals)

    col_width = 30 
    non_term_width = 15 

    with open(filename, "w", encoding="utf-8") as file:
        file.write("+" + "-" * (non_term_width + 2) + "+" + ("-" * (col_width + 2) + "+") * len(terminals) + "\n")
        file.write("| {:<{}} |".format("Non-Term", non_term_width))
        for terminal in terminals:
            file.write(" {:<{}} |".format(terminal, col_width))
        file.write("\n")
        file.write("+" + "-" * (non_term_width + 2) + "+" + ("-" * (col_width + 2) + "+") * len(terminals) + "\n")

        for non_terminal in parse_table:
            file.write("| {:<{}} |".format(non_terminal, non_term_width))
            for terminal in terminals:
                if terminal in parse_table[non_terminal]:
                    production = " ".join(parse_table[non_terminal][terminal].split())
                    file.write(" {:<{}} |".format(production, col_width))
                else:
                    file.write(" {:<{}} |".format("[]", col_width))
            file.write("\n")
        file.write("+" + "-" * (non_term_width + 2) + "+" + ("-" * (col_width + 2) + "+") * len(terminals) + "\n")


def display_token_table(tokens):
    headers = ['Token Name', 'Token Value']
    col_width = max(len(str(token)) for token in tokens) + 2

    # Header
    print("+" + "-" * (col_width + 2) + "+" + ("-" * (col_width + 2) + "+"))
    print("| {:<{}} | {:<{}} |".format(headers[0], col_width, headers[1], col_width))
    print("+" + "-" * (col_width + 2) + "+" + ("-" * (col_width + 2) + "+"))

    for token in tokens:
        print("| {:<{}} | {:<{}} |".format(token[0], col_width, token[1], col_width))
    print("+" + "-" * (col_width + 2) + "+" + ("-" * (col_width + 2) + "+"))

lexer = Lexer(TOKEN_PATTERNS)

# Main
if __name__ == "__main__":
    input_code = """
    int main() {
        float x = 3.14;
        int y = x + 5;
        return y;
    }
    """

    tokens = lexer.tokenize(input_code)
    print("Tokens:")
    display_token_table(tokens)

    mapped_tokens = map_tokens_to_grammar(tokens)

    follow_sets = compute_follow()
    print(follow_sets)
    parse_table = create_parse_table(grammar, first_sets, follow_sets)
    saved_parse_table = save_parse_table(parse_table , filename="parse_table.txt")
