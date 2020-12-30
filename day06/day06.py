import pathlib
from itertools import takewhile

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a series of records

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        stripped = map(str.rstrip, file)
        blocks = ([line, *takewhile(bool, stripped)] for line in stripped)
        records = [[set(line) for line in block] for block in blocks]
        print(sum(len(set.union(*record)) for record in records))
        print(sum(len(set.intersection(*record)) for record in records))


if __name__ == '__main__':
    parser = MainArgs(description='Count the unique characters'
                                  ' in each record')
    main(parser.parse_args())
