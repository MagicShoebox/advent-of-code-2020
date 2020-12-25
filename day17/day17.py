import pathlib
from collections import namedtuple
from typing import List
from typing import Union

import numpy as np
from tap import Tap

ORIGIN = (10, 10, 10)
WORLD = (21, 21, 21)


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a starting layer
    inactive: str  # The character representing an inactive point/cube
    active: str  # The character representing an active point/cube

    def configure(self):
        self.add_argument('file', type=pathlib.Path)
        self.add_argument('inactive')
        self.add_argument('active')


def main(args: MainArgs):
    with args.file.open('r') as file:
        start = np.genfromtxt(file, dtype=str, delimiter=1, comments=None)

    world = np.full(WORLD, args.inactive)
    world[(*ORIGIN[:-2],
           slice(ORIGIN[0] - start.shape[0] // 2, ORIGIN[0] + start.shape[0] // 2),
           slice(ORIGIN[1] - start.shape[1] // 2, ORIGIN[1] + start.shape[1] // 2))
    ] = start

    part1Result = part1(world, args.inactive, args.active, 6)
    print(np.count_nonzero(part1Result == args.active))


def part1(world: np.ndarray, inactive: str, active: str, cycles: int) -> np.ndarray:
    for _ in range(cycles):
        actives = np.pad(np.where(world == active, 1, 0), 1)
        neighbors = np.sum([actives[x] for x in slicer(actives.ndim)], 0)
        update = np.where(np.logical_and(world == inactive, neighbors == 3), active, '')
        update = np.where(
            np.logical_and(world == active, np.logical_or(neighbors < 2, neighbors > 3)), inactive, update)
        world = np.where(update != '', update, world)
    return world


def slicer(dimension: int, includeOrigin: bool = False) -> List[tuple[Union[slice, list[slice]]]]:
    slices = [slice(None, -2), slice(1, -1), slice(2, None)]
    return [tuple(slices[y // 3 ** x % 3]
                  for x in range(dimension))
            for y in range(3 ** dimension)
            if includeOrigin or y != 3 ** dimension // 2]


if __name__ == '__main__':
    parser = MainArgs(description='3D Conway\'s Game of Life')
    main(parser.parse_args())
