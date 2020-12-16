from tap import Tap
import pathlib
import typing


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of integers, one per line
    target: int  # The total sum to search for

    def configure(self):
        self.add_argument('file', type=pathlib.Path)
        self.add_argument('target')


def main(args: MainArgs):
    with args.file.open('r') as file:
        x1, x2 = findIntegers(file, args.target)
    print(x1 * x2)


def findIntegers(file: typing.TextIO, target: int) -> (int, int):
    # Note: if the number of lines * the size of an integer is larger than the target,
    # it would be more efficient to simply use a boolean array the size of the target.
    seen = set()
    for line in file:
        current = int(line)
        if current in seen:
            return current, target - current
        seen.add(target - current)
    raise ValueError("Target not found in all sums")

if __name__ == '__main__':
    parser = MainArgs(description='Determine which two integers'
                                  ' in a list sum to a third')
    main(parser.parse_args())
