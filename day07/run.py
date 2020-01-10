from typing import List
from pydantic import BaseModel
import itertools

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


def get_codes(instruction_code):
    opcode = instruction_code % 100
    param_mode_1 = bool(instruction_code % 1000 - (instruction_code % 100))
    param_mode_2 = bool(instruction_code % 10000 - (instruction_code % 1000))
    param_mode_3 = bool(instruction_code % 100000 - (instruction_code % 10000))

    return opcode, param_mode_1, param_mode_2, param_mode_3


class Computer(BaseModel):
    memory: List[int]
    history: List[RanInstruction]=[]
    inputs: List=[]
    outputs: List=[]
    index: int=0
    terminated: bool=False

    def get_var(self, var, param_mode):
        if param_mode:
            return var
        else:
            return self.memory[var]

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
            opcode, pm_1, pm_2, pm_3 = get_codes(self.memory[self.index])
            instructionType = instructionMap[opcode]

            if instructionType in arith_instructions:
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
                self.memory[instructed.instruction.output_address] = instructed.result

            elif instructionType in io_instructions:
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
                    self.memory[instruct.save_address] = value
                else:
                    instruct = OutputInstruction(
                        opcode=opcode,
                        address=self.index,
                        output_value=var_1,
                    )
                    self.outputs.append(instruct.output_value)

                instructed = instruct.assign_operate()

            elif instructionType in jmp_instructions:
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


# def run_amps(combo, source_mem):
#     next_sig = 0
#     for input_sig in combo:
#         computer = Computer(
#             memory=source_mem.copy(),
#             inputs=[input_sig, next_sig],
#         )
#         computer.run()
#         next_sig = computer.outputs[0]

#     return next_sig

def run_amps(combo, source_mem):
    # def all_running 
    next_sig = 0
    computers = [Computer(memory=source_mem.copy(), inputs=[]) for x in range (5)]
    for input_sig, computer in zip(combo, computers):
        computer.inputs.append(input_sig)

    while not all(comp.terminated for comp in computers):
        for comp in computers:
            comp.inputs.append(next_sig)
            comp.run()
            next_sig = comp.outputs.pop()

    return next_sig

def run_combos(source_mem):
    combos = [x for x in itertools.permutations(range(5), 5)]

    results = [run_amps(combo, source_mem) for combo in combos]
    return max(results)


def run_feedback_combos(source_mem):
    combos = [x for x in itertools.permutations(range(5, 10), 5)]
    results = [run_amps(combo, source_mem) for combo in combos]
    return max(results)


test_programs_1 = parse_opcodes('3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0\n')
test_programs_2 = parse_opcodes('3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0\n')
test_programs_3 = parse_opcodes('3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0\n')

assert run_amps([4,3,2,1,0], test_programs_1) == 43210
assert run_amps([0,1,2,3,4], test_programs_2) == 54321
assert run_amps([1,0,4,3,2], test_programs_3) == 65210

assert run_combos(test_programs_1) == 43210
assert run_combos(test_programs_2) == 54321
assert run_combos(test_programs_3) == 65210

with open('input.txt') as f:
    input_mem = parse_opcodes(f.read())
result = run_combos(input_mem)
print('Result stage 1: %s' % result)

test_programs_4 = parse_opcodes('3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5')
test_programs_5 = parse_opcodes('3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10')

assert run_amps([9,8,7,6,5], test_programs_4) == 139629729
assert run_amps([9,7,8,5,6], test_programs_5) == 18216

result = run_feedback_combos(input_mem)
print('Result stage 2: %s' % result)
