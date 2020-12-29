import pathlib
from typing import Literal
from typing import TextIO

from tap import Tap

Direction = Literal['ne', 'e', 'se', 'sw', 'w', 'nw']


class MainArgs(Tap):
    file: pathlib.Path  # A text file with two public keys
    base: int  # The base for each public key
    prime: int  # A prime

    def configure(self):
        self.add_argument('file', type=pathlib.Path)
        self.add_argument('base')
        self.add_argument('prime')


def main(args: MainArgs):
    with args.file.open('r') as file:
        key1, key2 = readPublicKeys(file)
    secret1 = crack(key1, args.base, args.prime)
    print(modPower(key2, secret1, args.prime))


def crack(key: int, base: int, prime: int) -> int:
    x = 1
    k = 0
    while x != key:
        k += 1
        x = x * base % prime
    return k


def modPower(base: int, exponent: int, mod: int):
    x = 1
    for _ in range(exponent):
        x = x * base % mod
    return x


def readPublicKeys(file: TextIO) -> tuple[int, int]:
    return int(next(file)), int(next(file))


if __name__ == '__main__':
    parser = MainArgs(description='Public-Private Key Encryption (sort of)')
    main(parser.parse_args())
