import pathlib
import typing

from tap import Tap

DIRECTION = typing.Literal['n', 'x', 'y']


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a field of characters to count across
    background: str  # The character to *not* count in the text field (ie ground)
    delta_x: int  # The horizontal part of the slope
    delta_y: int  # The vertical part of the slope
    wrap: DIRECTION  # Whether to wrap neither direction, the horizontal, or the vertical

    def configure(self):
        # TODO: validate args
        self.add_argument('file', type=pathlib.Path)
        self.add_argument('background')
        self.add_argument('delta_x')
        self.add_argument('delta_y')
        self.add_argument('wrap')


def main(args: MainArgs):
    with args.file.open('r') as file:
        print(countCharacters(file, args.background, args.delta_x, args.delta_y, args.wrap))


def countCharacters(file: typing.TextIO, background: str, delta_x: int, delta_y: int, wrap: DIRECTION) -> int:
    count = 0
    x_position = 0
    lines = iter(file)
    line = next(lines).rstrip()
    while True:
        delta_lines = delta_y
        while delta_lines > 0:
            try:
                line = next(lines).rstrip()
                delta_lines -= 1
            except StopIteration:
                if wrap != 'y':
                    break
                file.seek(0)
        if delta_lines > 0:
            break
        x_position += delta_x
        if x_position >= len(line):
            if wrap != 'x':
                break
            x_position %= len(line)
        if line[x_position] != background:
            count += 1
    return count


if __name__ == '__main__':
    parser = MainArgs(description='Count the number of characters encountered'
                                  ' in a repeating text field')
    main(parser.parse_args())
