import pathlib
import re
from functools import reduce
from typing import TextIO

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of rules and data

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        rules, messages = readFile(file)

    print(sum(1
              for result in (rules[0]({message})
                             for message in messages)
              if '' in result))


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
            def exact(messages: set[str], letter=match.group('letter')) -> set[str]:
                return {message[len(letter):]
                        for message in messages
                        if len(message) >= len(letter) and message[:len(letter)] == letter}

            rules[id] = exact
        else:
            def nested(messages: set[str],
                       cases=tuple([int(id) for id in branch.split()] for branch in line.split('|'))) \
                    -> set[str]:
                cases = (reduce(
                    lambda m, f: m if len(m) == 0 else f(m),
                    (rules[c] for c in case),
                    messages)
                    for case in cases)
                return {r for c in cases for r in c}

            rules[id] = nested

    messages = []
    for line in file:
        messages.append(line.rstrip())

    return rules, messages


if __name__ == '__main__':
    parser = MainArgs(description='Apply nested pattern matching rules')
    main(parser.parse_args())
