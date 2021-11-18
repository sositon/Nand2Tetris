"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is:
        input_lines = input_file.read().splitlines()
        new_lines = list()
        for line in input_lines:
            line = line.strip(" ")
            line = line.replace("\t", "")
            line = line.split("//")
            if not line[0]:
                continue
            line = line[0].split(" ")
            new_line = list()
            for arg in line:
                if arg and "//" not in arg:
                    new_line.append(arg)
            new_lines.append(new_line)

        self.lines = new_lines
        self.end_line = len(new_lines)
        self.line_counter = 0
        self.cur_command = self.lines[self.line_counter]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        return bool(self.line_counter < self.end_line)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        # Your code goes here!
        self.line_counter += 1
        if self.has_more_commands():
            self.cur_command = self.lines[self.line_counter]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        # Your code goes here!
        command_length = len(self.cur_command)
        command = self.cur_command[0]
        if command_length == 1:
            return "C_ARITHMETIC"
        if command_length == 3:
            if command == "pop":
                return "C_POP"
            if command == "push":
                return "C_PUSH"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        # Your code goes here!

        return self.cur_command[0] if self.command_type() == "C_ARITHMETIC" \
            else self.cur_command[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        # Your code goes here!
        return int(self.cur_command[2])
