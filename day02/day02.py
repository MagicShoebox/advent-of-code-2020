import pathlib
import re
import typing

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of requirements and strings, one per line

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        count = countPasswords(file)
    print(count)


def countPasswords(file: typing.TextIO) -> int:
    linePattern = re.compile('^(?P<min>\d+)-(?P<max>\d+) (?P<letter>\w): (?P<password>\w+)$')
    # haha list comprehension go brrrrrr
    return sum(1
               for line in file
               if (match := linePattern.match(line))
               and int(match.group('min')) <= match.group('password').count(match.group('letter')) <= int(match.group('max')))


if __name__ == '__main__':
    parser = MainArgs(description='Count the number of strings that'
                                  ' meet their specific requirements')
    main(parser.parse_args())
