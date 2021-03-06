"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


def remove_comments(string):
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string

    return regex.sub(_replacer, string)


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.

    An Xxx .jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of space characters,
    newline characters, and comments, which are ignored. There are three
    possible comment formats: /* comment until closing */ , /** API comment
    until closing */ , and // comment until the line’s end.

    ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’);
    xxx: regular typeface is used for names of language constructs
    (‘non-terminals’);
    (): parentheses are used for grouping of language constructs;
    x | y: indicates that either x or y can appear;
    x?: indicates that x appears 0 or 1 times;
    x*: indicates that x appears 0 or more times.

    ** Lexical elements **
    The Jack language includes five types of terminal elements (tokens).
    1. keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' |
    'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' | 'false'
    | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 'while' | 'return'
    2. symbol:  '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
    '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    3. integerConstant: A decimal number in the range 0-32767.
    4. StringConstant: '"' A sequence of Unicode characters not including
    double quote or newline '"'
    5. identifier: A sequence of letters, digits, and underscore ('_') not
    starting with a digit.


    ** Program structure **
    A Jack program is a collection of classes, each appearing in a separate
    file. The compilation unit is a class. A class is a sequence of tokens
    structured according to the following context free syntax:

    class: 'class' className '{' classVarDec* subroutineDec* '}'
    classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    type: 'int' | 'char' | 'boolean' | className
    subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
        subroutineName '(' parameterList ')' subroutineBody
    parameterList: ((type varName) (',' type varName)*)?
    subroutineBody: '{' varDec* statements '}'
    varDec: 'var' type varName (',' varName)* ';'
    className: identifier
    subroutineName: identifier
    varName: identifier


    ** Statements **
    statements: statement*
    statement: letStatement | ifStatement | whileStatement | doStatement |
    returnStatement
    letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
    statements '}')?
    whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    doStatement: 'do' subroutineCall ';'
    returnStatement: 'return' expression? ';'


    ** Expressions **
    expression: term (op term)*
    term: integerConstant | stringConstant | keywordConstant | varName |
    varName '['expression']' | subroutineCall | '(' expression ')' | unaryOp
    term
    subroutineCall: subroutineName '(' expressionList ')' | (className |
    varName) '.' subroutineName '(' expressionList ')'
    expressionList: (expression (',' expression)* )?
    op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    unaryOp: '-' | '~' | '^' | '#'
    keywordConstant: 'true' | 'false' | 'null' | 'this'

    If you are wondering whether some Jack program is valid or not, you should
    use the built-in JackCompiler to compiler it. If the compilation fails, it
    is invalid. Otherwise, it is valid.
    """
    KEY_WORDS = ["class", "constructor", "function", "method", "field",
                 "static", "var", "int", "char", "boolean", "void", "true",
                 "false", "null", "this", "let", "do", "if", "else",
                 "while", "return"]
    SYMBOLS = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*",
               "/", "&", "|", "<", ">", "=", "~", "#", "^"]
    SPECIAL_SYMBOLS = {"<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;"}

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        input_file = input_stream.read()
        """comments handling"""
        input_file = remove_comments(input_file)
        input_lines = input_file.splitlines()
        """ init variables"""
        tokens = list()
        str_const_flag = False
        str_const = ""
        line_part_2 = ""
        for line in input_lines:
            """pre process"""
            line = line.strip()
            line = line.replace("\t", "")
            line = line.replace("    ", "")
            """string constant"""
            if line.find('"') != -1:
                str_const_flag = True
                idx_2 = line.find('"')
                idx_3 = line.find('"', idx_2 + 1)
                str_const = line[idx_2:idx_3]
                line_part_2 = line[idx_3 + 1:]
                line = line[:idx_2]
            self.line_to_tokens(line, tokens)
            """string constant"""
            if str_const_flag:
                tokens.append(str_const)
                str_const_flag = False
                self.line_to_tokens(line_part_2, tokens)

        self.tokens = tokens
        self.cur_token = ""
        self.token_count = -1
        self.last_token = len(tokens)

    def line_to_tokens(self, line: str, tokens: [str]) -> None:
        """
        gets a line and add the all the tokens in line to the tokens array
        """
        temp_tok = ""
        for letter in line:
            if letter == " ":
                if temp_tok:
                    tokens.append(temp_tok)
                    temp_tok = ""
                continue
            if letter in self.SYMBOLS:
                if temp_tok:
                    tokens.append(temp_tok)
                    temp_tok = ""
                tokens.append(letter)
                continue
            else:
                temp_tok += letter
        if temp_tok:
            tokens.append(temp_tok)

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        return self.token_count < self.last_token

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # Your code goes here!
        self.token_count += 1
        if self.has_more_tokens():
            self.cur_token = self.tokens[self.token_count]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        token = self.cur_token
        if token in self.KEY_WORDS:
            return "KEYWORD"
        elif token in self.SYMBOLS:
            return "SYMBOL"
        elif token.startswith('"'):
            return "STRING_CONST"
        elif token.isdigit() and 0 <= int(token) <= 32767:
            return "INT_CONST"
        elif token.isidentifier():
            return "IDENTIFIER"
        else:
            return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        return self.cur_token

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        # Your code goes here!
        if self.cur_token in self.SPECIAL_SYMBOLS:
            return self.SPECIAL_SYMBOLS[self.cur_token]
        return self.cur_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        # Your code goes here!
        return self.cur_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        # Your code goes here!
        return int(self.cur_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        # Your code goes here!
        return self.cur_token[1:]
