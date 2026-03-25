# Πιστικόπουλος Βασίλειος 5336
# Ευτυχία Μαρκοπούλου 5281

# Για να τρέξετε τον μεταφραστή, χρησιμοποιείστε την εντολή : python 5336_5281.py < όνομα_αρχείου>.gr

# θα παραχθούν τα αρχεία:
# - <όνομα_αρχείου>.c 
# - <όνομα_αρχείου>.int (τετράδες)
# - <όνομα_αρχείου>.sym (πίνακας συμβόλων)
# - <όνομα_αρχείου>.asm (assembly)



import sys
import os
    #dictionary που κραταει τα tokens και τους τυπους τους
TOKEN_ENUM = {
    # Λέξεις-κλειδιά
    "πρόγραμμα": "PROGRAMTK",
    "δήλωση": "DECLARATIONTK",
    "εάν": "IFTK",
    "τότε": "THENTK",
    "αλλιώς": "ELSETK",
    "εάν_τέλος": "IFENDTK",
    "όσο": "WHILETK",
    "όσο_τέλος": "WHILEENDTK",
    "επανάλαβε": "DOWHILETK",
    "μέχρι": "UNTILTK",
    "για": "FORTK",
    "έως": "TOTK",
    "με_βήμα": "STEPKTK",
    "για_τέλος": "FORENDTK",
    "διάβασε": "READTK",
    "γράψε": "WRITETK",
    "συνάρτηση": "FUNCTIONTK",
    "τέλος_συνάρτησης": "FUNCTIONENDTK",
    "διαδικασία": "PROCEDURETK",
    "τέλος_διαδικασίας": "PROCEDUREENDTK",
    "διαπροσωπεία": "INTERFACETK",
    "είσοδος": "INPUTTK",
    "έξοδος": "OUTPUTTK",
    "αρχή_συνάρτησης": "BEGINFUNCTIONTK",
    "αρχή_διαδικασίας": "BEGINPROCEDURETK",
    "αρχή_προγράμματος": "BEGINPROGRAMTK",
    "τέλος_προγράμματος": "ENDPROGRAMTK",
    "ή": "ORTK",
    "και": "ANDTK",
    "εκτέλεσε": "CALLTK",
    "όχι": "NOTTK",
    


    # Σύμβολα
    ":=": "ASSIGNTK",
    "+": "PLUSTK",
    "-": "MINUSTK",
    "*": "MULTTK",
    "/": "DIVTK",
    "=": "EQTK",
    "<>": "NEQTK",
    "<": "LTKTK",
    ">": "GTKTK",
    "<=": "LEQTK",
    ">=": "GEQTK",
    ";": "SEMICOLONTK",
    ",": "COMMATK",
    ":": "COLONTK",
    "(": "LPARENTK",
    ")": "RPARENTK",
    "[": "LBRACKTK",
    "]": "RBRACKTK",
    "{": "LBRACETK",
    "}": "RBRACETK",
    "%": "REFERENCETK",
    

    # Ειδικά tokens
    "ID": "IDTK",
    "INTEGER": "CONSTTK",
    "EOF": "EOFTK",
    "ERROR": "ERRORTK",
}
def get_name_from_token_type(token_type):
    # Επιστρέφει το όνομα του token από τον τύπο του
    for token_key in TOKEN_ENUM.keys():
        if TOKEN_ENUM[token_key] == token_type:
            return token_key
    
def is_letter(c):
    # Επιστρέφει True αν ο χαρακτήρας είναι ελληνικό ή λατινικό γράμμα
    return c.isalpha()

def is_digit(c):
    # Επιστρέφει True αν είναι ψηφίο 0-9
    return c.isdigit()

#κλαση για τη δημιουργία των tokens, κραταει τον τυπο, τιμη, γραμμη και στηλη του token
class Token:
    def __init__(self, type_, value, line, column=None):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f'Token(type={self.type}, value="{self.value}", line={self.line}, column={self.column})'

# Κλαση για τον λεκτικό αναλυτη
class Lexer:
    def __init__(self, input_code):
        self.input_code = input_code
        self.pos = 0  # δείκτης στην τρέχουσα θέση του κειμένου
        self.line = 1  # αρχική γραμμή
        self.column = 0  # αρχική στήλη
        self.current_char = self.input_code[self.pos] if self.pos < len(self.input_code) else None

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        else:
            self.column += 1

        self.pos += 1
        if self.pos < len(self.input_code):
            self.current_char = self.input_code[self.pos]
        else:
            self.current_char = None


    def skip_whitespace(self):
        #Αγνοεί τα κενά και τα σχόλια
        while self.current_char is not None and (self.current_char.isspace() or self.current_char == '{'):
            if self.current_char == '{':  # σχόλια
                self.skip_comment()
            else:
                self.advance()

    def skip_comment(self):
        # Παραλείπει σχόλια
        while self.current_char is not None and self.current_char != '}':
            self.advance()
        self.advance()  # Προχωρά στον χαρακτήρα μετά το '}'

    def get_next_token(self):
        self.skip_whitespace()

        if self.current_char is None:
            return Token("EOFTK", "EOF", self.line, self.column)

        if self.current_char.isdigit():
            return self.handle_number()

        if self.current_char.isalpha():
            return self.handle_identifier_or_keyword()

        if self.current_char in "+-*/=<>,;:()[]{}%":
            return self.handle_symbol()

        # Αν δεν αναγνωρίζεται
        err_char = self.current_char
        self.advance()  
        return Token("ERROR", err_char, self.line, self.column)


    def handle_number(self):
        # Επεξεργάζεται αριθμούς 
        num = ""
        while self.current_char is not None and self.current_char.isdigit():
            num += self.current_char
            self.advance()


        return Token("CONSTTK", num, self.line, self.column)

    def handle_identifier_or_keyword(self):
        # Επεξεργάζεται αναγνωριστικά και λέξεις-κλειδιά
        identifier = ""
        start_column = self.column  # αποθηκεύουμε αρχική στήλη
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            identifier += self.current_char
            self.advance()

        identifier = identifier.strip()

        # Έλεγχος μήκους για ID
        if identifier not in TOKEN_ENUM and len(identifier) > 30:
            return Token("ERROR", f"ID '{identifier}' υπερβαίνει το μέγιστο επιτρεπτό μήκος (30 χαρακτήρες)", self.line, start_column)

        # Αν είναι λέξη-κλειδί, επιστρέφουμε τον κατάλληλο τύπο
        if identifier in TOKEN_ENUM:
            return Token(TOKEN_ENUM[identifier], identifier, self.line, start_column)

        # Αν είναι απλά αναγνωριστικό
        return Token("IDTK", identifier, self.line, start_column)


    def handle_symbol(self):
        symbol = self.current_char
        self.advance()

        # Έλεγχος για διπλούς τελεστές: <=, >=, :=, <>, ==
        if symbol == "<" and self.current_char == ">":
            symbol += self.current_char
            self.advance()
        elif symbol in "<>:=!" and self.current_char == "=":
            symbol += self.current_char
            self.advance()

        if symbol in TOKEN_ENUM:
            return Token(TOKEN_ENUM[symbol], symbol, self.line, self.column)

        return Token("ERROR", symbol, self.line, self.column)


def is_executable_statement(token_type):
            return token_type in ("IDTK", "IFTK", "WHILETK", "DOWHILETK", "FORTK", "CALLTK", "READTK", "WRITETK")

#κλαση για τον συντακτικό αναλυτή
class Parser:

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        global symbol_table
        self.symbol_table = symbol_table
        self.symbol_table.parser = self


    def error(self, expected=None):
        token = self.current_token
        message = ""

        if expected:
            message += f"SyntaxError: Περίμενα {expected} (\"{get_name_from_token_type(expected)}\"), αλλά βρέθηκε {token.type} (\"{token.value}\")\n"
        else:
            message += f"SyntaxError: Μη αναμενόμενο token: {token.type} (\"{token.value}\")\n"

        message += f"   ↳ Θέση: γραμμή {token.line}, στήλη {token.column}\n"

        # Αν μπορούμε, δείχνουμε το context (γραμμή πηγαίου κώδικα)
        if hasattr(self.lexer, "input_code"):
            source_lines = self.lexer.input_code.splitlines()
            if 0 < token.line <= len(source_lines):
                source_line = source_lines[token.line - 1]
                message += f"\n   {source_line}\n"
                message += "   " + " " * (token.column - 1) + "↑ εδώ\n"
        raise SyntaxError(message)


    def for_assignment_stat(self):
        var_name = self.current_token.value
        self.check_if_declared(var_name)   #Έλεγχος αν έχει δηλωθεί
        self.eat("IDTK")
        self.eat("ASSIGNTK")
        expr_place = self.expression()
        genQuad(":=", expr_place, "_", var_name)

        return var_name  


    def should_eat_semicolon(self):
        block_end_tokens = {
            "FUNCTIONENDTK", "PROCEDUREENDTK", "ENDPROGRAMTK",
            "IFENDTK", "FORENDTK", "WHILEENDTK", "UNTILTK", "ELSETK"
        }
        return self.current_token.type not in block_end_tokens

    def eat(self, token_type):
        print(f"[eat] Περιμένω '{get_name_from_token_type(token_type)}', έχω {self.current_token}")

        if (self.current_token.value.isdigit()) :
            print(f"[eat] Έλεγχος αν είναι έγκυρος ακέραιος: {self.current_token.value}")
            self.checkInteger(self.current_token)
            if self.current_token.type == "ERROR":
                raise SyntaxError(f"Σφάλμα αναγνωριστικού: {self.current_token.value}\n"
                                f"   ↳ Θέση: γραμμή {self.current_token.line}, στήλη {self.current_token.column}\n")
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(expected=token_type)

    def check_if_declared(self, name, allow_function_as_call=False):
        entity = self.symbol_table.lookup(name)
        if entity is None:
            raise SymbolTableError(f"Σφάλμα πίνακα συμβόλων: Η μεταβλητή ή συνάρτηση '{name}' δεν έχει δηλωθεί πριν χρησιμοποιηθεί!", self.current_token.line, self.current_token.column)

        if entity.entity_type == "function":
            if not allow_function_as_call:
                return entity  
        elif entity.entity_type == "procedure":
            raise SymbolTableError(f"Σφάλμα πίνακα συμβόλων: Το '{name}' είναι διαδικασία και δεν μπορεί να χρησιμοποιηθεί ως μεταβλητή ή συνάρτηση!", self.current_token.line, self.current_token.column)


        return entity



    def checkInteger(self, token):
        try:
            value = int(token.value)
            print(f"[checkInteger] {value} είναι έγκυρος ακέραιος")
        except ValueError:
            raise SyntaxError(f"Invalid integer value: {token.value}")
        # Έλεγχος αν είναι έγκυρος ακέραιος
        if not (-32767 <= int(value) <= 32767):
            message = f"Integer value out of range: {value}"
            
            message += f"   ↳ Θέση: γραμμή {token.line}, στήλη {token.column}\n"
            if hasattr(self.lexer, "input_code"):
                source_lines = self.lexer.input_code.splitlines()
                if 0 < token.line <= len(source_lines):
                    source_line = source_lines[token.line - 1]
                    message += f"\n   {source_line}\n"
                    message += "   " + " " * (token.column - 1) + "↑ εδώ\n"
                raise SyntaxError(message)
    
    def parse(self):
        self.program()

    def program(self):
        self.symbol_table.open_scope(is_function_or_proc=False)
    # Άνοιγμα νέου scope για το πρόγραμμα
        self.eat("PROGRAMTK")
        program_name = self.current_token.value
        
        global program_identifier_name
        program_identifier_name = program_name
        
        self.symbol_table.insert(program_name, "program")  # Καταγραφή του προγράμματος
        self.eat("IDTK")
        genQuad("begin_block", program_name, "_", "_")
        self.block()
        genQuad("halt", "_", "_", "_")
        genQuad("end_block", program_name, "_", "_")
        self.eat("ENDPROGRAMTK")
        
        program_entity = self.symbol_table.lookup(program_name)
        if program_entity:
            current_scope = self.symbol_table.current_scope
            program_entity.framelength = current_scope.framelength

        assembly_units.append((list(quadList), copy.deepcopy(self.symbol_table)))
        quadList.clear()
        self.symbol_table.close_scope()




    def branch_op(op, reg1, reg2, label):
        if op == '=':
            return f"beq {reg1}, {reg2}, L{label}\n"
        if op == '<>':
            return f"bne {reg1}, {reg2}, L{label}\n"
        if op == '<':
            return f"blt {reg1}, {reg2}, L{label}\n"
        if op == '>':
            return f"bgt {reg1}, {reg2}, L{label}\n"
        if op == '<=':
            return f"ble {reg1}, {reg2}, L{label}\n"
        if op == '>=':
            return f"bge {reg1}, {reg2}, L{label}\n"

    def block(self):
        while self.current_token.type in ("DECLARATIONTK", "FUNCTIONTK", "PROCEDURETK"):
            self.block_part()

        self.eat("BEGINPROGRAMTK")

        while self.current_token.type in (
            "IDTK", "IFTK", "WHILETK", "DOWHILETK", "FORTK", "CALLTK", "READTK", "WRITETK"
        ):
            self.stat()


    def block_part(self):
        if self.current_token.type == "DECLARATIONTK":
            self.declaration()
        elif self.current_token.type == "FUNCTIONTK":
            self.function()
        elif self.current_token.type == "PROCEDURETK":
            self.procedure()
        else:
            self.error("DECLARATIONTK, FUNCTIONTK or PROCEDURETK")

    def declaration(self):
        self.eat("DECLARATIONTK")
        var_name = self.current_token.value
        self.symbol_table.insert(var_name, "variable")  #  Εισαγωγή μεταβλητής
        self.eat("IDTK")
        while self.current_token.type == "COMMATK":
            self.eat("COMMATK")
            var_name = self.current_token.value
            self.symbol_table.insert(var_name, "variable")  
            self.eat("IDTK")


    def stat(self):
        if self.current_token.type == "IDTK":
            self.assignment_stat()
        elif self.current_token.type == "IFTK":
            self.if_stat()
        elif self.current_token.type == "WHILETK":
            self.while_stat()
        elif self.current_token.type == "DOWHILETK":
            self.do_while_stat()
        elif self.current_token.type == "FORTK":
            self.for_stat()
        elif self.current_token.type == "CALLTK":
            self.call_stat()
        elif self.current_token.type == "READTK":
            self.read_stat()
        elif self.current_token.type == "WRITETK":
            self.write_stat()
        else:
            self.error("statement")

    




    def assignment_stat(self, expect_semicolon=True):
        var_name = self.current_token.value
        entity = self.check_if_declared(var_name, allow_function_as_call=True)

        if entity.entity_type == "function":
            pass  # επιτρέπεται να δέχεται ανάθεση (για την τιμή επιστροφής)
        elif entity.entity_type not in ("variable", "parameter CV", "parameter REF", "temporary"):
            raise Exception(f"Σφάλμα: Το '{var_name}' δεν μπορεί να δεχτεί ανάθεση!")

        self.eat("IDTK")
        self.eat("ASSIGNTK")
        expr_place = self.expression()
        genQuad(":=", expr_place, "_", var_name)
        if expect_semicolon and self.should_eat_semicolon():
            self.eat("SEMICOLONTK")

    def while_stat(self):
        self.eat("WHILETK")
        start_quad = nextQuad()
        Btrue, Bfalse = self.condition()
        self.eat("DOWHILETK")
        backpatch(Btrue, nextQuad())

        while is_executable_statement(self.current_token.type):
            self.stat()

        genQuad("jump", "_", "_", start_quad)
        backpatch(Bfalse, nextQuad())
        self.eat("WHILEENDTK")


        if is_executable_statement(self.current_token.type):
            if self.current_token.type == "SEMICOLONTK":
                self.eat("SEMICOLONTK")
            else:
                self.error("SEMICOLONTK")
        else:
            if self.current_token.type == "SEMICOLONTK":
                self.eat("SEMICOLONTK")


    
    def do_while_stat(self):
        self.eat("DOWHILETK")
        start_quad = nextQuad()
        
        while self.current_token.type in ("IDTK", "IFTK", "WHILETK", "DOWHILETK", "FORTK", "CALLTK", "READTK", "WRITETK"):
            self.stat()

        self.eat("UNTILTK")
        Btrue, Bfalse = self.condition()
        backpatch(Bfalse, start_quad)




    def for_stat(self):
        self.eat("FORTK")
        id_var = self.current_token.value
        self.assignment_stat(expect_semicolon=False)
        self.eat("TOTK")
        limit = self.expression()

        step = "1"
        if self.current_token.type == "STEPKTK":
            self.eat("STEPKTK")
            step = self.expression()

        loop_start = nextQuad()
        check_label = nextQuad() + 2
        genQuad("<=", id_var, limit, check_label)
        Btrue = makeList(nextQuad())
        genQuad("jump", "_", "_", "_")

        self.eat("DOWHILETK")
        backpatch(Btrue, nextQuad())

        while is_executable_statement(self.current_token.type):
            self.stat()

        temp_next = newTemp()
        genQuad("+", id_var, step, temp_next)
        genQuad(":=", temp_next, "_", id_var)
        genQuad("jump", "_", "_", loop_start)

        backpatch([check_label - 1], nextQuad())  # κλείσιμο του jump
        self.eat("FORENDTK")

        if is_executable_statement(self.current_token.type):
            if self.current_token.type == "SEMICOLONTK":
                self.eat("SEMICOLONTK")
            else:
                self.error("SEMICOLONTK")
        else:
            if self.current_token.type == "SEMICOLONTK":
                self.eat("SEMICOLONTK")







    def call_stat(self):
        self.eat("CALLTK")
        func_name = self.current_token.value
        entity = self.symbol_table.lookup(func_name)
        if entity is None:
            raise SymbolTableError(f"Η διαδικασία ή συνάρτηση '{func_name}' δεν έχει δηλωθεί!", self.current_token.line, self.current_token.column)
        if entity.entity_type not in ("procedure", "function"):
            raise SymbolTableError(f"Το '{func_name}' δεν είναι συνάρτηση ή διαδικασία και δεν μπορεί να κληθεί!", self.current_token.line, self.current_token.column)
        self.eat("IDTK")
        self.eat("LPARENTK")

        actuals = []

        while self.current_token.type != "RPARENTK":
            if self.current_token.type == "REFERENCETK":
                self.eat("REFERENCETK")
                var = self.current_token.value
                self.check_if_declared(var)
                self.eat("IDTK")
                actuals.append(("REF", var))
            else:
                var = self.current_token.value
                self.check_if_declared(var)
                self.eat("IDTK")
                actuals.append(("CV", var))

            if self.current_token.type == "COMMATK":
                self.eat("COMMATK")
            else:
                break

        self.eat("RPARENTK")
        if self.should_eat_semicolon():
            self.eat("SEMICOLONTK")

        for mode, var in actuals:
            genQuad("par", var, mode, "_")

        genQuad("call", func_name, "_", "_")


    def read_stat(self):
        self.eat("READTK")  
        var = self.current_token.value
        self.check_if_declared(var)
        self.eat("IDTK")
        genQuad("in", var, "_", "_")

        while self.current_token.type == "COMMATK":
            self.eat("COMMATK")
            var = self.current_token.value
            self.check_if_declared(var)
            self.eat("IDTK")
            genQuad("in", var, "_", "_")
        if self.should_eat_semicolon():
            self.eat("SEMICOLONTK")




    def write_stat(self):
        self.eat("WRITETK")
        self.write_list()
        if self.should_eat_semicolon():
            self.eat("SEMICOLONTK")

    def write_list(self):
        
        expr_result = self.expression()
        genQuad("out", expr_result, "_", "_")

        while self.current_token.type == "COMMATK":
            self.eat("COMMATK")
            expr_result = self.expression()
            genQuad("out", expr_result, "_", "_")




    def read_list(self):
        var_name = self.current_token.value
        self.check_if_declared(var_name)
        self.eat("IDTK")

        genQuad("in", var, "_", "_")
        while self.current_token.type == "COMMATK":
            self.eat("COMMATK")
            var = self.current_token.value
            self.check_if_declared(var)
            self.eat("IDTK")
            genQuad("in", var, "_", "_")

    def actual_arguments(self):
        if self.current_token.type == "REFERENCETK":  # Αν είναι αναφορά
            self.eat("REFERENCETK")
            arg = self.current_token.value
            self.eat("IDTK")
            genQuad("par", arg, "REF", "_")
        else:
            arg = self.expression()
            genQuad("par", arg, "CV", "_")

        while self.current_token.type == "COMMATK":
            self.eat("COMMATK")
            if self.current_token.type == "REFERENCETK":
                self.eat("REFERENCETK")
                arg = self.current_token.value
                self.eat("IDTK")
                genQuad("par", arg, "REF", "_")
            else:
                arg = self.expression()
                genQuad("par", arg, "CV", "_")



    def do_while_stat(self):
        start_quad = nextQuad()  # Αρχή του loop

        self.eat("DOWHILETK")
        while is_executable_statement(self.current_token.type):
            self.stat()

        self.eat("UNTILTK")
        Btrue, Bfalse = self.condition()

        backpatch(Bfalse, start_quad)  # Αν είναι False, ξανακάνει επανάληψη

        if is_executable_statement(self.current_token.type):
            if self.current_token.type == "SEMICOLONTK":
                self.eat("SEMICOLONTK")
            else:
                self.error("SEMICOLONTK")
        else:
            if self.current_token.type == "SEMICOLONTK":
                self.eat("SEMICOLONTK")


    def expression(self):
        term1 = self.term()
        while self.current_token.type in ("PLUSTK", "MINUSTK"):
            op = self.current_token.value
            self.eat(self.current_token.type)
            term2 = self.term()
            temp = newTemp()
            genQuad(op, term1, term2, temp)
            term1 = temp
        return term1

    
    def condition(self):
        if self.current_token.type == "LBRACKTK":
            self.eat("LBRACKTK")
            Btrue, Bfalse = self.condition()
            self.eat("RBRACKTK")
        elif self.current_token.type == "NOTTK":
            self.eat("NOTTK")
            if self.current_token.type == "LPARENTK":
                self.eat("LPARENTK")
                Btrue, Bfalse = self.condition()
                self.eat("RPARENTK")
            else:
                Btrue, Bfalse = self.bool_factor()
            return Bfalse, Btrue
        else:
            Btrue, Bfalse = self.bool_factor()

        while self.current_token.type in ("ANDTK", "ORTK"):
            op = self.current_token.type
            self.eat(op)

            if op == "ANDTK":
                backpatch(Btrue, nextQuad())
                Q2_true, Q2_false = self.condition()
                Btrue = Q2_true
                Bfalse = mergeList(Bfalse, Q2_false)

            elif op == "ORTK":
                backpatch(Bfalse, nextQuad())
                Q2_true, Q2_false = self.condition()
                Btrue = mergeList(Btrue, Q2_true)
                Bfalse = Q2_false

        return Btrue, Bfalse


    def bool_factor(self):
        if self.current_token.type == "NOTTK":
            self.eat("NOTTK")
            if self.current_token.type == "LPARENTK":
                self.eat("LPARENTK")
                Btrue, Bfalse = self.condition()
                self.eat("RPARENTK")
            elif self.current_token.type == "LBRACKTK":
                self.eat("LBRACKTK")
                Btrue, Bfalse = self.condition()
                self.eat("RBRACKTK")
            else:
                Btrue, Bfalse = self.bool_factor()
            return Bfalse, Btrue

        elif self.current_token.type == "LPARENTK":
            self.eat("LPARENTK")
            Btrue, Bfalse = self.condition()
            self.eat("RPARENTK")
            return Btrue, Bfalse

        elif self.current_token.type == "LBRACKTK":
            self.eat("LBRACKTK")
            Btrue, Bfalse = self.condition()
            self.eat("RBRACKTK")
            return Btrue, Bfalse

        else:
            
            E1 = self.expression()
            relop_token = self.current_token
            if relop_token.type in ("EQTK", "NEQTK", "LTKTK", "GTKTK", "LEQTK", "GEQTK"):
                relop_str = relop_token.value
                self.eat(relop_token.type)
                E2 = self.expression()

                trueList = makeList(nextQuad())
                trueLabel = nextQuad() + 2
                genQuad(relop_str, E1, E2, trueLabel)

                falseList = makeList(nextQuad())
                genQuad("jump", "_", "_", "_")

                return trueList, falseList
            else:
                self.error("Relational Operator")




    def term_prime(self):
        while self.current_token.type in ("MULTTK", "DIVTK"):
            self.eat(self.current_token.type)
            self.factor()

    def factor(self):
        sign = 1

        if self.current_token.type in ("PLUSTK", "MINUSTK"):
            if self.current_token.type == "MINUSTK":
                sign = -1
            self.eat(self.current_token.type)

        if self.current_token.type == "IDTK":
            id_name = self.current_token.value
            entity = self.check_if_declared(id_name, allow_function_as_call=True) 
            self.eat("IDTK")

            if self.current_token.type == "LPARENTK":
                # Είναι function call
                self.eat("LPARENTK")
                args = []
                while self.current_token.type != "RPARENTK":
                    if self.current_token.type == "REFERENCETK":
                        self.eat("REFERENCETK")
                        arg = self.current_token.value
                        self.check_if_declared(arg)
                        self.eat("IDTK")
                        genQuad("par", arg, "REF", "_")
                    else:
                        arg = self.expression()
                        genQuad("par", arg, "CV", "_")

                    if self.current_token.type == "COMMATK":
                        self.eat("COMMATK")
                    else:
                        break

                self.eat("RPARENTK")

                result = newTemp()
                genQuad("par", result, "RET", "_")
                genQuad("call", id_name, "_", "_")
                return result

            return id_name  # απλή μεταβλητή (όχι κλήση)

        elif self.current_token.type == "CONSTTK":
            const_value = self.current_token.value
            self.eat("CONSTTK")

            if sign == -1:
                temp = newTemp()
                genQuad("-", "0", const_value, temp)
                return temp
            return const_value

        elif self.current_token.type == "LPARENTK":
            self.eat("LPARENTK")
            exp = self.expression()
            self.eat("RPARENTK")
            if sign == -1:
                temp = newTemp()
                genQuad("-", "0", exp, temp)
                return temp
            return exp

        else:
            self.error("factor")


    
    def bool_term(self):
        E1 = self.expression()
        relop = self.current_token.type
        if relop in ("EQTK", "NEQTK", "LTKTK", "GTKTK", "LEQTK", "GEQTK"):
            self.eat(relop)
            E2 = self.expression()

            trueList = makeList(nextQuad())
            genQuad(get_name_from_token_type(relop), E1, E2, "_")

            falseList = makeList(nextQuad())
            genQuad("jump", "_", "_", "_")

            return (trueList, falseList)
        else:
            self.error("Relational Operator")
    

    def expression_prime(self):
        while self.current_token.type in ("PLUSTK", "MINUSTK"):
            self.eat(self.current_token.type)
            self.term()

    def term(self):
        factor1 = self.factor()
        while self.current_token.type in ("MULTTK", "DIVTK"):
            op = self.current_token.value
            self.eat(self.current_token.type)
            factor2 = self.factor()
            temp = newTemp()
            genQuad(op, factor1, factor2, temp)
            factor1 = temp
        return factor1

    def function(self):
        self.eat("FUNCTIONTK")
        func_name = self.current_token.value
        self.eat("IDTK")

        if len(self.symbol_table.scopes) >= 1:
            #  Καταχώρισε στο parent scope (πριν ανοίξει το καινούριο)
            self.symbol_table.insert(func_name, "function")
        
        self.symbol_table.open_scope(is_function_or_proc=True)

        self.eat("LPARENTK")
        self.parameter_list()
        self.eat("RPARENTK")
        self.interface_part(func_name)

        genQuad("begin_block", func_name, "_", "_")
        self.eat("BEGINFUNCTIONTK")

        # δέχεται δηλώσεις και εμφωλευμένα block_part
        while self.current_token.type in ("DECLARATIONTK", "FUNCTIONTK", "PROCEDURETK"):
            self.block_part()

        while self.current_token.type in ("IDTK", "IFTK", "WHILETK", "DOWHILETK", "FORTK", "CALLTK", "READTK", "WRITETK"):
            self.stat()
        
        # Αν δεν έγινε return, βάλε αυτόματα retv στο τέλος
        if self.symbol_table.lookup_in_current_scope(func_name) is None:
            self.symbol_table.insert(func_name, "variable")

        genQuad("retv", func_name, "_", "_")
        genQuad("end_block", func_name, "_", "_")

        self.eat("FUNCTIONENDTK")
        assembly_units.append((list(quadList), copy.deepcopy(self.symbol_table)))
        quadList.clear()

        self.symbol_table.close_scope()


    def procedure(self):
        self.eat("PROCEDURETK")
        proc_name = self.current_token.value

        self.symbol_table.insert(proc_name, "procedure")
        self.eat("IDTK")
        self.symbol_table.open_scope(is_function_or_proc=True)

        self.eat("LPARENTK")
        self.parameter_list()
        self.eat("RPARENTK")
        self.interface_part(proc_name)

        genQuad("begin_block", proc_name, "_", "_")
        self.eat("BEGINPROCEDURETK")

        while self.current_token.type in ("DECLARATIONTK", "FUNCTIONTK", "PROCEDURETK"):
            self.block_part()

        while self.current_token.type in ("IDTK", "IFTK", "WHILETK", "DOWHILETK", "FORTK", "CALLTK", "READTK", "WRITETK"):
            self.stat()

        genQuad("end_block", proc_name, "_", "_")


        self.eat("PROCEDUREENDTK")
        
        assembly_units.append((list(quadList), copy.deepcopy(self.symbol_table)))
        quadList.clear()

        self.symbol_table.close_scope()



    def parameter_list(self):
        if self.current_token.type in ("IDTK", "REFERENCETK"):
            self.parameter()
            while self.current_token.type == "COMMATK":
                self.eat("COMMATK")
                self.parameter()
    
    def parameter(self):
        if self.current_token.type == "REFERENCETK":
            self.eat("REFERENCETK")
            param_name = self.current_token.value
            self.symbol_table.insert(param_name, "parameter REF")  # Εισαγωγή parameter by reference
            self.eat("IDTK")
        else:
            param_name = self.current_token.value
            self.symbol_table.insert(param_name, "parameter CV")   # Εισαγωγή parameter by value
            self.eat("IDTK")


    def interface_part(self, func_name):
        self.eat("INTERFACETK")
        if self.current_token.type == "INPUTTK":
            self.eat("INPUTTK")
            self.id_list()
        if self.current_token.type == "OUTPUTTK":
            self.eat("OUTPUTTK")
            self.id_list(allow_function_name_as_output=True, current_function_name=func_name)



    def id_list(self, allow_function_name_as_output=False, current_function_name=None):
        var_name = self.current_token.value

        if allow_function_name_as_output and var_name == current_function_name:
            # Μην το εισάγεις ξανά, είναι το όνομα της συνάρτησης
            self.eat("IDTK")
        else:
            existing_entity = self.symbol_table.lookup_in_current_scope(var_name)
            if existing_entity:
                if existing_entity.entity_type.startswith("parameter"):
                    pass  # ήδη δηλωμένο ως parameter
                else:
                    raise SymbolTableError(f"Σφάλμα πίνακα συμβόλων: Το όνομα '{var_name}' υπάρχει ήδη ως {existing_entity.entity_type}!", self.symbol_table.parser.current_token.line, self.symbol_table.parser.current_token.column)

            else:
                self.symbol_table.insert(var_name, "variable")
            self.eat("IDTK")

        while self.current_token.type == "COMMATK":
            self.eat("COMMATK")
            var_name = self.current_token.value

            if allow_function_name_as_output and var_name == current_function_name:
                self.eat("IDTK")
            else:
                existing_entity = self.symbol_table.lookup_in_current_scope(var_name)
                if existing_entity:
                    if existing_entity.entity_type.startswith("parameter"):
                        pass
                    else:
                        raise SymbolTableError(f"Σφάλμα πίνακα συμβόλων: Το όνομα '{var_name}' υπάρχει ήδη ως {existing_entity.entity_type}!", self.symbol_table.parser.current_token.line, self.symbol_table.parser.current_token.column)

                else:
                    self.symbol_table.insert(var_name, "variable")
                self.eat("IDTK")


    def if_stat(self):
        self.eat("IFTK")
        Btrue, Bfalse = self.condition()
        self.eat("THENTK")
        
        backpatch(Btrue, nextQuad())
        while is_executable_statement(self.current_token.type):
            self.stat()
        
        if self.current_token.type == "ELSETK":
            ifList = makeList(nextQuad())
            genQuad("jump", "_", "_", "_")
            backpatch(Bfalse, nextQuad())
            self.eat("ELSETK")
            while is_executable_statement(self.current_token.type):
                self.stat()
            backpatch(ifList, nextQuad())
        else:
            backpatch(Bfalse, nextQuad())

        self.eat("IFENDTK")

        if is_executable_statement(self.current_token.type):
            if self.current_token.type == "SEMICOLONTK":
                self.eat("SEMICOLONTK")
            else:
                self.error("SEMICOLONTK")
        else:
            if self.current_token.type == "SEMICOLONTK":
                self.eat("SEMICOLONTK")



temp_counter = 0

class Quad:
    def __init__(self, label, operator, operand1, operand2, result):
        self.label = label
        self.operator = operator
        self.operand1 = operand1
        self.operand2 = operand2
        self.result = result

    def __repr__(self):
        return f"{self.label}: ({self.operator}, {self.operand1}, {self.operand2}, {self.result})"

# Αρχικοποίηση λίστας τετράδων
quadList = []
assembly_units = []  # Για αποθήκευση όλων των (quads, symbol_table snapshot)
import copy


# Επιστρέφει τον αριθμό της επόμενης τετράδας
def nextQuad():
    return len(quadList) + 1


# Δημιουργεί μια νέα τετράδα
def genQuad(operator, operand1, operand2, result):
    # Ελέγχουμε αν κάποιο operand είναι ακέραιος και υπερβαίνει τα όρια
    for operand in [operand1, operand2, result]:
        if isinstance(operand, str) and operand.lstrip('-').isdigit():
            int_val = int(operand)
            if not (-32767 <= int_val <= 32767):
                # Εμφανίζουμε μήνυμα λάθους 
                raise ValueError(f"Integer literal {int_val} εκτός επιτρεπτών ορίων [-32767, 32767]")

    # Δημιουργία τετράδας
    label = nextQuad()
    quad = Quad(label, operator, operand1, operand2, result)
    quadList.append(quad)


# Δημιουργία νέας προσωρινής μεταβλητής
temp_counter = 0

def newTemp():
    global temp_counter
    temp_counter += 1
    temp_name = f"t@{temp_counter}"
    symbol_table.insert(temp_name, "temporary")  # Προσθήκη στον πίνακα συμβόλων ως temporary
    return temp_name




# Δημιουργεί κενή λίστα
def emptyList():
    return []

# Δημιουργεί μια λίστα με ένα στοιχείο
def makeList(x):
    return [x]

# Ενώνει δύο λίστες
def mergeList(list1, list2):
    return list1 + list2

# Συμπληρώνει (backpatch) τις τετράδες της λίστας `patchList` με την ετικέτα `label`
def backpatch(patchList, label):
    for quadIndex in patchList:
        if quadIndex <= len(quadList):
            quadList[quadIndex - 1].result = label


# ---------------- Παραγωγή .c ----------------


def write_to_c(filename,outfile):

    def add_to_list(lst, x):
        try:
            int(x)
            float(x)
            numerical = True
        except:
            numerical = False
        if x not in lst and not numerical:
            lst.append(x)
        return lst

    variables = []

    fout = open(outfile, 'w', encoding='utf-8')
    print("#include <stdio.h>", file=fout)
    print("\nint main()", file=fout)
    print("{", file=fout)

    with open(filename, 'r', encoding='utf-8') as file:
        for s in file:
            s = s.replace(':=', "#").replace(":", ',')
            words = s.split(',')
            for i, w in enumerate(words):
                words[i] = w.strip().replace('#', ':=').replace('@', '$')
            if words[1]==':=':
                    variables = add_to_list(variables,words[2])
                    variables = add_to_list(variables, words[4])
            if words[1]=='+' or words[1]=='-' or words[1]=='*' or words[1]=='/' :
                    variables = add_to_list(variables,words[2])
                    variables = add_to_list(variables, words[3])
                    variables = add_to_list(variables, words[4])
            if words[1]=='=' or words[1]=='<>' or words[1]=='<=' or words[1]=='>=' or words[1]=='>' or words[1]=='<':
                variables = add_to_list(variables, words[2])
                variables = add_to_list(variables, words[3])
    for x in variables:
        print("int",x,';',file=fout)
    print(file=fout)


    with open(filename, 'r', encoding='utf-8') as file:
        for s in file:
            
            s = s.replace(':=', "#").replace(":", ',')
            words = s.split(',')
            for i, w in enumerate(words):
                words[i] = w.strip().replace('#', ':=').replace('@', '$')
            print('L'+words[0]+': ',end='',file=fout)
            if words[1]==':=': print(words[4]+'='+words[2]+';',end='',file=fout)
            elif words[1]=='+':  print(words[4]+'='+words[2]+'+'+words[3]+';',end='',file=fout)
            elif words[1]=='-':  print(words[4]+'='+words[2]+'-'+words[3]+';',end='',file=fout)
            elif words[1]=='*':  print(words[4]+'='+words[2]+'*'+words[3]+';',end='',file=fout)
            elif words[1]=='/':  print(words[4]+'='+words[2]+'/'+words[3]+';',end='',file=fout)
            elif words[1]=='jump':  print('goto L'+words[4]+';',end='',file=fout)
            elif words[1] == 'jump_if_true': print(f'if ({words[2]}) goto L{words[4]};', end='', file=fout)
            elif words[1]=='=':  print('if ('+words[2]+' == '+words[3]+') goto L'+words[4]+';',end='',file=fout)
            elif words[1]=='<>':  print('if ('+words[2]+' != '+words[3]+') goto L'+words[4]+';',end='',file=fout)
            elif words[1]=='<=':  print('if ('+words[2]+' <= '+words[3]+') goto L'+words[4]+';',end='',file=fout)
            elif words[1]=='>=':  print('if ('+words[2]+' >= '+words[3]+') goto L'+words[4]+';',end='',file=fout)
            elif words[1]=='>':  print('if ('+words[2]+' > '+words[3]+') goto L'+words[4]+';',end='',file=fout)
            elif words[1]=='<':  print('if ('+words[2]+' < '+words[3]+') goto L'+words[4]+';',end='',file=fout)
            elif words[1]=='out':  print('printf("%d\\n",'+words[2]+');',end='',file=fout)
            elif words[1]=='in':  print('scanf("%d",&'+words[2]+');',end='',file=fout)
            elif words[1] == 'begin_block' or words[1] == 'end_block' or words[1]=='halt': pass
            elif words[1] in ('par', 'call', 'retv', 'ret'):
                print(f'// skipped unsupported: {words[1]} {words[2]} {words[3]} {words[4]}', file=fout)

            else:
                print('unknown operator:',words)
                sys.exit(1)
            print(file=fout)
    print('}\n',file=fout)
    fout.close()

# ---------------- Πίνακας Συμβόλων ----------------

class Entity:
    def __init__(self, name, entity_type, nesting_level, offset=None, parMode=None, startQuad=None, framelength=None):
        self.name = name
        self.entity_type = entity_type
        self.nesting_level = nesting_level
        self.offset = offset  
        self.parMode = parMode  
        self.startQuad = startQuad  
        self.framelength = framelength  


    def __repr__(self):
        desc = f"{self.name} ({self.entity_type}, nesting level {self.nesting_level}"
        if self.entity_type in ("variable", "parameter CV", "parameter REF", "temporary"):
            desc += f", offset {self.offset}"
        desc += ")"
        return desc



class Scope:
    def __init__(self, nesting_level, is_function_or_proc=False):
        self.nesting_level = nesting_level
        self.entities = []
        self.offset = 0  
        self.framelength = 0
        self.is_function_or_proc = is_function_or_proc

    def insert_entity(self, entity):
        self.entities.append(entity)

    def __repr__(self):
        result = f"Scope level {self.nesting_level} (framelength = {self.framelength} bytes):\n"
        for entity in self.entities:
            result += f"  {entity}\n"
        return result


class SymbolTableError(Exception):
    def __init__(self, message, line=None, column=None):
        full_message = message
        if line is not None and column is not None:
            full_message += f"\n   ↳ Θέση: γραμμή {line}, στήλη {column}"
        super().__init__(full_message)


class SymbolTableManager:
    def __init__(self):
        self.scopes = []
        self.current_scope = None
        self.parser = None  


    def open_scope(self, is_function_or_proc=False):
        new_scope = Scope(len(self.scopes), is_function_or_proc)
        
        
        if is_function_or_proc:
            new_scope.offset = 8
        
        self.scopes.append(new_scope)
        self.current_scope = new_scope

    def insert_into_parent_scope(self, name, entity_type):
        if len(self.scopes) >= 2:
            parent_scope = self.scopes[-2]
            for entity in parent_scope.entities:
                if entity.name == name:
                    raise SymbolTableError(f"Σφάλμα πίνακα συμβόλων: Το όνομα '{name}' υπάρχει ήδη στο εξωτερικό scope!", self.parser.current_token.line, self.parser.current_token.column)

            entity = Entity(name, entity_type, parent_scope.nesting_level)
            parent_scope.insert_entity(entity)
        else:
            # Αν δεν έχει γονικό scope, αγνόησέ το
            pass

    def lookup_in_current_scope(self, name):
        if self.current_scope is not None:
            for entity in self.current_scope.entities:
                if entity.name == name:
                    return entity
        return None

    def lookup(self, name):
        for scope in reversed(self.scopes):
            for entity in scope.entities:
                if entity.name == name:
                    return entity
        return None
    
    def close_scope(self, sym_filename=None):
        if sym_filename is None and hasattr(self.parser, "sym_filename"):
            sym_filename = self.parser.sym_filename
        if self.scopes:
            scope = self.scopes[-1]

            # Πριν το close , υπολογίζουμε framelength
            scope.framelength = scope.offset

            # Ενημέρωση framelength για τις τοπικές μεταβλητές
            for entity in scope.entities:
                if entity.entity_type in ("program", "function", "procedure"):
                    entity.framelength = scope.framelength

            print("\nΠίνακας Συμβόλων στο κλείσιμο του Scope:")
            print(scope)

            with open(sym_filename, "a", encoding="utf-8") as f:
                f.write(f"\n Πίνακας Συμβόλων στο κλείσιμο του Scope:\n")
                f.write(f"{scope}\n")

            
            

            self.scopes.pop()
            if self.scopes:
                self.current_scope = self.scopes[-1]
            else:
                self.current_scope = None




    def insert(self, name, entity_type):
        if self.current_scope is not None:
            # ελεγχος αν το όνομα υπάρχει ήδη στο ίδιο scope
            for entity in self.current_scope.entities:
                if entity.name == name:
                    if entity.entity_type != entity_type:
                        raise SymbolTableError(f"Σφάλμα πίνακα συμβόλων: Το όνομα '{name}' υπάρχει ήδη ως {entity.entity_type} και δεν μπορεί να ξαναχρησιμοποιηθεί ως {entity_type} στο ίδιο scope!", self.parser.current_token.line, self.parser.current_token.column)

                    else:
                        raise SymbolTableError(f"Σφάλμα πίνακα συμβόλων: Το όνομα '{name}' έχει ήδη δηλωθεί στο ίδιο scope!", self.parser.current_token.line, self.parser.current_token.column)


            entity = Entity(name, entity_type, self.current_scope.nesting_level)

            if entity_type in ("variable", "parameter CV", "parameter REF", "temporary"):
                entity.offset = self.current_scope.offset
                self.current_scope.offset += 4
            else:
                entity.offset = None

            self.current_scope.insert_entity(entity)
        else:
            print(f"Προσπάθησα να εισάγω '{name}' αλλά δεν υπάρχει ενεργό scope!")



# Δημιουργία global symbol_table
symbol_table = SymbolTableManager()
# --------------------------------------------------

# ----------------  Assembly ----------------
quads=[]
global label_offset
label_offset = 0
# Δημιουργία assembly κώδικα από τις τετράδες
def generate_assembly(quads, symbol_table):
    global asm_lines
    asm_lines = build_assembly_lines(quads, symbol_table)
   

def loadvr(v, r, symbol_table):
        code = ""
        if v.isdigit():
            code += f"li {r}, {v}\n"
        else:
            entity = symbol_table.lookup(v)
            if entity is None:
                raise Exception(f"Σφάλμα: Δεν βρέθηκε entity για τη μεταβλητή '{v}' στο loadvr/storerv")

            if entity.nesting_level == 0:
                # καθολική μεταβλητή
                code += f"lw {r}, -{entity.offset}(gp)\n"
            elif entity.nesting_level == symbol_table.current_scope.nesting_level:
                # τοπική μεταβλητή / παράμετρος / temp
                if entity.entity_type == "parameter REF":
                    code += f"lw t0, -{entity.offset}(sp)\n"
                    code += f"lw {r}, 0(t0)\n"
                else:
                    code += f"lw {r}, -{entity.offset}(sp)\n"
            else:
                # από πρόγονο
                code += gnlvcode(v, symbol_table)
                if entity.entity_type == "parameter REF":
                    code += f"lw t0, 0(t0)\n"
                code += f"lw {r}, 0(t0)\n"
        return code


def build_assembly_lines(quads, symbol_table):
    global label_offset
    param_counter = 0
    asm_lines = []

    current_nesting_level = symbol_table.current_scope.nesting_level if symbol_table.current_scope else 0

    for quad in quads:
        global label_offset
        label_number = quad.label + label_offset
        asm_lines.append(f"L{label_number}:")
        op, x, y, z = quad.operator, quad.operand1, quad.operand2, quad.result

        if op == ":=":
            asm_lines.append(loadvr(x, 't1', symbol_table))
            asm_lines.append(storerv('t1', z, symbol_table))

        elif op in ("+", "-", "*", "/"):
            asm_lines.append(loadvr(x, 't1', symbol_table))
            asm_lines.append(loadvr(y, 't2', symbol_table))
            asm_lines.append(f"{riscv_op(op)} t1, t1, t2")
            asm_lines.append(storerv('t1', z, symbol_table))

        elif op in ("=", "<>", "<", ">", "<=", ">="):
            asm_lines.append(loadvr(x, 't1', symbol_table))
            asm_lines.append(loadvr(y, 't2', symbol_table))
            branch_op = {
                "=": "beq",
                "<>": "bne",
                "<": "blt",
                ">": "bgt",
                "<=": "ble",
                ">=": "bge"
            }[op]
            asm_lines.append(f"{branch_op} t1, t2, L{z}")

        elif op == "jump_if_true":
            asm_lines.append(loadvr(x, 't1', symbol_table))
            asm_lines.append(f"bnez t1, L{z}")

        elif op == "jump":
            asm_lines.append(f"j L{z}")

        elif op == "out":
            asm_lines.append(loadvr(x, 'a0', symbol_table))
            asm_lines.append("li a7, 1")
            asm_lines.append("ecall")

        elif op == "in":
            asm_lines.append("li a7, 5")
            asm_lines.append("ecall")
            asm_lines.append(storerv('a0', x, symbol_table))

        elif op == "halt":
            asm_lines.append("li a0, 0")
            asm_lines.append("li a7, 93")
            asm_lines.append("ecall")

        elif op == "begin_block":
            if x == program_identifier_name:
                asm_lines.append("main:")
            entity = symbol_table.lookup(x)
            framelen = entity.framelength if entity and entity.framelength is not None else symbol_table.current_scope.offset

            asm_lines.append(f"addi sp, sp, {framelen}")
            if x == program_identifier_name:
                asm_lines.append("add gp, sp, zero")
                asm_lines.append("add s0, sp, zero")
            asm_lines.append("sw ra, 0(sp)")

        elif op == "end_block":
            asm_lines.append("lw ra, 0(sp)")
            asm_lines.append("jr ra")

        elif op == "ret":
            asm_lines.append("lw ra, 0(sp)")
            asm_lines.append("jr ra")
        
        elif op == "retv":
            asm_lines.append(loadvr(x, "t1", symbol_table))
            asm_lines.append("lw t0, -8(sp)")
            asm_lines.append("sw t1, 0(t0)")
        
        elif op == "par":
            if y == "CV":
                asm_lines.append(loadvr(x, 't0', symbol_table))
                offset = 12 + 4 * param_counter
                asm_lines.append(f"sw t0, -{offset}(s0)")
            elif y == "REF":
                entity = symbol_table.lookup(x)
                if entity.nesting_level == current_nesting_level:
                    asm_lines.append(f"addi t0, sp, -{entity.offset}")
                else:
                    asm_lines.append(gnlvcode(x, symbol_table))
                offset = 12 + 4 * param_counter
                asm_lines.append(f"sw t0, -{offset}(s0)")
            elif y == "RET":
                entity = symbol_table.lookup(x)
                asm_lines.append(f"addi t0, sp, -{entity.offset}")
                asm_lines.append("sw t0, -8(s0)")
            param_counter += 1

        elif op == "call":
            called_entity = symbol_table.lookup(x)

            if called_entity is None:
                raise Exception(f"Σφάλμα: Δεν βρέθηκε entity για την κλήση της '{x}'")

            # Υπολογίζουμε framelength fallback αν δεν έχει αποθηκευτεί
            framelen = called_entity.framelength
            if framelen is None:
                for scope in symbol_table.scopes:
                    if scope.nesting_level == called_entity.nesting_level:
                        framelen = scope.offset
                        break
                if framelen is None:
                    framelen = 0

            # Υπολογισμός και αποθήκευση του static link στο -4(s0)
            if called_entity.nesting_level == current_nesting_level:
                asm_lines.append("lw t0, -4(sp)")
                asm_lines.append("sw t0, -4(s0)")
            else:
                # Πρέπει να ανέβουμε nesting_level - called_level φορές από τρέχον scope
                levels_up = current_nesting_level - called_entity.nesting_level 
                asm_lines.append("add t0, sp, zero")  # αρχικοποιούμε t0 με τρέχον sp
                for _ in range(levels_up):
                    asm_lines.append("lw t0, -4(t0)")
                asm_lines.append("sw t0, -4(s0)")

            # Αναπροσαρμογή sp και κλήση
            asm_lines.append(f"addi sp, sp, {framelen}")
            asm_lines.append(f"jal {x}")
            asm_lines.append(f"addi sp, sp, -{framelen}")
            param_counter = 0



        else:
            asm_lines.append(f"# Unsupported quad: {quad}")
    
    
    label_offset += len(quads)


    return asm_lines



def riscv_op(op):
    if op == '+':
        return 'add'
    if op == '-':
        return 'sub'
    if op == '*':
        return 'mul'
    if op == '/':
        return 'div'
    
def storerv(r, v, symbol_table):
    code = ""
    entity = symbol_table.lookup(v)
    if entity is None:
        raise Exception(f"Σφάλμα: Δεν βρέθηκε entity για τη μεταβλητή '{v}' στο loadvr/storerv")
    if entity.nesting_level == 0:
        code += f"sw {r}, -{entity.offset}(gp)\n"
    elif entity.nesting_level == symbol_table.current_scope.nesting_level:
        if entity.entity_type == "parameter REF":
            code += f"lw t0, -{entity.offset}(sp)\n"
            code += f"sw {r}, 0(t0)\n"
        else:
            code += f"sw {r}, -{entity.offset}(sp)\n"
    else:
        code += gnlvcode(v, symbol_table)
        if entity.entity_type == "parameter REF":
            code += f"lw t0, 0(t0)\n"
        code += f"sw {r}, 0(t0)\n"
    return code



def gnlvcode(v, symbol_table):
    code = ""
    entity = symbol_table.lookup(v)
    if entity is None:
        raise Exception(f"Σφάλμα: Δεν βρέθηκε entity για τη μεταβλητή '{v}' στο loadvr/storerv")

    levels_up = symbol_table.current_scope.nesting_level - entity.nesting_level

    code += "lw t0, -4(sp)\n"  # πάμε στον γονέα
    for _ in range(levels_up - 1):
        code += "lw t0, -4(t0)\n"  # ανεβαίνουμε πρόγονο-πρόγονο

    code += f"addi t0, t0, -{entity.offset}\n"
    return code

# ---------------- Ορισμός main ----------------
def main():
    
    if len(sys.argv) != 2:
        print("Σφάλμα Σύνταξης Κλήσης Μεταφραστή: python bill.py <αρχείο.gr>")
        return

    filename = sys.argv[1]

    # Έλεγχος επέκτασης .gr
    if not filename.endswith(".gr"):
        print("Επιτρέπονται μόνο αρχεία με κατάληξη .gr")
        return

    # Έλεγχος ύπαρξης αρχείου
    if not os.path.exists(filename):
        print(f"Το αρχείο \"{filename}\" δεν βρέθηκε.")
        return
    
    sym_filename = filename.replace('.gr', '.sym')
    int_filename = filename.replace('.gr', '.int')
    c_filename = filename.replace('.gr', '.c')
    asm_filename = filename.replace('.gr', '.asm')
    
    if os.path.exists(asm_filename):
        os.remove(asm_filename)


    if os.path.exists(sym_filename):
        os.remove(sym_filename)
        

    # Ανάγνωση πηγαίου κώδικα
    with open(filename, "r", encoding="utf-8") as f:
        input_code = f.read()
        # Αρχικοποίηση για κάθε νέο πρόγραμμα
    
    symbol_table.scopes.clear()
    symbol_table.current_scope = None
    quadList.clear()

    try:
        global asm_file
        asm_file = open(asm_filename, 'w', encoding='utf-8')
        
        global asm_lines
        asm_lines = []

        lexer = Lexer(input_code)
        parser = Parser(lexer)
        parser.sym_filename = sym_filename

        symbol_table.scopes.clear()
        symbol_table.current_scope = None
        parser.parse()

        print("\n Η σύνταξη είναι σωστή!\n")
        print(" Τετράδες που παρήχθησαν (ενδιάμεσος κώδικας):")
        
        # Collect all quads across all units
        all_quads = []
        for quads, _ in assembly_units:
            all_quads += quads
            for quad in quads:
                print(quad)

        # Save them to .int
        with open(int_filename, 'w', encoding='utf-8') as f:
            for quad in all_quads:
                result = quad.result if quad.result != "_" else "_"
                f.write(f"{quad.label} : {quad.operator} , {quad.operand1} , {quad.operand2} , {result}\n")

        # Κάλεσε build_assembly_lines για κάθε σύνολο τετράδων
        asm_lines = [".data", ".text", f"j main"]
        for quads, table in assembly_units:
            asm_lines += build_assembly_lines(quads, table)


        print(f"Το αρχείο .int γράφτηκε επιτυχώς στο '{int_filename}'")

        # Μετατροπή τετράδων σε αρχείο .c
        write_to_c(int_filename, c_filename)
        print(f"Το αρχείο .c γράφτηκε επιτυχώς στο '{c_filename}'")
        
        # Eγγραφή assembly κώδικα σε αρχείο .asm
        with open(asm_filename, 'w', encoding='utf-8') as f:
            for line in asm_lines:
                f.write(line + "\n")
        print(f"Το αρχείο .asm γράφτηκε επιτυχώς στο '{asm_filename}'")

    
    except SymbolTableError as e:
        print("\n" + "-" * 40)
        print(e)
        print("-" * 40 + "\n")

    except SyntaxError as e:
        print("\n" + "-" * 40)
        print("Συντακτικό λάθος:")
        print(e)
        print("-" * 40 + "\n")

    except Exception as e:
        print("\n" + "-" * 40)
        print("Άγνωστο σφάλμα:")
        print(e)
        print("-" * 40 + "\n")



if __name__ == "__main__":
    main()
