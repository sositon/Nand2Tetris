"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads and assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        input_lines = input_file.read().splitlines()
        new_lines = list()
        for line in input_lines:
            line = line.replace(" ", "")
            if line[0:2] == "//":
                continue
            if not line:
                continue
            line = line.split("//")[0]
            new_lines.append(line)



        self.lines = new_lines
        self.current_line = 0
        self.end_line = len(new_lines)
        self.current_command = new_lines[self.current_line]

    def init_between_passes(self) -> None:
        self.current_line = 0
        self.current_command = self.lines[self.current_line]
        return

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return bool(self.current_line < self.end_line)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        # Your code goes here!
        self.current_line += 1
        if self.has_more_commands():
            self.current_command = self.lines[self.current_line]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.current_command[0] == "@":
            return "A_COMMAND"
        if self.current_command[0] == "(":
            return "L_COMMAND"
        return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        # Your code goes here!
        command = self.command_type()
        if command == "A_COMMAND":
            return self.current_command[1:]
        return self.current_command[1:-1]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!

        dest = self.current_command
        if "=" in dest:
            dest = dest.split("=")
            return dest[0]
        return ""

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        comp = self.current_command
        if "=" in comp:
            comp = comp.split("=")
            if ";" in comp[1]:
                comp = comp[1].split(";")
                return comp[0]
            return comp[1]
        elif ";" in comp:
            comp = comp.split(";")
            return comp[0]
        return ""

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        jump = self.current_command
        if ";" in jump:
            jump = jump.split(";")
            return jump[1]
        return ""
