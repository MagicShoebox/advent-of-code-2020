import pathlib
import re
import typing
from itertools import takewhile
from typing import Callable

from tap import Tap

VALIDATION = Callable[[dict], bool]


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a series of records

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def part1Valid(record: dict):
    return {'byr', 'iyr', 'eyr', 'hgt', 'hcl', 'ecl', 'pid'}.issubset(record)


def part2Valid(record: dict):
    fields = {
        'byr': lambda x: 1920 <= int(x) <= 2002,
        'iyr': lambda x: 2010 <= int(x) <= 2020,
        'eyr': lambda x: 2020 <= int(x) <= 2030,
        'hgt': lambda x: x[-2:] == 'cm' and 150 <= int(x[:-2]) <= 193
                         or x[-2:] == 'in' and 59 <= int(x[:-2]) <= 76,
        'hcl': lambda x: re.match('^#[0-9a-f]{6}$', x),
        'ecl': lambda x: x in {'amb', 'blu', 'brn', 'gry', 'grn', 'hzl', 'oth'},
        'pid': lambda x: re.match('^\\d{9}$', x)
    }
    return all(key in record and rule(record[key]) for key, rule in fields.items())


def main(args: MainArgs):
    with args.file.open('r') as file:
        print(countRecords(file, part1Valid))
        file.seek(0)
        print(countRecords(file, part2Valid))


def countRecords(file: typing.TextIO, isValid: VALIDATION) -> int:
    stripped = map(str.rstrip, file)
    blocks = ([line, *takewhile(bool, stripped)] for line in stripped)
    records = (dict(field.split(':') for line in block for field in line.split()) for block in blocks)
    return sum(1 for record in records if isValid(record))


if __name__ == '__main__':
    parser = MainArgs(description='Count the number of records'
                                  ' that contain all required fields')
    main(parser.parse_args())
