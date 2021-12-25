"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import *
from VMWriter import *
from SymbolTable import *

INT_CONST = "INT_CONST"
STRING_CONST = "STRING_CONST"
IDENTIFIER = "IDENTIFIER"

OPEN_BRACKETS = "["
COMMA = ","
DOUBLE_SPACE = "  "
SEMICOLON = ";"
DOT = "."
OPEN_PARENTHESIS = "("
CLOSE_PARENTHESIS = ")"

HEADERS_DIC = {"KEYWORD": "keyword", "SYMBOL": "symbol",
               "IDENTIFIER": "identifier", "INT_CONST": "integerConstant",
               "STRING_CONST": "stringConstant"}
OP = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
UNARY_OP = ['-', '~', '#', '^']
KEYWORD_CONST = ['true', 'false', 'null', 'this']


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: JackTokenizer,
                 output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.tokenizer.advance()
        self.vm = VMWriter(output_stream)
        self.sy = SymbolTable()
        self.class_type = ""
        self.subroutine_list = list()
        self.label_counter = 0
        # Current compiled subroutine dict:
        self.current_subroutine = {"func_type": "", "ret_type": "", "name": ""}
        self.compile_class()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.tokenizer.advance()
        # classname
        self.class_type = self.tokenizer.identifier()
        self.tokenizer.advance()
        self.tokenizer.advance()

        if self.tokenizer.cur_token in ["field", "static"]:
            self.compile_class_var_dec()
        if self.tokenizer.cur_token in ['constructor', 'function', 'method']:
            self.compile_subroutine()
        self.tokenizer.advance()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        while self.tokenizer.cur_token in ["field", "static"]:
            t_kind = self.tokenizer.cur_token
            self.tokenizer.advance()
            t_type = self.tokenizer.cur_token
            self.define_symbol(t_kind, t_type)
            while self.tokenizer.cur_token == COMMA:
                self.define_symbol(t_kind, t_type)
            self.tokenizer.advance()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        while self.tokenizer.cur_token in ['constructor', 'function',
                                           'method']:
            self.sy.start_subroutine()
            self.current_subroutine["func_type"] = self.tokenizer.cur_token
            self.tokenizer.advance()
            self.current_subroutine["ret_type"] = self.tokenizer.cur_token
            self.tokenizer.advance()
            # adds subroutine name to list
            self.subroutine_list.append(
                f"{self.class_type}.{self.tokenizer.cur_token}")
            self.tokenizer.advance()  # "("
            self.tokenizer.advance()
            # if Method: adds 'this' to symbol table
            if self.current_subroutine["func_type"] == self.sy.METHOD:
                self.sy.define("this", self.class_type, self.sy.ARG)
            # General subroutine:
            self.compile_parameter_list()  # Finished tokenizer.cur_token = ")"
            # subroutineBody
            self.tokenizer.advance()  # "{"
            self.tokenizer.advance()  # "(varDec)?"
            if self.tokenizer.cur_token == "var":
                self.compile_var_dec()
            # Write function deceleration in VM
            self.vm.write_function(self.subroutine_list[-1],
                                   self.sy.var_count(self.sy.VAR))
            if self.current_subroutine["func_type"] == self.sy.METHOD:
                # aligns the virtual memory segment this with the base address of the object
                self.vm.write_push(self.sy.ARG, 0)
                self.vm.write_pop(self.sy.POINTER, 0)
            if self.current_subroutine["func_type"] == self.sy.CONS:
                self.vm.write_push(self.sy.CONSTANT,
                                   self.sy.var_count(self.sy.FIELD))
                self.vm.write_call("Memory.Alloc", 1)
                self.vm.write_pop(self.sy.POINTER, 0)
            # Statements:
            self.compile_statements()
            self.tokenizer.advance()  # "}"

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        if self.tokenizer.cur_token in ["int", "char", "boolean"] or \
                self.tokenizer.token_type() == IDENTIFIER:
            t_type = self.tokenizer.cur_token
            self.define_symbol(self.sy.ARG, t_type)
            while self.tokenizer.cur_token == COMMA:
                self.tokenizer.advance()
                t_type = self.tokenizer.cur_token
                self.define_symbol(self.sy.ARG, t_type)

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        while self.tokenizer.cur_token == "var":
            self.tokenizer.advance()
            t_type = self.tokenizer.cur_token
            self.define_symbol(self.sy.VAR, t_type)
            while self.tokenizer.cur_token == COMMA:
                self.define_symbol(self.sy.VAR, t_type)
            self.tokenizer.advance()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        statements_dic = {"let": self.compile_let,
                          "if": self.compile_if,
                          "while": self.compile_while,
                          "do": self.compile_do,
                          "return": self.compile_return}
        while self.tokenizer.cur_token in statements_dic:
            statements_dic[self.tokenizer.cur_token]()

    def compile_do(self) -> None:
        """Compiles a do statement."""

        self.tokenizer.advance()  # eats "do"
        first_name = self.tokenizer.cur_token
        self.tokenizer.advance()
        if self.tokenizer.cur_token == OPEN_PARENTHESIS:
            self.tokenizer.advance()  # eats "("
            n_param = self.compile_expression_list()
            self.tokenizer.advance()  # eats ")"
            """"""
            self.vm.write_call(f"{self.class_type}.{first_name}", n_param)
            """"""
        elif self.tokenizer.cur_token == DOT:
            # if Method push reference to the object
            if self.sy.type_of(first_name):
                self.vm.write_push(self.sy.kind_of(first_name),
                                   self.sy.index_of(first_name))
            self.tokenizer.advance()
            second_name = self.tokenizer.cur_token
            self.tokenizer.advance()
            self.tokenizer.advance()  # eats "("
            n_param = self.compile_expression_list()
            self.tokenizer.advance()  # eats ")"
            if self.sy.type_of(first_name):
                self.vm.write_call(f"{self.sy.type_of(first_name)}."
                                   f"{second_name}", n_param + 1)
            else:
                self.vm.write_call(f"{first_name}.{second_name}", n_param)
        self.vm.write_pop(self.sy.TEMP, 0)
        self.tokenizer.advance()  # eats ";"

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.tokenizer.advance()  # eats "return"
        if self.current_subroutine[
            "func_type"] == self.sy.CONS:  # If constructor
            self.vm.write_push(self.sy.POINTER, 0)
            self.tokenizer.advance()  # eats "this"
        elif self.current_subroutine[
            "ret_type"] == self.sy.VOID:  # if void return 0
            self.vm.write_push(self.sy.CONSTANT, 0)
        else:
            self.compile_expression()
        self.tokenizer.advance()  # eats ";"
        self.vm.write_return()

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.tokenizer.advance()    # eats "let"
        var = self.tokenizer.cur_token
        self.tokenizer.advance()
        if self.tokenizer.cur_token == OPEN_BRACKETS:
            self.tokenizer.advance()
            self.compile_expression()
            self.tokenizer.advance()
        self.tokenizer.advance()    # eats "="
        self.compile_expression()
        self.vm.write_pop(self.sy.kind_of(var), self.sy.index_of(var))
        self.tokenizer.advance()    # eats ";"

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # while head label:
        label1 = self.class_type + "." + str(self.label_counter)
        self.label_counter += 1
        self.vm.write_label(label1)
        for _ in range(2):  # eats 'while ('
            self.tokenizer.advance()
        self.compile_expression()
        self.vm.write_arithmetic("NOT")
        for _ in range(2):  # eats ') {'
            self.tokenizer.advance()
        # if to skip while
        label2 = self.class_type + "." + str(self.label_counter)
        self.label_counter += 1
        self.vm.write_if(label2)
        # compile statements
        self.compile_statements()
        # go to head label
        self.vm.write_goto(label1)
        # while end label
        self.vm.write_label(label2)
        self.tokenizer.advance()  # eats '}'

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.label_counter += 1
        label_false = "IF_FALSE" + "." + str(self.label_counter)
        label_end_block = "IF_END" + "." + str(self.label_counter)

        # if block compilation
        for _ in range(2):  # eats 'if ('
            self.tokenizer.advance()
        self.compile_expression()
        self.vm.write_arithmetic("NOT")
        for _ in range(2):  # eats ') {'
            self.tokenizer.advance()
        label1 = self.class_type + "." + str(self.label_counter)
        self.label_counter += 1
        # if go to else
        self.vm.write_if(label1)
        # regular if statmentes
        self.compile_statements()
        self.tokenizer.advance()  # eats '}'
        if self.tokenizer.cur_token == "else":
            for _ in range(2):  # eats 'else {'
                self.tokenizer.advance()
            self.compile_statements()  # Compile else block statements
            self.tokenizer.advance()  # eats '}'
            self.vm.write_label(label_end_block)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!
        self.compile_term()
        while self.tokenizer.cur_token in OP:
            self.tokenizer.advance()
            self.compile_term()

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        if self.tokenizer.token_type() is INT_CONST:
            self.vm.write_push(self.sy.CONSTANT, self.tokenizer.cur_token)
            self.tokenizer.advance()
        elif self.tokenizer.cur_token in KEYWORD_CONST:
            if self.tokenizer.cur_token in ["null", "false"]:
                self.vm.write_push(self.sy.CONSTANT, 0)
            elif self.tokenizer.cur_token == "true":
                self.vm.write_push(self.sy.CONSTANT, 1)
                self.vm.write_arithmetic("NEG")
            else:
                # if 'this'
                self.vm.write_push(self.sy.POINTER, 0)
            self.tokenizer.advance()
        if self.tokenizer.token_type() is STRING_CONST:
            self.tokenizer.advance()
        elif self.tokenizer.cur_token in KEYWORD_CONST:
            self.tokenizer.advance()
        elif self.tokenizer.cur_token in UNARY_OP:
            unary_op = self.tokenizer.cur_token
            self.tokenizer.advance()
            self.compile_term()
        elif self.tokenizer.cur_token == OPEN_PARENTHESIS:
            self.tokenizer.advance()
            self.compile_expression()
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == IDENTIFIER:
            first_name = self.tokenizer.cur_token
            self.tokenizer.advance()
            if self.tokenizer.cur_token == OPEN_BRACKETS:
                self.tokenizer.advance()
                self.compile_expression()
                self.tokenizer.advance()
            elif self.tokenizer.cur_token == OPEN_PARENTHESIS:
                self.tokenizer.advance()  # eats "("
                n_param = self.compile_expression_list()
                self.tokenizer.advance()  # eats ")"
                self.vm.write_call(f"{self.class_type}.{first_name}", n_param)
            elif self.tokenizer.cur_token == DOT:
                # if Method push reference to the object
                if self.sy.type_of(first_name):  # if varName
                    self.vm.write_push(self.sy.kind_of(first_name),
                                       self.sy.index_of(first_name))
                self.tokenizer.advance()  # eats '.'
                second_name = self.tokenizer.cur_token
                self.tokenizer.advance()  # eats second_name
                self.tokenizer.advance()  # eats "("
                n_param = self.compile_expression_list()
                self.tokenizer.advance()  # eats ")"
                if self.sy.type_of(first_name):
                    self.vm.write_call(f"{self.sy.type_of(first_name)}."
                                       f"{second_name}", n_param + 1)
                else:
                    self.vm.write_call(f"{first_name}.{second_name}", n_param)
            else:
                self.vm.write_push(self.sy.kind_of(first_name),self.sy.index_of(first_name))

    def compile_expression_list(self, n=0) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        if self.tokenizer.cur_token != CLOSE_PARENTHESIS:
            n += 1
            self.compile_expression()
            while self.tokenizer.cur_token == COMMA:
                n += 1
                self.tokenizer.advance()
                self.compile_expression()
        return n

    def define_symbol(self, t_kind, t_type):
        self.tokenizer.advance()
        t_name = self.tokenizer.cur_token
        self.sy.define(t_name, t_type, t_kind)
        self.tokenizer.advance()
