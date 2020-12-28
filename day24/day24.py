import pathlib
import re
from functools import reduce
from typing import Iterable
from typing import Literal
from typing import TextIO
from typing import get_args

import numpy as np
from tap import Tap

Direction = Literal['ne', 'e', 'se', 'sw', 'w', 'nw']


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of directions
    size: int  # The size of the floor

    def configure(self):
        self.add_argument('file', type=pathlib.Path)
        self.add_argument('size')


def main(args: MainArgs):
    # I'd like to make this an expanding array, but a static size is much easier
    with args.file.open('r') as file:
        directions = readDirections(file)
        origin, floor = initializeFloor(args.size, directions)
    print(np.count_nonzero(floor))


def initializeFloor(size: int, directions: Iterable[Iterable[Direction]]) -> tuple[tuple[int, int], np.ndarray]:
    floor = np.zeros((size, size), dtype=bool)
    origin = floor.shape[0] // 2, floor.shape[1] // 2
    for path in directions:
        destination = followPath(origin, path)
        floor[destination] = ~floor[destination]
    return origin, floor


def followPath(origin: tuple[int, int], path: Iterable[Direction]) -> tuple[int, int]:
    directions = {
        'ne': (-1, 1),
        'e': (0, 1),
        'se': (1, 0),
        'sw': (1, -1),
        'w': (0, -1),
        'nw': (-1, 0)
    }
    return tuple(reduce(lambda i, s: i + directions[s], path, np.array(origin)))


def readDirections(file: TextIO) -> Iterable[Iterable[Direction]]:
    pattern = re.compile('|'.join(get_args(Direction)))
    # noinspection PyTypeChecker
    return ((m.group(0) for m in pattern.finditer(line)) for line in file)


if __name__ == '__main__':
    parser = MainArgs(description='Hexagonal Grid')
    main(parser.parse_args())
