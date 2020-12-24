import pathlib
import re
from math import prod
from typing import TextIO

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of rules and sample data

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        rules, myTicket, tickets = readFile(file)

    print(sum(value
              for ticket in tickets
              for value in ticket
              if not any(valid(value) for valid in rules.values())))

    tickets = [ticket
               for ticket in tickets
               if all(any(valid(value) for valid in rules.values()) for value in ticket)]

    ticketColumns = ([ticket[i] for ticket in tickets] for i in range(len(rules)))

    possibleFields = [{field
                       for field, valid in rules.items()
                       if all(valid(value) for value in column)}
                      for column in ticketColumns]

    while any(len(possibleField) > 1 for possibleField in possibleFields):
        for certainField in (x for x in possibleFields if len(x) == 1):
            for possibleField in (x for x in possibleFields if x is not certainField):
                possibleField.difference_update(certainField)

    print(prod(myTicket[index]
               for index, field
               in enumerate(possibleFields)
               if field.pop().split()[0] == 'departure'))


def readFile(file: TextIO):
    rules = {}
    rulePattern = \
        re.compile(r'^(?P<field>[\w ]+): (?P<lower1>\d+)-(?P<upper1>\d+) or (?P<lower2>\d+)-(?P<upper2>\d+)\s*$')

    for line in file:
        if not (match := rulePattern.match(line)):
            break
        lower1 = int(match.group('lower1'))
        upper1 = int(match.group('upper1'))
        lower2 = int(match.group('lower2'))
        upper2 = int(match.group('upper2'))
        # https://stackoverflow.com/a/2295372/3491874
        # Use default parameters to capture the values in lambda
        rules[match.group('field')] = \
            lambda x, l1=lower1, u1=upper1, l2=lower2, u2=upper2: l1 <= x <= u1 or l2 <= x <= u2

    next(file)  # Header
    myTicket = [int(x) for x in next(file).split(',')]
    next(file)  # Blank line

    tickets = []
    next(file)  # Header
    for line in file:
        tickets.append([int(x) for x in line.split(',')])

    return rules, myTicket, tickets


if __name__ == '__main__':
    parser = MainArgs(description='Deduce order of fields'
                                  ' from field rules and sample data')
    main(parser.parse_args())
