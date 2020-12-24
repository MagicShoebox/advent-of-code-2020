import pathlib
import re
import typing
from dataclasses import dataclass
from functools import reduce
from operator import or_ as logical_or
from typing import Iterable
from typing import Union

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of masks and values

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


@dataclass
class MemInstruction:
    address: int
    value: int


@dataclass
class MaskInstruction:
    mask: str


def main(args: MainArgs):
    with args.file.open('r') as file:
        memory = part1(readInstructions(file))
        print(sum(memory.values()))
        file.seek(0)
        memory = part2(readInstructions(file))
        print(sum(memory.values()))


def part1(instructions: Iterable[Union[MemInstruction, MaskInstruction]]) -> dict[int, int]:
    memory = dict()
    mask = None
    values = None
    for instruction in instructions:
        if isinstance(instruction, MaskInstruction):
            mask = int(''.join('1' if c == 'X' else '0' for c in instruction.mask), 2)
            values = int(''.join('0' if c == 'X' else c for c in instruction.mask), 2)
        else:
            # Applying the mask with AND forces 0 into all non-X digits, then OR replaces with values
            memory[instruction.address] = instruction.value & mask | values
    return memory


def part2(instructions: Iterable[Union[MemInstruction, MaskInstruction]]) -> dict[int, int]:
    memory = dict()
    mask = None
    floating = None
    for instruction in instructions:
        if isinstance(instruction, MaskInstruction):
            mask = int(''.join('1' if c == 'X' else c for c in instruction.mask), 2)
            floating = [idx for idx, c in enumerate(reversed(instruction.mask)) if c == 'X']
        elif floating:
            # Each floating bit is a binary digit, so n bits have 2^n permutations
            for permutation in range(2 ** len(floating)):
                # Isolate each digit of the permutation then shift the remaining places to put it in floating spot
                # Combine these with OR to produce a set of floating digits in the appropriate spots
                floatValue = reduce(
                    logical_or,
                    ((permutation & 1 << digit) << (floating[digit] - digit) for digit in range(len(floating))))
                # Applying the mask with OR forces 1 into all the X spots, then AND replaces float digits
                memory[(instruction.address | mask) & ~floatValue] = instruction.value

    return memory


def readInstructions(file: typing.TextIO) -> Iterable[Union[MemInstruction, MaskInstruction]]:
    memPattern = re.compile(r'^mem\[(?P<address>\d+)] = (?P<value>\d+)\s*$')
    for line in file:
        if match := memPattern.match(line):
            yield MemInstruction(int(match.group('address')), int(match.group('value')))
        else:
            yield MaskInstruction(line.split()[2])


if __name__ == '__main__':
    parser = MainArgs(description='Apply bitmasks'
                                  ' and calculate a sum')
    main(parser.parse_args())
