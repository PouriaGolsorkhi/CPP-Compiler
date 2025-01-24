import re

TOKEN_PATTERNS = [
    ("reservedword", r"\b(int|float|void|return|if|while|cin|cout|continue|break|include|using|iostream|namespace|std|main)\b"),
    ("identifier", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("number", r"\b\d+(\.\d+)?\b"),  
    ("symbol", r"[\|,;+\-*/=!><=()\{\}]"),  
    ("string", r"(['\"]).*?\1"),  
    ("WHITESPACE", r"\s+"), 
]

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

# testing the lexical analyzer and tokenization:

if __name__ == "__main__":

    input_code = """
    int main() {
        float x = 3.14;
        int y = x + 5;
        return y;
    }
    """

    tokens = lexical_analyzer(input_code)

    print("Tokens :")
    for token in tokens:
        print(token)

