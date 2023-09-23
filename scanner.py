from symbolTableManager import SymbolTableManager
dfa_matrix = {
    0: {"digit": 1, "letter": 20, "/": 4, "symbol": 10, "*": 11, "=": 14, "whitespace": 17, "\n": 17, "other": 19},
    1: {"digit": 1, "letter": 18, "/": 2, "symbol": 2, "*": 2, "=": 2, "whitespace": 2, "\n": 2, "other": 19},
    2: {"digit": None, "letter": None, "/": None, "symbol": None, "*": None, "=": None, "whitespace": None, "\n": None,
        "other": None},
    3: {"digit": None, "letter": None, "/": None, "symbol": None, "*": None, "=": None, "whitespace": None, "\n": None,
        "other": None},
    4: {"digit": None, "letter": None, "/": 8, "symbol": None, "*": 5, "=": None, "whitespace": None, "\n": None,
        "other": 19},
    5: {"digit": 5, "letter": 5, "/": 5, "symbol": 5, "*": 6, "=": 5, "whitespace": 5, "\n": 5, "other": 5},
    6: {"digit": 5, "letter": 5, "/": 7, "symbol": 5, "*": 6, "=": 5, "whitespace": 5, "\n": 5, "other": 5},
    7: {"digit": None, "letter": None, "/": None, "symbol": None, "*": None, "=": None, "whitespace": None, "\n": None,
        "other": None},
    8: {"digit": 8, "letter": 8, "/": 8, "symbol": 8, "*": 8, "=": 8, "whitespace": 8, "\n": 9, "other": 8},
    9: {"digit": None, "letter": None, "/": None, "symbol": None, "*": None, "=": None, "whitespace": None, "\n": None,
        "other": None},
    10: {"digit": None, "letter": None, "/": None, "symbol": None, "*": None, "=": None, "whitespace": None, "\n": None,
         "other": None},
    11: {"digit": None, "letter": None, "/": 13, "symbol": None, "*": None, "=": None, "whitespace": None, "\n": None,
         "other": 19},
    13: {"digit": None, "letter": None, "/": None, "symbol": None, "*": None, "=": None, "whitespace": None, "\n": None,
         "other": None},
    14: {"digit": 16, "letter": 16, "/": 16, "symbol": 16, "*": 16, "=": 15, "whitespace": 16, "\n": 16, "other": 19},
    15: {"digit": None, "letter": None, "/": None, "symbol": None, "*": None, "=": None, "whitespace": None, "\n": None,
         "other": None},
    16: {"digit": None, "letter": None, "/": None, "symbol": None, "*": None, "=": None, "whitespace": None, "\n": None,
         "other": None},
    17: {"digit": None, "letter": None, "/": None, "symbol": None, "*": None, "=": None, "whitespace": 17, "\n": None,
         "other": None},
    18: {"digit": None, "letter": None, "/": None, "symbol": None, "*": None, "=": None, "whitespace": None, "\n": None,
         "other": None},
    19: {"digit": None, "letter": None, "/": None, "symbol": None, "*": None, "=": None, "whitespace": None, "\n": None,
         "other": None},
    20: {"digit": 20, "letter": 20, "/": 3, "symbol": 3, "*": 3, "=": 3, "whitespace": 3, "\n": 3, "other": 19}
}

error_states = {13, 18, 19}
final_states = {2, 3, 7, 9, 13, 10, 15, 16, 17, 4, 11}
final_star_states = {2, 3, 16}  # states regarding NUM, ID and KEYWORD, and = Symbol

symbols = [";", ":", ",", "[", "]", "(", ")", "{", "}", "+", "-", "<"]
letters = [chr(n) for n in range(ord("a"), ord("z") + 1)] + [chr(n) for n in range(ord("A"), ord("Z") + 1)]
digits = [str(n) for n in range(0, 10)]
whitespaces = [" ", "\r", "\f", "\v", "\t"]


def read_input():
    f = open("input.txt", "r")
    result = f.read()
    return result


def get_char_type(current_char):
    if current_char in symbols:
        return "symbol"
    if current_char in digits:
        return "digit"
    if current_char in letters:
        return "letter"
    if current_char in whitespaces:
        return "whitespace"
    if current_char == "/" or current_char == "*" or current_char == "=" or current_char == "\n":
        return current_char
    return "other"


class Scanner:
    def __init__(self, symbol_table_manager : SymbolTableManager):
        self.lineno = 1
        self.input = read_input()
        self.lexical_errors = {self.lineno: []}
        self.tokens = {self.lineno: []}
        self.keywords = ["if", "else", "void", "int", "while", "break", "switch", "default", "case", "return",
                         "endif"]
        self.symbol_table_manager = symbol_table_manager
        for keyword in self.keywords:
            self.symbol_table_manager.insert_keyword(keyword)

    def get_next_token(self):
        cur_state = 0
        end_of_input = False
        while True:
            end_of_input = end_of_input or (self.input == "")
            if end_of_input:
                if cur_state == 5 or cur_state == 6 or cur_state == 8:
                    seen_comment = self.input[:7]
                    error_message = seen_comment
                    if len(self.input) > 7:
                        error_message = error_message + "..."
                    self.lexical_errors[self.lineno].append((error_message, "Unclosed comment"))
                return "EOF", "$"
            error_seen = False
            longest_token = None
            cur_state = 0
            next_state = None
            for i in range(len(self.input) + 1):  # read characters from input until reaching None state
                if cur_state in error_states:
                    self.save_errors(cur_state, i)
                    self.input = self.input[i:]  # panic mode
                    error_seen = True
                    break
                if cur_state in final_states:
                    if cur_state in final_star_states:
                        longest_token = [cur_state, self.input[:i - 1]]
                    else:
                        longest_token = [cur_state, self.input[:i]]
                if i == len(self.input):
                    current_char = self.input[i - 1]
                else:
                    current_char = self.input[i]
                current_char_type = get_char_type(current_char)
                next_state = dfa_matrix[cur_state][current_char_type]
                if next_state is None:
                    break
                if i == len(self.input):
                    end_of_input = True
                    break
                cur_state = next_state
            if not error_seen and not end_of_input and (next_state is None):
                if longest_token:
                    state = longest_token[0]
                    lexeme = longest_token[1]
                    token_type = self.state_to_type(state, lexeme)
                    self.input = self.input[len(lexeme):]  # go further in the input (for next tokens)
                    if token_type == "WHITESPACE" or token_type == "COMMENT":  # no need to save these tokens, and only these tokens can change line number
                        self.change_lineno(lexeme)
                        continue
                    self.tokens[self.lineno].append((token_type, lexeme))
                    if token_type == "ID" and \
                            not self.symbol_table_manager.is_in_symbol_table(lexeme):  # add IDs to symbol table
                        self.symbol_table_manager.insert_id(lexeme)
                        # self.symbol_table.append(lexeme)
                    return token_type, lexeme

    def save_errors(self, state, i):
        if state == 19:
            self.lexical_errors[self.lineno].append((self.input[:i], "Invalid input"))
        elif state == 18:
            self.lexical_errors[self.lineno].append((self.input[:i], "Invalid number"))
        elif state == 13:
            self.lexical_errors[self.lineno].append((self.input[:i], "Unmatched comment"))

    def change_lineno(self, lexeme: str):
        count_of_newlines = lexeme.count("\n")
        for i in range(1, count_of_newlines + 1):
            self.tokens[self.lineno + i] = []
            self.lexical_errors[self.lineno + i] = []
        self.lineno += count_of_newlines

    def state_to_type(self, state, lexeme):
        if state == 17:
            return "WHITESPACE"
        if state == 7 or state == 9:
            return "COMMENT"
        if state == 10 or state == 15 or state == 16 or state == 11 or state == 4:
            return "SYMBOL"
        if state == 3:
            if lexeme in self.keywords:
                return "KEYWORD"
            return "ID"
        if state == 2:
            return "NUM"
        return None

    def get_lineno(self):
        return self.lineno
