import pathlib
import typing
from typing import List
from collections import Counter
from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of integers

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        jolts = readJolts(file)
    jolts = [0] + jolts + [jolts[-1] + 3]  # Socket and laptop
    gaps = [y - x for x, y in zip(jolts, jolts[1:])]
    frequencies = Counter(gaps)
    print(frequencies[1] * frequencies[3])


def readJolts(file: typing.TextIO) -> List[int]:
    return sorted(int(line) for line in file)


if __name__ == '__main__':
    parser = MainArgs(description='Count the gaps in a list of integers')
    main(parser.parse_args())
