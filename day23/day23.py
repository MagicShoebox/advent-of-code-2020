import pathlib
from dataclasses import dataclass
from typing import TextIO

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a starting cup order

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


@dataclass
class Cup:
    label: int
    next: 'Cup'


def main(args: MainArgs):
    with args.file.open('r') as file:
        cups, minCup, maxCup = readCups(file)
    part1 = cupGame(cups, 100, minCup, maxCup)
    cups = find(cups, 1)
    current = cups.next
    solution = ''
    while current != cups:
        solution += str(current.label)
        current = current.next
    print(solution)

    # cups = cups + [Cup(i) for i in range(max(cups) + 1, 10 ** 6 + 1)]
    # part2 = cupGame(cups, 10 ** 7)
    # index = cups.index(Cup(1))
    # print(cups[index + 1] * cups[index + 2])


def cupGame(cups: Cup, moves: int, minCup: int, maxCup: int):
    labels = {}
    labels[cups.label] = cups
    current = cups.next
    while current != cups:
        labels[current.label] = current
        current = current.next
    for _ in range(moves):
        moving = set()
        first = cups.next
        last = cups
        for _ in range(3):
            last = last.next
            moving.add(last.label)
        target = cups.label - 1 if cups.label > minCup else maxCup
        while target in moving:
            target = target - 1 if target > minCup else maxCup
        destination = labels[target]
        cups.next, destination.next, last.next = last.next, first, destination.next
        cups = cups.next
    return cups


def find(current: Cup, target: int) -> Cup:
    start = current
    while current.label != target:
        if current.next == start:
            return start
        current = current.next
    return current


def readCups(file: TextIO) -> tuple[Cup, int, int]:
    tail = None
    minCup = 10 ** 4
    maxCup = -1
    for digit in reversed(list(next(file).rstrip())):
        label = int(digit)
        if label > maxCup:
            maxCup = label
        if label < minCup:
            minCup = label
        tail = Cup(label, tail)
    head = tail
    while tail.next is not None:
        tail = tail.next
    tail.next = head
    return head, minCup, maxCup


if __name__ == '__main__':
    parser = MainArgs(description='Cup reordering')
    main(parser.parse_args())
