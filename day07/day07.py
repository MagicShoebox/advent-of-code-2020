import pathlib
import re
import typing
from typing import List

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a series of records
    target: str  # The target node to count ancestors

    def configure(self):
        self.add_argument('file', type=pathlib.Path)
        self.add_argument('target')


def main(args: MainArgs):
    with args.file.open('r') as file:
        rules = readRules(file)
    print(len(getAncestors(rules, args.target)))
    print(sum(quantity for quantity, color in getDescendants(rules, args.target)))


def getAncestors(rules: List[tuple[str, List[tuple[int, str]]]], target: str) -> set[str]:
    parents = {}
    for parent, children in rules:
        for quantity, color in children:
            parents.setdefault(color, []).append(parent)

    nextParents = parents.get(target, [])
    ancestors = set()
    while nextParents:
        parent = nextParents.pop(0)
        nextParents.extend(parents.get(parent, []))
        ancestors.add(parent)
    return ancestors


def getDescendants(rules: List[tuple[str, List[tuple[int, str]]]], target: str) -> List[tuple[int, str]]:
    children = {parent: children for parent, children in rules}

    nextChildren: List[tuple[int, str]] = children.get(target, [])
    descendants = []
    while nextChildren:
        parentQuantity, parentColor = nextChildren.pop(0)
        nextChildren.extend((parentQuantity * childQuantity, childColor)
                            for childQuantity, childColor in children.get(parentColor, []))
        descendants.append((parentQuantity, parentColor))
    return descendants


def readRules(file: typing.TextIO) -> List[tuple[str, List[tuple[int, str]]]]:
    linePattern = re.compile(r'^(?P<parent>.+) bags contain (?P<children>.+)\.\s*$')
    childPattern = re.compile(r'^(?P<quantity>\d+) (?P<color>.+) bags?$')
    return [(parentMatch.group('parent'),
             [(int(childMatch.group('quantity')),
               childMatch.group('color'))
              for child in parentMatch.group('children').split(', ')
              if (childMatch := childPattern.match(child))])
            for line in file
            if (parentMatch := linePattern.match(line))]


if __name__ == '__main__':
    parser = MainArgs(description='Count the ancestors of a node'
                                  ' in a directed acyclic graph')
    main(parser.parse_args())
