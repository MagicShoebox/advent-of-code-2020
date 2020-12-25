import pathlib
import re
from functools import reduce
from typing import TextIO
from typing import Union

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of rules and data

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        rules, messages = readFile(file)

    print(sum(1
              for message in messages
              if rules[0](message) == ''))


def readFile(file: TextIO):
    rules = {}
    rulePattern = re.compile(r'^(?P<id>\d+): (?P<rule>.+)\s*$')
    exactPattern = re.compile(r'^"(?P<letter>\w+)"\s*$')

    for line in file:
        if not (match := rulePattern.match(line)):
            break
        id = int(match.group('id'))
        line = match.group('rule')
        if (match := exactPattern.match(line)):
            def exact(message: str, letter=match.group('letter')) -> Union[str, bool]:
                if len(message) >= len(letter) and message[:len(letter)] == letter:
                    return message[len(letter):]
                return False

            rules[id] = exact
        else:
            def nested(message: str, cases=tuple([int(id) for id in branch.split()] for branch in line.split('|'))) \
                    -> Union[str, bool]:
                cases = (reduce(
                    lambda m, f: False if m is False else f(m),
                    (rules[id] for id in case),
                    message)
                    for case in cases)
                result = [c for c in cases if c is not False]
                if result:
                    return result[0]
                return False

            rules[id] = nested

    messages = []
    for line in file:
        messages.append(line.rstrip())

    return rules, messages


if __name__ == '__main__':
    parser = MainArgs(description='Apply nested pattern matching rules')
    main(parser.parse_args())
