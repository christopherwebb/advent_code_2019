from typing import List
from pydantic import BaseModel


class Instruction(BaseModel):
    opcode: int
    address: int


class TerminateInstruction(Instruction):
    next_step = 1


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


class RanInstruction(BaseModel):
    instruction: Instruction
    result: int


class ComputedResult(BaseModel):
    memory: List[int]
    history: List[RanInstruction]


def run(memory) -> ComputedResult:
    index = 0

    keep_running = True
    history = []
    while keep_running:
        opcode = memory[index]

        if opcode == 1 or opcode == 2:
            loc_1, loc_2, loc_3 = memory[index+1:index+4]

            instructionType = AddInstruction if opcode == 1 else MulInstruction
            instruct = instructionType(
                opcode=1,
                address=index,
                noun=memory[loc_1],
                verb=memory[loc_2],
                output_address=loc_3,
            )

            instructed = instruct.assign_operate()
            memory[instructed.instruction.output_address] = instructed.result

        elif opcode == 99:
            instruct = TerminateInstruction(opcode=opcode, address=index)
            keep_running = False

        index += instruct.next_step
        history.append(instructed)

    return ComputedResult(memory=memory, history=history)

# 1,0,0,0,99 becomes 2,0,0,0,99 (1 + 1 = 2).
# 2,3,0,3,99 becomes 2,3,0,6,99 (3 * 2 = 6).
# 2,4,4,5,99,0 becomes 2,4,4,5,99,9801 (99 * 99 = 9801).
# 1,1,1,4,99,5,6,0,99 becomes 30,1,1,4,2,5,6,0,99.

test_1 = [1, 0, 0, 0, 99]
test_2 = [2, 3, 0, 3, 99]
test_3 = [2, 4, 4, 5, 99, 0]
test_4 = [1, 1, 1, 4, 99, 5, 6, 0, 99]

assert run(test_1).memory == [2, 0, 0, 0, 99]
assert run(test_2).memory == [2, 3, 0, 6, 99]
assert run(test_3).memory == [2, 4, 4, 5, 99, 9801]
assert run(test_4).memory == [30, 1, 1, 4, 2, 5, 6, 0, 99]

def parse_opcodes(input_str):
    return [int(x) for x in input_str.strip().split(',')]

assert run(parse_opcodes('1,0,0,0,99\n')).memory == [2, 0, 0, 0, 99]
assert run(parse_opcodes('2,3,0,3,99\n')).memory == [2, 3, 0, 6, 99]
assert run(parse_opcodes('2,4,4,5,99,0\n')).memory == [2, 4, 4, 5, 99, 9801]
assert run(parse_opcodes('1,1,1,4,99,5,6,0,99\n')).memory == [30, 1, 1, 4, 2, 5, 6, 0, 99]

with open('input.txt') as f:
    input_mem = parse_opcodes(f.read())

input_mem[1] = 12
input_mem[2] = 2

results = run(input_mem[:])
print("Memory at 0: %s" % results.memory[0])

for noun in range(99):
    for verb in range(99):
        input_instance = input_mem[:]
        input_instance[1] = noun
        input_instance[2] = verb

        results = run(input_instance)
        if results.memory[0] == 19690720:
            # what_i_want = 
            print('Part 2 %s' % (
                100 * noun + verb
            ))
