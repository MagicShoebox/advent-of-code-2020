import pathlib
import typing
from collections import Counter
from typing import List
import math

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of integers

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        jolts = readJolts(file)
    jolts = [0] + jolts + [jolts[-1] + 3]  # Socket and laptop
    gaps = [y - x for x, y in zip(jolts, jolts[1:])]
    frequencies = Counter(gaps)
    print(frequencies[1] * frequencies[3])
    # Gaps of length 3 cannot be changed
    # Runs of length 1 allow for multiple solutions
    runLengths = []
    runLength = 0
    for gap in gaps:
        if gap == 3:
            if runLength > 0:
                runLengths.append(runLength)
                runLength = 0
        else:
            runLength += 1
    print(math.prod(countCompositions(runLength, 3) for runLength in runLengths))


def countCompositions(target: int, maxPart: int) -> int:
    # Hope you like combinatorics
    # https://math.stackexchange.com/a/21779/821687
    # t = target, n = parts, m = max part
    # Generating function: $(x + x^2 + \cdots + x^m)^n$
    # After identities, $x^n\ \sum_{k=0}^n(-1)^k{n \choose k}x^{mk}\ \sum_{r=0}^\infty{r + n - 1 \choose r}x^r$
    # We want the coefficients x^t, so t=n+mk+r, n=1..target, k=0..floor((t-n)/m), r=t-n-mk
    compositions = 0
    for n in range(1, target + 1):
        for k in range((target - n) // maxPart + 1):
            r = target - n - maxPart * k
            compositions += (-1)**k * math.comb(n, k) * math.comb(r + n - 1, r)
    return compositions

def readJolts(file: typing.TextIO) -> List[int]:
    return sorted(int(line) for line in file)


if __name__ == '__main__':
    parser = MainArgs(description='Count the gaps in a list of integers')
    main(parser.parse_args())
