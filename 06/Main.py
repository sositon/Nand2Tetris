"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code

A = "A_COMMAND"
C = "C_COMMAND"
L = "L_COMMAND"
C_REGULAR = "111"
C_SHIFT = "101"
NEW_LINE = "\n"


def number_to_16bit(num: int) -> str:
    return '{0:016b}'.format(num)


def assemble_file(input_file: typing.TextIO,
                  output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    #
    # You should use the two-pass implementation suggested in the book:
    #
    # *Initialization*
    # Initialize the symbol table with all the predefined symbols and their
    # pre-allocated RAM addresses, according to section 6.2.3 of the book.

    symbol_table = SymbolTable()
    parser = Parser(input_file=input_file)

    while parser.has_more_commands():
        if parser.command_type() == L:
            tmp_symbol = parser.symbol()
            if not symbol_table.contains(tmp_symbol):
                tmp_address = parser.current_line
                symbol_table.add_entry(tmp_symbol, tmp_address)
                parser.lines.pop(tmp_address)
                parser.current_line -= 1
                parser.end_line -= 1
        parser.advance()

    parser.init_between_passes()
    while parser.has_more_commands():
        # A command
        if parser.command_type() == A:
            tmp_symbol = parser.symbol()
            if not tmp_symbol.isdigit():
                if symbol_table.contains(tmp_symbol):
                    output_file.write(number_to_16bit(
                        symbol_table.get_address(tmp_symbol)) + NEW_LINE)
                else:
                    symbol_table.add_entry(tmp_symbol, symbol_table.next_free)
                    symbol_table.next_free += 1
                    output_file.write(number_to_16bit(
                        symbol_table.get_address(tmp_symbol)) + NEW_LINE)
            else:
                output_file.write(number_to_16bit(int(tmp_symbol)) + NEW_LINE)
        # C command
        elif parser.command_type() == C:
            dest = Code.dest(parser.dest())
            comp = parser.comp()
            comp_b = Code.comp(comp)
            jump = Code.jump(parser.jump())
            if ">" in comp or "<" in comp:
                output_file.write(C_SHIFT + comp_b + dest + jump + NEW_LINE)
            else:
                output_file.write(C_REGULAR + comp_b + dest + jump + NEW_LINE)
        # L command
        elif parser.command_type() == L:
            tmp_address = symbol_table.get_address(parser.symbol())
            output_file.write(number_to_16bit(tmp_address) + NEW_LINE)
        parser.advance()


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
