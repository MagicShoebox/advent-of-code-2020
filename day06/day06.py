import pathlib
import typing
from typing import Iterable
from typing import List

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a series of records

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        records = readRecords(file)
        print(sum(len(set.union(*record)) for record in records))
        print(sum(len(set.intersection(*record)) for record in records))


def readRecords(file: typing.TextIO) -> Iterable[Iterable[set[str]]]:
    return [[set(answer for answer in line)
             for line in lines]
            for lines in readRecordLines(file)]


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
    parser = MainArgs(description='Count the unique characters'
                                  ' in each record')
    main(parser.parse_args())
