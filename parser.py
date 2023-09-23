from anytree import Node, RenderTree
import json
from scanner import Scanner
from codeGenerator import CodeGenerator
from symbolTableManager import SymbolTableManager


class Parser:
    def __init__(self):
        self.symbol_table_manager = SymbolTableManager()
        self.scanner = Scanner(self.symbol_table_manager)
        self.code_generator = CodeGenerator(self.symbol_table_manager)
        self.syntax_errors = []
        self.root = Node("program")
        data = json.load(open('table.json'))
        self.terminals = data['terminals']
        self.non_terminals = data['non_terminals']
        self.first = data['first']
        self.follow = data['follow']
        self.grammar = data['grammar']
        self.parse_table = data['parse_table']

    def run(self):
        finished = False
        stack = ["0"]  # at first, we push 0 into stack
        node_stack = []
        cur_token, token = self.get_next_token()
        while not finished:
            state = stack[-1]
            if cur_token in self.parse_table[state].keys():  # non-empty entry
                action = self.parse_table[state][cur_token].split("_")
                if action[0] == "shift":  # SHIFT
                    stack.append(action[1])
                    node_stack.append(Node(token))  # add current token to parse tree, node_stack
                    cur_token, token = self.get_next_token()
                elif action[0] == "reduce":  # REDUCE
                    rule = self.grammar[action[1]]
                    self.code_generator.code_gen(action[1], self.get_token_for_error(token))
                    r = len(rule) - 2  # len(rhs) = len(rule) -{(len(->) + len(lhs)} [, len(lhs) = 1 (CFG)]
                    A = rule[0]  # A = lhs
                    if not (r == 1 and rule[2] == "epsilon"):  # not epsilon rule
                        children = node_stack[-r:]  # children = rhs
                        del node_stack[-r:]
                        del stack[-r:]
                    else:  # epsilon rule
                        # len(rhs) = 0 -> no pop from stack
                        children = [Node("epsilon")]  # children = rhs = epsilon
                    node_stack.append(Node(A, children=children))  # add lhs to parse tree, node_stack
                    top = stack[-1]
                    s = self.parse_table[top][A].split("_")[1]  # goto GOTO(top)
                    stack.append(s)
                elif action[0] == "accept":  # ACCEPT
                    Node(cur_token, parent=node_stack[0])  # add $ to parse tree
                    del node_stack[-1]
                    finished = True
            else:  # error (empty entry)
                token_for_error = self.get_token_for_error(token)
                new_str = "#" + str(self.scanner.get_lineno()) + " : syntax error , illegal " + str(token_for_error)
                self.syntax_errors.append(new_str)
                cur_token, token = self.get_next_token()  # discard current token
                while True:
                    s = stack[-1]
                    if not self.has_goto(s):  # a) Skip till you reach a state S which has a goto to another
                        # non-terminal
                        del stack[-1]
                        new_str = "syntax error , discarded " + node_stack[-1].name + " from stack"
                        self.syntax_errors.append(new_str)
                        del node_stack[-1]
                        continue
                    GOTOs, non_ts = self.get_goto(s)  # GOTOs : all non-terminals in goto(s) with their goto state
                    # result , non_ts: alphabetically sorted non-terminals
                    A = None
                    goto = None
                    found_t = False
                    while not found_t:  # b) Discard zero or more input symbols till you reach a symbol that can follow
                        # one of the non-terminals in the goto of s
                        for non_t in non_ts:
                            if cur_token in self.follow[non_t]:
                                A = non_t
                                goto = GOTOs[A]
                                found_t = True
                                break
                        if found_t:
                            break
                        token_for_error = self.get_token_for_error(token)
                        new_str = "#" + str(self.scanner.get_lineno()) + " : syntax error , discarded " + str(
                            token_for_error) + " from input"
                        self.syntax_errors.append(new_str)
                        cur_token, token = self.get_next_token()
                        if cur_token == "$":
                            new_str = "#" + str(self.scanner.get_lineno()) + " : syntax error , Unexpected EOF"
                            self.syntax_errors.append(new_str)
                            return
                    new_str = "#" + str(self.scanner.get_lineno()) + " : syntax error , missing " + str(A)
                    self.syntax_errors.append(new_str)
                    # c) Stack the non-terminal A and goto [S,A] and continue parsing as normal
                    stack.append(goto)
                    node_stack.append(Node(A))
                    break
        self.save_code(self.code_generator.get_code())

    def get_next_token(self):
        while True:
            token_type, lexeme = self.scanner.get_next_token()  # calls scanner for next token
            if token_type == "WHITESPACE" or token_type == "COMMENT":  # ignores token if it is whitespace or comment
                continue
            if lexeme in self.terminals:
                token = lexeme
            else:
                token = token_type
            return token, str("(" + token_type + ", " + lexeme + ")")

    def write_parse_tree(self, node_stack):  # write on parse tree file using anytree render method
        res_str = ""
        for pre, fill, node in RenderTree(node_stack[-1]):
            res_str += ("%s%s" % (pre, node.name)) + "\n"
        f = open("parse_tree.txt", "w+")
        f.write(res_str.strip())
        f.close()

    def has_goto(self, s):  # check if state has goto to any other state
        line = self.parse_table[s]
        for key in line:
            if line[key].startswith("goto"):
                return True
        return False

    def get_goto(self, s):  # return all non-terminals with goto and their goto, and also an alphabetically sorted
        # list of these non-terminals
        keys = []
        goto = {}
        line = self.parse_table[s]
        for key, value in sorted(line.items()):
            if value.startswith("goto"):
                goto[key] = value.split("_")[1]
                keys.append(key)
        return goto, keys

    def write_errors(self):  # writes errors in syntax_errors.txt
        res_str = ""
        if not self.syntax_errors:
            res_str = "There is no syntax error."
        else:
            for error in self.syntax_errors:
                res_str += error + "\n"
        f = open("syntax_errors.txt", "w+")
        f.write(res_str)
        f.close()

    def get_token_for_error(self, token):
        lexeme = token.split(" ")[1][:-1]
        return lexeme

    def save_code(self, pb: dict):
        to_save = ""
        lines = []
        for line in pb:
            lines.append(int(line))
        for line in sorted(lines):
            to_save += str(line) + "\t" + pb[line] + "\n"
        f = open("output.txt", "w+")
        f.write(to_save)
        f.close()
