class SymbolTableManager:
    def __init__(self):
        self.symbol_table = {}
        """
        {lexeme : [type , addr , size]}
        """
        self.addr_counter = 500

    def insert_id(self, lexeme: str):
        self.symbol_table[lexeme] = ["int", None, None]

    def insert_keyword(self, lexeme: str):
        self.symbol_table[lexeme] = ["keyword", None, None]

    def set_id(self, addr, size):
        lexeme = None
        for each_lexeme in self.symbol_table:
            if self.symbol_table[each_lexeme][1] == addr:
                lexeme = each_lexeme
                break
        self.symbol_table[lexeme][1] = self.addr_counter
        self.symbol_table[lexeme][2] = size
        self.addr_counter += (4 * size)

    def get_addr(self, lexeme: str):
        if self.symbol_table[lexeme][1] is None:
            self.symbol_table[lexeme][1] = self.addr_counter
            self.addr_counter += 4
        return self.symbol_table[lexeme][1]

    def get_addr_for_temp(self):
        self.addr_counter += 4
        return self.addr_counter - 4

    def is_in_symbol_table(self, lexeme: str):
        return lexeme in self.symbol_table
