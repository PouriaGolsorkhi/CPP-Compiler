import re
from collections import defaultdict

TOKEN_PATTERNS = [
    ("reservedword", r"\b(int|float|void|return|if|while|cin|cout|continue|break|include|using|iostream|namespace|std|main)\b"),
    ("identifier", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("number", r"\b\d+(\.\d+)?\b"),  
    ("symbol", r"[\|,;+\-*/=!><=()\{\}]"),  
    ("string", r"(['\"]).*?\1"),  
    ("WHITESPACE", r"\s+"), 
]

# CFG
cfg = {
    "Start": ["S N M"],
    "S": ["#include S", "ε"],
    "N": ["using namespace std;", "ε"],
    "M": ["int main() { T V }"],
    "T": ["Id T", "L T", "Loop T", "Input T", "Output T", "ε"],
    "V": ["return 0;", "ε"],
    "Id": ["int L", "float L"],
    "L": ["identifier Assign Z"],
    "Z": [", identifier Assign Z", ";"],
    "Loop": ["while(Expression) { T }"],
    "Input": ["cin >> identifier F;"],
    "Output": ["cout << CH;"],
    "C": ["number", "string", "identifier"],
}

# First
first_sets = {
    "Start": {"#", "using", "int"},
    "S": {"#", "ε"},
    "N": {"using", "ε"},
    "M": {"int"},
    "T": {"int", "float", "while", "cin", "cout", "ε"},
    "V": {"return", "ε"},
    "Id": {"int", "float"},
    "L": {"identifier"},
    "Z": {",", ";"},
    "Loop": {"while"},
    "Input": {"cin"},
    "Output": {"cout"},
    "C": {"number", "string", "identifier"},
}

# Follow
follow_sets = {
    "Start": {"$"},
    "S": {"using", "int"},
    "N": {"int"},
    "M": {"$"},
    "T": {"return", "}"},
    "V": {"}"},
    "Id": {"identifier"},
    "L": {"T"},
    "Z": {"T"},
    "Loop": {"T"},
    "Input": {"T"},
    "Output": {"T"},
    "C": {";"},
}

def lexical_analyzer(input_code):
    tokens = []
    position = 0

    while position < len(input_code):
        match_found = False

        for token_type, pattern in TOKEN_PATTERNS:
            regex = re.compile(pattern)
            match = regex.match(input_code, position)  
            
            if match:
                lexeme = match.group(0)
                if token_type != "WHITESPACE":  
                    tokens.append((token_type, lexeme))
                position += len(lexeme)  
                match_found = True
                break  

        if not match_found:
            raise ValueError(f"Unexpected character at position {position}: {input_code[position]}")

    return tokens

def create_parse_table(cfg, first_sets, follow_sets):
    """
    Generate a Parse Table for an LL(1) grammar.
    """
    parse_table = defaultdict(dict)

    for non_terminal, productions in cfg.items():
        for production in productions:
            first = compute_first(production, first_sets)

            for terminal in first - {"ε"}:
                parse_table[non_terminal][terminal] = production

            if "ε" in first:
                for terminal in follow_sets.get(non_terminal, []):
                    parse_table[non_terminal][terminal] = production

    return parse_table

def compute_first(production, first_sets):
    """
    Compute the First set for a given production.
    """
    first = set()
    for symbol in production.split():
        if symbol.islower() or symbol in {",", ";", "(", ")"}:
            first.add(symbol)
            break
        elif symbol in first_sets:
            first.update(first_sets[symbol] - {"ε"})
            if "ε" not in first_sets[symbol]:
                break
        else:
            break
    return first

def display_parse_table(parse_table):
    """
    Display the parse table in a readable format.
    """
    terminals = sorted({t for rules in parse_table.values() for t in rules})
    non_terminals = sorted(parse_table.keys())

    print(f"{'Non-Terminal':<15} | {' | '.join(terminals)}")
    print("-" * (17 + len(terminals) * 4))

    for non_terminal in non_terminals:
        row = [non_terminal]
        for terminal in terminals:
            row.append(parse_table[non_terminal].get(terminal, " "))
        print(f"{row[0]:<15} | {' | '.join(row[1:])}")


# testing the lexical analyzer and tokenization:

if __name__ == "__main__":

    input_code = """
    int main() {
        float x = 3.14;
        int y = x + 5;
        return y;
    }
    """
    
    print("Step 1: Token Table Generation")
    tokens = lexical_analyzer(input_code)
    for token in tokens:
        print(token)

    print("\nStep 2: Parse Table Generation")
    parse_table = create_parse_table(cfg, first_sets, follow_sets)
    display_parse_table(parse_table)


