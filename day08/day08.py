import pathlib
import re
import typing
from typing import List

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a series of instructions

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        instructions = readInstructions(file)
    print(stopOnLoop(instructions))


def stopOnLoop(instructions: List[tuple[str, int]]) -> int:
    accumulator = 0
    instructionPointer = 0

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

    loopDetection = set()
    while instructionPointer not in loopDetection:
        loopDetection.add(instructionPointer)
        instruction, argument = instructions[instructionPointer]
        cpu[instruction](argument)
    return accumulator


def readInstructions(file: typing.TextIO) -> List[tuple[str, int]]:
    pattern = re.compile(r'^(?P<instruction>.+) (?P<argument>[+-]\d+)\s*$')
    return [(match.group('instruction'), int(match.group('argument')))
            for line in file
            if (match := pattern.match(line))]


if __name__ == '__main__':
    parser = MainArgs(description='Execute a series of simple instructions')
    main(parser.parse_args())
