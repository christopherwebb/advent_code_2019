from typing import List
from pydantic import BaseModel
import itertools
from enum import IntEnum
from defaultlist import defaultlist


class Instruction(BaseModel):
    opcode: int
    address: int

    def assign_operate(self):
        return RanInstruction(
            instruction=self,
            result=0,
        )

    def get_next_index(self, old_index):
        return old_index + self.next_step


class TerminateInstruction(Instruction):
    next_step = 1


class IOInstruction(Instruction):
    next_step = 2


class InputInstruction(IOInstruction):
    save_address: int
    input_val: int


class OutputInstruction(IOInstruction):
    output_value: int


class ArithInstruction(Instruction):
    noun: int
    verb: int
    output_address: int
    next_step = 4

    def assign_operate(self):
        return RanInstruction(
            instruction=self,
            result=self.operate(),
        )


class AddInstruction(ArithInstruction):
    def operate(self):
        return self.noun + self.verb


class MulInstruction(ArithInstruction):
    def operate(self):
        return self.noun * self.verb


class LessThanInstruction(ArithInstruction):
    def operate(self):
        return int(self.noun < self.verb)


class EqualsInstruction(ArithInstruction):
    def operate(self):
        return int(self.noun == self.verb)


class JumpInstruction(Instruction):
    condition: int
    jump_address: int
    next_step = 3

    def get_next_index(self, old_index):
        if self.condition_passes():
            return self.jump_address
        else:
            return super().get_next_index(old_index)


class JumpIfTrueInstruction(JumpInstruction):
    def condition_passes(self):
        return bool(self.condition)


class JumpIfFalseInstruction(JumpInstruction):
    def condition_passes(self):
        return not bool(self.condition)


class AdjustRelativeInstruction(Instruction):
    next_step = 2
    relative_add: int


class RanInstruction(BaseModel):
    instruction: Instruction
    result: int


class ModeEnum(IntEnum):
    POSITION_MODE = 0
    IMMEDIATE_MODE = 1
    RELATIVE_MODE = 2


def get_digit(number, digit):
    return number // 10**digit % 10


def get_codes(instruction_code):
    opcode = instruction_code % 100
    param_mode_1 = ModeEnum(get_digit(instruction_code, 2))
    param_mode_2 = ModeEnum(get_digit(instruction_code, 3))
    param_mode_3 = ModeEnum(get_digit(instruction_code, 4))

    return opcode, param_mode_1, param_mode_2, param_mode_3


class Computer(BaseModel):
    memory: List[int]
    history: List[RanInstruction]=[]
    inputs: List=[]
    outputs: List=[]
    index: int=0
    relative_base: int=0
    terminated: bool=False

    def get_var(self, var, param_mode: ModeEnum):
        if param_mode == ModeEnum.POSITION_MODE:
            self.pad_mem(var)
            return self.memory[var]
        elif param_mode == ModeEnum.IMMEDIATE_MODE:
            return var
        elif param_mode == ModeEnum.RELATIVE_MODE:
            self.pad_mem(self.relative_base + var)
            return self.memory[self.relative_base + var]

    def pad_mem(self, new_length):
        self.memory += [0] * ((new_length + 1) - len(self.memory))

    def get_address(self, var, param_mode: ModeEnum):
        if param_mode == ModeEnum.POSITION_MODE:
            return var
        elif param_mode == ModeEnum.RELATIVE_MODE:
            return self.relative_base + var

    def set_address(self, address, value, param_mode: ModeEnum):
        act_address = self.get_address(address, param_mode)
        self.pad_mem(act_address)
        self.memory[act_address] = value


    def run(self):
        # index = 0
        # keep_running = True

        instructionMap = {
            1: AddInstruction,
            2: MulInstruction,
            3: InputInstruction,
            4: OutputInstruction,
            5: JumpIfTrueInstruction,
            6: JumpIfFalseInstruction,
            7: LessThanInstruction,
            8: EqualsInstruction,
            9: AdjustRelativeInstruction,
            99: TerminateInstruction,
        }

        arith_instructions = [
            AddInstruction,
            MulInstruction,
            LessThanInstruction,
            EqualsInstruction
        ]

        io_instructions = [
            InputInstruction,
            OutputInstruction,
        ]

        jmp_instructions = [
            JumpIfTrueInstruction,
            JumpIfFalseInstruction,
        ]

        while not self.terminated:
            self.pad_mem(self.index)
            opcode, pm_1, pm_2, pm_3 = get_codes(self.memory[self.index])
            instructionType = instructionMap[opcode]

            if instructionType in arith_instructions:
                self.pad_mem(self.index + 3)
                loc_1, loc_2, loc_3 = self.memory[self.index+1:self.index+4]

                var_1 = self.get_var(loc_1, pm_1)
                var_2 = self.get_var(loc_2, pm_2)

                instruct = instructionType(
                    opcode=opcode,
                    address=self.index,
                    noun=var_1,
                    verb=var_2,
                    output_address=loc_3,
                )

                instructed = instruct.assign_operate()
                # self.pad_mem(instructed.instruction.output_address)
                # self.memory[instructed.instruction.output_address] = instructed.result
                self.set_address(instructed.instruction.output_address, instructed.result, pm_3)

            elif instructionType in io_instructions:
                self.pad_mem(self.index + 1)
                loc_1 = self.memory[self.index+1]
                var_1 = self.get_var(loc_1, pm_1)

                if instructionType == InputInstruction:
                    if not self.inputs:
                        return

                    value = self.inputs.pop(0)
                    instruct = InputInstruction(
                        opcode=opcode,
                        address=self.index,
                        save_address=loc_1,
                        input_val=value
                    )

                    # if pm_1 == ModeEnum.POSITION_MODE:
                    #     address = instruct.save_address
                    # else:
                    #   address = self.relative_base + instruct.save_address
                    # address = get_address
                    # self.pad_mem(address)
                    # self.memory[address] = value
                    self.set_address(instruct.save_address, value, pm_1)
                else:
                    instruct = OutputInstruction(
                        opcode=opcode,
                        address=self.index,
                        output_value=var_1,
                    )
                    self.outputs.append(instruct.output_value)

                instructed = instruct.assign_operate()

            elif instructionType in jmp_instructions:
                self.pad_mem(self.index + 2)
                loc_1, loc_2 = self.memory[self.index+1:self.index+3]

                var_1 = self.get_var(loc_1, pm_1)
                var_2 = self.get_var(loc_2, pm_2)

                instruct = instructionType(
                    opcode=opcode,
                    address=self.index,
                    condition=var_1,
                    jump_address=var_2,
                )

                instructed = instruct.assign_operate()

            elif instructionType == AdjustRelativeInstruction:
                self.pad_mem(self.index + 1)
                loc_1 = self.memory[self.index+1]
                var_1 = self.get_var(loc_1, pm_1)

                instruct = instructionType(
                    opcode=opcode,
                    address=self.index,
                    relative_add=var_1
                )
                self.relative_base += instruct.relative_add
                instructed = instruct.assign_operate()

            elif opcode == 99:
                instruct = TerminateInstruction(
                    opcode=opcode, address=self.index
                )
                self.terminated = True
                instructed = instruct.assign_operate()

            self.index = instruct.get_next_index(self.index)
            self.history.append(instructed)

        # return computer


def parse_opcodes(input_str):
    return [int(x) for x in input_str.strip().split(',')]


def create_and_run(codes, inputs=None):
    inputs = inputs or []
    computer = Computer(memory=codes.copy(), inputs=inputs)
    computer.run()
    return computer


test_programs_1 = parse_opcodes('109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99\n')
test_programs_2 = parse_opcodes('1102,34915192,34915192,7,4,7,99,0\n')
test_programs_3 = parse_opcodes('104,1125899906842624,99\n')

test_comp_1 = create_and_run(test_programs_1)
test_comp_2 = create_and_run(test_programs_2)
test_comp_3 = create_and_run(test_programs_3)

assert test_comp_1.outputs == [109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99]
assert len(str(test_comp_2.outputs[0])) == 16
assert test_comp_3.outputs == [1125899906842624]

with open('input.txt') as f:
    input_mem = parse_opcodes(f.read())
computer = create_and_run(input_mem, [1])
print('Result stage 1: %s' % computer.outputs)

computer = create_and_run(input_mem, [2])
print('Result stage 2: %s' % computer.outputs)

