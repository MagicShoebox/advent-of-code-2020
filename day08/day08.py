import pathlib
import re
import typing
from collections import OrderedDict
from typing import List

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a series of instructions

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        instructions = readInstructions(file)
    success, accumulator, executionPath = execute(instructions)
    print(accumulator)
    for bugCandidatePointer in reversed(executionPath):
        bugCandidate = instructions[bugCandidatePointer]
        if bugCandidate[0] == 'acc':
            continue
        instructions[bugCandidatePointer] = ('jmp' if bugCandidate[0] == 'nop' else 'nop', bugCandidate[1])
        success, accumulator, _ = execute(instructions)
        if success:
            break
        instructions[bugCandidatePointer] = bugCandidate
    print(accumulator)


def execute(instructions: List[tuple[str, int]]) -> tuple[bool, int, OrderedDict[int, None]]:
    instructionPointer = 0
    accumulator = 0

    def acc(x):
        nonlocal accumulator, instructionPointer
        accumulator += x
        instructionPointer += 1

    def jmp(x):
        nonlocal instructionPointer
        instructionPointer += x

    def nop(_):
        nonlocal instructionPointer
        instructionPointer += 1

    cpu = {
        'acc': acc,
        'jmp': jmp,
        'nop': nop
    }

    executionPath = OrderedDict()
    while instructionPointer not in executionPath and instructionPointer < len(instructions):
        executionPath[instructionPointer] = None
        instruction, argument = instructions[instructionPointer]
        cpu[instruction](argument)
    return instructionPointer == len(instructions), accumulator, executionPath


def readInstructions(file: typing.TextIO) -> List[tuple[str, int]]:
    pattern = re.compile(r'^(?P<instruction>.+) (?P<argument>[+-]\d+)\s*$')
    return [(match.group('instruction'), int(match.group('argument')))
            for line in file
            if (match := pattern.match(line))]


if __name__ == '__main__':
    parser = MainArgs(description='Execute a series of simple instructions')
    main(parser.parse_args())
