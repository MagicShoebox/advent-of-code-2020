import pathlib
import typing
from collections import OrderedDict
from typing import List

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a series of integers

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        target = findNotInPriors(file)
        print(target)
        file.seek(0)
        sequence = findSumSequence(file, target)
        print(min(sequence) + max(sequence))


def findSumSequence(file: typing.TextIO, target: int) -> List[int]:
    sequence = []
    sum = 0
    for number in (int(line) for line in file):
        sequence.append(number)
        sum += number
        while sum > target:
            sum -= sequence.pop(0)
        if sum == target:
            return sequence


def findNotInPriors(file: typing.TextIO):
    numbers = iter(int(line) for line in file)
    priors = OrderedDict()
    for _ in range(25):
        priors[next(numbers)] = None
    while targetInPriors(priors, target := next(numbers)):
        del priors[firstKeyInOrderedDictionary(priors)]
        priors[target] = None
    return target


def targetInPriors(priors: OrderedDict[int], target: int) -> bool:
    for prior in priors:
        if target - prior in priors:
            return True
    return False


def firstKeyInOrderedDictionary(dictionary: OrderedDict):
    for key in dictionary:
        return key


if __name__ == '__main__':
    parser = MainArgs(description='Crack the XMAS cipher')
    main(parser.parse_args())
