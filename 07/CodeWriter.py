"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""
    segment_dic = {"local": "LCL", "argument": "ARG", "this": "THIS",
                   "that": "THAT", "temp": 5, "pointer": 3}
    push_SP = "@SP\n" \
              "AM=M+1\n" \
              "A=A-1\n" \
              "M=D\n"
    pop_SP = "@SP\n" \
             "AM=M-1\n" \
             "A=A+1\n" \
             "D=M\n"

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_stream = output_stream
        name = output_stream.name.split("/")[-1].replace(".asm", "")
        self.file_name = name

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        pass

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        # Your code goes here!
        pass

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        if command == "C_PUSH":
            push_functions = {"local": self.push_lcl_arg_this_that,
                              "argument": self.push_lcl_arg_this_that,
                              "this": self.push_lcl_arg_this_that,
                              "that": self.push_lcl_arg_this_that,
                              "temp": self.push_tmp_pt,
                              "pointer": self.push_tmp_pt,
                              "constant": self.push_constant,
                              "static": self.push_static}
            self.output_stream.write(push_functions[segment](segment, index))
        elif command == "C_POP":
            pass

    def close(self) -> None:
        """Closes the output file."""
        # Your code goes here!
        pass

    @staticmethod
    def push_constant(segment: str, index: int) -> str:
        return f"// push {segment} {index}\n" \
               f"@{index}\n" \
               "D=A\n" + CodeWriter.push_SP

    @staticmethod
    def push_lcl_arg_this_that(segment: str, index: int) -> str:
        return f"// push {segment} {index}\n" \
               f"@{index}\n" \
               "D=A\n" \
               f"@{CodeWriter.segment_dic[segment]}\n" \
               "A=D+M\n" \
               "D=M\n" + CodeWriter.push_SP

    @staticmethod
    def pop_lcl_arg_this_that(segment: str, index: int) -> str:
        return f"// pop {segment} {index}\n" \
               "@SP\n" \
               "AM=M-1\n" \
               "A=A+1\n" \
               "D=M\n" \
               f"@{segment}\n" \
               f""

    @staticmethod
    def push_tmp_pt(segment: str, index: int) -> str:
        return f"// push {segment} {index}\n" \
               f"@{CodeWriter.segment_dic[segment] + index}\n" \
               "D=M\n" + CodeWriter.push_SP

    @staticmethod
    def pop_tmp_pt(segment: str, index: int):
        return f"// pop {segment} {index}\n" + CodeWriter.pop_SP + \
               f"@{CodeWriter.segment_dic[segment] + index}\n" \
               f"M=D\n"

    def push_static(self, segment: str, index: int) -> str:
        return f"// push {segment} {index}\n" \
               f"@{self.file_name}.{index}\n" \
               "D=M\n" + CodeWriter.push_SP

    def pop_static(self, segment: str, index: int) -> str:
        return f"// pop {segment} {index}\n" + CodeWriter.pop_SP + \
               f"@{self.file_name}.{index}\n" \
               f"M=D\n"

