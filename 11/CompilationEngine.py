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
        # Your code goes here!
        self.tokenizer = input_stream
        self.tokenizer.advance()
        self.output_stream = output_stream
        self.indent_counter = 0
        self.indent = DOUBLE_SPACE
        self.vm = VMWriter(output_stream)
        self.sy = SymbolTable()
        self.class_type = ""
        self.subroutine_list = list()
        self.compile_class()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        self.print_open_header("class")
        self.print_token()
        self.class_type = self.tokenizer.identifier()
        self.print_token()
        self.print_token()
        if self.tokenizer.cur_token in ["field", "static"]:
            self.compile_class_var_dec()
        if self.tokenizer.cur_token in ['constructor', 'function', 'method']:
            self.compile_subroutine()
        self.print_token()
        self.print_close_header("class")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        while self.tokenizer.cur_token in ["field", "static"]:
            self.print_open_header("classVarDec")
            t_kind = self.tokenizer.cur_token
            self.print_token()
            t_type = self.tokenizer.cur_token
            self.print_token()
            t_name = self.tokenizer.cur_token
            self.sy.define(t_name, t_type, t_kind)
            self.print_token()
            while self.tokenizer.cur_token == COMMA:
                self.print_token()
                t_name = self.tokenizer.cur_token
                self.sy.define(t_name, t_type, t_kind)
                self.print_token()
            self.print_token()
            self.print_close_header("classVarDec")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # subroutineDec
        while self.tokenizer.cur_token in ['constructor', 'function',
                                           'method']:
            self.print_open_header("subroutineDec")
            self.sy.start_subroutine()
            if self.tokenizer.cur_token in [self.sy.CONS, self.sy.METHOD]:
                self.sy.define("this", self.class_type, self.sy.ARG)
            for _ in range(2):
                self.print_token()
            self.subroutine_list.append(self.tokenizer.cur_token)
            for _ in range(2):
                self.print_token()
            self.compile_parameter_list()
            self.print_token()
            # subroutineBody
            self.print_open_header("subroutineBody")
            self.print_token()
            if self.tokenizer.cur_token == "var":
                self.compile_var_dec()
            self.compile_statements()
            self.print_token()
            self.print_close_header("subroutineBody")
            self.print_close_header("subroutineDec")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        self.print_open_header("parameterList")
        if self.tokenizer.cur_token in ["int", "char", "boolean"] or \
                self.tokenizer.token_type() == IDENTIFIER:
            t_type = self.tokenizer.cur_token
            self.print_token()
            t_name = self.tokenizer.cur_token
            self.sy.define(t_name, t_type, self.sy.ARG)
            self.print_token()
            while self.tokenizer.cur_token == COMMA:
                self.print_token()
                t_type = self.tokenizer.cur_token
                self.print_token()
                t_name = self.tokenizer.cur_token
                self.sy.define(t_name, t_type, self.sy.ARG)
                self.print_token()
        self.print_close_header("parameterList")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        while self.tokenizer.cur_token == "var":
            self.print_open_header("varDec")
            self.print_token()
            t_type = self.tokenizer.cur_token
            self.print_token()
            t_name = self.tokenizer.cur_token
            self.sy.define(t_name, t_type, self.sy.VAR)
            self.print_token()
            while self.tokenizer.cur_token == COMMA:
                self.print_token()
                t_name = self.tokenizer.cur_token
                self.sy.define(t_name, t_type, self.sy.VAR)
                self.print_token()
            self.print_token()
            self.print_close_header("varDec")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        self.print_open_header("statements")
        statements_dic = {"let": self.compile_let,
                          "if": self.compile_if,
                          "while": self.compile_while,
                          "do": self.compile_do,
                          "return": self.compile_return}
        while self.tokenizer.cur_token in statements_dic:
            statements_dic[self.tokenizer.cur_token]()
        self.print_close_header("statements")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.print_open_header("doStatement")
        for _ in range(2):
            self.print_token()
        if self.tokenizer.cur_token == OPEN_PARENTHESIS:
            self.print_token()
            self.compile_expression_list()
            self.print_token()
        elif self.tokenizer.cur_token == DOT:
            for _ in range(3):
                self.print_token()
            self.compile_expression_list()
            self.print_token()
        self.print_token()
        self.print_close_header("doStatement")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        self.print_open_header("letStatement")
        for _ in range(2):
            self.print_token()
        if self.tokenizer.cur_token == OPEN_BRACKETS:
            self.print_token()
            self.compile_expression()
            self.print_token()
        self.print_token()
        self.compile_expression()
        self.print_token()
        self.print_close_header("letStatement")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.print_open_header("whileStatement")
        for _ in range(2):
            self.print_token()
        self.compile_expression()
        for _ in range(2):
            self.print_token()
        self.compile_statements()
        self.print_token()
        self.print_close_header("whileStatement")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        self.print_open_header("returnStatement")
        self.print_token()
        if self.tokenizer.cur_token == SEMICOLON:
            self.print_token()
        else:
            self.compile_expression()
            self.print_token()
        self.print_close_header("returnStatement")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        self.print_open_header("ifStatement")
        for _ in range(2):
            self.print_token()
        self.compile_expression()
        for _ in range(2):
            self.print_token()
        self.compile_statements()
        self.print_token()
        if self.tokenizer.cur_token == "else":
            for _ in range(2):
                self.print_token()
            self.compile_statements()
            self.print_token()
        self.print_close_header("ifStatement")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!
        self.print_open_header("expression")
        self.compile_term()
        while self.tokenizer.cur_token in OP:
            self.print_token()
            self.compile_term()
        self.print_close_header("expression")

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
        # Your code goes here!
        self.print_open_header("term")
        if self.tokenizer.token_type() in [INT_CONST, STRING_CONST]:
            self.print_token()
        elif self.tokenizer.cur_token in KEYWORD_CONST:
            self.print_token()
        elif self.tokenizer.cur_token in UNARY_OP:
            self.print_token()
            self.compile_term()
        elif self.tokenizer.cur_token == OPEN_PARENTHESIS:
            self.print_token()
            self.compile_expression()
            self.print_token()
        elif self.tokenizer.token_type() == IDENTIFIER:
            self.print_token()
            if self.tokenizer.cur_token == OPEN_BRACKETS:
                self.print_token()
                self.compile_expression()
                self.print_token()
            elif self.tokenizer.cur_token == OPEN_PARENTHESIS:
                self.print_token()
                self.compile_expression_list()
                self.print_token()
            elif self.tokenizer.cur_token == DOT:
                for _ in range(3):
                    self.print_token()
                self.compile_expression_list()
                self.print_token()
        self.print_close_header("term")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        self.print_open_header("expressionList")
        if self.tokenizer.cur_token != CLOSE_PARENTHESIS:
            self.compile_expression()
            while self.tokenizer.cur_token == COMMA:
                self.print_token()
                self.compile_expression()
        self.print_close_header("expressionList")

    def print_open_header(self, header):
        self.output_stream.write(self.indent * self.indent_counter)
        self.output_stream.write(f"<{header}>\n")
        self.indent_counter += 1

    def print_close_header(self, header):
        self.indent_counter -= 1
        self.output_stream.write(self.indent * self.indent_counter)
        self.output_stream.write(f"</{header}>\n")

    def print_token(self):
        token = self.tokenizer.cur_token
        if self.tokenizer.token_type() == IDENTIFIER:
            self.print_identifier(token)
            return
        elif self.tokenizer.token_type() == STRING_CONST:
            token = self.tokenizer.string_val()
        elif token in self.tokenizer.SPECIAL_SYMBOLS:
            token = self.tokenizer.SPECIAL_SYMBOLS[token]
        header = HEADERS_DIC[self.tokenizer.token_type()]

        self.output_stream.write(self.indent * self.indent_counter)
        self.output_stream.write(f"<{header}> {token} </{header}>\n")
        self.tokenizer.advance()

    def print_identifier(self, token):
        header = HEADERS_DIC[self.tokenizer.token_type()]
        kind = self.sy.kind_of(token)
        type = self.sy.type_of(token)
        index = self.sy.index_of(token)
        if kind and type and index is not None:
            token = (token, kind, type, index)

        self.output_stream.write(self.indent * self.indent_counter)
        self.output_stream.write(f"<{header}> {token} </{header}>\n")
        self.tokenizer.advance()

