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
    cups = cupGame(cups, 100, minCup, maxCup)
    cups = find(cups, 1)
    current = cups.next
    solution = ''
    while current != cups:
        solution += str(current.label)
        current = current.next
    print(solution)

    with args.file.open('r') as file:
        cups, minCup, maxCup = readCups(file, 10 ** 6)
    cups = cupGame(cups, 10 ** 7, minCup, maxCup)
    cups = find(cups, 1)
    print(cups.next.label * cups.next.next.label)


def cupGame(cups: Cup, moves: int, minCup: int, maxCup: int) -> Cup:
    labels = {cups.label: cups}
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


def readCups(file: TextIO, maxCup: int = None) -> tuple[Cup, int, int]:
    tail = None
    minCup = 10 ** 4
    maxRead = -1
    for digit in reversed(list(next(file).rstrip())):
        label = int(digit)
        if label > maxRead:
            maxRead = label
        if label < minCup:
            minCup = label
        tail = Cup(label, tail)
    head = tail
    while tail.next is not None:
        tail = tail.next

    if maxCup is None:
        maxCup = maxRead
        tail.next = head
    else:
        newTail = Cup(maxCup, head)
        for label in range(maxCup - 1, maxRead, -1):
            newTail = Cup(label, newTail)
        tail.next = newTail

    return head, minCup, maxCup


if __name__ == '__main__':
    parser = MainArgs(description='Cup reordering')
    main(parser.parse_args())
