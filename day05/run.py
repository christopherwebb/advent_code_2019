from typing import List
from pydantic import BaseModel


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


class RanInstruction(BaseModel):
    instruction: Instruction
    result: int


class Computer(BaseModel):
    memory: List[int]
    history: List[RanInstruction]=[]
    inputs: List=[]
    outputs: List=[]

    def get_var(self, var, param_mode):
        if param_mode:
            return var
        else:
            return self.memory[var]


def get_codes(instruction_code):
    opcode = instruction_code % 100
    param_mode_1 = bool(instruction_code % 1000 - (instruction_code % 100))
    param_mode_2 = bool(instruction_code % 10000 - (instruction_code % 1000))
    param_mode_3 = bool(instruction_code % 100000 - (instruction_code % 10000))

    return opcode, param_mode_1, param_mode_2, param_mode_3


def run(computer: Computer):
    index = 0

    keep_running = True
    instructionMap = {
        1: AddInstruction,
        2: MulInstruction,
        3: InputInstruction,
        4: OutputInstruction,
        5: JumpIfTrueInstruction,
        6: JumpIfFalseInstruction,
        7: LessThanInstruction,
        8: EqualsInstruction,
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

    while keep_running:
        opcode, pm_1, pm_2, pm_3 = get_codes(computer.memory[index])
        instructionType = instructionMap[opcode]

        if instructionType in arith_instructions:
            loc_1, loc_2, loc_3 = computer.memory[index+1:index+4]

            var_1 = computer.get_var(loc_1, pm_1)
            var_2 = computer.get_var(loc_2, pm_2)

            instruct = instructionType(
                opcode=opcode,
                address=index,
                noun=var_1,
                verb=var_2,
                output_address=loc_3,
            )

            instructed = instruct.assign_operate()
            computer.memory[instructed.instruction.output_address] = instructed.result

        elif instructionType in io_instructions:
            loc_1 = computer.memory[index+1]
            var_1 = computer.get_var(loc_1, pm_1)

            if instructionType == InputInstruction:
                value = computer.inputs.pop()
                instruct = InputInstruction(
                    opcode=opcode,
                    address=index,
                    save_address=loc_1,
                    input_val=value
                )
                computer.memory[instruct.save_address] = value
            else:
                instruct = OutputInstruction(
                    opcode=opcode,
                    address=index,
                    output_value=var_1,
                )
                computer.outputs.append(instruct.output_value)

            instructed = instruct.assign_operate()

        elif instructionType in jmp_instructions:
            loc_1, loc_2 = computer.memory[index+1:index+3]

            var_1 = computer.get_var(loc_1, pm_1)
            var_2 = computer.get_var(loc_2, pm_2)

            instruct = instructionType(
                opcode=opcode,
                address=index,
                condition=var_1,
                jump_address=var_2,
            )

            instructed = instruct.assign_operate()

        elif opcode == 99:
            instruct = TerminateInstruction(opcode=opcode, address=index)
            keep_running = False
            instructed = instruct.assign_operate()

        index = instruct.get_next_index(index)
        computer.history.append(instructed)

    return computer

def parse_opcodes(input_str):
    return [int(x) for x in input_str.strip().split(',')]

print(get_codes(1002))
assert get_codes(1002) == (2, 0, 1, 0)

assert run(Computer(memory=parse_opcodes('1002,4,3,4,33\n'))).memory == [1002, 4, 3, 4, 99]

test_io = run(Computer(memory=parse_opcodes('3,0,4,0,99\n'), inputs=[76]))
assert test_io.inputs == []
assert test_io.outputs == [76]

test_mems = {
    'mem1': parse_opcodes('3,9,8,9,10,9,4,9,99,-1,8\n'),
    'mem2': parse_opcodes('3,9,7,9,10,9,4,9,99,-1,8\n'),
    'mem3': parse_opcodes('3,3,1108,-1,8,3,4,3,99\n'),
    'mem4': parse_opcodes('3,3,1107,-1,8,3,4,3,99\n'),
    'mem5': parse_opcodes('3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9\n'),
    'mem6': parse_opcodes('3,3,1105,-1,9,1101,0,0,12,4,12,99,1\n'),
    'mem7': parse_opcodes('3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99\n'),
}

for test_mem, tests in [
    ['mem1', [
        [6, 0],
        [7, 0],
        [8, 1],
        [9, 0],
    ]],
    ['mem2', [
        [6, 1],
        [7, 1],
        [8, 0],
        [9, 0],
    ]],
    ['mem3', [
        [6, 0],
        [7, 0],
        [8, 1],
        [9, 0],
    ]],
    ['mem4', [
        [6, 1],
        [7, 1],
        [8, 0],
        [9, 0],
    ]],
    ['mem5', [
        [0, 0],
        [1, 1],
    ]],
    ['mem6', [
        [0, 0],
        [1, 1],
    ]],
    ['mem7', [
        [7, 999],
        [8, 1000],
        [9, 1001],
    ]],
]:
    for test_input, test_output in tests:
        print('Running test: %s %s %s' % (test_mem, test_input, test_output))
        test_memory = test_mems[test_mem].copy()
        mem_before = test_memory.copy()
        try:
            test_computer = run(Computer(
                memory=test_memory,
                inputs=[test_input],
            ))
        except:
            print('Memory before: %s' % mem_before)
            print('History: %s' % test_computer.history)
            print('Memory after: %s' % test_computer.memory)

        print('Test result: %s' % test_computer.outputs)
        assert test_computer.outputs == [test_output]

with open('input.txt') as f:
    input_mem = parse_opcodes(f.read())
comp = run(Computer(memory=input_mem.copy(), inputs=[1]))
print(comp.outputs)

comp = run(Computer(memory=input_mem.copy(), inputs=[5]))
print(comp.outputs)
