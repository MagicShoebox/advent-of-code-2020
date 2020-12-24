import pathlib
from typing import Iterable

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of integers
    ordinal: int  # The ordinal of the number to return

    def configure(self):
        self.add_argument('file', type=pathlib.Path)
        self.add_argument('ordinal')


def main(args: MainArgs):
    with args.file.open('r') as file:
        starting = (int(line) for line in file)
        last = numbersGame(starting, args.ordinal)
    print(last)


def numbersGame(starting: Iterable[int], turns: int) -> int:
    turn = 0
    spoken = None
    priors = None
    numbers = dict()
    for spoken in starting:
        priors = numbers.setdefault(spoken, [])
        priors.append(turn)
        turn += 1
    while turn < turns:
        if len(priors) > 1:
            spoken = priors[-1] - priors.pop(0)
        else:
            spoken = 0
        priors = numbers.setdefault(spoken, [])
        priors.append(turn)
        turn += 1
    return spoken


if __name__ == '__main__':
    parser = MainArgs(description='Numbers game')
    main(parser.parse_args())
