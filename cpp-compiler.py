import re
from collections import defaultdict

# کلاس گره‌های درخت پارس
class ParseTreeNode:
    def __init__(self, symbol):
        self.symbol = symbol  
        self.children = []    

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self, level=0, prefix=""):
        if self.symbol in grammar:  
            ret = f"{prefix}├── [Non-Terminal] {repr(self.symbol)}\n"
        else:  # Terminal
            ret = f"{prefix}├── [Terminal] {repr(self.symbol)}\n"
        
        for i, child in enumerate(self.children):
            if i == len(self.children) - 1:
                ret += child.__repr__(level + 1, prefix + "    ")
            else:
                ret += child.__repr__(level + 1, prefix + "│   ")

        return ret





# تعریف الگوهای توکن‌ها
TOKEN_PATTERNS = [
    ("reservedword", r"\b(int|float|void|return|if|while|cin|cout|continue|break|using|iostream|namespace|std|main|for|class|#include)\b"),
    ("preprocessor", r"#\w+"),
    ("identifier", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("number", r"\b\d+(\.\d+)?\b"),
    ("integer", r"\b\d+\b"),
    ("symbol", r"(<<|>>|<=|>=|==|!=|\+|\-|\*|/|=|;|,|\(|\)|\{|}|\[|\]|\<|\>)"),
    ("string", r"(['\"]).*?\1"),
    ("WHITESPACE", r"\s+"),
]


# Lexer برای شناسایی توکن‌ها
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


# گرامر
grammar = {
    "Start": ["S N M"],
    "S": ["#include < iostream > S", "ε"],
    "N": ["using namespace std ;", "ε"],
    "M": ["int main ( ) { T V }"],
    "T": ["Id T", "L T", "Loop T", "Input T", "Output T", "ε"],
    "V": ["return integer ;", "ε"],
    "Id": ["int L", "float L"],
    "L": ["identifier Assign Z"],
    "Z": [", identifier Assign Z", ";"],
    "Operation": ["number P", "integer P","identifier P"],
    "P": ["O W P", "ε"],
    "O": ["+", "-", "*"],
    "W": ["number","integer", "identifier"],
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


# مجموعه‌های First
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


def compute_follow():
    follow_sets = {}
    for lhs in grammar:
        follow_sets[lhs] = set()
    follow_sets["Start"].add("$")
    changed = True
    while(changed):
        changed = False
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
                                    changed = True
                                break
                            after_size = len(follow_sets[sym])
                            if after_size != before_size:
                                changed = True
                        if allepsilon:
                            follow_sets[sym].update(follow_sets[lhs])
                            after_size = len(follow_sets[sym])
                            if after_size != before_size:
                                changed = True
    return follow_sets


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
                # محاسبه مجموعه‌های Follow برای نماد غیرپایانه
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
    headers = ['Token Name', 'Token Value', 'Hash']
    col_width = 20  # عرض ستون‌ها

    # Header
    print("+" + "+".join(["-" * (col_width + 2) for _ in headers]) + "+")
    print("| " + " | ".join(f"{header:<{col_width}}" for header in headers) + " |")
    print("+" + "+".join(["-" * (col_width + 2) for _ in headers]) + "+")

    # Rows
    ordered_tokens = ['reservedword', 'identifier', 'symbol', 'number', 'string']
    displayed = set()
    for token_name in ordered_tokens:
        token_values = [t[1] for t in tokens if t[0] == token_name]
        for token_value in token_values:
            if (token_name, token_value) not in displayed:
                hash_value = hash(token_name + token_value) 
                print("| " + " | ".join(f"{str(value):<{col_width}}" for value in [token_name, token_value, hash_value]) + " |")
                displayed.add((token_name, token_value))
    # Footer
    print("+" + "+".join(["-" * (col_width + 2) for _ in headers]) + "+")

    # Footer
    print("+" + "+".join(["-" * (col_width + 2) for _ in headers]) + "+")



def predictive_parser_with_tree(parse_table, tokens):
    stack = ["$", "Start"]
    root = ParseTreeNode("Start")
    node_stack = [root]
    i = 0
    a = tokens[i]

    while stack[-1] != "$":
        X = stack[-1]
        current_node = node_stack[-1]

        if X == a:
            stack.pop()
            node_stack.pop()
            i += 1
            if i < len(tokens):
                a = tokens[i]
        elif X not in parse_table:
            raise SyntaxError(f"Unexpected symbol '{a}', expected '{X}'")
        elif a not in parse_table[X]:
            raise KeyError(f"No production rule found for '{X}' with lookahead symbol '{a}'")
        else:
            production = parse_table[X][a]
            stack.pop()
            node_stack.pop()
            for symbol in reversed(production.split()):
                if symbol != "ε":
                    stack.append(symbol)
                child_node = ParseTreeNode(symbol)
                current_node.add_child(child_node)
                node_stack.append(child_node)

    return root


# نگاشت توکن‌ها به نمادهای گرامر
def map_tokens_to_grammar(tokens):
    mapped_tokens = []
    for token_type, token_value in tokens:
        if token_type == "Id":
            mapped_tokens.append("Id")  
        elif token_type == "identifier":
            mapped_tokens.append("identifier")      
        elif token_type == "number":
            if '.' in token_value: 
                mapped_tokens.append("number")  
            else:
                mapped_tokens.append("integer")  
        elif token_type == "string":
            mapped_tokens.append("string")
        elif token_type == "symbol":
            mapped_tokens.append(token_value)  
        else:
            mapped_tokens.append(token_value)
    return mapped_tokens




# ایجاد Lexer و تجزیه‌گر
lexer = Lexer(TOKEN_PATTERNS)

# Main
if __name__ == "__main__":
    print("Enter your code (end input with a blank line):")
    
    input_code = ""
    while True:
        line = input()
        if line == "":
            break
        input_code += line + "\n"
        
        
    # تحلیل لغوی
    tokens = lexer.tokenize(input_code)
    print("Tokens:")
    display_token_table(tokens)

    # نگاشت توکن‌ها به نمادهای گرامر
    mapped_tokens = map_tokens_to_grammar(tokens)

    # محاسبه مجموعه‌های Follow
    follow_sets = compute_follow()
    print(follow_sets)
    # ایجاد جدول پارس
    parse_table = create_parse_table(grammar, first_sets, follow_sets)
    saved_parse_table = save_parse_table(parse_table , filename="parse_table.txt")
 
    try:
        parse_tree_root = predictive_parser_with_tree(parse_table, mapped_tokens)
        print("\nParse Tree:")
        print(parse_tree_root)
    except Exception as e:
        print(f"Error during parsing: {e}")
