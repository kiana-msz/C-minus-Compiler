from symbolTableManager import SymbolTableManager


class CodeGenerator:

    def __init__(self, symbol_table_manager: SymbolTableManager):
        self.ss = []
        self.symbol_table_manager = symbol_table_manager
        self.temp_counter = 500
        self.i = 0
        self.pb = {}
        self.breaks_of_scopes = []

    def code_gen(self, action_symbol, input_lexeme):
        action_symbol = int(action_symbol)
        if action_symbol == 72:
            self.pid(input_lexeme)
        elif action_symbol == 54 or action_symbol == 58 or action_symbol == 50:
            self.p0()
        elif action_symbol == 55 or action_symbol == 59 or action_symbol == 51:
            self.p1()
        elif action_symbol == 52:
            self.add_sub()
        elif action_symbol == 56:
            self.mult_div()
        elif action_symbol == 69:
            self.save()
        elif action_symbol == 70:
            self.jpf_save()
        elif action_symbol == 34:
            self.jp()
        elif action_symbol == 33:
            self.jpf()
        elif action_symbol == 73:
            self.label()
        elif action_symbol == 35:
            self.while_def()
        elif action_symbol == 31:
            self.jp_t_while()
        elif action_symbol == 48:
            self.relop()
        elif action_symbol == 71:
            self.pnum(input_lexeme)
        elif action_symbol == 29:
            self.output()
        elif action_symbol == 75:
            self.jpf_case()
        elif action_symbol == 74:
            self.ptop()
        elif action_symbol == 76 or action_symbol == 30:
            self.pop1()
        elif action_symbol == 78:
            self.popvar()
        elif action_symbol == 76:
            self.insert_id()
        elif action_symbol == 77:
            self.insert_arr()
        elif action_symbol == 47:
            self.insert_correct_arr()
        elif action_symbol == 79:
            self.new_scope()
        elif action_symbol == 38:
            self.switch_def()

    def pid(self, input_lexeme):
        addr = self.symbol_table_manager.get_addr(input_lexeme)
        self.ss.append(addr)

    def p_lexeme(self, input_lexeme):
        self.ss.append(input_lexeme)

    def add_sub(self):
        t = self.symbol_table_manager.get_addr_for_temp()
        if self.ss[-2] == 0:
            self.pb[self.i] = str("(ADD, " + str(self.ss[-3]) + ", " + str(self.ss[-1]) + ", " + str(t) + " )")
        else:
            self.pb[self.i] = str("(SUB, " + str(self.ss[-3]) + ", " + str(self.ss[-1]) + ", " + str(t) + " )")
        self.i += 1
        del self.ss[-3:]
        self.ss.append(str(t))

    def mult_div(self):
        t = self.symbol_table_manager.get_addr_for_temp()
        if self.ss[-2] == 0:
            self.pb[self.i] = str("(MULT, " + str(self.ss[-3]) + ", " + str(self.ss[-1]) + ", " + str(t) + " )")
        else:
            self.pb[self.i] = str("(DIV, " + str(self.ss[-3]) + ", " + str(self.ss[-1]) + ", " + str(t) + " )")
        self.i += 1
        del self.ss[-3:]
        self.ss.append(str(t))

    def assign(self):
        self.pb[self.i] = str("(ASSIGN, " + str(self.ss[-1]) + ", " + str(self.ss[-2]) + ",   )")
        self.i += 1
        del self.ss[-2:]

    def save(self):
        self.ss.append(str(self.i))
        self.i += 1

    def jpf_save(self):
        self.pb[int(self.ss[-1])] = str("(JPF, " + str(self.ss[-2]) + ", " + str(self.i + 1) + ",   )")
        del self.ss[-2:]
        self.ss.append(str(self.i))
        self.i += 1

    def jp(self):
        self.pb[int(self.ss[-1])] = str("(JP, " + str(self.i) + ",  ,   )")
        del self.ss[-1]

    def jpf(self):
        self.pb[int(self.ss[-1])] = str("(JPF, " + str(self.ss[-2]) + ", " + str(self.i) + ",   )")
        del self.ss[-2:]

    def ptemp(self):
        t = self.symbol_table_manager.get_addr_for_temp()
        self.ss.append(str(t))

    def label(self):
        self.ss.append(str(self.i))

    def while_def(self):
        self.pb[int(self.ss[-1])] = str("(JPF, " + str(self.ss[-2]) + ", " + str(self.i + 1) + ",   )")
        self.pb[self.i] = str("(JP, " + str(self.ss[-3]) + ",  ,   )")
        for j in self.breaks_of_scopes[-1]:
            self.pb[j] = str("(JP, " + str(self.i + 1) + ",  ,   )")
        del self.breaks_of_scopes[-1]
        self.i += 1
        del self.ss[-3:]

    def jp_t_while(self):
        self.breaks_of_scopes[-1].append(self.i)
        self.i += 1

    def relop(self):
        t = self.symbol_table_manager.get_addr_for_temp()
        if self.ss[-2] == 0:
            self.pb[self.i] = str("(LT, " + str(self.ss[-3]) + ", " + str(self.ss[-1]) + ", " + str(t) + " )")
        else:
            self.pb[self.i] = str("(EQ, " + str(self.ss[-3]) + ", " + str(self.ss[-1]) + ", " + str(t) + " )")
        self.i += 1
        del self.ss[-3:]
        self.ss.append(str(t))

    def p0(self):
        self.ss.append(0)

    def p1(self):
        self.ss.append(1)

    def declare_var(self):
        self.pb[self.i] = str("(ASSIGN, #0, " + str(self.ss[-1]) + ",   )")
        self.i += 1
        del self.ss[-1]

    def pnum(self, input_lexeme):
        self.ss.append(str("#" + input_lexeme))

    def output(self):
        self.pb[self.i] = str("(PRINT, " + str(self.ss[-1]) + ",  ,   )")
        self.i += 1
        del self.ss[-1]

    def jpf_case(self):
        t = self.symbol_table_manager.get_addr_for_temp()
        self.pb[int(self.ss[-2])] = str("(EQ, " + str(self.ss[-4]) + ", " + str(self.ss[-3]) + ", " + str(t) + " )")
        self.pb[int(self.ss[-1])] = str("(JPF, " + str(t) + ", " + str(self.i) + ",   )")
        del self.ss[-3:]

    def ptop(self):
        self.ss.append(self.ss[-1])

    def pop1(self):
        del self.ss[-1]

    def popvar(self):
        self.pb[self.i] = str("(ASSIGN, " + str(self.ss[-1]) + ", " + str(self.ss[-2]) + ",   )")
        self.i += 1
        del self.ss[-1]

    def insert_id(self):
        self.symbol_table_manager.set_id(self.ss[-1], 1)
        del self.ss[-1]

    def insert_arr(self):
        size = self.ss[-1]
        size = int(size.split('#')[1])
        self.symbol_table_manager.set_id(self.ss[-2], size)
        del self.ss[-2]

    def get_code(self):
        return self.pb

    def get_addr_by_lexeme(self, lexeme):
        return self.symbol_table_manager.get_addr(lexeme)

    def insert_correct_arr(self):
        t = self.symbol_table_manager.get_addr_for_temp()
        self.pb[self.i] = str("(MULT, #4, " + str(self.ss[-1]) + ", " + str(t) + " )")
        self.pb[self.i + 1] = str("(ADD, #" + str(self.ss[-2]) + ", " + str(t) + ", " + str(t) + " )")
        self.i += 2
        del self.ss[-2:]
        self.ss.append(str("@" + str(t)))

    def new_scope(self):
        self.breaks_of_scopes.append([])

    def switch_def(self):
        for j in self.breaks_of_scopes[-1]:
            self.pb[j] = str("(JP, " + str(self.i) + ",  ,   )")
        del self.breaks_of_scopes[-1]
        del self.ss[-1]
