import pathlib

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with expressions to evaluate

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        print(sum(evaluate(line, set()) for line in file))
        file.seek(0)
        print(sum(evaluate(line, {'*'}) for line in file))


def evaluate(expression: str, deferred: set[str]) -> int:
    operations = {
        '+': lambda x, y: x + y,
        '*': lambda x, y: x * y
    }
    operands = []
    operators = []
    i = 0
    while i < len(expression):
        character = expression[i]
        if character.isspace():
            i += 1
            continue
        if character in {'+', '*'}:
            operators.append(character)
            i += 1
            continue
        j = i + 1
        if character.isdigit():
            while j < len(expression) and expression[j].isdigit():
                j += 1
            current = int(expression[i:j])
        else:
            depth = 1
            j = i + 1
            while j < len(expression) and depth > 0:
                if expression[j] == '(':
                    depth += 1
                elif expression[j] == ')':
                    depth -= 1
                j += 1
            current = evaluate(expression[i + 1:j - 1], deferred)
        i = j

        if not operands or operators[-1] in deferred:
            operands.append(current)
        else:
            operands.append(operations[operators.pop()](operands.pop(), current))

    while len(operators) > 0:
        operands.append(operations[operators.pop()](operands.pop(), operands.pop()))
    return operands[0]


if __name__ == '__main__':
    parser = MainArgs(description='Calculator with modified order of operations')
    main(parser.parse_args())
