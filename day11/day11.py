import pathlib

import numpy as np
from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a seating map
    empty: str  # The character to use for an empty seat
    occupied: str  # The character to use for an occupied seat

    def configure(self):
        self.add_argument('file', type=pathlib.Path)
        self.add_argument('empty')
        self.add_argument('occupied')


def main(args: MainArgs):
    with args.file.open('r') as file:
        ferry = np.genfromtxt(file, dtype=str, delimiter=1)
    part1Result = part1(ferry, args.empty, args.occupied)
    print(np.count_nonzero(part1Result == args.occupied))
    part2Result = part2(ferry, args.empty, args.occupied)
    print(np.count_nonzero(part2Result == args.occupied))


def part1(ferry: np.ndarray, empty: str, occupied: str) -> np.ndarray:
    update = np.array(['x'])
    while (update != '').any():
        # https://stackoverflow.com/a/53127289/3491874
        people = np.pad(np.where(ferry == occupied, 1, 0), 1)
        neighbors = np.sum([
            people[:-2, :-2],  # NW
            people[:-2, 1:-1],  # N
            people[:-2, 2:],  # NE
            people[1:-1, :-2],  # W
            people[1:-1, 2:],  # E
            people[2:, :-2],  # SW
            people[2:, 1:-1],  # S
            people[2:, 2:]  # SE
        ], 0)
        update = np.where(np.logical_and(ferry == empty, neighbors == 0), occupied, '')
        update = np.where(np.logical_and(ferry == occupied, neighbors >= 4), empty, update)
        ferry = np.where(update != '', update, ferry)
    return ferry


def part2(ferry: np.ndarray, empty: str, occupied: str) -> np.ndarray:
    addTuples = lambda x, y: tuple(sum(i) for i in zip(x, y))
    update = np.array(['x'])
    while (update != '').any():
        neighbors = np.zeros(ferry.shape, dtype=int)
        for index, value in np.ndenumerate(ferry):
            if value == empty or value == occupied:
                n = 0
                for direction in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    position = addTuples(index, direction)
                    while all(0 <= a < b for a, b in zip(position, ferry.shape)):
                        if ferry[position] == empty:
                            break
                        if ferry[position] == occupied:
                            n += 1
                            break
                        position = addTuples(position, direction)
                neighbors[index] = n
        update = np.where(np.logical_and(ferry == empty, neighbors == 0), occupied, '')
        update = np.where(np.logical_and(ferry == occupied, neighbors >= 5), empty, update)
        ferry = np.where(update != '', update, ferry)
    return ferry


if __name__ == '__main__':
    parser = MainArgs(description='Seating simulation ala Conway\'s'
                                  ' Game of Life')
    main(parser.parse_args())
