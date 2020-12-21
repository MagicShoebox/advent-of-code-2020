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
        print(countPasswordsPart1(file))
        file.seek(0)
        print(countPasswordsPart2(file))


def countPasswordsPart1(file: typing.TextIO) -> int:
    linePattern = re.compile(r'^(?P<min>\d+)-(?P<max>\d+) (?P<letter>\w): (?P<password>\w+)$')
    # haha generator expression go brrrrrr
    return sum(1
               for line in file
               if (match := linePattern.match(line))
               and int(match.group('min')) <= match.group('password').count(match.group('letter')) <= int(
        match.group('max')))


def countPasswordsPart2(file: typing.TextIO) -> int:
    linePattern = re.compile(r'^(?P<index1>\d+)-(?P<index2>\d+) (?P<letter>\w): (?P<password>\w+)$')
    return sum(1
               for line in file
               if (match := linePattern.match(line))
               and ((password := match.group('password'))[int(match.group('index1')) - 1] == (
        letter := match.group('letter')))
               ^ (password[int(match.group('index2')) - 1] == letter))


if __name__ == '__main__':
    parser = MainArgs(description='Count the number of strings that'
                                  ' meet their specific requirements')
    main(parser.parse_args())
