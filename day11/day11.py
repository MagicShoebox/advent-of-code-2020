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
    part1 = runUntilStable(ferry, args.empty, args.occupied)
    print(np.count_nonzero(part1 == args.occupied))


def runUntilStable(ferry: np.ndarray, empty: str, occupied: str) -> np.ndarray:
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


if __name__ == '__main__':
    parser = MainArgs(description='Seating simulation ala Conway\'s'
                                  ' Game of Life')
    main(parser.parse_args())
