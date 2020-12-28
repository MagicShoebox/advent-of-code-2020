import pathlib
from typing import NewType
from typing import TextIO
from tap import Tap

Cup = NewType('Cup', int)


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a starting cup order

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        cups = readCups(file)
    part1 = cupGame(cups[:], 100)
    print(''.join(str(part1[(part1.index(Cup(1)) + i) % len(part1)]) for i in range(1, len(part1))))

    # cups = cups + [Cup(i) for i in range(max(cups) + 1, 10 ** 6 + 1)]
    # part2 = cupGame(cups, 10 ** 7)
    # index = cups.index(Cup(1))
    # print(cups[index + 1] * cups[index + 2])


def cupGame(cups: list[Cup], moves: int):
    minCup, maxCup = min(cups), max(cups)
    # This would be more easily done with a circular linked list,
    # but Python doesn't ship with one and I didn't feel like writing it
    index = 0
    for _ in range(moves):
        current = cups[index]
        moving = []
        for _ in range(3):
            if index + 1 == len(cups):
                moving.append(cups.pop((index + 1) % len(cups)))
                index -= 1
            else:
                moving.append(cups.pop((index + 1) % len(cups)))
        target = current - 1 if current > minCup else maxCup
        while target in moving:
            target = target - 1 if target > minCup else maxCup
        destination = cups.index(target) + 1
        if destination <= index:
            index += len(moving)  # Don't wrap early, wait till end of loop
        while moving:
            cups.insert(destination, moving.pop())
        index = (index + 1) % len(cups)
    return cups


def readCups(file: TextIO) -> list[Cup]:
    return [Cup(int(x)) for x in list(next(file).rstrip())]


if __name__ == '__main__':
    parser = MainArgs(description='Cup reordering')
    main(parser.parse_args())
