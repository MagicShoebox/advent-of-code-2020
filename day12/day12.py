import pathlib
import typing
from dataclasses import dataclass

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a series of directions

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


@dataclass
class Position:
    x: int  # W-0-E
    y: int  # S-0-N
    direction: int  # E,S,W,N


def main(args: MainArgs):
    with args.file.open('r') as file:
        position = part1(file)
        print(position)
        print(abs(position.x) + abs(position.y))
        file.seek(0)
        position = part2(file)
        print(position)
        print(abs(position.x) + abs(position.y))


def part1(file: typing.TextIO) -> Position:
    position = Position(0, 0, 0)
    for instruction, quantity in ((line[0], int(line[1:])) for line in file):
        if instruction in {'W', 'S', 'L'} or instruction == 'F' and position.direction in {1, 2}:
            quantity *= -1
        if instruction in {'L', 'R'}:
            position.direction = (position.direction + quantity // 90) % 4
        elif instruction in {'W', 'E'} or instruction == 'F' and position.direction % 2 == 0:
            position.x += quantity
        else:
            position.y += quantity

    return position


def part2(file: typing.TextIO) -> Position:
    ship = Position(0, 0, 0)  # Direction unused
    waypoint = Position(10, 1, 0)  # Relative to ship, direction unused
    for instruction, quantity in ((line[0], int(line[1:])) for line in file):
        if instruction in {'L', 'R'}:
            # https://en.wikipedia.org/wiki/Rotation_matrix
            cos = [1, 0, -1, 0][quantity // 90]
            sin = [0, 1, 0, -1][quantity // 90]
            if instruction == 'R':
                sin *= -1
            waypoint.x, waypoint.y = waypoint.x * cos - waypoint.y * sin, waypoint.x * sin + waypoint.y * cos
            continue
        if instruction in {'W', 'S'}:
            quantity *= -1
        if instruction in {'W', 'E'}:
            waypoint.x += quantity
        elif instruction in {'S', 'N'}:
            waypoint.y += quantity
        else:
            ship.x += waypoint.x * quantity
            ship.y += waypoint.y * quantity

    return ship


if __name__ == '__main__':
    parser = MainArgs(description='Summarize sequence'
                                  ' of movement instructions')
    main(parser.parse_args())
