"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """
    # constants
    LOCAL = "local"
    ARG = "argument"
    STATIC = "static"
    FIELD = "field"
    VAR = "var"
    THIS = "this"
    THAT = "that"
    CLASS = "class"
    SUBROUTINE = "subroutine"
    CONS = "constructor"
    METHOD = "method"
    POINTER = "pointer"
    CONSTANT = "constant"
    VOID = "void"
    TEMP = "temp"

    # tuple indexing
    KIND = 0
    TYPE = 1
    INDEX = 2

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        # Your code goes here!
        self.class_table = dict()
        self.subroutine_table = dict()
        self.kind_counter_table = {self.VAR: 0, self.ARG: 0, self.STATIC: 0, self.FIELD: 0}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_table = dict()
        self.kind_counter_table[self.VAR] = 0
        self.kind_counter_table[self.ARG] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind == self.STATIC:
            self.class_table[name] = (kind, type, self.kind_counter_table[kind])
        elif kind == self.FIELD:
            self.class_table[name] = (self.THIS, type, self.kind_counter_table[kind])
        elif kind == self.VAR:
            self.subroutine_table[name] = (self.LOCAL, type, self.kind_counter_table[kind])
        elif kind == self.ARG:
            self.subroutine_table[name] = (kind, type, self.kind_counter_table[kind])
        self.kind_counter_table[kind] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        # Your code goes here!
        return self.kind_counter_table[kind]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][self.KIND]
        elif name in self.class_table:
            return self.class_table[name][self.KIND]
        return ""

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][self.TYPE]
        elif name in self.class_table:
            return self.class_table[name][self.TYPE]
        return ""

    def index_of(self, name: str):
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][self.INDEX]
        elif name in self.class_table:
            return self.class_table[name][self.INDEX]
        return None
