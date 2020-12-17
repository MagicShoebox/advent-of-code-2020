import pathlib
import typing
from math import prod

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of integers, one per line
    size: int  # The number of integers to combine
    target: int  # The total sum to search for

    def configure(self):
        # TODO: add validation (size > 0, target > 0)
        self.add_argument('file', type=pathlib.Path)
        self.add_argument('size')
        self.add_argument('target')


def main(args: MainArgs):
    with args.file.open('r') as file:
        integers = findIntegers(file, args.size, args.target)
    print(prod(integers))


def findIntegers(file: typing.TextIO, size: int, target: int) -> list[int]:
    targets = [{target}]
    targets.extend([set() for _ in range(size - 1)])
    for line in file:
        current = int(line)
        if current in targets[-1]:
            result = [current]
            for level in targets[-2::-1]:
                for remainder in level:
                    if sum(result) + target - remainder in targets[1]:
                        result.append(remainder - sum(result))
                        break
            if len(result) == size:
                return result
        else:
            for level in range(size - 2, -1, -1):
                for remainder in targets[level]:
                    new_target = remainder - current
                    if new_target > 0:
                        targets[level + 1].add(new_target)
    raise ValueError("Target not found in all sums")


if __name__ == '__main__':
    parser = MainArgs(description='Determine the product of integers'
                                  ' that sum to a target')
    main(parser.parse_args())
