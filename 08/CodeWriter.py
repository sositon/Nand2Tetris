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
             "D=M\n" \
             "M=0\n"
    SYS_INIT = "@256\n" \
               "D=A\n" \
               "@SP\n" \
               "M=D\n"

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """

        self.output_stream = output_stream
        self.file_name = ""
        self.cur_function_name = ""
        self.label_counter = 0
        self.func_counter = 0
        # Bootstrap
        self.output_stream.write(CodeWriter.SYS_INIT)
        self.write_call("Sys.init", 0)

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        self.file_name = filename

    def close(self) -> None:
        """Closes the output file."""
        # Your code goes here!
        self.output_stream.close()

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        # Your code goes here!
        arithmetic_functions = {"add": self.add_sub, "sub": self.add_sub,
                                "eq": self.eq,
                                "gt": self.gt,
                                "lt": self.lt,
                                "and": self.and_or, "or": self.and_or,
                                "not": self.neg_not_shift,
                                "neg": self.neg_not_shift,
                                "shiftleft": self.neg_not_shift,
                                "shiftright": self.neg_not_shift
                                }
        self.output_stream.write(arithmetic_functions[command](command))

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
            pop_functions = {"local": self.pop_lcl_arg_this_that,
                             "argument": self.pop_lcl_arg_this_that,
                             "this": self.pop_lcl_arg_this_that,
                             "that": self.pop_lcl_arg_this_that,
                             "temp": self.pop_tmp_pt,
                             "pointer": self.pop_tmp_pt,
                             "static": self.pop_static}
            self.output_stream.write(pop_functions[segment](segment, index))

    def write_label(self, label: str) -> None:
        self.output_stream.write(f"({self.cur_function_name}.{label})\n")

    def write_goto(self, label: str) -> None:
        self.output_stream.write(f"//goto {label}\n"
                                 f"@{self.cur_function_name}.{label}\n0;JMP\n")

    def write_if(self, label: str) -> None:
        self.output_stream.write(f"//if-goto {label}\n"
                                 f"@SP\nAM=M-1\nD=M\nM=0\n"
                                 f"@{self.cur_function_name}.{label}\nD;JNE\n")

    def write_function(self, function_name: str, n_vars: int) -> None:
        self.cur_function_name = function_name
        self.output_stream.write(f"// function {function_name} {n_vars}\n")
        self.output_stream.write(f"({function_name})\n")
        [self.write_push_pop("C_PUSH", "constant", 0) for _ in range(n_vars)]

    def write_call(self, function_name: str, n_args: int) -> None:
        self.output_stream.write(f"// call {function_name} {n_args}\n")
        # push return address
        self.output_stream.write(f"@{self.file_name}$ret.{self.func_counter}\n"
                                 f"D=A\n" + CodeWriter.push_SP)
        # push LCL ARG THIS THAT
        self.output_stream.write(f"@LCL\nD=M\n" + CodeWriter.push_SP)
        self.output_stream.write(f"@ARG\nD=M\n" + CodeWriter.push_SP)
        self.output_stream.write(f"@THIS\nD=M\n" + CodeWriter.push_SP)
        self.output_stream.write(f"@THAT\nD=M\n" + CodeWriter.push_SP)
        # ARG = SP - 5 - n_args
        self.output_stream.write(f"@SP\nD=M\n@5\nD=D-A\n@{n_args}\n"
                                 f"D=D-A\n@ARG\nM=D\n")
        # LCL = SP
        self.output_stream.write(f"@SP\nD=M\n@LCL\nM=D\n")
        self.output_stream.write(f"@{function_name}\n0;JMP\n")
        self.output_stream.write(f"({self.file_name}$ret.{self.func_counter})\n")
        self.func_counter += 1

    def write_return(self) -> None:
        self.output_stream.write(f"// return\n")
        # end_frame = LCL // R13
        self.output_stream.write(f"@LCL\nD=M\n@R13\nM=D\n")
        # ret_addr = *(end_frame - 5) // R14
        self.output_stream.write(f"@5\nD=D-A\nA=D\nD=M\n@R14\nM=D\n")
        # *ARG = pop()
        self.output_stream.write(CodeWriter.pop_SP + f"@ARG\nA=M\nM=D\n")
        # SP = ARG + 1
        self.output_stream.write("@ARG\nD=M+1\n@SP\nM=D\n")
        # THAT = *(end_frame - 1)
        self.output_stream.write("@R13\nD=M\n@1\nD=D-A\nA=D\nD=M\n@THAT\nM=D\n")
        # THIS = *(end_frame - 2)
        self.output_stream.write("@R13\nD=M\n@2\nD=D-A\nA=D\nD=M\n@THIS\nM=D\n")
        # ARG = *(end_frame - 3)
        self.output_stream.write("@R13\nD=M\n@3\nD=D-A\nA=D\nD=M\n@ARG\nM=D\n")
        # LCL = *(end_frame - 4)
        self.output_stream.write("@R13\nD=M\n@4\nD=D-A\nA=D\nD=M\n@LCL\nM=D\n")
        # goto ret_addr
        self.output_stream.write("@14\nA=M\n0;JMP\n")

    # arithmetic implementations
    @staticmethod
    def add_sub(command: str) -> str:
        end = "M=D+M\n" if command == "add" else "M=M-D\n"
        return f"// {command}\n" + CodeWriter.pop_SP + \
               f"A=A-1\n" + end

    @staticmethod
    def neg_not_shift(command: str) -> str:
        operand_dic = {"neg": "-M", "not": "!M",
                       "shiftleft": "M<<", "shiftright": "M>>"}
        return f"// {command}\n" \
               f"@SP\n" \
               f"A=M-1\n" \
               f"M={operand_dic[command]}\n"

    def eq(self, command: str) -> str:
        res = f"// {command}\n" \
              "@SP\n" \
              "AM=M-1\n" \
              "D=M\n" \
              "M=0\n" \
              "@R15\n" \
              "M=D\n" \
              f"@POS.{self.label_counter}\n" \
              f"D;JGT\n" \
              f"@SP\n" \
              f"A=M-1\n" \
              f"D=M\n" \
              f"M=0\n" \
              f"@CONTINUE.{self.label_counter}\n" \
              f"D;JGT\n" \
              f"@REG.{self.label_counter}\n" \
              f"0;JMP\n" \
              f"(POS.{self.label_counter})\n" \
              f"@SP\n" \
              f"A=M-1\n" \
              f"D=M\n" \
              f"M=0\n" \
              f"@CONTINUE.{self.label_counter}\n" \
              f"D;JLT\n" \
              f"(REG.{self.label_counter})\n" \
              f"@R15\n" \
              f"D=D-M\n" \
              f"@CONTINUE.{self.label_counter}\n" \
              f"D;JLT\n" \
              f"D;JGT\n" \
              f"(TRUE.{self.label_counter})\n" \
              f"@SP\n" \
              f"A=M-1\n" \
              f"M=-1\n" \
              f"(CONTINUE.{self.label_counter})\n"
        self.label_counter += 1
        return res

    def gt(self, command: str) -> str:
        res = f"// {command}\n" \
              "@SP\n" \
              "AM=M-1\n" \
              "D=M\n" \
              "M=0\n" \
              "@R15\n" \
              "M=D\n" \
              f"@NEG.{self.label_counter}\n" \
              f"D;JLT\n" \
              f"@SP\n" \
              f"A=M-1\n" \
              f"D=M\n" \
              f"M=0\n" \
              f"@CONTINUE.{self.label_counter}\n" \
              f"D;JLT\n" \
              f"@REG.{self.label_counter}\n" \
              f"0;JMP\n" \
              f"(NEG.{self.label_counter})\n" \
              f"@SP\n" \
              f"A=M-1\n" \
              f"D=M\n" \
              f"M=0\n" \
              f"@TRUE.{self.label_counter}\n" \
              f"D;JGT\n" \
              f"(REG.{self.label_counter})\n" \
              f"@R15\n" \
              f"D=D-M\n" \
              f"@CONTINUE.{self.label_counter}\n" \
              f"D;JLE\n" \
              f"(TRUE.{self.label_counter})\n" \
              f"@SP\n" \
              f"A=M-1\n" \
              f"M=-1\n" \
              f"(CONTINUE.{self.label_counter})\n"
        self.label_counter += 1
        return res

    def lt(self, command: str) -> str:
        res = f"// {command}\n" \
              "@SP\n" \
              "AM=M-1\n" \
              "D=M\n" \
              "M=0\n" \
              "@R15\n" \
              "M=D\n" \
              f"@POS.{self.label_counter}\n" \
              f"D;JGT\n" \
              f"@SP\n" \
              f"A=M-1\n" \
              f"D=M\n" \
              f"M=0\n" \
              f"@CONTINUE.{self.label_counter}\n" \
              f"D;JGT\n" \
              f"@REG.{self.label_counter}\n" \
              f"0;JMP\n" \
              f"(POS.{self.label_counter})\n" \
              f"@SP\n" \
              f"A=M-1\n" \
              f"D=M\n" \
              f"M=0\n" \
              f"@TRUE.{self.label_counter}\n" \
              f"D;JLT\n" \
              f"(REG.{self.label_counter})\n" \
              f"@R15\n" \
              f"D=D-M\n" \
              f"@CONTINUE.{self.label_counter}\n" \
              f"D;JGE\n" \
              f"(TRUE.{self.label_counter})\n" \
              f"@SP\n" \
              f"A=M-1\n" \
              f"M=-1\n" \
              f"(CONTINUE.{self.label_counter})\n"
        self.label_counter += 1
        return res

    @staticmethod
    def and_or(command: str) -> str:
        operand = "&" if command == "and" else "|"
        return f"// {command}\n" \
               + CodeWriter.pop_SP + \
               f"A=A-1\n" \
               f"M=D{operand}M\n"

    # push pop implementations
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
               f"@{index}\n" \
               f"D=A\n" \
               f"@{CodeWriter.segment_dic[segment]}\n" \
               f"D=D+M\n" \
               f"@R15\n" \
               f"M=D\n" \
               + CodeWriter.pop_SP + \
               f"@R15\n" \
               f"A=M\n" \
               f"M=D\n"

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
