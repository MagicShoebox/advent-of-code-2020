import pathlib
import typing
from typing import Callable
from typing import List

from tap import Tap

VALIDATION = Callable[[dict], bool]


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a series of records

    def configure(self):
        self.add_argument('file', type=pathlib.Path)

def part1Valid(record: dict):
    return {'byr', 'iyr', 'eyr', 'hgt', 'hcl', 'ecl', 'pid'}.issubset(record)

def part2Valid(record: dict):
    return True

def main(args: MainArgs):
    with args.file.open('r') as file:
        print(countRecords(file, part1Valid))
        file.seek(0)
        print(countRecords(file, part2Valid))


def countRecords(file: typing.TextIO, isValid: VALIDATION) -> int:
    return sum(1
               for record
               in (dict(field.split(':')
                        for line
                        in lines
                        for field
                        in line.split())
                   for lines
                   in readRecordLines(file))
               if isValid(record))


def readRecordLines(file: typing.TextIO) -> List[str]:
    lines = []
    for line in file:
        line = line.rstrip()
        if len(line) > 0:
            lines.append(line)
        else:
            yield lines
            lines = []
    if len(lines) > 0:
        yield lines


if __name__ == '__main__':
    parser = MainArgs(description='Count the number of records'
                                  ' that contain all required fields')
    main(parser.parse_args())
