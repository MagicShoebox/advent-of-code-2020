import pathlib
import typing

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of binary codes

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        seats = sorted(readSeats(file))
        print(max(seats))
        print([x + 1 for x, y in zip(seats, seats[1:]) if y - x != 1])


def readSeats(file: typing.TextIO):
    letterToDigit = lambda x: '1' if x in {'B', 'R'} else '0'
    return (int("".join(map(letterToDigit, line.rstrip())), 2) for line in file)


if __name__ == '__main__':
    parser = MainArgs(description='Find the highest ID'
                                  ' contained in a list of binary codes')
    main(parser.parse_args())
