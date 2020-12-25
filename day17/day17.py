import pathlib
from typing import List
from typing import Union

import numpy as np
from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a starting layer
    inactive: str  # The character representing an inactive point/cube
    active: str  # The character representing an active point/cube
    dimensions: int  # The number of dimensions
    size: int  # The size of the hypercube in each dimension
    cycles: int  # The number of cycles to run

    def configure(self):
        self.add_argument('file', type=pathlib.Path)
        self.add_argument('inactive')
        self.add_argument('active')
        self.add_argument('dimensions')
        self.add_argument('size')
        self.add_argument('cycles')


def main(args: MainArgs):
    with args.file.open('r') as file:
        start = np.genfromtxt(file, dtype=str, delimiter=1, comments=None)

    origin = [args.size // 2 for _ in range(args.dimensions)]

    world = np.full([args.size for _ in range(args.dimensions)], args.inactive)
    world[(*origin[:-2],
           slice(origin[0] - start.shape[0] // 2, origin[0] + start.shape[0] // 2),
           slice(origin[1] - start.shape[1] // 2, origin[1] + start.shape[1] // 2))
    ] = start

    world = run(world, args.inactive, args.active, args.cycles)
    print(np.count_nonzero(world == args.active))


def run(world: np.ndarray, inactive: str, active: str, cycles: int) -> np.ndarray:
    for _ in range(cycles):
        actives = np.pad(np.where(world == active, 1, 0), 1)
        neighbors = np.sum([actives[x] for x in slicer(actives.ndim)], 0)
        update = np.where(np.logical_and(world == inactive, neighbors == 3), active, '')
        update = np.where(
            np.logical_and(world == active, np.logical_or(neighbors < 2, neighbors > 3)), inactive, update)
        world = np.where(update != '', update, world)
    return world


def slicer(dimensions: int, includeOrigin: bool = False) -> List[tuple[Union[slice, list[slice]]]]:
    slices = [slice(None, -2), slice(1, -1), slice(2, None)]
    return [tuple(slices[y // 3 ** x % 3]
                  for x in range(dimensions))
            for y in range(3 ** dimensions)
            if includeOrigin or y != 3 ** dimensions // 2]


if __name__ == '__main__':
    parser = MainArgs(description='3D Conway\'s Game of Life')
    main(parser.parse_args())
